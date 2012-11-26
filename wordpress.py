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

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kopi.settings")

from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.utils.timezone import utc

from author.models import Author
from blog.models import Post, Page
from inlines import parser

class WordpressParser:

    def __init__(self, filename):
        
        self.tree = ElementTree()
        self.tree.parse(filename)

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


    def findTags(self):
        channel = self.tree.find("channel")
        tags =  channel.getiterator("{http://wordpress.org/export/1.2/}tag")
        for tag in tags:
            slug = tag.find("{http://wordpress.org/export/1.2/}tag_slug").text
            name = tag.find("{http://wordpress.org/export/1.2/}tag_name").text
            

    def findItems(self):
        items = self.tree.getiterator("item")
        cpt_post = 0

        for item in items:
            item_type = item.find("{http://wordpress.org/export/1.2/}post_type").text
            item_title = item.find("title").text            
            if item_type == "attachment":
                pass
            elif item_type == "post":
                cpt_post += 1
                self.addPost(item)
            elif item_type == "page":
                pass

        print("Found {0} posts".format(cpt_post))


    def addPost(self, item):
        #print(item_type, item_title)
        title = item.find("title").text # Nouveau Blog!
        link = item.find("link").text # http://mart-e.be/?p=68 ou http://mart-e.be/post/nouveau-blog
        post_id = item.find("{http://wordpress.org/export/1.2/}post_id").text # 68
        pub_date = item.find("pubDate").text # Fri, 05 Feb 2010 11:14:00 +0000
        author = item.find("{http://purl.org/dc/elements/1.1/}creator").text # mart
        content = item.find("{http://purl.org/rss/1.0/modules/content/}encoded").text # the whole article
        slug = item.find("{http://wordpress.org/export/1.2/}post_name").text # nouveau-blog
        allow_comments = item.find("{http://wordpress.org/export/1.2/}comment_status").text # open
        status = item.find("{http://wordpress.org/export/1.2/}status").text # publish
        publish = item.find("{http://wordpress.org/export/1.2/}post_date").text # 2010-01-05 15:09:00
        # <category domain="post_tag" nicename="cryptographie"><![CDATA[cryptographie]]></category>
        # <category domain="category" nicename="gnu-linux"><![CDATA[GNU/Linux]]></category>
        # <category domain="post_tag" nicename="privacy"><![CDATA[privacy]]></category>
        # <category domain="post_tag" nicename="truecrypt"><![CDATA[truecrypt]]></category>
        
        posts = Post.objects.filter(slug=slug)
        if len(posts) != 0:
            print("Skipping {0}".format(slug))
            return posts[0]

        print("Creating post '"+title+"'")
        #print("Creating post '{0}'".format(title.decode('utf-8')))
        post = Post()
        post.title = title
        if slug:
            post.slug = slug[:50]
        else:
            post.slug = slugify(title)[:50]
        if author != self.author_name:
            raise Exception("Unknown author {0}".format(author))
        post.author = self.author
        post.body = content
        post.body_html = markdown(parser.inlines(content), output_format="html5")
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
        # still tags to do
        
        post.save()
        return post


if __name__ == "__main__":
    #execute_from_command_line("syncdb")
    
    wp = WordpressParser("wordpress.xml")
    wp.identifyAuthor()
    wp.findTags()
    wp.findItems()
