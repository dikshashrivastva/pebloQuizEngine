# Peblo Quiz Engine 🎓

An AI-powered content ingestion and adaptive quiz engine built with FastAPI, SQLite, and Google Gemini.

## Architecture
```
PDF Upload → Text Extraction (PyMuPDF) → Chunking → SQLite Storage
                                                          ↓
                                              Gemini AI Quiz Generation
                                                          ↓
                                              FastAPI Quiz Endpoints
                                                          ↓
                                              Student Answers + Adaptive Difficulty
```

## Tech Stack

- **Backend**: Python + FastAPI
- **Database**: SQLite (via SQLAlchemy)
- **PDF Parsing**: PyMuPDF (fitz)
- **AI/LLM**: Google Gemini 1.5 Flash
- **Adaptive Logic**: Custom rule-based difficulty adjustment

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/peblo-quiz-engine.git
cd peblo-quiz-engine
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### 5. Run the server
```bash
uvicorn main:app --reload
```

### 6. Open API docs
Visit: http://127.0.0.1:8000/docs

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /ingest | Upload a PDF |
| POST | /generate-quiz?source_id=XXX | Generate questions |
| GET | /quiz?difficulty=easy | Get quiz questions |
| POST | /submit-answer | Submit student answer |
| GET | /student/{id}/stats | Get student stats |

## Adaptive Difficulty

- 2 correct answers in a row → difficulty increases (easy → medium → hard)
- 2 wrong answers in a row → difficulty decreases (hard → medium → easy)