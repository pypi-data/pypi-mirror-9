from django.contrib.syndication.views import Feed
from blogg.models import Post


class LatestPosts(Feed):
    title = "Blog"
    link = "/rss/"
    description = "Latest Posts"

    def items(self):
        return Post.objects.published()[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.teaser
