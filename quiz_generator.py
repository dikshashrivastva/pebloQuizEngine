from openai import OpenAI
import os
import json
import re
from dotenv import load_dotenv
from database import SessionLocal
from models import ContentChunk, QuizQuestion

load_dotenv(override=True)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

def clean_json_response(text: str) -> str:
    """Remove markdown code blocks and extract JSON array."""
    text = re.sub(r"```json", "", text)
    text = re.sub(r"```", "", text)
    text = text.strip()
    # Extract just the JSON array
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if match:
        return match.group(0)
    return text

def generate_questions_for_chunk(chunk_text: str, chunk_id: str, subject: str = "General"):
    prompt = f"""Generate exactly 3 quiz questions from this educational content.
Return ONLY a JSON array with no markdown, no explanation, just the array.

Content:
{chunk_text}

Required JSON format:
[
  {{"question": "...", "type": "MCQ", "options": ["A", "B", "C", "D"], "answer": "A", "difficulty": "easy"}},
  {{"question": "True or False: ...", "type": "TrueFalse", "options": ["True", "False"], "answer": "True", "difficulty": "easy"}},
  {{"question": "Fill in the blank: ...", "type": "FillBlank", "options": [], "answer": "...", "difficulty": "medium"}}
]"""

    response = client.chat.completions.create(
        model="google/gemma-3-4b-it:free",
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.choices[0].message.content
    cleaned = clean_json_response(raw)
    questions = json.loads(cleaned)
    return questions

def generate_quiz_for_source(source_id: str):
    db = SessionLocal()
    try:
        chunks = db.query(ContentChunk).filter(ContentChunk.source_id == source_id).all()

        if not chunks:
            return {"error": "No chunks found for this source_id"}

        total_generated = 0

        for chunk in chunks:
            if len(chunk.text) < 50:
                continue

            try:
                questions = generate_questions_for_chunk(chunk.text, chunk.id)
                for q in questions:
                    quiz_q = QuizQuestion(
                        chunk_id=chunk.id,
                        question=q["question"],
                        question_type=q["type"],
                        options=json.dumps(q.get("options", [])),
                        answer=q["answer"],
                        difficulty=q.get("difficulty", "easy").lower()
                    )
                    db.add(quiz_q)
                    total_generated += 1

            except Exception as e:
                print(f"Skipping chunk {chunk.id} due to error: {e}")
                continue

        db.commit()
        return {"source_id": source_id, "questions_generated": total_generated}

    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
