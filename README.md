# 공익제보 아카이브 (Whistle)

참여연대 공익제보지원센터에서 운영하는 공익제보자 사건 기록 및 관리 시스템.

- **공개 사이트**: http://3.35.116.112/
- **관리 패널**: http://3.35.116.112/dashboard/whistle/

## 기술 스택

- **Backend**: Django 4.0.7 / Python 3.9
- **Database**: MySQL (PyMySQL)
- **Storage**: AWS S3 (django-storages + boto3)
- **서버**: Gunicorn + Nginx (Docker)
- **배포**: GitHub Actions → EC2 자동 배포 (`main` push 시)

## 이중 인터페이스 구조

| 구분 | URL | 인증 | UI 프레임워크 | 베이스 템플릿 |
|------|-----|------|--------------|--------------|
| 공개 사이트 | `/`, `/cases/`, `/<pk>/` | 불필요 | Tailwind CSS | `layout_whistle.html` / standalone |
| 관리 패널 | `/dashboard/whistle/` | 필요 (`LoginRequiredMixin`) | Bootstrap 5 | `config/templates/layout.html` |

## 데이터 모델

```
WhistleCase (공익제보 사건)
├── WhistleTimeline (타임라인) ── FK
├── WhistleArticle (관련기사) ── FK
└── WhistleCheer (응원글) ── FK
```

### WhistleCase 주요 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `title` | CharField | 사건명 |
| `case_year` | CharField | 제보년도 (셀렉트 박스) |
| `whistleblower` | CharField | 제보자 성명 |
| `organization` | CharField | 신고대상 (choices: 7개 항목) |
| `category` | CharField | 공익침해분야 (choices: 6개 항목) |
| `tags` | CharField | 주요태그 (쉼표 구분 문자열) |
| `hide` | BooleanField | 공개/비공개 제어 |
| `content`, `situation`, `awards`, `support` 등 | TextField | 리치 텍스트 (Summernote) |

## URL 구조

### 공개 페이지
| URL | 뷰 | 설명 |
|-----|-----|------|
| `/` | `WhistleHomeView` | 홈페이지 |
| `/about/` | `AboutView` | 사이트 소개 |
| `/cases/` | `PublicWhistleListView` | 사건 목록 (필터: 공익침해분야, 신고대상) |
| `/<pk>/` | `PublicWhistleDetailView` | 사건 상세 |
| `/<pk>/cheer/` | `whistle_cheer_create` | 응원글 작성 API (POST) |
| `/<pk>/cheer/list/` | `whistle_cheer_list_api` | 응원글 목록 API |

### 관리 패널 (`/dashboard/whistle/`)
| URL | 뷰 | 설명 |
|-----|-----|------|
| ` ` | `WhistleDashboardView` | 대시보드 |
| `cases/` | `WhistleCaseListView` | 사건 목록 (검색, 필터, 정렬) |
| `<pk>/` | `WhistleCaseDetailView` | 사건 상세 (타임라인/관련기사 인라인 CRUD) |
| `create/` | `WhistleCaseCreateView` | 사건 등록 |
| `<pk>/edit/` | `WhistleCaseUpdateView` | 사건 수정 |
| `tags/` | `TagStatsView` | 태그 통계 |
| `timeline/` | `WhistleTimelineListView` | 타임라인 목록 |
| `article/` | `WhistleArticleListView` | 관련기사 목록 |
| `cheer/` | `WhistleCheerListView` | 응원글 관리 |
| `api/tags/` | `tag_list_api` | 기존 태그 목록 API (자동완성용) |
| `api/whistle-search/` | `whistle_search_api` | 사건 검색 API (자동완성용) |

## 주요 기능

### 사건 등록/수정 폼
- **제보년도**: DB 최소년도 ~ 현재년도 셀렉트 박스
- **신고대상**: 7개 항목 셀렉트 박스 (교육기관, 군·정보기관, 민간기업, 비영리단체, 수사·조사기관, 행정·공공기관, 기타)
- **공익침해분야**: 6개 항목 셀렉트 박스
- **주요태그**: 자동완성 + 직접입력 태그 칩 UI (`/api/tags/`에서 기존 태그 로드)

### 사건 상세 페이지 (관리)
- 타임라인: 인라인 추가/수정/삭제 (페이지 이동 없음)
- 관련기사: 인라인 추가/수정/삭제 (페이지 이동 없음)

### 사건 목록 (관리)
- 검색: 사건명, 제보자, 태그
- 필터: 공익침해분야, 신고대상 (조합 가능)
- 정렬: 사건명, 제보년도, 비공개 (오름차순/내림차순)

### 태그 통계
- 태그별 사건 수 집계
- 가나다순/건수순 정렬
- 태그 클릭 시 해당 사건 목록 표시

### 공개 사이트
- 카드 그리드 형태 사건 목록
- 필터: 공익침해분야, 신고대상
- 검색: 사건명, 제보자, 태그 등 전문 검색
- 응원글 작성 (비로그인 가능, JSON API)

## 로컬 개발

```bash
# 가상환경 활성화
source venv/bin/activate

# 서버 실행
python manage.py runserver

# 마이그레이션
python manage.py makemigrations whistle
python manage.py migrate

# 정적 파일 수집 (S3 업로드)
python manage.py collectstatic
```

## Docker 배포

```bash
docker-compose up --build
```

- **web**: Gunicorn (port 8000)
- **nginx**: 리버스 프록시 (port 80)

## 환경 변수 (.env)

| 변수 | 설명 |
|------|------|
| `MYSQL_HOST` | MySQL 호스트 |
| `MYSQL_DB` | 데이터베이스 이름 |
| `MYSQL_USERNAME` | MySQL 사용자 |
| `MYSQL_PASSWORD` | MySQL 비밀번호 |
| `AWS_STORAGE_BUCKET_NAME` | S3 버킷 이름 |
| `AWS_ACCESS_KEY_ID` | AWS 액세스 키 |
| `AWS_SECRET_ACCESS_KEY` | AWS 시크릿 키 |

## 프로젝트 구조

```
config/                     # Django 프로젝트 설정
├── settings.py
├── urls.py
├── wsgi.py
└── templates/
    ├── layout.html         # 관리 패널 베이스 (Bootstrap 5, 사이드바)
    └── _pagination.html

whistle/                    # 메인 앱
├── models.py               # 데이터 모델
├── views.py                # 뷰 (공개 + 관리)
├── forms.py                # 폼 (Summernote 위젯 포함)
├── urls.py                 # 관리 패널 URL (app_name="whistle")
├── admin.py                # Django Admin 설정
├── migrations/             # DB 마이그레이션
└── templates/whistle/
    ├── dashboard.html      # 대시보드
    ├── whistle_*.html      # 사건 CRUD
    ├── timeline_*.html     # 타임라인
    ├── article_*.html      # 관련기사
    ├── cheer_list.html     # 응원글 관리
    ├── tag_stats.html      # 태그 통계
    ├── home.html           # 공개 홈
    ├── public_list.html    # 공개 목록
    ├── public_detail.html  # 공개 상세
    └── about.html          # 사이트 소개

.github/workflows/
└── deploy.yml              # 자동 배포 (main push → EC2)
```

## 참고 사항

- 이 프로젝트는 기존 django_watch 프로젝트와 **같은 MySQL DB를 공유**합니다. whistle 테이블만 관리하며 다른 앱 테이블에 영향 없습니다.
- 타임라인/관련기사 추가는 사건 상세 페이지의 인라인 폼으로만 가능합니다 (독립 추가 페이지 없음).
- 응원글(`WhistleCheer`)은 공개 사이트에서 비로그인 사용자가 JSON API로 작성합니다.
- 리치 텍스트 필드는 `django-summernote` 위젯을 사용합니다.

## 의존성

| 패키지 | 버전 | 용도 |
|--------|------|------|
| Django | 4.0.7 | 웹 프레임워크 |
| django-bootstrap5 | 22.1 | Bootstrap 5 템플릿 |
| django-summernote | 0.8.20.0 | 리치 텍스트 에디터 |
| django-storages | 1.14.2 | S3 스토리지 백엔드 |
| django-dotenv | 1.4.2 | .env 파일 로드 |
| boto3 | 1.34.21 | AWS SDK |
| gunicorn | 20.1.0 | WSGI 서버 |
| Pillow | 9.2.0 | 이미지 처리 |
| PyMySQL | 1.1.0 | MySQL 커넥터 |
| django-debug-toolbar | 3.7.0 | 개발용 디버그 툴 |
