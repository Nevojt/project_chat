from fastapi import status, HTTPException, Depends, APIRouter, Response
from sqlalchemy.orm import Session
from ...auth import oauth2
from app.database.database import get_db
from app.models import models
from app.schemas import user

router = APIRouter(
    prefix="/user_status",
    tags=['User Status'],
)


@router.get("/")
async def get_posts(db: Session = Depends(get_db)): # , current_user: int = Depends(oauth2.get_current_user)
    """
    Get a list of all user status.

    Args:
        db (Session, optional): The database session object.

    Returns:
        List[schemas.UserStatus]: A list of user status objects.
    """
    posts = db.query(models.User_Status).all()
    return posts


@router.get("/{user_name}")
async def get_post(user_name: str, db: Session = Depends(get_db)):  # , current_user: int = Depends(oauth2.get_current_user)
    """
    Get a single user status by their username.

    Args:
        user_name (str): The username of the user whose status is to be retrieved.
        db (Session, optional): The database session object.

    Raises:
        HTTPException: A 404 NOT FOUND error is raised if no user status is found for the given username.

    Returns:
        List[schemas.UserStatus]: A list of user status objects, or an empty list if no user status is found.
    """
    post = db.query(models.User_Status).filter(models.User_Status.user_name == user_name).all()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with user_name: {user_name} not found")
    return post

# @router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserStatusPost)
# async def create_posts(post: schemas.UserStatusCreate, db: Session = Depends(get_db)): # , current_user: int = Depends(oauth2.get_current_user)

    
#     # print(current_user.user_name)
#     post = models.User_Status(**post.dict())
#     db.add(post)
#     db.commit()
#     db.refresh(post)    
#     return post



@router.put("/{user_id}", status_code=status.HTTP_200_OK)
def update_post(user_id: int, update_post: user.UserStatusUpdate, db: Session = Depends(get_db)): # , current_user: int = Depends(oauth2.get_current_user)
    """
    Updates the status of a user post based on the provided user ID and updated post details.

    Args:
        user_id (int): The ID of the user whose post is to be updated.
        update_post (schemas.UserStatusUpdate): The updated post details.
        db (Session, optional): Database session dependency. Defaults to Depends(get_db).

    Raises:
        HTTPException: Raises a 404 error if no post is found for the given user ID.

    Returns:
        models.User_Status: The updated user post after the changes have been committed to the database.
    """
    
    post_query = db.query(models.User_Status).filter(models.User_Status.user_id == user_id)
    post = post_query.first()
    
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with user_id: {user_id} not found")
    
    post_query.update(update_post.model_dump(), synchronize_session=False)
    
    db.commit()
    return post_query.first()