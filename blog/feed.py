from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from blog.models import Post

class RSSPostFeed(Feed):
    title = "Kopi blog post"
    link = "/"
    description = "Latests blog posts"

    def items(self):
        return Post.objects.order_by('-publish')[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.body

class AtomPostFeed(RSSPostFeed):
	feed_type = Atom1Feed
	subtitle = RSSPostFeed.description