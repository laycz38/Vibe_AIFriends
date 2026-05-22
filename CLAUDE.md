# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

AIFriends is an interview-experience sharing community (AI 面经社区). Django 6.0 + Vue 3 + TailwindCSS v4 + daisyUI v5, SQLite for storage. The frontend builds into `backend/static/frontend/` and Django serves the SPA in production.

## Commands

```bash
# Backend dev server
cd backend && python manage.py runserver          # → :8000

# Frontend dev server (HMR, port 5173 fixed)
cd frontend && npm run dev                        # → :5173

# Production build (outputs to ../backend/static/frontend/)
cd frontend && npm run build

# Database migrations
cd backend && python manage.py makemigrations     # create
cd backend && python manage.py migrate            # apply
```

There are no tests or linters configured yet.

## Architecture

### Backend (Django)

Single Django app `web` contains everything — models, views, and URLs. The project-level `backend/` holds only settings and root URL config.

**Models** (`web/models.py`):
- `UserProfile` — 1:1 with `User`, stores `photo_base64` (text) and `bio`
- `InterviewNote` — the main content entity (title, content, company, position, difficulty, cover_base64, likes counter)
- `InterviewNoteLike` — unique constraint on (user, note), toggle pattern
- `InterviewNoteFavorite` — same toggle pattern with unique constraint
- `InterviewNoteComment` — FK to user + note, ordered by `-created_at`

Images are stored as **base64 strings in TextField columns**, not as file uploads. The `process_base64()` utility in `web/views/image_utils.py` handles compression.

**View patterns** — all function-based with `@api_view(['GET'/'POST'])` and `@permission_classes([...])`:
- Views are organized by feature: `views/note/`, `views/user/account/`, `views/chat/`, `views/tts/`
- Each view file exports a single function (e.g., `get_list`, `toggle_like`)
- Common serialization helpers live in `common.py` within each views subdirectory
- API response envelope: `{'result': 'success', ...}` or `{'result': 'error', 'message': '...'}`
- Auth: `AllowAny` for public endpoints, `IsAuthenticated` for protected ones

**TTS (语音合成)** — Aliyun DashScope CosyVoice (通义实验室生成式语音大模型) replaces browser SpeechSynthesis:
- `utils/aliyun_tts.py` — `synthesize()` returns full audio via SDK; `synthesize_stream()` yields chunks via `ResultCallback`
- `views/tts/synthesize.py` — `POST /api/tts/synthesize/`, returns `{audio: base64, format: 'mp3'}`
- `views/tts/stream.py` — `POST /api/tts/stream/`, returns `Content-Type: audio/mpeg` streaming response (首包 ~0.5s)
- Frontend uses `MediaSource` API for progressive playback: first chunk plays immediately, rest streams in
- Voices: `longanhuan` (female, 龙安欢) and `longanyang` (male, 龙安洋), configurable via `VOICE_MAP`
- Env var: `DASHSCOPE_API_KEY` (sk- prefix)
- Fallback chain: streaming → non-streaming SDK → browser `SpeechSynthesis`

**ASR (语音识别)** — DashScope WebSocket API, model `gummy-realtime-v1`:
- `views/tts/asr.py` — `POST /api/tts/asr/`, accepts PCM audio via FormData, returns `{result, text}`
- Browser VAD via `@ricky0123/vad-web` detects speech start/end, sends Float32→PCM16 to backend
- Microphone component (`components/chat/Microphone.vue`) handles VAD lifecycle
- Toggle mic/keyboard in chat input area; recognized text auto-fills and sends

**URL routing** — all routes in `web/urls.py` (not project-level). The last two patterns handle SPA fallback: `path('', index)` for `/` and `re_path(r'^(?!media/|static/|assets/).*$', index)` for all other frontend routes. Static/media files are only served by Django in DEBUG mode; in production Nginx handles them.

**Auth flow**: JWT via SimpleJWT. Login returns `access` + `access_token` (both the same value) in the response body and sets `refresh_token` as an httponly cookie. Refresh rotation is enabled.

**Settings**: `DEBUG` and `SECRET_KEY` read from environment variables. CORS allows localhost:5173 and the production domain. Timezone is Asia/Shanghai.

### Frontend (Vue 3)

**Key dependencies**: Vue 3 (Composition API, `<script setup>`), Pinia (user store), Vue Router 5, axios, daisyUI + TailwindCSS v4.

**Build output**: Vite builds to `../backend/static/frontend/` (configured in `vite.config.js`). Dev server is fixed at port 5173.

**State management** — single Pinia store (`stores/user.js`):
- State: `accessToken`, `user` object, `hasPulledUserInfo` boolean
- Persisted to localStorage
- `isLoggedIn` getter checks both token and user presence
- `pullUserInfo()` fetches `/api/user/account/info/` once and caches (guarded by `hasPulledUserInfo`)
- `handleAuthResponse()` is the shared post-login/register handler

**API layer** (`js/http/api.js`):
- axios instance with `withCredentials: true`
- Request interceptor attaches `Authorization: Bearer <token>`
- Response interceptor handles 401s with a **token refresh queue pattern**: the first failed request triggers a refresh call; subsequent concurrent failures queue up and replay on success
- Base URL is `http://127.0.0.1:8000` in dev, empty string in production (same-origin)

**Router** (`router/index.js`):
- `meta.requiresAuth` on protected routes triggers redirect to login with `?redirect=` query param
- `App.vue` also calls `pullUserInfo()` on mount and redirects if the current route requires auth

**Layout**: `App.vue` wraps `<RouterView />` in `<NavBar>`. NavBar uses daisyUI's drawer component (responsive: `drawer-open` on `lg+`, toggle on mobile) with sidebar nav links and a top header bar with user dropdown.

**daisyUI/Tailwind v4 setup**: Tailwind v4 is imported via the Vite plugin (`@tailwindcss/vite`), not PostCSS. daisyUI v5 is imported in `main.css`.
