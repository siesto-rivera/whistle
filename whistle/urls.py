from django.urls import path
from . import views

app_name = "whistle"

urlpatterns = [
    # 대시보드
    path("", views.WhistleDashboardView.as_view(), name="dashboard"),
    # API
    path("api/whistle-search/", views.whistle_search_api, name="whistle_search_api"),
    path("api/tags/", views.tag_list_api, name="tag_list_api"),
    # 태그 통계
    path("tags/", views.TagStatsView.as_view(), name="tag_stats"),
    # 공익제보 사건
    path("cases/", views.WhistleCaseListView.as_view(), name="case_list"),
    path("<int:pk>/", views.WhistleCaseDetailView.as_view(), name="case_detail"),
    path("create/", views.WhistleCaseCreateView.as_view(), name="case_create"),
    path("<int:pk>/edit/", views.WhistleCaseUpdateView.as_view(), name="case_update"),
    # 타임라인
    path("timeline/", views.WhistleTimelineListView.as_view(), name="timeline_list"),
    path("timeline/<int:pk>/", views.WhistleTimelineDetailView.as_view(), name="timeline_detail"),
    path("timeline/<int:pk>/edit/", views.WhistleTimelineUpdateView.as_view(), name="timeline_update"),
    # 관련기사
    path("article/", views.WhistleArticleListView.as_view(), name="article_list"),
    path("article/<int:pk>/", views.WhistleArticleDetailView.as_view(), name="article_detail"),
    path("article/<int:pk>/edit/", views.WhistleArticleUpdateView.as_view(), name="article_update"),
    # 응원글
    path("cheer/", views.WhistleCheerListView.as_view(), name="cheer_list"),
    path("cheer/<int:pk>/delete/", views.whistle_cheer_delete, name="cheer_delete"),
]
