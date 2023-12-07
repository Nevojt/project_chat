from fastapi import status, HTTPException, Depends, APIRouter, Response
from sqlalchemy.orm import Session
from .. import models, schemas, database, oauth2

router = APIRouter(
    prefix="/vote",
    tags=['Vote']
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user)):
    """
    Handles the voting process for a message. Users can cast or retract their vote on a specific message.

    Args:
        vote (schemas.Vote): The vote details, including message ID and vote direction.
        db (Session, optional): Database session dependency. Defaults to Depends(database.get_db).
        current_user (int): The ID of the current user, obtained through authentication.

    Raises:
        HTTPException: Raises a 404 error if the message to be voted on does not exist.
        HTTPException: Raises a 409 conflict error if the user has already voted on the specific message and is attempting to vote again.
        HTTPException: Raises a 404 error if the user tries to retract a vote that does not exist.

    Returns:
        dict: A confirmation message indicating the successful addition or deletion of a vote.
    """
    
    message = db.query(models.Message).filter(models.Message.id == vote.message_id).first()
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Message with id: {vote.message_id} does not exist")
    
    vote_query = db.query(models.Vote).filter(
        models.Vote.message_id == vote.message_id, models.Vote.user_id == current_user.id
    )
    found_vote = vote_query.first()
    
    if (vote.dir == 1):
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"User {current_user.id} has already voted on post {vote.message_id}")
        
        new_vote = models.Vote(message_id = vote.message_id, user_id = current_user.id)
        db.add(new_vote)
        db.commit()
        return {"message": "Successfully added voted "}
        
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Vote does not exist")
            
        vote_query.delete(synchronize_session=False)
        db.commit()
        
        return {"message": "Successfully deleted vote"}