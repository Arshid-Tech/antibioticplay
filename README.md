# 💊 AntibioticPlay

![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![Vue.js](https://img.shields.io/badge/Frontend-Vue.js_3_+_PWA-4FC08D?logo=vue.js)
![Flask](https://img.shields.io/badge/Backend-Flask_+_SQLAlchemy-000000?logo=flask)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791?logo=postgresql)
![License](https://img.shields.io/badge/License-GPLv3-blue)

**AntibioticPlay** is an interactive, gamified Progressive Web Application (PWA) designed to teach antimicrobial pharmacotherapy—including classification, dosage forms, dosing ratios, clinical decision-making, and antimicrobial stewardship (AMS)—to pharmacy students.

---

## ✨ Key Features

### 🎮 Gamified Learning & Clinical Practice
* **Interactive Question Engine:** Supports Drag & Drop Matching, Drag & Drop Ordering, Fill-in-the-Blank, Multiple Select, True/False, Image Labeling, and **Case-Based Clinical Vignettes** (`clinical-case`) simulating real community pharmacy and hospital scenarios.
* **Micro-Lessons:** Concise pre-stage clinical summaries highlighting key dosing rules, drug interactions, and Iranian market formulations.
* **Adaptive Gamification:** Question-type-aware speed bonuses, answer streaks, XP & leveling, competitive leagues (Bronze, Silver, Gold, Diamond), achievement badges, and scientist avatar dialogues (Fleming, Waksman, Domagk, Florey, Hodgkin, Bugie, Tu Youyou).
* **Daily Challenge & Async Duels:** Daily 5-question mixed challenge with bonus XP, plus shareable peer-to-peer duel links after completing any quiz stage.

### 🗂️ Smart Spaced-Repetition Flashcards
* **Hybrid Leitner + SM-2 Algorithm:** 5-box mastery progression with personalized review intervals (`Hard`, `Medium`, `Easy`), category filtering, bookmarking, and keyboard shortcuts (`Space`, `1`, `2`, `3`).
* **Auto-Queued Weaknesses:** Incorrect answers during quizzes automatically queue related flashcards into Box 1 for immediate review.

### 📱 Progressive Web App (PWA)
* Installable on Android, iOS, and Desktop (`vite-plugin-pwa`) with an RTL Persian manifest, Workbox runtime caching (`NetworkFirst` for APIs, `CacheFirst` for media/fonts), offline fallback, and an in-app install/update prompt.

### 📋 Built-in Research Evaluation (MEEGA+) & Admin CMS
* **Internal 31-Item MEEGA+ Survey:** Replaces external survey links with an integrated demographic + 27-item Likert questionnaire linked directly to user performance logs, with XP incentives and duplicate-submission protection.
* **Admin CMS (`/admin`):** Role-protected management panel for creating/editing stages, micro-lessons, questions, flashcards, and user roles without modifying code.
* **Research Analytics & SPSS Exports:** Real-time KPIs, per-stage attempt/completion metrics, 4-domain MEEGA+ summaries, and one-click `UTF-8-SIG` CSV downloads (`users`, `survey`, and joined `combined` datasets ready for Excel & SPSS).

---

## 🛠 Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | Vue 3, Vite, Pinia, Vue Router, Axios, FontAwesome, `vite-plugin-pwa` |
| **Backend** | Python, Flask, Flask-RESTful, Flask-SQLAlchemy, Flask-Migrate, Flask-JWT-Extended, Gunicorn |
| **Database** | PostgreSQL (Production on Render) / SQLite (Local Development fallback) |
| **Deployment** | Render Blueprint (`render.yaml`) — Frontend, Backend, and Managed PostgreSQL |

---

## 🚀 One-Click Deployment on Render

The entire stack (Frontend, Backend, and PostgreSQL database) is defined in `render.yaml`:

1. In the [Render Dashboard](https://dashboard.render.com/), click **New → Blueprint** and connect this repository.
2. Render automatically provisions:
   * `antibioticplay-db` (Managed PostgreSQL)
   * `antibioticplay-backend` (Flask API with auto-generated `SECRET_KEY` and `JWT_SECRET_KEY`, auto-linked `DATABASE_URL`, and automatic initial seeding via `python seed_db.py --if-empty`)
   * `antibioticplay-frontend` (Vue 3 PWA)
3. To bootstrap an admin account automatically on deploy, add the following environment variables to `antibioticplay-backend` in Render:
   * `ADMIN_USERNAME`
   * `ADMIN_EMAIL`
   * `ADMIN_PASSWORD`
4. Verify the backend deployment at `https://<your-backend>.onrender.com/health` (`{"database": "connected", "status": "ok"}`).

---

## 💻 Local Development

### Prerequisites
* Python 3.10+
* Node.js 20+
* PostgreSQL (optional — defaults to a local SQLite database `antibioticplay.db` if `DATABASE_URL` is not set)

### 1. Clone the repository
```bash
git clone https://github.com/contrarianist/antibioticplay.git
cd antibioticplay
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv

# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

pip install -r requirements.txt

# Seed units, quizzes, clinical vignettes, micro-lessons, badges, and flashcards
python seed_db.py

# (Optional) Promote an existing user to admin
python seed_db.py --make-admin <username_or_email>

# Run development server (http://127.0.0.1:5000)
python run.py
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
The frontend runs at `http://localhost:5173` and proxies `/api` requests to `http://127.0.0.1:5000`.

---

## 📄 License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)** — see the [LICENSE](LICENSE) file for details.
