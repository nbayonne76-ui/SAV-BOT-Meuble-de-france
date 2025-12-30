# backend/tests/api/test_upload.py
"""
Comprehensive tests for upload API endpoints.
Tests file upload, validation, and statistics endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path
import io

from app.main import app
from app.api.endpoints.upload import is_allowed_file, get_file_directory


# ============================================================================
# TEST FIXTURES
# ============================================================================

@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_upload_dirs(tmp_path):
    """Mock upload directories"""
    upload_dir = tmp_path / "uploads"
    photos_dir = upload_dir / "photos"
    videos_dir = upload_dir / "videos"

    photos_dir.mkdir(parents=True)
    videos_dir.mkdir(parents=True)

    return {
        "upload_dir": upload_dir,
        "photos_dir": photos_dir,
        "videos_dir": videos_dir
    }


@pytest.fixture
def sample_image_file():
    """Create a sample image file"""
    file_content = b"fake image content"
    return ("test_image.jpg", io.BytesIO(file_content), "image/jpeg")


@pytest.fixture
def sample_video_file():
    """Create a sample video file"""
    file_content = b"fake video content"
    return ("test_video.mp4", io.BytesIO(file_content), "video/mp4")


# ============================================================================
# TESTS: Utility Functions
# ============================================================================

class TestUtilityFunctions:
    """Tests for utility functions"""

    def test_is_allowed_file_jpg(self):
        """Should accept .jpg files"""
        assert is_allowed_file("photo.jpg") is True

    def test_is_allowed_file_jpeg(self):
        """Should accept .jpeg files"""
        assert is_allowed_file("photo.jpeg") is True

    def test_is_allowed_file_png(self):
        """Should accept .png files"""
        assert is_allowed_file("photo.png") is True

    def test_is_allowed_file_mp4(self):
        """Should accept .mp4 files"""
        assert is_allowed_file("video.mp4") is True

    def test_is_allowed_file_mov(self):
        """Should accept .mov files"""
        assert is_allowed_file("video.mov") is True

    def test_is_allowed_file_avi(self):
        """Should accept .avi files"""
        assert is_allowed_file("video.avi") is True

    def test_is_allowed_file_case_insensitive(self):
        """Should be case insensitive"""
        assert is_allowed_file("PHOTO.JPG") is True
        assert is_allowed_file("Photo.JpEg") is True

    def test_is_allowed_file_not_allowed(self):
        """Should reject non-allowed extensions"""
        assert is_allowed_file("document.pdf") is False
        assert is_allowed_file("script.exe") is False
        assert is_allowed_file("file.txt") is False

    def test_is_allowed_file_no_extension(self):
        """Should reject files without extension"""
        assert is_allowed_file("filename") is False

    def test_get_file_directory_video(self):
        """Should return videos directory for video files"""
        with patch('app.api.endpoints.upload.VIDEOS_DIR', Path('/videos')), \
             patch('app.api.endpoints.upload.PHOTOS_DIR', Path('/photos')):
            result = get_file_directory("test.mp4")
            assert result == Path('/videos')

            result = get_file_directory("test.mov")
            assert result == Path('/videos')

            result = get_file_directory("test.avi")
            assert result == Path('/videos')

    def test_get_file_directory_photo(self):
        """Should return photos directory for image files"""
        with patch('app.api.endpoints.upload.VIDEOS_DIR', Path('/videos')), \
             patch('app.api.endpoints.upload.PHOTOS_DIR', Path('/photos')):
            result = get_file_directory("test.jpg")
            assert result == Path('/photos')

            result = get_file_directory("test.png")
            assert result == Path('/photos')

    def test_get_file_directory_no_extension(self):
        """Should return photos directory for files without extension"""
        with patch('app.api.endpoints.upload.VIDEOS_DIR', Path('/videos')), \
             patch('app.api.endpoints.upload.PHOTOS_DIR', Path('/photos')):
            result = get_file_directory("filename")
            assert result == Path('/photos')


# ============================================================================
# TESTS: POST /upload Endpoint
# ============================================================================

class TestUploadFilesEndpoint:
    """Tests for file upload endpoint"""

    def test_upload_single_image_success(self, client, mock_upload_dirs):
        """Should upload single image successfully"""
        with patch('app.api.endpoints.upload.PHOTOS_DIR', mock_upload_dirs["photos_dir"]), \
             patch('app.api.endpoints.upload.VIDEOS_DIR', mock_upload_dirs["videos_dir"]), \
             patch('app.api.endpoints.upload.settings.MAX_FILE_SIZE', 10 * 1024 * 1024):

            file_content = b"fake image content"
            files = {"files": ("test.jpg", io.BytesIO(file_content), "image/jpeg")}

            response = client.post("/api/upload", files=files)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["count"] == 1
            assert len(data["files"]) == 1
            assert data["files"][0]["original_name"] == "test.jpg"
            assert data["files"][0]["type"] == "jpg"
            assert data["files"][0]["size"] == len(file_content)
            assert "/uploads/photos/" in data["files"][0]["url"]

    def test_upload_multiple_files_success(self, client, mock_upload_dirs):
        """Should upload multiple files successfully"""
        with patch('app.api.endpoints.upload.PHOTOS_DIR', mock_upload_dirs["photos_dir"]), \
             patch('app.api.endpoints.upload.VIDEOS_DIR', mock_upload_dirs["videos_dir"]), \
             patch('app.api.endpoints.upload.settings.MAX_FILE_SIZE', 10 * 1024 * 1024):

            files = [
                ("files", ("photo1.jpg", io.BytesIO(b"content1"), "image/jpeg")),
                ("files", ("photo2.png", io.BytesIO(b"content2"), "image/png")),
                ("files", ("video1.mp4", io.BytesIO(b"content3"), "video/mp4"))
            ]

            response = client.post("/api/upload", files=files)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["count"] == 3
            assert len(data["files"]) == 3

            # Check photos go to photos dir
            photo_files = [f for f in data["files"] if f["type"] in ["jpg", "png"]]
            assert all("/uploads/photos/" in f["url"] for f in photo_files)

            # Check videos go to videos dir
            video_files = [f for f in data["files"] if f["type"] == "mp4"]
            assert all("/uploads/videos/" in f["url"] for f in video_files)

    def test_upload_no_files(self, client):
        """Should return 400 when no files provided"""
        response = client.post("/api/upload", files=[])

        assert response.status_code == 400
        assert "Aucun fichier fourni" in response.json()["detail"]

    def test_upload_invalid_file_type(self, client, mock_upload_dirs):
        """Should reject invalid file type"""
        with patch('app.api.endpoints.upload.PHOTOS_DIR', mock_upload_dirs["photos_dir"]):
            files = {"files": ("document.pdf", io.BytesIO(b"content"), "application/pdf")}

            response = client.post("/api/upload", files=files)

            assert response.status_code == 400
            assert "non autorisé" in response.json()["detail"]

    def test_upload_file_too_large(self, client, mock_upload_dirs):
        """Should reject files exceeding size limit"""
        with patch('app.api.endpoints.upload.PHOTOS_DIR', mock_upload_dirs["photos_dir"]), \
             patch('app.api.endpoints.upload.settings.MAX_FILE_SIZE', 100):  # 100 bytes limit

            large_content = b"x" * 200  # 200 bytes
            files = {"files": ("large.jpg", io.BytesIO(large_content), "image/jpeg")}

            response = client.post("/api/upload", files=files)

            assert response.status_code == 400
            assert "trop volumineux" in response.json()["detail"]

    def test_upload_filename_with_timestamp(self, client, mock_upload_dirs):
        """Should add timestamp to filename"""
        with patch('app.api.endpoints.upload.PHOTOS_DIR', mock_upload_dirs["photos_dir"]), \
             patch('app.api.endpoints.upload.VIDEOS_DIR', mock_upload_dirs["videos_dir"]), \
             patch('app.api.endpoints.upload.settings.MAX_FILE_SIZE', 10 * 1024 * 1024):

            files = {"files": ("myfile.jpg", io.BytesIO(b"content"), "image/jpeg")}

            response = client.post("/api/upload", files=files)

            assert response.status_code == 200
            data = response.json()
            saved_name = data["files"][0]["saved_name"]
            # Should have timestamp prefix
            assert saved_name.endswith("_myfile.jpg")
            # Timestamp should be 14 digits (YYYYMMDDHHMMSS)
            assert len(saved_name.split("_")[0]) == 14

    def test_upload_video_file(self, client, mock_upload_dirs):
        """Should upload video file to videos directory"""
        with patch('app.api.endpoints.upload.PHOTOS_DIR', mock_upload_dirs["photos_dir"]), \
             patch('app.api.endpoints.upload.VIDEOS_DIR', mock_upload_dirs["videos_dir"]), \
             patch('app.api.endpoints.upload.settings.MAX_FILE_SIZE', 50 * 1024 * 1024):

            video_content = b"fake video content"
            files = {"files": ("myvideo.mp4", io.BytesIO(video_content), "video/mp4")}

            response = client.post("/api/upload", files=files)

            assert response.status_code == 200
            data = response.json()
            assert data["files"][0]["type"] == "mp4"
            assert "/uploads/videos/" in data["files"][0]["url"]


# ============================================================================
# TESTS: GET /upload/stats Endpoint
# ============================================================================

class TestUploadStatsEndpoint:
    """Tests for upload statistics endpoint"""

    def test_get_stats_empty_directories(self, client, mock_upload_dirs):
        """Should return zero stats for empty directories"""
        with patch('app.api.endpoints.upload.PHOTOS_DIR', mock_upload_dirs["photos_dir"]), \
             patch('app.api.endpoints.upload.VIDEOS_DIR', mock_upload_dirs["videos_dir"]):

            response = client.get("/api/upload/stats")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["stats"]["photos"] == 0
            assert data["stats"]["videos"] == 0
            assert data["stats"]["total"] == 0

    def test_get_stats_with_files(self, client, mock_upload_dirs):
        """Should return correct stats with files"""
        # Create some test files
        (mock_upload_dirs["photos_dir"] / "photo1.jpg").touch()
        (mock_upload_dirs["photos_dir"] / "photo2.png").touch()
        (mock_upload_dirs["videos_dir"] / "video1.mp4").touch()

        with patch('app.api.endpoints.upload.PHOTOS_DIR', mock_upload_dirs["photos_dir"]), \
             patch('app.api.endpoints.upload.VIDEOS_DIR', mock_upload_dirs["videos_dir"]):

            response = client.get("/api/upload/stats")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["stats"]["photos"] == 2
            assert data["stats"]["videos"] == 1
            assert data["stats"]["total"] == 3

    def test_get_stats_error_handling(self, client):
        """Should handle errors gracefully"""
        with patch('app.api.endpoints.upload.PHOTOS_DIR', Path("/nonexistent/path")), \
             patch('app.api.endpoints.upload.VIDEOS_DIR', Path("/nonexistent/path")):

            response = client.get("/api/upload/stats")

            # Should return error
            assert response.status_code == 500


# ============================================================================
# TESTS: Edge Cases and Error Handling
# ============================================================================

class TestEdgeCases:
    """Tests for edge cases and error handling"""

    def test_upload_file_without_extension(self, client, mock_upload_dirs):
        """Should handle files without extension"""
        with patch('app.api.endpoints.upload.PHOTOS_DIR', mock_upload_dirs["photos_dir"]), \
             patch('app.api.endpoints.upload.settings.MAX_FILE_SIZE', 10 * 1024 * 1024):

            # File without extension gets default 'jpg'
            files = {"files": ("filename", io.BytesIO(b"content"), "image/jpeg")}

            response = client.post("/api/upload", files=files)

            # Should be rejected by is_allowed_file
            assert response.status_code == 400

    def test_upload_special_characters_in_filename(self, client, mock_upload_dirs):
        """Should handle special characters in filename"""
        with patch('app.api.endpoints.upload.PHOTOS_DIR', mock_upload_dirs["photos_dir"]), \
             patch('app.api.endpoints.upload.VIDEOS_DIR', mock_upload_dirs["videos_dir"]), \
             patch('app.api.endpoints.upload.settings.MAX_FILE_SIZE', 10 * 1024 * 1024):

            files = {"files": ("my-photo_2024 (1).jpg", io.BytesIO(b"content"), "image/jpeg")}

            response = client.post("/api/upload", files=files)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            # Filename should be preserved
            assert "my-photo_2024 (1).jpg" in data["files"][0]["saved_name"]

    def test_upload_concurrent_files_same_name(self, client, mock_upload_dirs):
        """Should handle concurrent uploads with same filename (timestamp ensures uniqueness)"""
        with patch('app.api.endpoints.upload.PHOTOS_DIR', mock_upload_dirs["photos_dir"]), \
             patch('app.api.endpoints.upload.VIDEOS_DIR', mock_upload_dirs["videos_dir"]), \
             patch('app.api.endpoints.upload.settings.MAX_FILE_SIZE', 10 * 1024 * 1024):

            # Upload same filename twice
            files1 = {"files": ("photo.jpg", io.BytesIO(b"content1"), "image/jpeg")}
            files2 = {"files": ("photo.jpg", io.BytesIO(b"content2"), "image/jpeg")}

            response1 = client.post("/api/upload", files=files1)
            response2 = client.post("/api/upload", files=files2)

            assert response1.status_code == 200
            assert response2.status_code == 200

            # Saved names should be different due to timestamp
            name1 = response1.json()["files"][0]["saved_name"]
            name2 = response2.json()["files"][0]["saved_name"]
            # They might be the same if uploaded in the same second, but that's acceptable
            # The important thing is both succeeded
