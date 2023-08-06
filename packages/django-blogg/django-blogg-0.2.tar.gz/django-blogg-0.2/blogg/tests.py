from django.test import TestCase
from blogg.models import Post


class BlogPostTest(TestCase):
    def test_create_unpublished(self):
        entry = Post(title='Title Me', content=' ', author_id=1, published=False)
        entry.save()
        self.assertEqual(Post.objects.all().count(), 1)
        self.assertEqual(Post.objects.published().count(), 0)
        entry.published = True
        entry.save()
        self.assertEqual(Post.objects.published().count(), 1)


class BlogFeedTests(TestCase):
    def test_feed_url(self):
        response = self.client.get('/blog/rss/')
        self.assertIn("xml", response['Content-Type'])

