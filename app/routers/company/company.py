
from os import name
from typing import List
from fastapi import File, Form, Query, UploadFile, status, HTTPException, Depends, APIRouter, Response
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, asc
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth import oauth2
from app.database.database import get_db
from app.database.async_db import get_async_session


from app.models.company_model import Company
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanySchema
from app.config.config import settings


router = APIRouter(
    prefix="/company",
    tags=['Company'],
)



@router.post("/companies/", response_model=CompanySchema)
def create_company(company: CompanyCreate, db: Session = Depends(get_db)):
    db_company = db.query(Company).filter(Company.subdomain == company.subdomain).first()
    
    if db_company is not None:
        raise HTTPException(status_code=400, detail="Company with the same subdomain already exists")
    
    db_company = Company(**company.model_dump())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

@router.get("/companies/{company_id}", response_model=CompanySchema)
def read_company(company_id: int, db: Session = Depends(get_db)):
    db_company = db.query(Company).filter(Company.id == company_id).first()
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return db_company

@router.get("/subdomain/{subdomain}", response_model=CompanySchema)
def read_company_by_subdomain(subdomain: str, db: Session = Depends(get_db)):
    db_company = db.query(Company).filter(Company.subdomain == subdomain).first()
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return db_company

@router.put("/companies/{company_id}", response_model=CompanySchema)
def update_company(company_id: int, company: CompanyUpdate, db: Session = Depends(get_db)):
    db_company = db.query(Company).filter(Company.id == company_id).first()
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    
    for key, value in company.model_dump(exclude_unset=True).items():
        setattr(db_company, key, value)
    
    db.commit()
    db.refresh(db_company)
    return db_company

@router.delete("/companies/{company_id}", response_model=CompanySchema)
def delete_company(company_id: int, db: Session = Depends(get_db)):
    db_company = db.query(Company).filter(Company.id == company_id).first()
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    db.delete(db_company)
    db.commit()
    return db_company