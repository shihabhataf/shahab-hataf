# ☄ شهاب هتف — Arabic News & Articles Platform

A modern, full-featured Arabic RTL news and articles website built with Flask.

## Features
- 🌗 Dark / Light mode
- ☎ Mobile-first responsive design
- ⌘ Auth (login, register, profile)
- ✍ Rich article editor with image upload & YouTube embed
- ♡ Like, ⌘ Save, ☞ Comment
- 📁 Categories & # Tags
- ⛨ Admin dashboard
- ⌕ Full-text search
- ⚡ SEO-friendly slugs

## Quick Start

```bash
pip install -r requirements.txt
python run.py
```

Open http://localhost:5000

**Admin:** admin@shahab.com / admin123

## Project Structure

```
shahab_hataf/
├── app/
│   ├── __init__.py       # App factory + seeding
│   ├── models.py         # SQLAlchemy models
│   ├── forms.py          # WTForms
│   ├── utils.py          # Image helpers
│   └── routes/
│       ├── main.py       # Home, search, category, tag
│       ├── auth.py       # Login, register, logout
│       ├── articles.py   # CRUD, like, save, comment
│       ├── user.py       # Profile, settings
│       └── admin.py      # Admin dashboard
├── templates/            # Jinja2 HTML templates
├── static/
│   ├── css/main.css
│   ├── js/main.js
│   └── img/
├── config.py
├── run.py
└── requirements.txt
```
