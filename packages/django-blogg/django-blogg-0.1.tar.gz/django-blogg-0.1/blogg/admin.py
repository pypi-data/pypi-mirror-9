from django.contrib import admin
from django.db.models import TextField
from django_markdown.admin import MarkdownModelAdmin
from django_markdown.widgets import AdminMarkdownWidget
from blogg.models import Post, Tag


class PostAdmin(MarkdownModelAdmin):
    list_display = ['title', 'created']
    list_filter = ['published', 'created']
    search_fields = ['title', 'content']
    date_hierarchy = 'created'
    save_on_top = True
    prepopulated_fields = {"slug": ("title",)}
    formfield_overrides = {TextField: {'widget': AdminMarkdownWidget}}


admin.site.register(Post, PostAdmin)
admin.site.register(Tag)
