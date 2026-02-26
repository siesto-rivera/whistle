from django.db import models


class WhistleCase(models.Model):
    CATEGORY_CHOICES = [
        ("인권", "인권"),
        ("노동", "노동"),
        ("환경", "환경"),
        ("건강", "건강"),
        ("안전", "안전"),
        ("소비자이익", "소비자이익"),
        ("공정한 경쟁", "공정한 경쟁"),
        ("교육", "교육"),
        ("민주주의/행정공정성", "민주주의/행정공정성"),
        ("기타/침해영역", "기타/침해영역"),
    ]

    thumbnail = models.ImageField("썸네일", upload_to="whistle/thumbnails/", blank=True)
    title = models.CharField("사건명", max_length=150, default="")
    case_year = models.CharField("제보년도", max_length=4, default="")
    whistleblower = models.CharField("제보자 성명", max_length=100, default="")
    organization = models.CharField("제보대상기관", max_length=150, default="")
    category = models.CharField("공익침해영역", max_length=50, choices=CATEGORY_CHOICES, default="")
    tags = models.CharField("주요태그", max_length=255, default="")
    content = models.TextField("제보내용", blank=True)
    situation = models.TextField("제보자 상황", blank=True)
    awards = models.TextField("수상이력", blank=True)
    support = models.TextField("참여연대 지원", blank=True)
    media_coverage = models.TextField("미디어_언론보도", blank=True)
    media_detail = models.TextField("언론보도 내역", blank=True)
    media_photo = models.TextField("미디어_사진", blank=True)
    quote = models.TextField("제보자 한마디", blank=True)
    hidden_violation = models.TextField("비공개_위반행위", blank=True)
    hidden_disadvantage = models.TextField("비공개_불이익상세", blank=True)
    memo = models.TextField("참고", blank=True)
    hide = models.BooleanField("비공개", default=False)

    class Meta:
        verbose_name = "공익제보 사건"
        verbose_name_plural = "공익제보 사건"

    def __str__(self):
        return self.title


class WhistleTimeline(models.Model):
    case = models.ForeignKey(WhistleCase, on_delete=models.CASCADE)
    rdate = models.DateField("날짜", null=True)
    title = models.CharField("제목", max_length=150, default="")
    contents = models.TextField("내용", blank=True)

    class Meta:
        verbose_name = "타임라인"
        verbose_name_plural = "타임라인"

    def __str__(self):
        return self.title


class WhistleCheer(models.Model):
    case = models.ForeignKey(WhistleCase, on_delete=models.CASCADE, related_name="cheers")
    author_name = models.CharField("작성자명", max_length=50)
    content = models.TextField("응원 메시지")
    created_at = models.DateTimeField("작성일", auto_now_add=True)

    class Meta:
        verbose_name = "응원글"
        verbose_name_plural = "응원글"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.author_name} → {self.case.title}"


class WhistleArticle(models.Model):
    case = models.ForeignKey(WhistleCase, on_delete=models.CASCADE)
    rdate = models.DateField("날짜", null=True, blank=True)
    category = models.CharField("출처", max_length=50, default="")
    title = models.CharField("제목", max_length=150, default="")
    link = models.CharField("URL", max_length=255, default="")

    class Meta:
        verbose_name = "관련기사"
        verbose_name_plural = "관련기사"

    def __str__(self):
        return self.title
