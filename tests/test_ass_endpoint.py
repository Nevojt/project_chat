
from unittest.mock import Mock

from fastapi import Depends, APIRouter, status, HTTPException

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

def test_ass_endpoint(self):
    # Arrange
    test_token = "test_token"
    test_session = Mock()
    test_user = Mock()
    mock_oauth2_verify_access_token = Mock(return_value=test_user)
    test_response = Mock(status_code=status.HTTP_200_OK)
    test_router = APIRouter(tags=['ASS'])

    # Act
    test_router.get('/ass')(
        Depends(lambda: test_token),
        session=Depends(lambda: test_session)
    )

    # Assert
    mock_oauth2_verify_access_token.assert_called_once_with(test_token, credentials_exception)
    test_session.query.return_value.get.assert_called_once_with(test_user.sub)
    test_response.return_value = test_user
    self.assertEqual(test_response, test_router.get('/ass')(
        Depends(lambda: test_token),
        session=Depends(lambda: test_session)
    ))