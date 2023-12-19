from fastapi import status, HTTPException, Depends, APIRouter
from ..database import get_db
from .. import models, schemas, utils, oauth2, send_mail

router = APIRouter(
    prefix="/users",
    tags=['Users'],
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
async def created_user(user: schemas.UserCreate, db: Depends = Depends(get_db)):
    """
    Creates a new user in the database with the provided user details. It also checks for email uniqueness and hashes the password.

    Args:
        user (schemas.UserCreate): The user details for creating a new user.
        db (Session, optional): Database session dependency. Defaults to Depends(get_db).

    Raises:
        HTTPException: Raises a 424 error if a user with the given email already exists.

    Returns:
        models.User: The newly created user, along with their information, after being added to the database.
    """
    
    
    # Check if a user with the given email already exists
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()

    if existing_user:
        raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY,
                            detail=f"User {existing_user.email} already exists")

    
    # Hash the user's password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    
    # Create a new user and add it to the database
    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user) 
    
    # Create a User_Status entry for the new user
    post = models.User_Status(user_id=new_user.id, user_name=new_user.user_name, name_room="Hell")
    db.add(post)
    db.commit()
    db.refresh(post)
    
    
    
    
    # token = oauth2.create_access_token(data={"user_id": new_user.id})
    # registration_link = f"http://127.0.0.1:8000/verify_email?token={token}"
    # await send_mail.send_registration_mail("Вітаємо з реєстрацією!", new_user.email,
    #                                        {
    #                                         "title": "Registration",
    #                                         "name": user.user_name,
    #                                         "reset_link": registration_link
    #                                         })
    
    
    
    return new_user
     
        
    


# @router.get('/{email}', response_model=schemas.UserInfo)
# def get_user_mail(email: str, db: Session = Depends(get_db)):
    
#     # Query the database for a user with the given email
#     user = db.query(models.User).filter(models.User.email == email).first()
    
#     # If the user is not found, raise an HTTP 404 error
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"User with email {email} not found")
        
#     return user


# @router.get("/", response_model=List[schemas.UserInfo])
# async def get_email(db: Session = Depends(get_db)):
#     # Query the database for all users
#     posts = db.query(models.User).all()
#     return posts