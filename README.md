# Tech Advisor App

AI-powered tech advisor application with a Next.js frontend and FastAPI backend.

## Project structure

```
tech-advisor-app/
├── frontend/   # Next.js web app
└── backend/    # FastAPI API server
```

## Prerequisites

- Node.js 20+
- Python 3.13+

## Getting started

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Open [http://localhost:8000/docs](http://localhost:8000/docs) for the API docs.

## Environment variables

Copy `.env.example` to `.env` and fill in your values before running locally.
