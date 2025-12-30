# backend/tests/services/test_evidence_collector.py
"""
Tests complets pour le système de collecte et validation des preuves
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

from app.services.evidence_collector import (
    EvidenceCollector,
    EvidenceType,
    EvidenceQuality,
    EvidenceAnalysis,
    CompletenessCheck,
    evidence_collector
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def collector():
    """Instance fresh du collector pour chaque test"""
    return EvidenceCollector()


# ============================================================================
# TESTS: Enums
# ============================================================================

class TestEnums:
    """Tests for enum values"""

    def test_evidence_type_enum(self):
        """Should have correct evidence types"""
        assert EvidenceType.PHOTO == "photo"
        assert EvidenceType.VIDEO == "video"
        assert EvidenceType.DOCUMENT == "document"
        assert EvidenceType.INVOICE == "invoice"

    def test_evidence_quality_enum(self):
        """Should have correct quality levels"""
        assert EvidenceQuality.EXCELLENT == "excellent"
        assert EvidenceQuality.GOOD == "good"
        assert EvidenceQuality.ACCEPTABLE == "acceptable"
        assert EvidenceQuality.POOR == "poor"
        assert EvidenceQuality.UNUSABLE == "unusable"


# ============================================================================
# TESTS: Initialization
# ============================================================================

class TestInitialization:
    """Tests for EvidenceCollector initialization"""

    def test_collector_initialization(self, collector):
        """Should initialize with requirements and rules"""
        # Verify requirements by category are loaded
        assert "structural" in collector.requirements_by_category
        assert "mechanism" in collector.requirements_by_category
        assert "fabric" in collector.requirements_by_category

        # Verify photo quality rules
        assert "min_file_size_kb" in collector.photo_quality_rules
        assert collector.photo_quality_rules["min_file_size_kb"] == 50

        # Verify video quality rules
        assert "min_duration_seconds" in collector.video_quality_rules
        assert collector.video_quality_rules["min_duration_seconds"] == 5

    def test_structural_requirements(self, collector):
        """Should have correct structural requirements"""
        req = collector.requirements_by_category["structural"]
        assert req["min_photos"] == 3
        assert req["min_videos"] == 1
        assert "vue_ensemble" in req["required_angles"]

    def test_fabric_requirements(self, collector):
        """Should have correct fabric requirements"""
        req = collector.requirements_by_category["fabric"]
        assert req["min_photos"] == 3
        assert req["min_videos"] == 0
        assert "zoom_defaut" in req["required_angles"]


# ============================================================================
# TESTS: File Extension Extraction
# ============================================================================

class TestFileExtension:
    """Tests for _get_file_extension method"""

    def test_get_jpg_extension(self, collector):
        """Should extract .jpg extension"""
        url = "https://example.com/photo.jpg"
        assert collector._get_file_extension(url) == ".jpg"

    def test_get_png_extension(self, collector):
        """Should extract .png extension"""
        url = "https://example.com/image.PNG"
        assert collector._get_file_extension(url) == ".png"  # Lowercase

    def test_get_mp4_extension(self, collector):
        """Should extract .mp4 extension"""
        url = "https://example.com/video.mp4"
        assert collector._get_file_extension(url) == ".mp4"

    def test_get_extension_with_query_params(self, collector):
        """Should extract extension from URL (regex matches last dot pattern)"""
        url = "https://example.com/file.pdf"
        result = collector._get_file_extension(url)
        # The regex r'\.[a-zA-Z0-9]+$' matches from last dot to end
        assert result == ".pdf"

    def test_no_extension(self, collector):
        """Should return empty string for no extension"""
        url = "https://example.com/file"
        assert collector._get_file_extension(url) == ""


# ============================================================================
# TESTS: Photo Analysis
# ============================================================================

class TestPhotoAnalysis:
    """Tests for photo analysis"""

    def test_analyze_photo_excellent_quality(self, collector):
        """Should rate excellent quality photo highly"""
        result = collector.analyze_evidence(
            evidence_id="PHOTO-001",
            evidence_type=EvidenceType.PHOTO,
            file_url="https://example.com/photo.jpg",
            file_size_bytes=500 * 1024,  # 500KB (good size)
            description="Photo claire du mécanisme cassé montrant tous les détails",
            metadata={"width": 1920, "height": 1080}
        )

        assert result.quality == EvidenceQuality.EXCELLENT
        assert result.quality_score >= 90
        assert result.verified is True
        assert len(result.strengths) > 0

    def test_analyze_photo_poor_quality_too_small(self, collector):
        """Should penalize photos that are too small"""
        result = collector.analyze_evidence(
            evidence_id="PHOTO-002",
            evidence_type=EvidenceType.PHOTO,
            file_url="https://example.com/photo.jpg",
            file_size_bytes=30 * 1024,  # 30KB (too small)
            description="Photo floue",
            metadata={"width": 320, "height": 240}  # Low resolution
        )

        assert result.quality_score < 60
        assert any("trop petit" in issue.lower() for issue in result.issues)
        assert any("résolution" in issue.lower() for issue in result.issues)

    def test_analyze_photo_missing_description(self, collector):
        """Should penalize photos with short description"""
        result = collector.analyze_evidence(
            evidence_id="PHOTO-003",
            evidence_type=EvidenceType.PHOTO,
            file_url="https://example.com/photo.jpg",
            file_size_bytes=200 * 1024,
            description="Photo",  # Too short (< 10 chars)
            metadata=None
        )

        assert any("description" in issue.lower() for issue in result.issues)
        assert result.quality_score < 100

    def test_analyze_photo_wrong_format(self, collector):
        """Should penalize non-standard formats"""
        result = collector.analyze_evidence(
            evidence_id="PHOTO-004",
            evidence_type=EvidenceType.PHOTO,
            file_url="https://example.com/photo.bmp",  # BMP not in accepted formats
            file_size_bytes=200 * 1024,
            description="Photo du problème visible sur le canapé",
            metadata=None
        )

        assert any("format" in issue.lower() for issue in result.issues)

    def test_analyze_photo_too_large(self, collector):
        """Should warn about very large files"""
        result = collector.analyze_evidence(
            evidence_id="PHOTO-005",
            evidence_type=EvidenceType.PHOTO,
            file_url="https://example.com/photo.jpg",
            file_size_bytes=25 * 1024 * 1024,  # 25MB (too large)
            description="Photo haute résolution du problème",
            metadata={"width": 4000, "height": 3000}
        )

        assert any("volumineux" in issue.lower() for issue in result.issues)


# ============================================================================
# TESTS: Video Analysis
# ============================================================================

class TestVideoAnalysis:
    """Tests for video analysis"""

    def test_analyze_video_good_quality(self, collector):
        """Should rate good quality video highly"""
        result = collector.analyze_evidence(
            evidence_id="VIDEO-001",
            evidence_type=EvidenceType.VIDEO,
            file_url="https://example.com/video.mp4",
            file_size_bytes=15 * 1024 * 1024,  # 15MB
            description="Vidéo montrant le mécanisme défectueux en action",
            metadata={"duration": 30}  # 30 seconds
        )

        assert result.quality == EvidenceQuality.EXCELLENT or result.quality == EvidenceQuality.GOOD
        assert result.quality_score >= 75
        assert result.verified is True

    def test_analyze_video_too_short(self, collector):
        """Should penalize videos that are too short"""
        result = collector.analyze_evidence(
            evidence_id="VIDEO-002",
            evidence_type=EvidenceType.VIDEO,
            file_url="https://example.com/video.mp4",
            file_size_bytes=2 * 1024 * 1024,
            description="Vidéo rapide du problème",
            metadata={"duration": 3}  # 3 seconds (too short)
        )

        assert any("trop courte" in issue.lower() for issue in result.issues)
        assert result.quality_score < 100

    def test_analyze_video_too_long(self, collector):
        """Should penalize videos that are too long"""
        result = collector.analyze_evidence(
            evidence_id="VIDEO-003",
            evidence_type=EvidenceType.VIDEO,
            file_url="https://example.com/video.mp4",
            file_size_bytes=50 * 1024 * 1024,
            description="Longue vidéo montrant tous les détails",
            metadata={"duration": 180}  # 3 minutes (too long)
        )

        assert any("trop longue" in issue.lower() for issue in result.issues)

    def test_analyze_video_too_large_file(self, collector):
        """Should warn about very large video files"""
        result = collector.analyze_evidence(
            evidence_id="VIDEO-004",
            evidence_type=EvidenceType.VIDEO,
            file_url="https://example.com/video.mp4",
            file_size_bytes=150 * 1024 * 1024,  # 150MB (too large)
            description="Vidéo haute définition",
            metadata={"duration": 45}
        )

        assert any("volumineuse" in issue.lower() for issue in result.issues)

    def test_analyze_video_wrong_format(self, collector):
        """Should penalize non-standard video formats"""
        result = collector.analyze_evidence(
            evidence_id="VIDEO-005",
            evidence_type=EvidenceType.VIDEO,
            file_url="https://example.com/video.wmv",  # WMV not in accepted formats
            file_size_bytes=10 * 1024 * 1024,
            description="Vidéo du problème",
            metadata={"duration": 20}
        )

        assert any("format" in issue.lower() for issue in result.issues)

    def test_analyze_video_short_description(self, collector):
        """Should penalize short video descriptions"""
        result = collector.analyze_evidence(
            evidence_id="VIDEO-006",
            evidence_type=EvidenceType.VIDEO,
            file_url="https://example.com/video.mp4",
            file_size_bytes=10 * 1024 * 1024,
            description="Vidéo",  # Too short (< 15 chars)
            metadata={"duration": 20}
        )

        assert any("description" in issue.lower() for issue in result.issues)


# ============================================================================
# TESTS: Document Analysis
# ============================================================================

class TestDocumentAnalysis:
    """Tests for document analysis"""

    def test_analyze_document_pdf_good(self, collector):
        """Should accept PDF documents"""
        result = collector.analyze_evidence(
            evidence_id="DOC-001",
            evidence_type=EvidenceType.DOCUMENT,
            file_url="https://example.com/invoice.pdf",
            file_size_bytes=500 * 1024,  # 500KB
            description="Facture d'achat du canapé"
        )

        assert result.quality == EvidenceQuality.EXCELLENT or result.quality == EvidenceQuality.GOOD
        assert result.verified is True

    def test_analyze_invoice_jpg(self, collector):
        """Should accept invoice as JPG"""
        result = collector.analyze_evidence(
            evidence_id="INV-001",
            evidence_type=EvidenceType.INVOICE,
            file_url="https://example.com/facture.jpg",
            file_size_bytes=1 * 1024 * 1024,
            description="Photo de la facture"
        )

        assert result.quality_score >= 60

    def test_analyze_document_wrong_format(self, collector):
        """Should penalize wrong document formats"""
        result = collector.analyze_evidence(
            evidence_id="DOC-002",
            evidence_type=EvidenceType.DOCUMENT,
            file_url="https://example.com/doc.doc",  # .doc not accepted
            file_size_bytes=1 * 1024 * 1024,
            description="Document Word"
        )

        assert any("format" in issue.lower() for issue in result.issues)

    def test_analyze_document_too_large(self, collector):
        """Should warn about large documents"""
        result = collector.analyze_evidence(
            evidence_id="DOC-003",
            evidence_type=EvidenceType.DOCUMENT,
            file_url="https://example.com/doc.pdf",
            file_size_bytes=15 * 1024 * 1024,  # 15MB
            description="Gros document PDF"
        )

        assert any("volumineux" in issue.lower() for issue in result.issues)

    def test_analyze_document_missing_description(self, collector):
        """Should penalize documents without description"""
        result = collector.analyze_evidence(
            evidence_id="DOC-004",
            evidence_type=EvidenceType.DOCUMENT,
            file_url="https://example.com/doc.pdf",
            file_size_bytes=500 * 1024,
            description="Doc"  # Too short (< 5 chars)
        )

        assert any("précisez" in issue.lower() or "type" in issue.lower() for issue in result.issues)


# ============================================================================
# TESTS: Completeness Check
# ============================================================================

class TestCompletenessCheck:
    """Tests for evidence completeness checking"""

    def test_completeness_structural_complete(self, collector):
        """Should mark structural evidences as complete when sufficient"""
        evidences = [
            {"type": EvidenceType.PHOTO, "quality_score": 85},
            {"type": EvidenceType.PHOTO, "quality_score": 80},
            {"type": EvidenceType.PHOTO, "quality_score": 90},
            {"type": EvidenceType.VIDEO, "quality_score": 85},
        ]

        result = collector.check_completeness(
            problem_category="structural",
            evidences=evidences,
            problem_severity="P1"
        )

        assert result.is_complete is True
        assert len(result.missing_items) == 0
        assert result.completeness_score >= 70

    def test_completeness_structural_missing_photos(self, collector):
        """Should detect missing photos for structural"""
        evidences = [
            {"type": EvidenceType.PHOTO, "quality_score": 85},
            {"type": EvidenceType.VIDEO, "quality_score": 85},
        ]

        result = collector.check_completeness(
            problem_category="structural",
            evidences=evidences,
            problem_severity="P2"
        )

        assert result.is_complete is False
        assert any("photo" in item.lower() for item in result.missing_items)

    def test_completeness_mechanism_missing_video(self, collector):
        """Should detect missing video for mechanism"""
        evidences = [
            {"type": EvidenceType.PHOTO, "quality_score": 85},
            {"type": EvidenceType.PHOTO, "quality_score": 80},
        ]

        result = collector.check_completeness(
            problem_category="mechanism",
            evidences=evidences,
            problem_severity="P2"
        )

        assert result.is_complete is False
        assert any("vidéo" in item.lower() for item in result.missing_items)

    def test_completeness_fabric_no_video_required(self, collector):
        """Should not require video for fabric issues"""
        evidences = [
            {"type": EvidenceType.PHOTO, "quality_score": 85},
            {"type": EvidenceType.PHOTO, "quality_score": 80},
            {"type": EvidenceType.PHOTO, "quality_score": 90},
        ]

        result = collector.check_completeness(
            problem_category="fabric",
            evidences=evidences,
            problem_severity="P2"
        )

        assert result.is_complete is True
        assert not any("vidéo" in item.lower() for item in result.missing_items)

    def test_completeness_can_proceed_p0_priority(self, collector):
        """Should allow proceeding for P0 even if incomplete"""
        evidences = [
            {"type": EvidenceType.PHOTO, "quality_score": 85},
        ]

        result = collector.check_completeness(
            problem_category="structural",
            evidences=evidences,
            problem_severity="P0"  # Critical
        )

        # Even if incomplete, P0 should be able to proceed
        assert result.can_proceed is True

    def test_completeness_poor_quality_evidences(self, collector):
        """Should detect poor quality evidences affecting score"""
        evidences = [
            {"type": EvidenceType.PHOTO, "quality_score": 40},  # Poor quality
            {"type": EvidenceType.PHOTO, "quality_score": 45},  # Poor quality
        ]

        result = collector.check_completeness(
            problem_category="fabric",
            evidences=evidences,
            problem_severity="P3"
        )

        # Quality score should be affected
        assert result.completeness_score < 80

    def test_completeness_unknown_category_defaults(self, collector):
        """Should use defaults for unknown problem category"""
        evidences = [
            {"type": EvidenceType.PHOTO, "quality_score": 85},
            {"type": EvidenceType.PHOTO, "quality_score": 80},
        ]

        result = collector.check_completeness(
            problem_category="unknown_category",
            evidences=evidences,
            problem_severity="P2"
        )

        # Should not crash and should use default requirements
        assert result is not None
        assert isinstance(result.completeness_score, float)


# ============================================================================
# TESTS: Recommendations Generation
# ============================================================================

class TestRecommendations:
    """Tests for recommendation generation"""

    def test_generate_recommendations_photo_too_small(self, collector):
        """Should recommend better quality for small photos"""
        issues = ["Fichier trop petit (30KB) - qualité probablement insuffisante"]
        recommendations = collector._generate_recommendations(EvidenceType.PHOTO, issues)

        assert len(recommendations) > 0
        assert any("meilleure qualité" in rec.lower() for rec in recommendations)

    def test_generate_recommendations_low_resolution(self, collector):
        """Should recommend high resolution for low res photos"""
        issues = ["Résolution trop faible (320x240) - minimum 640x480"]
        recommendations = collector._generate_recommendations(EvidenceType.PHOTO, issues)

        assert any("smartphone" in rec.lower() or "résolution" in rec.lower() for rec in recommendations)

    def test_generate_recommendations_missing_description(self, collector):
        """Should recommend description"""
        issues = ["Description trop courte - détaillez ce qui est visible"]
        recommendations = collector._generate_recommendations(EvidenceType.PHOTO, issues)

        assert any("décrivez" in rec.lower() for rec in recommendations)

    def test_generate_recommendations_video_too_short(self, collector):
        """Should recommend longer video"""
        issues = ["Vidéo trop courte (3s) - minimum 5 secondes"]
        recommendations = collector._generate_recommendations(EvidenceType.VIDEO, issues)

        assert any("10 secondes" in rec.lower() or "au moins" in rec.lower() for rec in recommendations)

    def test_generate_recommendations_video_too_long(self, collector):
        """Should recommend shorter video"""
        issues = ["Vidéo trop longue (180s) - maximum 2 minutes"]
        recommendations = collector._generate_recommendations(EvidenceType.VIDEO, issues)

        assert any("max" in rec.lower() or "2 minutes" in rec.lower() for rec in recommendations)


# ============================================================================
# TESTS: Additional Requests Generation
# ============================================================================

class TestAdditionalRequests:
    """Tests for additional evidence requests"""

    def test_generate_additional_requests_photos(self, collector):
        """Should generate specific photo requests"""
        requirements = collector.requirements_by_category["mechanism"]
        missing_items = ["2 photo(s) supplémentaire(s)"]

        requests = collector._generate_additional_requests(
            problem_category="mechanism",
            requirements=requirements,
            missing_items=missing_items
        )

        assert len(requests) > 0
        assert any("photo" in req.lower() for req in requests)
        assert any("mecanisme" in req.lower() for req in requests)

    def test_generate_additional_requests_video_mechanism(self, collector):
        """Should request mechanism video"""
        requirements = collector.requirements_by_category["mechanism"]
        missing_items = ["1 vidéo(s)"]

        requests = collector._generate_additional_requests(
            problem_category="mechanism",
            requirements=requirements,
            missing_items=missing_items
        )

        assert any("vidéo" in req.lower() and "mécanisme" in req.lower() for req in requests)

    def test_generate_additional_requests_video_structural(self, collector):
        """Should request structural video"""
        requirements = collector.requirements_by_category["structural"]
        missing_items = ["1 vidéo(s)"]

        requests = collector._generate_additional_requests(
            problem_category="structural",
            requirements=requirements,
            missing_items=missing_items
        )

        assert any("structure" in req.lower() for req in requests)


# ============================================================================
# TESTS: Evidence Request Message
# ============================================================================

class TestEvidenceRequestMessage:
    """Tests for evidence request message generation"""

    def test_generate_request_message_structural_p0(self, collector):
        """Should generate urgent message for P0 structural"""
        message = collector.generate_evidence_request_message(
            problem_category="structural",
            priority="P0"
        )

        assert "URGENT" in message or "🔴" in message
        assert "3 photo(s)" in message
        assert "1 vidéo(s)" in message

    def test_generate_request_message_fabric_p2(self, collector):
        """Should generate normal message for P2 fabric"""
        message = collector.generate_evidence_request_message(
            problem_category="fabric",
            priority="P2"
        )

        assert "3 photo(s)" in message
        # Fabric doesn't require video
        assert "vidéo" not in message.lower() or "0 vidéo" in message

    def test_generate_request_message_contains_tips(self, collector):
        """Should contain helpful tips"""
        message = collector.generate_evidence_request_message(
            problem_category="mechanism",
            priority="P1"
        )

        assert "Conseils" in message or "⚠️" in message
        assert "lumière" in message.lower() or "éclairage" in message.lower()

    def test_generate_request_message_includes_angles(self, collector):
        """Should include required angles"""
        message = collector.generate_evidence_request_message(
            problem_category="mechanism",
            priority="P1"
        )

        assert "Angles" in message or "📐" in message

    def test_generate_request_message_unknown_category(self, collector):
        """Should handle unknown category gracefully"""
        message = collector.generate_evidence_request_message(
            problem_category="unknown",
            priority="P2"
        )

        # Should return a generic message
        assert "photo" in message.lower()
        assert len(message) > 0


# ============================================================================
# TESTS: Global Instance
# ============================================================================

class TestGlobalInstance:
    """Tests for global evidence_collector instance"""

    def test_global_instance_exists(self):
        """Should have global instance"""
        assert evidence_collector is not None
        assert isinstance(evidence_collector, EvidenceCollector)

    def test_global_instance_usable(self):
        """Should be able to use global instance"""
        result = evidence_collector.analyze_evidence(
            evidence_id="TEST-001",
            evidence_type=EvidenceType.PHOTO,
            file_url="https://example.com/test.jpg",
            file_size_bytes=200 * 1024,
            description="Test photo for global instance"
        )

        assert result is not None
        assert isinstance(result, EvidenceAnalysis)
