from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import shutil
import os
import json

from database import engine, get_db, Base
from models import QuizQuestion, StudentAnswer, StudentLevel
from ingestion import ingest_pdf
from quiz_generator import generate_quiz_for_source
from adaptive import update_difficulty, get_student_difficulty

# Create all tables in the database
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Peblo Quiz Engine", version="1.0.0")

UPLOAD_DIR = "uploaded_pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ─── 1. INGEST PDF ────────────────────────────────────────────────────────────

@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    """Upload a PDF and extract + store its content."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    result = ingest_pdf(file_path, file.filename)
    return JSONResponse(content={"message": "PDF ingested successfully", "data": result})


# ─── 2. GENERATE QUIZ ─────────────────────────────────────────────────────────

@app.post("/generate-quiz")
def generate_quiz(source_id: str):
    """Generate quiz questions for a given source document ID."""
    result = generate_quiz_for_source(source_id)
    return JSONResponse(content={"message": "Quiz generated", "data": result})


# ─── 3. GET QUIZ QUESTIONS ────────────────────────────────────────────────────

@app.get("/quiz")
def get_quiz(
    topic: str = None,
    difficulty: str = None,
    student_id: str = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve quiz questions.
    If student_id is provided, difficulty is auto-detected from their level.
    """
    query = db.query(QuizQuestion)

    if student_id and not difficulty:
        difficulty = get_student_difficulty(student_id)

    if difficulty:
        query = query.filter(QuizQuestion.difficulty == difficulty)

    if topic:
        from models import ContentChunk
        chunk_ids = db.query(ContentChunk.id).filter(
            ContentChunk.topic.ilike(f"%{topic}%")
        ).all()
        chunk_ids = [c[0] for c in chunk_ids]
        query = query.filter(QuizQuestion.chunk_id.in_(chunk_ids))

    questions = query.limit(10).all()

    result = []
    for q in questions:
        result.append({
            "id": q.id,
            "question": q.question,
            "type": q.question_type,
            "options": json.loads(q.options) if q.options else [],
            "difficulty": q.difficulty,
            "chunk_id": q.chunk_id
        })

    return JSONResponse(content={"questions": result, "count": len(result)})


# ─── 4. SUBMIT ANSWER ─────────────────────────────────────────────────────────

class AnswerInput(BaseModel):
    student_id: str
    question_id: str
    selected_answer: str

@app.post("/submit-answer")
def submit_answer(payload: AnswerInput, db: Session = Depends(get_db)):
    """Submit a student's answer and update adaptive difficulty."""
    question = db.query(QuizQuestion).filter(QuizQuestion.id == payload.question_id).first()

    if not question:
        raise HTTPException(status_code=404, detail="Question not found.")

    is_correct = int(payload.selected_answer.strip().lower() == question.answer.strip().lower())

    answer = StudentAnswer(
        student_id=payload.student_id,
        question_id=payload.question_id,
        selected_answer=payload.selected_answer,
        is_correct=is_correct
    )
    db.add(answer)
    db.commit()

    new_difficulty = update_difficulty(payload.student_id, bool(is_correct))

    return JSONResponse(content={
        "correct": bool(is_correct),
        "correct_answer": question.answer,
        "new_difficulty_level": new_difficulty,
        "message": "Great job! Level up!" if is_correct else "Keep practicing!"
    })


# ─── 5. STUDENT STATS ─────────────────────────────────────────────────────────

@app.get("/student/{student_id}/stats")
def student_stats(student_id: str, db: Session = Depends(get_db)):
    """Get a student's performance stats."""
    answers = db.query(StudentAnswer).filter(StudentAnswer.student_id == student_id).all()
    total = len(answers)
    correct = sum(1 for a in answers if a.is_correct == 1)
    level = get_student_difficulty(student_id)

    return JSONResponse(content={
        "student_id": student_id,
        "total_answered": total,
        "correct": correct,
        "accuracy": f"{round((correct/total)*100, 1)}%" if total > 0 else "0%",
        "current_difficulty": level
    })


# ─── ROOT ─────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "Welcome to Peblo Quiz Engine 🎓", "docs": "/docs"}