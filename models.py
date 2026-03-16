from sqlalchemy import Column, String, Integer, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import datetime
import uuid

def gen_id():
    return str(uuid.uuid4())[:8].upper()

class SourceDocument(Base):
    __tablename__ = "source_documents"

    id = Column(String, primary_key=True, default=gen_id)
    filename = Column(String, nullable=False)
    subject = Column(String)
    grade = Column(Integer)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)

    chunks = relationship("ContentChunk", back_populates="source")


class ContentChunk(Base):
    __tablename__ = "content_chunks"

    id = Column(String, primary_key=True, default=gen_id)
    source_id = Column(String, ForeignKey("source_documents.id"))
    topic = Column(String)
    text = Column(Text)

    source = relationship("SourceDocument", back_populates="chunks")
    questions = relationship("QuizQuestion", back_populates="chunk")


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id = Column(String, primary_key=True, default=gen_id)
    chunk_id = Column(String, ForeignKey("content_chunks.id"))
    question = Column(Text)
    question_type = Column(String)
    options = Column(Text)
    answer = Column(String)
    difficulty = Column(String)

    chunk = relationship("ContentChunk", back_populates="questions")


class StudentAnswer(Base):
    __tablename__ = "student_answers"

    id = Column(String, primary_key=True, default=gen_id)
    student_id = Column(String, nullable=False)
    question_id = Column(String, ForeignKey("quiz_questions.id"))
    selected_answer = Column(String)
    is_correct = Column(Integer)
    submitted_at = Column(DateTime, default=datetime.datetime.utcnow)


class StudentLevel(Base):
    __tablename__ = "student_levels"

    student_id = Column(String, primary_key=True)
    difficulty = Column(String, default="easy")
    score = Column(Float, default=0.0)