from django.contrib import admin
from django_summernote.admin import SummernoteModelAdminMixin

from whistle.models import WhistleCase, WhistleTimeline, WhistleArticle, WhistleCheer


@admin.register(WhistleCase)
class WhistleCaseAdmin(SummernoteModelAdminMixin, admin.ModelAdmin):
    list_display = (
        "title",
        "case_year",
        "whistleblower",
        "organization",
        "category",
        "tags",
        "hide",
    )
    search_fields = ("title", "whistleblower",)
    summernote_fields = (
        "content",
        "situation",
        "awards",
        "support",
        "media_coverage",
        "media_detail",
        "media_photo",
        "quote",
        "hidden_violation",
        "hidden_disadvantage",
        "memo",
    )


@admin.register(WhistleTimeline)
class WhistleTimelineAdmin(admin.ModelAdmin):
    list_display = (
        "case",
        "rdate",
        "title",
        "contents",
    )
    raw_id_fields = ("case",)
    search_fields = ("case__title",)
    search_help_text = "검색항목:사건명"


@admin.register(WhistleCheer)
class WhistleCheerAdmin(admin.ModelAdmin):
    list_display = ("case", "author_name", "short_content", "created_at")
    search_fields = ("case__title", "author_name")
    search_help_text = "검색항목:사건명, 작성자"
    raw_id_fields = ("case",)

    @admin.display(description="내용")
    def short_content(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content


@admin.register(WhistleArticle)
class WhistleArticleAdmin(admin.ModelAdmin):
    list_display = (
        "case",
        "rdate",
        "category",
        "title",
        "link",
    )
    raw_id_fields = ("case",)
    search_fields = ("case__title",)
    search_help_text = "검색항목:사건명"
