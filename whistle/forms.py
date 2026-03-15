from datetime import date

from django import forms
from django_summernote.widgets import SummernoteWidget

from .models import WhistleCase, WhistleTimeline, WhistleArticle, WhistleCheer


class WhistleCaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        current_year = date.today().year
        min_year = WhistleCase.objects.exclude(case_year="").order_by("case_year").values_list("case_year", flat=True).first()
        start = int(min_year) if min_year else current_year
        choices = [("", "---------")] + [(str(y), str(y)) for y in range(start, current_year + 1)]
        self.fields["case_year"].widget = forms.Select(attrs={"class": "form-select"}, choices=choices)

    class Meta:
        model = WhistleCase
        fields = [
            "thumbnail", "title", "case_year", "whistleblower", "organization",
            "category", "tags", "content", "situation",
            "awards", "support", "media_coverage", "media_detail",
            "media_photo", "quote", "hidden_violation",
            "hidden_disadvantage", "memo", "hide",
        ]
        widgets = {
            "thumbnail": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "case_year": forms.TextInput(attrs={"class": "form-control", "maxlength": 4}),
            "whistleblower": forms.TextInput(attrs={"class": "form-control"}),
            "organization": forms.Select(attrs={"class": "form-select"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "tags": forms.HiddenInput(),
            "content": SummernoteWidget(),
            "situation": SummernoteWidget(),
            "awards": SummernoteWidget(),
            "support": SummernoteWidget(),
            "media_coverage": SummernoteWidget(),
            "media_detail": SummernoteWidget(),
            "media_photo": SummernoteWidget(),
            "quote": SummernoteWidget(),
            "hidden_violation": SummernoteWidget(),
            "hidden_disadvantage": SummernoteWidget(),
            "memo": SummernoteWidget(),
            "hide": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class WhistleTimelineForm(forms.ModelForm):
    class Meta:
        model = WhistleTimeline
        fields = ["case", "rdate", "title", "contents"]
        widgets = {
            "case": forms.HiddenInput(),
            "rdate": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "contents": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
        }


class WhistleCheerForm(forms.ModelForm):
    class Meta:
        model = WhistleCheer
        fields = ["author_name", "content"]
        widgets = {
            "author_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "이름"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "응원 메시지를 남겨주세요"}),
        }


class WhistleArticleForm(forms.ModelForm):
    class Meta:
        model = WhistleArticle
        fields = ["case", "rdate", "category", "title", "link"]
        widgets = {
            "case": forms.HiddenInput(),
            "rdate": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "category": forms.TextInput(attrs={"class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "link": forms.TextInput(attrs={"class": "form-control"}),
        }
