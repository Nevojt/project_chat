from typing import List
from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth import oauth2
from app.database.database import get_db
from app.database.async_db import get_async_session

from app.models import room_model, user_model
from app.schemas.invitaton import InvitationSchema

router = APIRouter(
    prefix='/invitations',
    tags=['Invitations'],
)


@router.get("/", response_model=List[InvitationSchema])
async def get_pending_invitations(db: Session = Depends(get_db), 
                                  current_user: user_model.User = Depends(oauth2.get_current_user)):
    """
    Get a list of all pending invitations for the current user.

    Parameters:
        db (Session): The database session object
        current_user (user_model.User): The current user

    Returns:
        List[InvitationSchema]: A list of invitation objects

    Raises:
        HTTPException: If no invitations are found
    """
    invitations = db.query(room_model.RoomInvitation).filter(
        room_model.RoomInvitation.recipient_id == current_user.id,
        room_model.RoomInvitation.status == 'pending'
    ).all()
    
    if not invitations:
        raise HTTPException(status_code=404, detail="No pending invitations found")

    return invitations

@router.post('/invite_user')
async def invite_user_to_room(room_id: int, recipient_id: int, 
                              db: AsyncSession = Depends(get_async_session), 
                              current_user: user_model.User = Depends(oauth2.get_current_user)):
    
    room_get = select(room_model.Rooms).where(room_model.Rooms.id == room_id,
                                          room_model.Rooms.owner == current_user.id,
                                          room_model.Rooms.secret_room == True)
    result = await db.execute(room_get)
    existing_room = result.scalar_one_or_none()
    
    if existing_room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Room with ID {room_id} not found")
        
    #  Create invitation
    new_invitation = room_model.RoomInvitation(
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
                                current_user: user_model.User = Depends(oauth2.get_current_user)):
    
    if current_user.blocked == True:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User with ID {current_user.id} is blocked")
        
    # Checking the availability of the invitation
    invitation_query = select(room_model.RoomInvitation).where(
        room_model.RoomInvitation.id == invitation_id,
        room_model.RoomInvitation.recipient_id == current_user.id
    )
    result = await db.execute(invitation_query)
    invitation = result.scalar_one_or_none()
    
    if not invitation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Invitation with ID {invitation_id} not found")
    # Processing the response to the invitation
    if accepted:
        invitation.status = 'accepted'
        new_manager_room = room_model.RoomsManager(user_id=current_user.id, room_id=invitation.room_id)
        db.add(new_manager_room)
    else:
        invitation.status ='declined'
        
    await db.commit()
    return {"message": "Invitation response recorded"}