#!/usr/bin/env python2
#
# Parse an wordpress xml export file
# create the author
# import the posts 
#
# <rss version="2.0"
# 	xmlns:excerpt="http://wordpress.org/export/1.2/excerpt/"
# 	xmlns:content="http://purl.org/rss/1.0/modules/content/"
# 	xmlns:wfw="http://wellformedweb.org/CommentAPI/"
# 	xmlns:dc="http://purl.org/dc/elements/1.1/"
# 	xmlns:wp="http://wordpress.org/export/1.2/"
# >
#

from xml.etree.ElementTree import ElementTree
from markdown import markdown
from datetime import datetime
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kopi.settings")

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.files import File
from django.template.defaultfilters import slugify
from django.utils.timezone import utc

from author.models import Author
from blog.models import Post, Page
from comments.models import KopiComment
from media.models import Photo
from tagging.models import Tag
from inlines import parser

class WordpressParser:

    def __init__(self, xml_file, wp_content_dir):
        
        self.tree = ElementTree()
        self.tree.parse(xml_file)
        self.wp_content = wp_content_dir

    def identifySite(self):
        print("Identifying site")
        channel = self.tree.find("channel")
        title = channel.find("title").text
        url = channel.find("{http://wordpress.org/export/1.2/}base_site_url").text
        current_site = Site.objects.get_current()
        current_site.name = title
        current_site.domain = url[7:] # remove http://
        current_site.save()
        self.site = current_site

    def identifyAuthor(self):
        print("Creating author")
        channel = self.tree.find("channel")
        author_tree = channel.find("{http://wordpress.org/export/1.2/}author")
        self.author_name = author_tree.find("{http://wordpress.org/export/1.2/}author_login").text
        author_email = author_tree.find("{http://wordpress.org/export/1.2/}author_email").text

        users = User.objects.filter(username = self.author_name)
        if len(users) == 0:
            print("Creating user {0} with password 'password', don't forget to change it...".format(self.author_name))
            admin = User.objects.create_user(self.author_name, author_email, "password")
            admin.is_superuser = True
            admin.is_staff = True
            admin.save()
        else:
            print("User {0} found, skipping".format(users[0].username))
            admin = users[0]
        
        authors = Author.objects.filter(user = admin)
        if len(authors) == 0:
            print("Creating author for user {0}".format(admin.username))
            author = Author()
            author.user = admin
            author.save()
            self.author = author
        else:
            print("Author {0} present, skipping".format(authors[0].user.username))
            self.author = authors[0]
            

    def findItems(self):
        items = self.tree.getiterator("item")
        cpt_post = 0
        cpt_page = 0
        cpt_media = 0

        for item in items:
            item_type = item.find("{http://wordpress.org/export/1.2/}post_type").text
            item_title = item.find("title").text            
            if item_type == "attachment":
                if self.addMedia(item):
                    cpt_media += 1
            elif item_type == "post":
                cpt_post += 1
                self.addPost(item)
            elif item_type == "page":
                cpt_page += 1
                self.addPage(item)

        print("Found {0} posts, {1} pages and {2} medias".format(cpt_post, cpt_page, cpt_media))


    def addPost(self, item):
        #print(item_type, item_title)
        title = item.find("title").text # Nouveau Blog!
        link = item.find("link").text # http://mart-e.be/?p=68 ou http://mart-e.be/post/nouveau-blog
        post_id = item.find("{http://wordpress.org/export/1.2/}post_id").text # 68
        pub_date = item.find("pubDate").text # Fri, 05 Feb 2010 11:14:00 +0000
        author = item.find("{http://purl.org/dc/elements/1.1/}creator").text # mart
        content = item.find("{http://purl.org/rss/1.0/modules/content/}encoded").text # the whole article
        slug = item.find("{http://wordpress.org/export/1.2/}post_name").text # nouveau-blog (CAN BE EMPTY)
        allow_comments = item.find("{http://wordpress.org/export/1.2/}comment_status").text # open
        status = item.find("{http://wordpress.org/export/1.2/}status").text # publish
        publish = item.find("{http://wordpress.org/export/1.2/}post_date").text # 2010-01-05 15:09:00
        
        if slug:
            posts = Post.objects.filter(slug=slug)
        else:
            posts = Post.objects.filter(id=int(post_id))
        if len(posts) != 0:
            print("Skipping {0}".format(posts[0].slug))
            return posts[0]

        try:
            print("Creating post '"+title+"'")
        except:
            print("Creating post #"+post_id)
        #print("Creating post '{0}'".format(title.decode('utf-8')))
        post = Post()
        post.title = title
        post.id = post_id
        if slug:
            post.slug = slug[:50]
        else:
            post.slug = slugify(title)[:50]
        if author != self.author_name:
            raise Exception("Unknown author {0}".format(author))
        post.author = self.author
        post.body = content
        #post.body_html = markdown(parser.inlines(content), output_format="html5")
        # in wordpress don't use markdown
        post.body_html = post.body
        
        if status == "publish":
            post.status = 2
        else:
            post.status = 1
        if allow_comments == "open":
            post.allow_comments = True
        else:
            post.allow_comments = False
        post.publish = datetime.strptime(publish,"%Y-%m-%d %H:%M:%S").replace(tzinfo=utc)
        post.created = post.publish # really, who cares about that
        post.modifier = post.publish # still don't care
        
        post.save()

        self.addComments(item, post)

        self.addTags(item, post)
        
        return post

    def addPage(self, item):
        title = item.find("title").text # About
        link = item.find("link").text # http://mart-e.be/?p=2 ou http://mart-e.be/about
        page_id = item.find("{http://wordpress.org/export/1.2/}post_id").text # 2
        author = item.find("{http://purl.org/dc/elements/1.1/}creator").text # mart
        content = item.find("{http://purl.org/rss/1.0/modules/content/}encoded").text # the whole article
        slug = item.find("{http://wordpress.org/export/1.2/}post_name").text # nouveau-blog (CAN BE EMPTY)
        allow_comments = item.find("{http://wordpress.org/export/1.2/}comment_status").text # open
        status = item.find("{http://wordpress.org/export/1.2/}status").text # publish
        
        if slug:
            pages = Page.objects.filter(slug=slug)
        else:
            pages = Page.objects.filter(id=int(page_id))
        if len(pages) != 0:
            print("Skipping {0}".format(pages[0].slug))
            return pages[0]

        try:
            print("Creating page '"+title+"'")
        except:
            print("Creating page #"+page_id)
            
        page = Page()
        page.title = title
        page.id = page_id
        if slug:
            page.slug = slug[:50]
        else:
            page.slug = slugify(title)[:50]
        if author != self.author_name:
            raise Exception("Unknown author {0}".format(author))
        page.author = self.author
        page.body = content
        
        # in wordpress don't use markdown
        page.body_html = page.body
        
        if status == "publish":
            page.status = 2
        else:
            page.status = 1
        if allow_comments == "open":
            page.allow_comments = True
        else:
            page.allow_comments = False
                
        page.save()

        self.addComments(item, page)
        
        return page


    def addComments(self, item, target):
        """Parse `item` to find comments of `target`"""
        comments = item.getiterator("{http://wordpress.org/export/1.2/}comment")
        for comment in comments:
            comment_type = comment.find("{http://wordpress.org/export/1.2/}comment_type").text
            if comment_type == "pingback":
                # don't support pingback, not sure I will
                pass
            else:
                com = KopiComment()
                com.user_name = comment.find("{http://wordpress.org/export/1.2/}comment_author").text
                if not com.user_name:
                    com.user_name = ""
                com.user_email = comment.find("{http://wordpress.org/export/1.2/}comment_author_email").text
                if not com.user_email:
                    com.user_email = ""
                com.user_url = comment.find("{http://wordpress.org/export/1.2/}comment_author_url").text
                if not com.user_url:
                    com.user_url = ""
                com.comment = comment.find("{http://wordpress.org/export/1.2/}comment_content").text
                #com.comment_html = markdown(parser.inlines(com.comment), output_format="html5")
                comment_date = comment.find("{http://wordpress.org/export/1.2/}comment_date").text
                com.publish = datetime.strptime(comment_date,"%Y-%m-%d %H:%M:%S").replace(tzinfo=utc)
                
                com.content_type = ContentType.objects.get_for_model(target)
                com.object_pk = target.id
                com.site = self.site
                try:
                    com.save()
                except:
                    print("Error", com, com.user_url)


    def addTags(self,item,target):
        """Create the adequate tags
        
        TODO associate the tags to the post (one way so far)"""
        categories = item.getiterator("category")
        tags = ""
        for category in categories:
            if "domain" in category.attrib and category.attrib["domain"] == "post_tag":
                tags += category.attrib["nicename"] + " "
        target.tags = tags
        target.save()

    def addMedia(self,item):
        title = item.find("title").text # Ostrich reads newspaper
        link = item.find("link").text # http://mart-e.be/post/2013/01/18/media-id-la-presse-belge-evolue/3236806056_a0d1236ef3/
        media_id = item.find("{http://wordpress.org/export/1.2/}post_id").text # 2
        content = item.find("{http://purl.org/rss/1.0/modules/content/}encoded").text # the whole article
        slug = item.find("{http://wordpress.org/export/1.2/}post_name").text # nouveau-blog (CAN BE EMPTY)
        #allow_comments = item.find("{http://wordpress.org/export/1.2/}comment_status").text # open
        publish = item.find("{http://wordpress.org/export/1.2/}post_date").text # 2010-01-05 15:09:00
        
        attachment_url = item.find("{http://wordpress.org/export/1.2/}attachment_url").text
        if not attachment_url[-4:].lower() in [".jpg",".png",".gif"]:
            # TODO support other types            
            # raise Exception("Unknown file format {0}".format(attachment_url[-4:]))
            return False
        
        if slug:
            medias = Photo.objects.filter(slug=slug)
        else:
            medias = Page.objects.filter(id=int(media_id))
        if len(medias) != 0:
            print("Skipping {0}".format(medias[0].slug))
            return medias[0]

        try:
            print("Creating media '"+title+"'")
        except:
            print("Creating media #"+media_id)
            
        media = Photo()
        media.title = title
        media.id = media_id
        if slug:
            media.slug = slug[:50]
        else:
            media.slug = slugify(title)[:50]
        
        # move file
        # TODO use date from wordpress, not from today
        path = os.path.join(self.wp_content, attachment_url.split("wp-content/")[1])
        f = open(path, 'r')
        media.photo = File(f)

        publish = publish = datetime.strptime(publish,"%Y-%m-%d %H:%M:%S").replace(tzinfo=utc)
        media.uploaded = publish
        media.modified = publish
        media.save()        
        #media.save()
        f.close()


        return media

if __name__ == "__main__":
    #execute_from_command_line("syncdb")
    
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        xml_file = sys.argv[1]    
    else:
        xml_file = "wordpress.xml"

    if len(sys.argv) > 2 and os.path.isdir(sys.argv[2]):
        wp_content_dir = sys.argv[2]
    else:
        wp_content_dir = "wp-content"
        
    wp = WordpressParser(xml_file, wp_content_dir)
    wp.identifySite()
    wp.identifyAuthor()
    
    wp.findItems()
