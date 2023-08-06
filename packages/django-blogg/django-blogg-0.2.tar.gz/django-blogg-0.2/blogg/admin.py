from django.contrib import admin
from django.db.models import TextField
from django_markdown.admin import MarkdownModelAdmin
from django_markdown.widgets import AdminMarkdownWidget
from blogg.models import Post, Tag, Comment


class CommentInline(admin.TabularInline):
    model = Comment
    can_delete = False
    extra = 0


class PostAdmin(MarkdownModelAdmin):
    list_display = ['title', 'get_tags', 'created', 'modified', 'views', 'get_comments_count']
    list_filter = ['published', 'created', 'modified', 'tags']
    search_fields = ['title', 'teaser', 'content']
    save_on_top = True
    prepopulated_fields = {"slug": ("title",)}
    formfield_overrides = {TextField: {'widget': AdminMarkdownWidget}}
    inlines = [CommentInline]

    def get_tags(self, obj):
        return ", ".join([tag.slug for tag in obj.tags.all()])

    def get_comments_count(self, obj):
        total = obj.comments.count()
        published = obj.comments.published().count()
        return '%s/%s' % (published, total)
    get_comments_count.short_description = 'Comments'

    get_tags.short_description = 'Tags'

class TagAdmin(MarkdownModelAdmin):
    list_display = ['slug']
    search_fields = ['slug']
    save_on_top = True


admin.site.register(Post, PostAdmin)
admin.site.register(Tag, TagAdmin)
