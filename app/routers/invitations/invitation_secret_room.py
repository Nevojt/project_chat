from typing import List
from fastapi import status, HTTPException, Depends, APIRouter, Response
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth import oauth2
from app.database.database import get_db
from app.database.async_db import get_async_session

from app.models import models
from app.schemas.invitaton import InvitationSchema

router = APIRouter(
    prefix='/invitations',
    tags=['Invitations'],
)


@router.get("/", response_model=List[InvitationSchema])
async def get_pending_invitations(db: Session = Depends(get_db), 
                                  current_user: models.User = Depends(oauth2.get_current_user)):
    """
    Get a list of all pending invitations for the current user.

    Parameters:
        db (Session): The database session object
        current_user (models.User): The current user

    Returns:
        List[InvitationSchema]: A list of invitation objects

    Raises:
        HTTPException: If no invitations are found
    """
    invitations = db.query(models.RoomInvitation).filter(
        models.RoomInvitation.recipient_id == current_user.id,
        models.RoomInvitation.status == 'pending'
    ).all()
    
    if not invitations:
        raise HTTPException(status_code=404, detail="No pending invitations found")

    return invitations

@router.post('/invite_user')
async def invite_user_to_room(room_id: int, recipient_id: int, 
                              db: AsyncSession = Depends(get_async_session), 
                              current_user: models.User = Depends(oauth2.get_current_user)):
    
    room_get = select(models.Rooms).where(models.Rooms.id == room_id,
                                          models.Rooms.owner == current_user.id,
                                          models.Rooms.secret_room == True)
    result = await db.execute(room_get)
    existing_room = result.scalar_one_or_none()
    
    if existing_room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Room with ID {room_id} not found")
        
    #  Create invitation
    new_invitation = models.RoomInvitation(
        room_id=room_id,
        sender_id=current_user.id,
        recipient_id=recipient_id
    )
    db.add(new_invitation)
    await db.commit()
    return {"message": "Invitation sent to user"}

@router.post('/respond_invitation')
async def respond_to_invitation(invitation_id: int, accepted: bool,
                                db: AsyncSession = Depends(get_async_session), 
                                current_user: models.User = Depends(oauth2.get_current_user)):
    
    if current_user.blocked == True:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User with ID {current_user.id} is blocked")
        
    # Checking the availability of the invitation
    invitation_query = select(models.RoomInvitation).where(
        models.RoomInvitation.id == invitation_id,
        models.RoomInvitation.recipient_id == current_user.id
    )
    result = await db.execute(invitation_query)
    invitation = result.scalar_one_or_none()
    
    if not invitation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Invitation with ID {invitation_id} not found")
    # Processing the response to the invitation
    if accepted:
        invitation.status = 'accepted'
        new_manager_room = models.RoomsManager(user_id=current_user.id, room_id=invitation.room_id)
        db.add(new_manager_room)
    else:
        invitation.status ='declined'
        
    await db.commit()
    return {"message": "Invitation response recorded"}