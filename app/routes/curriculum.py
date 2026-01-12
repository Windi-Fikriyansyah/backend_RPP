from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.curriculum import Subject, CurriculumGoal
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/api/curriculum", tags=["curriculum"])

# Pydantic Schemas for Response
class SubjectResponse(BaseModel):
    id: int
    name: str
    category: str
    class Config:
        from_attributes = True

class GoalResponse(BaseModel):
    id: int
    phase: str
    element: str
    cp_content: str
    class Config:
        from_attributes = True

# Helper to seed data if empty (For demo purposes)
@router.post("/seed")
async def seed_data(db: AsyncSession = Depends(get_db)):
    # Check if subjects exist
    result = await db.execute(select(Subject))
    if result.scalars().first():
        return {"message": "Data already seeded"}
    
    # Create Subjects
    math = Subject(name="Matematika", category="Umum")
    ipas = Subject(name="IPAS", category="Umum")
    indo = Subject(name="Bahasa Indonesia", category="Umum")
    
    db.add_all([math, ipas, indo])
    await db.commit()
    await db.refresh(math)
    
    # Create Goals (Samples)
    goals = [
        # Matematika Fase B (Kelas 3-4)
        CurriculumGoal(subject_id=math.id, phase="B", element="Bilangan", cp_content="Peserta didik menunjukkan pemahaman dan intuisi bilangan (number sense) pada bilangan cacah sampai 10.000.", version="2024"),
        CurriculumGoal(subject_id=math.id, phase="B", element="Aljabar", cp_content="Peserta didik dapat mengisi nilai yang belum diketahui dalam sebuah kalimat matematika.", version="2024"),
        
        # Matematika Fase C (Kelas 5-6)
        CurriculumGoal(subject_id=math.id, phase="C", element="Bilangan", cp_content="Peserta didik dapat melakukan operasi perkalian dan pembagian bilangan cacah sampai 100.000.", version="2024"),

        # IPAS Fase B
        CurriculumGoal(subject_id=ipas.id, phase="B", element="Pemahaman IPAS", cp_content="Peserta didik menganalisis hubungan antara bentuk serta fungsi bagian tubuh pada manusia.", version="2024"),
    ]
    
    db.add_all(goals)
    await db.commit()
    
    return {"message": "Seeded successfully"}

@router.get("/subjects", response_model=List[SubjectResponse])
async def get_subjects(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Subject))
    return result.scalars().all()

@router.get("/goals", response_model=List[GoalResponse])
async def get_goals(subject_id: int, phase: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CurriculumGoal).where(
            CurriculumGoal.subject_id == subject_id,
            CurriculumGoal.phase == phase
        )
    )
    return result.scalars().all()
