# import io
# from fastapi.testclient import TestClient
# from app.routers.upload_file_google import create_upload_file


# client = TestClient(create_upload_file)

# def test_create_upload_file():
#     # Arrange
#     test_file = io.BytesIO(b"test content")
#     test_file_name = "test_file.txt"

#     # Act
#     response = client.post("/uploadfile/", files={"file": test_file, "filename": test_file_name})

#     # Assert
#     assert response.status_code == 200
#     assert response.json() == {"filename": test_file_name, "public_url": f"https://storage.googleapis.com/chatbuscket/test_file.txt"}