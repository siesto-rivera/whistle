from django.contrib import admin
from django.urls import path, include
from django.conf import settings

from whistle.views import (
    AboutView,
    WhistleHomeView,
    PublicWhistleListView,
    PublicWhistleDetailView,
    whistle_cheer_create,
    whistle_cheer_list_api,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("summernote/", include("django_summernote.urls")),
    # 관리자 페이지 (로그인 필요)
    path("dashboard/whistle/", include("whistle.urls")),
    # 공개 페이지
    path("", WhistleHomeView.as_view(), name="whistle_home"),
    path("about/", AboutView.as_view(), name="whistle_about"),
    path("cases/", PublicWhistleListView.as_view(), name="whistle_public_list"),
    path("<int:pk>/", PublicWhistleDetailView.as_view(), name="whistle_public_detail"),
    path("<int:pk>/cheer/", whistle_cheer_create, name="whistle_cheer_create"),
    path("<int:pk>/cheer/list/", whistle_cheer_list_api, name="whistle_cheer_list_api"),
]

if settings.DEBUG:
    urlpatterns += [
        path(route="__debug__/", view=include("debug_toolbar.urls")),
    ]

admin.site.site_header = "공익제보 아카이브"
admin.site.index_title = "관리자 페이지"
