from django.shortcuts import render, get_object_or_404
from blogg.models import Post, Tag


def index(request):
    posts = Post.objects.published()
    return render(request, 'blog/index.html', {'posts': posts})


def post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    post.increment_views()
    return render(request, 'blog/post.html', {'post': post})


def tag(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    posts = tag.posts.filter(published=True)
    return render(request, 'blog/index.html', {'posts': posts})
