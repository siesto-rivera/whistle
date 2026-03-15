# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

공익제보 아카이브 (Public Whistleblower Archive) — 참여연대 공익제보지원센터에서 운영하는 공익제보자 사건 기록 및 관리 시스템. Django 4.0.7 기반, 공개 사이트와 관리자 패널 이중 구조.

## Commands

```bash
# 로컬 개발 (Python 3.9 venv 사용)
source venv/bin/activate
python manage.py runserver

# 마이그레이션
python manage.py makemigrations whistle
python manage.py migrate

# Docker 배포
docker-compose up --build

# 정적 파일 (S3 업로드)
python manage.py collectstatic
```

배포: `main` 브랜치에 push하면 GitHub Actions가 EC2에 자동 배포 (`.github/workflows/deploy.yml`).

## Architecture

**프로젝트 설정**: `config/` (settings, urls, wsgi, templates)
**앱**: `whistle/` (유일한 앱)

### 이중 인터페이스 구조

- **공개 사이트** (`/`, `/cases/`, `/<pk>/`): 로그인 불필요, Tailwind CSS, `layout_whistle.html` 베이스 또는 standalone HTML
- **관리 패널** (`/dashboard/whistle/`): `LoginRequiredMixin`, Bootstrap 5, `config/templates/layout.html` 베이스 (사이드바 + 네비바)

### 모델 관계

`WhistleCase` ← FK ← `WhistleTimeline`, `WhistleArticle`, `WhistleCheer`
- Case의 `hide` 필드로 공개/비공개 제어
- Cheer는 공개 사이트에서 비로그인 사용자가 작성 가능 (JSON API)

### URL 구조

- `config/urls.py`: 공개 페이지 + admin + summernote + `include("whistle.urls")` at `dashboard/whistle/`
- `whistle/urls.py` (`app_name="whistle"`): 대시보드, CRUD 뷰, API 엔드포인트

### 템플릿 상속

- 관리 페이지: `{% extends "layout.html" %}` → `config/templates/layout.html`
- 공개 페이지: `layout_whistle.html` 또는 standalone (home.html, public_list.html, public_detail.html)
- 공용 컴포넌트: `_pagination.html`, `_whistle_autocomplete.html`

### 핵심 의존성

- `django-summernote`: 리치 텍스트 에디터 (WhistleCaseForm의 content 필드들)
- `django-storages` + `boto3`: AWS S3 정적/미디어 파일
- `PyMySQL`: MySQL 연결 (pymysql.install_as_MySQLdb())
- `django-dotenv`: .env 파일 로드 (manage.py에서 호출)

## Key Conventions

- 모든 관리 뷰는 `LoginRequiredMixin` 사용, `LOGIN_URL = "/admin/login/"`
- 한국어 UI (LANGUAGE_CODE = "ko-kr", TIME_ZONE = "Asia/Seoul")
- 이 프로젝트는 기존 django_watch 프로젝트와 **같은 MySQL DB를 공유** — whistle 테이블만 관리하며 다른 앱 테이블에 영향 없음
- 환경변수: MYSQL_HOST, MYSQL_DB, MYSQL_USERNAME, MYSQL_PASSWORD, AWS_* (.env 파일)
