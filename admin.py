from django.contrib import admin

from .models import *


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("name", "body", "post", "created_on", "active", "sum_rate")
    list_filter = ("active", "created_on")
    search_fields = ("name", "body")
    actions = ["approve_comments"]

    def approve_comments(self, request, queryset):
        queryset.update(active=True)


@admin.register(UserRate)
class RateAdmin(admin.ModelAdmin):
    list_display = ("user", "post", "rating")
    list_filter = ("user", "post")
    search_fields = ("user", "post")


@admin.register(Post)
class RateAdmin(admin.ModelAdmin):
    list_display = ("title", "creator", "slug", "date_pub", "post_views", "rating")
    list_filter = ("creator",)
    search_fields = ("title", "body")


@admin.register(CommentRate)
class RateAdmin(admin.ModelAdmin):
    list_display = ("user", "post", "comment", "rate")


@admin.register(PostFile)
class RateAdmin(admin.ModelAdmin):
    list_display = ("post", "file")
    list_filter = ("post",)
