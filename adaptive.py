from database import SessionLocal
from models import StudentLevel, StudentAnswer

DIFFICULTY_LEVELS = ["easy", "medium", "hard"]

def get_or_create_student_level(db, student_id: str) -> StudentLevel:
    """Get student's current difficulty level, or create a new one."""
    level = db.query(StudentLevel).filter(StudentLevel.student_id == student_id).first()
    if not level:
        level = StudentLevel(student_id=student_id, difficulty="easy", score=0.0)
        db.add(level)
        db.commit()
        db.refresh(level)
    return level

def update_difficulty(student_id: str, is_correct: bool):
    """
    Adaptive logic:
    - 2 correct in a row → increase difficulty
    - 2 wrong in a row → decrease difficulty
    """
    db = SessionLocal()
    try:
        level = get_or_create_student_level(db, student_id)

        recent = (
            db.query(StudentAnswer)
            .filter(StudentAnswer.student_id == student_id)
            .order_by(StudentAnswer.submitted_at.desc())
            .limit(2)
            .all()
        )

        current_index = DIFFICULTY_LEVELS.index(level.difficulty)

        if len(recent) >= 2:
            all_correct = all(r.is_correct == 1 for r in recent)
            all_wrong = all(r.is_correct == 0 for r in recent)

            if all_correct and current_index < len(DIFFICULTY_LEVELS) - 1:
                level.difficulty = DIFFICULTY_LEVELS[current_index + 1]
            elif all_wrong and current_index > 0:
                level.difficulty = DIFFICULTY_LEVELS[current_index - 1]

        db.commit()
        return level.difficulty

    finally:
        db.close()

def get_student_difficulty(student_id: str) -> str:
    db = SessionLocal()
    try:
        level = get_or_create_student_level(db, student_id)
        return level.difficulty
    finally:
        db.close()