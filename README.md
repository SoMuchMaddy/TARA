# TARA - Tracking and Administration for Rescue Animals (Felines)

<img width="300" alt="TARA Logo" src="https://github.com/user-attachments/assets/8cbec0a9-3c95-4223-af8f-803de9fb55d0" />

## Overview

TARA is a lightweight full-stack web application designed to help animal rescue volunteers track and manage cats in their care.

This project currently implements a functional MVP focused on core data management: creating, viewing, updating, and deleting cat records.

## Features (Current MVP)

* Add new cats with name and status
* View all cats in a dynamic list
* Edit existing cat information
* Delete cats from the system
* Persistent storage using SQLite

## Tech Stack

**Frontend**

* HTML
* Vanilla JavaScript (no frameworks)

**Backend**

* Python
* FastAPI
* SQLAlchemy

**Database**

* SQLite (`tara.db`)

## Project Structure

```
TARA/
├── frontend/        # Static UI (HTML + JS)
├── backend/
│   └── src/
│       └── app.py   # FastAPI application
├── docs/            # MVP planning + notes
├── tara.db          # SQLite database
└── README.md
```

## How It Works

The frontend communicates with a FastAPI backend via HTTP requests:

* `GET /cats` → fetch all cats
* `POST /cats` → create a new cat
* `PUT /cats/{id}` → update a cat
* `DELETE /cats/{id}` → remove a cat

The backend uses SQLAlchemy to interact with a SQLite database for persistent storage.

## Running the Project

### Backend

```bash
cd backend
pip install -r requirements.txt  # if you add one later
uvicorn src.app:app --reload
```

### Frontend

Open `frontend/index.html` in your browser.

## Current Limitations

* No user authentication
* No foster/adopter tracking yet
* Minimal UI (no framework/styling system)
* Single-table database (cats only)

## Roadmap

* Add foster/adopter entities
* Expand cat data (age, intake date, medical notes)
* Improve UI/UX
* Add search/filtering
* Deploy backend + frontend

## Purpose

This project was built as a practical exercise in full-stack development and to explore tools that could be useful for real-world animal rescue operations.

---
