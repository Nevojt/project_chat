from app import models, schemas
from app.routers import messages


def test_get_messages_room(db_session):
    # Arrange
    message1 = models.Socket(
        message="Message 1",
        rooms="room1",
        sender_id=1,
        receiver_id=2,
        id_return=1,
    )
    message2 = models.Socket(
        message="Message 2",
        rooms="room1",
        sender_id=1,
        receiver_id=3,
        id_return=2,
    )
    user1 = models.User(user_name="User 1", id=1, avatar="avatar1")
    user2 = models.User(user_name="User 2", id=2, avatar="avatar2")
    user3 = models.User(user_name="User 3", id=3, avatar="avatar3")
    vote1 = models.Vote(message=message1, dir=1)
    vote2 = models.Vote(message=message2, dir=1)
    db_session.add_all([message1, message2, user1, user2, user3, vote1, vote2])
    db_session.commit()

    # Act
    result = messages.get_messages_room(db_session, "room1")

    # Assert
    assert result == [
        schemas.SocketModel(
            created_at=message2.created_at,
            receiver_id=message2.receiver_id,
            message=message2.message,
            user_name=user2.user_name,
            avatar=user2.avatar,
            verified=user2.verified,
            id=message2.id,
            vote=1,
            id_return=message2.id_return,
        ),
        schemas.SocketModel(
            created_at=message1.created_at,
            receiver_id=message1.receiver_id,
            message=message1.message,
            user_name=user1.user_name,
            avatar=user1.avatar,
            verified=user1.verified,
            id=message1.id,
            vote=1,
            id_return=message1.id_return,
        ),
    ]


def test_get_messages_room_no_messages(db_session):
    # Arrange
    db_session.commit()

    # Act
    result = messages.get_messages_room(db_session, "room1")

    # Assert
    assert result == []


def test_get_messages_room_with_limit(db_session):
    # Arrange
    message1 = models.Socket(
        message="Message 1",
        rooms="room1",
        sender_id=1,
        receiver_id=2,
        id_return=1,
    )
    message2 = models.Socket(
        message="Message 2",
        rooms="room1",
        sender_id=1,
        receiver_id=3,
        id_return=2,
    )
    user1 = models.User(user_name="User 1", id=1, avatar="avatar1")
    user2 = models.User(user_name="User 2", id=2, avatar="avatar2")
    user3 = models.User(user_name="User 3", id=3, avatar="avatar3")
    vote1 = models.Vote(message=message1, dir=1)
    vote2 = models.Vote(message=message2, dir=1)
    db_session.add_all([message1, message2, user1, user2, user3, vote1, vote2])
    db_session.commit()

    # Act
    result = messages.get_messages_room(db_session, "room1", limit=1)

    # Assert
    assert result == [
        schemas.SocketModel(
            created_at=message2.created_at,
            receiver_id=message2.receiver_id,
            message=message2.message,
            user_name=user2.user_name,
            avatar=user2.avatar,
            verified=user2.verified,
            id=message2.id,
            vote=1,
            id_return=message2.id_return,
        ),
    ]


def test_get_messages_room_with_skip(db_session):
    # Arrange
    message1 = models.Socket(
        message="Message 1",
        rooms="room1",
        sender_id=1,
        receiver_id=2,
        id_return=1,
    )
    message2 = models.Socket(
        message="Message 2",
        rooms="room1",
        sender_id=1,
        receiver_id=3,
        id_return=2,
    )
    user1 = models.User(user_name="User 1", id=1, avatar="avatar1")
    user2 = models.User(user_name="User 2", id=2, avatar="avatar2")
    user3 = models.User(user_name="User 3", id=3, avatar="avatar3")
    vote1 = models.Vote(message=message1, dir=1)
    vote2 = models.Vote(message=message2, dir=1)
    db_session.add_all([message1, message2, user1, user2, user3, vote1, vote2])
    db_session.commit()

    # Act
    result = messages.get_messages_room(db_session, "room1", skip=1)

    # Assert
    assert result == [
        schemas.SocketModel(
            created_at=message1.created_at,
            receiver_id=message1.receiver_id,
            message=message1.message,
            user_name=user1.user_name,
            avatar=user1.avatar,
            verified=user1.verified,
            id=message1.id,
            vote=1,
            id_return=message1.id_return,
        ),
    ]