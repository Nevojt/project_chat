
from app import models, schemas
from app.routers.private_messages import get_private_recipient


def test_get_private_recipient(mocker):
    # Mock dependencies
    mock_db = mocker.Mock()
    mock_db.query.return_value.all.return_value = [
        (
            models.PrivateMessage(
                id=1,
                sender_id=1,
                recipient_id=2,
                is_read=True
            ),
            models.User(
                id=2,
                user_name="John Doe",
                avatar="https://example.com/avatar.png",
                verified=True
            )
        ),
        (
            models.PrivateMessage(
                id=2,
                sender_id=2,
                recipient_id=1,
                is_read=False
            ),
            models.User(
                id=1,
                user_name="Jane Doe",
                avatar="https://example.com/avatar2.png",
                verified=False
            )
        )
    ]

    # Call the function being tested
    result = get_private_recipient(user_id=1, db=mock_db)

    # Assert that the correct data was returned
    assert result == [
        schemas.PrivateInfoRecipient(
            recipient_id=2,
            recipient_name="John Doe",
            recipient_avatar="https://example.com/avatar.png",
            verified=True,
            is_read=True
        ),
        schemas.PrivateInfoRecipient(
            recipient_id=1,
            recipient_name="Jane Doe",
            recipient_avatar="https://example.com/avatar2.png",
            verified=False,
            is_read=False
        )
    ]