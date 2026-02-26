from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import formats
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView

from .forms import WhistleCaseForm, WhistleTimelineForm, WhistleArticleForm, WhistleCheerForm
from .models import WhistleCase, WhistleTimeline, WhistleArticle, WhistleCheer


# ── 공개 페이지 (로그인 불필요) ────────────────────────────────


class WhistleHomeView(TemplateView):
    template_name = "whistle/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recent_cases"] = WhistleCase.objects.filter(hide=False).order_by("-case_year", "-id")[:6]
        context["recent_cheers"] = WhistleCheer.objects.select_related("case").order_by("-created_at")[:6]
        context["total_cases"] = WhistleCase.objects.filter(hide=False).count()
        context["total_cheers"] = WhistleCheer.objects.count()
        return context


class PublicWhistleListView(ListView):
    model = WhistleCase
    context_object_name = "cases"
    template_name = "whistle/public_list.html"
    paginate_by = 12

    def get_queryset(self):
        queryset = WhistleCase.objects.filter(hide=False).order_by("-case_year", "-id")
        q = self.request.GET.get("q", "").strip()
        category = self.request.GET.get("category", "").strip()
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q)
                | Q(whistleblower__icontains=q)
                | Q(organization__icontains=q)
                | Q(category__icontains=q)
                | Q(tags__icontains=q)
                | Q(content__icontains=q)
                | Q(situation__icontains=q)
                | Q(awards__icontains=q)
                | Q(support__icontains=q)
                | Q(quote__icontains=q)
                | Q(media_coverage__icontains=q)
                | Q(media_detail__icontains=q)
            )
        if category:
            queryset = queryset.filter(category=category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "").strip()
        context["current_category"] = self.request.GET.get("category", "").strip()
        context["categories"] = WhistleCase.CATEGORY_CHOICES
        return context


class PublicWhistleDetailView(DetailView):
    model = WhistleCase
    template_name = "whistle/public_detail.html"
    context_object_name = "case"

    def get_queryset(self):
        return WhistleCase.objects.filter(hide=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["timelines"] = WhistleTimeline.objects.filter(case=self.object).order_by("-rdate")
        context["articles"] = WhistleArticle.objects.filter(case=self.object)
        context["cheer_form"] = WhistleCheerForm()
        if self.object.tags:
            context["tag_list"] = [t.strip() for t in self.object.tags.split(",") if t.strip()]
        return context


# ── API ──────────────────────────────────────────────────────


def whistle_search_api(request):
    """공익제보 사건 제목 검색 JSON API — 자동완성용"""
    q = request.GET.get("q", "").strip()
    if len(q) < 1:
        return JsonResponse([], safe=False)
    cases = WhistleCase.objects.filter(title__icontains=q).order_by("-case_year", "-id")[:20]
    results = [
        {"id": c.pk, "title": c.title}
        for c in cases
    ]
    return JsonResponse(results, safe=False)


# ── 관리 대시보드 ────────────────────────────────────────────────


class WhistleDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "whistle/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_cases"] = WhistleCase.objects.count()
        context["public_cases"] = WhistleCase.objects.filter(hide=False).count()
        context["hidden_cases"] = WhistleCase.objects.filter(hide=True).count()
        context["total_timelines"] = WhistleTimeline.objects.count()
        context["total_articles"] = WhistleArticle.objects.count()
        context["total_cheers"] = WhistleCheer.objects.count()
        context["recent_cases"] = WhistleCase.objects.order_by("-id")[:5]
        context["recent_cheers"] = WhistleCheer.objects.select_related("case").order_by("-created_at")[:5]
        context["categories"] = (
            WhistleCase.objects.filter(hide=False)
            .values_list("category", flat=True)
        )
        # 카테고리별 건수
        from django.db.models import Count
        context["category_stats"] = (
            WhistleCase.objects.filter(hide=False)
            .values("category")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        return context


# ── 공익제보 사건 ─────────────────────────────────────────────────


class WhistleCaseListView(LoginRequiredMixin, ListView):
    model = WhistleCase
    context_object_name = "cases"
    template_name = "whistle/whistle_list.html"
    paginate_by = 30

    def get_queryset(self):
        queryset = WhistleCase.objects.order_by("-case_year", "-id")
        q = self.request.GET.get("q", "").strip()
        category = self.request.GET.get("category", "").strip()
        if q:
            queryset = queryset.filter(title__icontains=q)
        if category:
            queryset = queryset.filter(category=category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "").strip()
        context["current_category"] = self.request.GET.get("category", "").strip()
        context["categories"] = WhistleCase.CATEGORY_CHOICES
        return context


class WhistleCaseDetailView(LoginRequiredMixin, DetailView):
    model = WhistleCase
    template_name = "whistle/whistle_detail.html"
    context_object_name = "case"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["timelines"] = WhistleTimeline.objects.filter(case=self.object).order_by("-rdate")
        context["articles"] = WhistleArticle.objects.filter(case=self.object)
        return context


class WhistleCaseCreateView(LoginRequiredMixin, CreateView):
    model = WhistleCase
    form_class = WhistleCaseForm
    template_name = "whistle/whistle_form.html"

    def get_success_url(self):
        return reverse_lazy("whistle:case_detail", kwargs={"pk": self.object.pk})


class WhistleCaseUpdateView(LoginRequiredMixin, UpdateView):
    model = WhistleCase
    form_class = WhistleCaseForm
    template_name = "whistle/whistle_form.html"

    def get_success_url(self):
        return reverse_lazy("whistle:case_detail", kwargs={"pk": self.object.pk})


# ── 타임라인 ─────────────────────────────────────────────────


class WhistleTimelineListView(LoginRequiredMixin, ListView):
    model = WhistleTimeline
    context_object_name = "timelines"
    template_name = "whistle/timeline_list.html"
    paginate_by = 30

    def get_queryset(self):
        queryset = WhistleTimeline.objects.select_related("case").order_by("-rdate", "-id")
        q = self.request.GET.get("q", "").strip()
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) | Q(case__title__icontains=q)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "").strip()
        return context


class WhistleTimelineDetailView(LoginRequiredMixin, DetailView):
    model = WhistleTimeline
    template_name = "whistle/timeline_detail.html"
    context_object_name = "timeline"


class WhistleTimelineCreateView(LoginRequiredMixin, CreateView):
    model = WhistleTimeline
    form_class = WhistleTimelineForm
    template_name = "whistle/timeline_form.html"

    def get_success_url(self):
        return reverse_lazy("whistle:timeline_detail", kwargs={"pk": self.object.pk})


class WhistleTimelineUpdateView(LoginRequiredMixin, UpdateView):
    model = WhistleTimeline
    form_class = WhistleTimelineForm
    template_name = "whistle/timeline_form.html"

    def get_success_url(self):
        return reverse_lazy("whistle:timeline_detail", kwargs={"pk": self.object.pk})


# ── 관련기사 ─────────────────────────────────────────────────


class WhistleArticleListView(LoginRequiredMixin, ListView):
    model = WhistleArticle
    context_object_name = "articles"
    template_name = "whistle/article_list.html"
    paginate_by = 30

    def get_queryset(self):
        queryset = WhistleArticle.objects.select_related("case").order_by("-id")
        q = self.request.GET.get("q", "").strip()
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) | Q(case__title__icontains=q)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "").strip()
        return context


class WhistleArticleDetailView(LoginRequiredMixin, DetailView):
    model = WhistleArticle
    template_name = "whistle/article_detail.html"
    context_object_name = "article"


class WhistleArticleCreateView(LoginRequiredMixin, CreateView):
    model = WhistleArticle
    form_class = WhistleArticleForm
    template_name = "whistle/article_form.html"

    def get_success_url(self):
        return reverse_lazy("whistle:article_detail", kwargs={"pk": self.object.pk})


class WhistleArticleUpdateView(LoginRequiredMixin, UpdateView):
    model = WhistleArticle
    form_class = WhistleArticleForm
    template_name = "whistle/article_form.html"

    def get_success_url(self):
        return reverse_lazy("whistle:article_detail", kwargs={"pk": self.object.pk})


# ── 응원글 (공개) ────────────────────────────────────────────


def _format_dt(dt):
    return f"{dt.year}.{dt.month}.{dt.day} {dt.strftime('%H:%M')}"


def whistle_cheer_list_api(request, pk):
    """응원글 목록 JSON API"""
    case = get_object_or_404(WhistleCase, pk=pk, hide=False)
    cheers = case.cheers.all()[:50]
    data = [
        {
            "author_name": c.author_name,
            "content": c.content,
            "created_at": _format_dt(c.created_at),
        }
        for c in cheers
    ]
    return JsonResponse({"cheers": data, "count": len(data)})


@require_POST
def whistle_cheer_create(request, pk):
    case = get_object_or_404(WhistleCase, pk=pk, hide=False)
    form = WhistleCheerForm(request.POST)
    if form.is_valid():
        cheer = form.save(commit=False)
        cheer.case = case
        cheer.save()
        return JsonResponse({
            "ok": True,
            "cheer": {
                "author_name": cheer.author_name,
                "content": cheer.content,
                "created_at": _format_dt(cheer.created_at),
            },
        })
    return JsonResponse({"ok": False, "errors": form.errors}, status=400)


# ── 응원글 (관리자) ──────────────────────────────────────────


class WhistleCheerListView(LoginRequiredMixin, ListView):
    model = WhistleCheer
    context_object_name = "cheers"
    template_name = "whistle/cheer_list.html"
    paginate_by = 30

    def get_queryset(self):
        queryset = WhistleCheer.objects.select_related("case").order_by("-created_at")
        q = self.request.GET.get("q", "").strip()
        if q:
            queryset = queryset.filter(
                Q(author_name__icontains=q) | Q(case__title__icontains=q)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "").strip()
        return context


@login_required
@require_POST
def whistle_cheer_delete(request, pk):
    cheer = get_object_or_404(WhistleCheer, pk=pk)
    cheer.delete()
    return redirect("whistle:cheer_list")
