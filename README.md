# Peblo Quiz Engine 🎓

A backend system that ingests educational PDF content, generates quiz questions using AI, and serves them through a REST API with adaptive difficulty based on student performance.

Built as part of the Peblo AI Backend Engineer Challenge.

---

## What It Does

1. You upload a PDF (educational content)
2. The system extracts and chunks the text
3. An AI model generates quiz questions from each chunk
4. Questions are stored in a database and served via API
5. Students submit answers and the system tracks their performance
6. Difficulty adjusts automatically based on how well the student is doing

---

## Tech Stack

- **Backend** — Python + FastAPI
- **Database** — SQLite via SQLAlchemy
- **PDF Parsing** — PyMuPDF
- **AI / LLM** — OpenRouter API (google/gemma-3-4b-it:free model)
- **Adaptive Logic** — Custom rule-based difficulty engine

---

## Project Structure
```
peblo-quiz-engine/
├── main.py            # FastAPI app and all route handlers
├── database.py        # Database connection and session setup
├── models.py          # SQLAlchemy table definitions
├── ingestion.py       # PDF extraction, cleaning, and chunking
├── quiz_generator.py  # AI-powered question generation
├── adaptive.py        # Student difficulty tracking logic
├── .env.example       # Environment variable template
├── requirements.txt   # Python dependencies
└── README.md
```

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/dikshashrivastva/pebloQuizEngine.git
cd pebloQuizEngine
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the root folder:
```
OPENROUTER_API_KEY=your_openrouter_api_key_here
DATABASE_URL=sqlite:///./peblo.db
```

You can get a free API key at https://openrouter.ai

### 5. Run the server
```bash
uvicorn main:app --reload
```

### 6. Open the API docs

Visit: http://127.0.0.1:8000/docs

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /ingest | Upload a PDF file |
| POST | /generate-quiz?source_id=XXX | Generate quiz questions from a source |
| GET | /quiz?difficulty=easy | Get quiz questions (filter by difficulty or topic) |
| POST | /submit-answer | Submit a student's answer |
| GET | /student/{student_id}/stats | Get a student's performance stats |

---

## How to Test the Endpoints

### Step 1 — Ingest a PDF
Go to `POST /ingest`, upload one of the provided PDFs, and copy the `source_id` from the response.

### Step 2 — Generate Quiz
Go to `POST /generate-quiz`, paste the `source_id` as a query parameter, and wait ~30 seconds for questions to be generated.

### Step 3 — Get Questions
```
GET /quiz?difficulty=easy
GET /quiz?topic=Science
```

### Step 4 — Submit an Answer
```json
POST /submit-answer
{
  "student_id": "S001",
  "question_id": "question_id_here",
  "selected_answer": "B"
}
```

### Step 5 — Check Student Stats
```
GET /student/S001/stats
```

---

## Adaptive Difficulty Logic

Every time a student submits an answer, the system checks their last 2 responses:

- 2 correct in a row → difficulty goes up (easy → medium → hard)
- 2 wrong in a row → difficulty goes down (hard → medium → easy)
- Mixed results → difficulty stays the same

This ensures students are always challenged at the right level.

---

## Sample Output

### Ingestion Response
```json
{
  "message": "PDF ingested successfully",
  "data": {
    "source_id": "5661DF4C",
    "chunks_created": 2,
    "subject": "Math",
    "grade": 1
  }
}
```

### Generated Question
```json
{
  "id": "FA1FF473",
  "question": "How many sides does a triangle have?",
  "type": "MCQ",
  "options": ["A. 2", "B. 3", "C. 4", "D. 5"],
  "difficulty": "easy",
  "chunk_id": "CACFA04C"
}
```

### Answer Submission Response
```json
{
  "correct": true,
  "correct_answer": "B",
  "new_difficulty_level": "medium",
  "message": "Great job! Level up!"
}


<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/13bc9704-0b45-4c05-b669-1a43bb044dfd" />

