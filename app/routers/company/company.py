
from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session

from app.auth import oauth2
from app.database.database import get_db

from app.models.company_model import Company
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanySchema


router = APIRouter(
    prefix="/company",
    tags=['Company'],
)



@router.post("/companies/", response_model=CompanySchema)
def create_company(company: CompanyCreate, db: Session = Depends(get_db),
                   current_user: int = Depends(oauth2.get_current_user)):
    
    if current_user.role != "super_admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN,
                            detail="The user is not a super admin, access is denied.")
    
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

@router.delete("/companies/{company_id}", response_model=CompanySchema) # , include_in_schema=True
def delete_company(company_id: int, db: Session = Depends(get_db),
                   current_user: int = Depends(oauth2.get_current_user)):
    
    
    db_company = db.query(Company).filter(Company.id == company_id).first()
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    
    if current_user.role != "super_admin":
        raise HTTPException(status_code=403,
                            detail="You are not authorized to delete this company")
    
    db.delete(db_company)
    db.commit()
    return db_company