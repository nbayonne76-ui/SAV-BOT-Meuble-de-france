# backend/tests/api/test_sav.py
"""
Comprehensive tests for SAV API endpoints.
Tests claim creation, evidence management, and ticket operations.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.main import app
from app.services.sav_workflow_engine import SAVTicket, TicketStatus
from app.services.evidence_collector import EvidenceType, EvidenceQuality


# ============================================================================
# TEST FIXTURES
# ============================================================================

@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_warranty_service():
    """Mock warranty service"""
    service = AsyncMock()

    mock_warranty = MagicMock()
    mock_warranty.warranty_id = "WARRANTY-001"
    mock_warranty.product_sku = "TEST-SKU"
    mock_warranty.customer_id = "customer@test.fr"

    service.create_warranty = AsyncMock(return_value=mock_warranty)
    service.check_warranty_coverage = AsyncMock(return_value=MagicMock(
        is_covered=True,
        component="Test Component",
        reason=None
    ))

    return service


@pytest.fixture
def mock_sav_workflow_engine():
    """Mock SAV workflow engine"""
    engine = MagicMock()

    # Mock ticket
    mock_ticket = MagicMock()
    mock_ticket.ticket_id = "SAV-TEST-001"
    mock_ticket.status = TicketStatus.OPEN
    mock_ticket.priority = "P1"
    mock_ticket.priority_score = 75
    mock_ticket.problem_category = "mechanism"
    mock_ticket.problem_severity = "P1"
    mock_ticket.problem_confidence = 0.85
    mock_ticket.auto_resolved = False
    mock_ticket.resolution_type = None
    mock_ticket.resolution_description = None
    mock_ticket.sla_response_deadline = datetime.now()
    mock_ticket.sla_intervention_deadline = datetime.now()
    mock_ticket.created_at = datetime.now()
    mock_ticket.evidences = []
    mock_ticket.actions = []

    # Mock warranty check result
    mock_warranty_check = MagicMock()
    mock_warranty_check.is_covered = True
    mock_warranty_check.component = "Mécanisme"
    mock_ticket.warranty_check_result = mock_warranty_check

    # Mock tone analysis
    mock_tone = MagicMock()
    mock_tone.tone = "frustrated"
    mock_tone.urgency = "high"
    mock_tone.emotion_score = 0.7
    mock_ticket.tone_analysis = mock_tone

    # Mock client summary
    mock_summary = MagicMock()
    mock_summary.summary_id = "SUMMARY-001"
    mock_summary.validation_required = False
    mock_summary.email_body = "Email body"
    mock_summary.sms_body = "SMS body"
    mock_summary.validation_link = None
    mock_ticket.client_summary = mock_summary

    engine.process_new_claim = AsyncMock(return_value=mock_ticket)
    engine.add_evidence = MagicMock(return_value=mock_ticket)
    engine.get_ticket_summary = MagicMock(return_value={"ticket_id": "SAV-TEST-001"})
    engine.active_tickets = {"SAV-TEST-001": mock_ticket}

    return engine


@pytest.fixture
def mock_evidence_collector():
    """Mock evidence collector"""
    collector = MagicMock()

    # Mock evidence analysis
    mock_analysis = MagicMock()
    mock_analysis.quality = EvidenceQuality.GOOD
    mock_analysis.quality_score = 80
    mock_analysis.issues = []
    mock_analysis.strengths = ["Clear photo", "Good lighting"]
    mock_analysis.recommendations = []
    mock_analysis.verified = True

    collector.analyze_evidence = MagicMock(return_value=mock_analysis)
    collector.generate_evidence_request_message = MagicMock(return_value="Veuillez fournir des photos")

    # Mock completeness check
    mock_completeness = MagicMock()
    mock_completeness.is_complete = True
    mock_completeness.completeness_score = 100
    mock_completeness.missing_items = []
    mock_completeness.additional_requests = []
    mock_completeness.can_proceed = True

    collector.check_completeness = MagicMock(return_value=mock_completeness)
    collector.requirements_by_category = {
        "structural": {"min_photos": 3, "min_videos": 1},
        "mechanism": {"min_photos": 2, "min_videos": 1}
    }

    return collector


# ============================================================================
# TESTS: POST /sav/create-claim Endpoint
# ============================================================================

class TestCreateClaimEndpoint:
    """Tests for create claim endpoint"""

    def test_create_claim_success(self, client, mock_warranty_service, mock_sav_workflow_engine, mock_evidence_collector):
        """Should create claim successfully"""
        with patch('app.api.endpoints.sav.warranty_service', mock_warranty_service), \
             patch('app.api.endpoints.sav.sav_workflow_engine', mock_sav_workflow_engine), \
             patch('app.api.endpoints.sav.evidence_collector', mock_evidence_collector):

            response = client.post("/api/sav/create-claim", json={
                "customer_id": "customer@test.fr",
                "order_number": "CMD-1234-56789",
                "product_sku": "OSLO-3P",
                "product_name": "Canapé OSLO 3 places",
                "problem_description": "Le mécanisme ne fonctionne plus",
                "purchase_date": "2024-01-01T00:00:00Z",
                "delivery_date": "2024-01-15T00:00:00Z",
                "customer_tier": "gold",
                "product_value": 1890.0
            })

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["ticket"]["ticket_id"] == "SAV-TEST-001"
            assert data["ticket"]["priority"] == "P1"
            assert data["ticket"]["problem_category"] == "mechanism"
            assert data["ticket"]["warranty_covered"] is True
            assert "evidence_requirements" in data
            assert "next_steps" in data

    def test_create_claim_with_auto_resolution(self, client, mock_warranty_service, mock_sav_workflow_engine, mock_evidence_collector):
        """Should handle auto-resolved claims"""
        # Modify mock ticket to be auto-resolved
        mock_ticket = mock_sav_workflow_engine.process_new_claim.return_value
        mock_ticket.auto_resolved = True
        mock_ticket.resolution_type = "auto_replacement"
        mock_ticket.resolution_description = "Pièce de remplacement envoyée"

        with patch('app.api.endpoints.sav.warranty_service', mock_warranty_service), \
             patch('app.api.endpoints.sav.sav_workflow_engine', mock_sav_workflow_engine), \
             patch('app.api.endpoints.sav.evidence_collector', mock_evidence_collector):

            response = client.post("/api/sav/create-claim", json={
                "customer_id": "customer@test.fr",
                "order_number": "CMD-1234-56789",
                "product_sku": "TEST-SKU",
                "product_name": "Test Product",
                "problem_description": "Petit problème mineur",
                "purchase_date": "2024-01-01T00:00:00Z",
                "delivery_date": "2024-01-15T00:00:00Z"
            })

            assert response.status_code == 200
            data = response.json()
            assert data["ticket"]["auto_resolved"] is True
            assert data["ticket"]["resolution_type"] == "auto_replacement"

    def test_create_claim_error_handling(self, client, mock_warranty_service):
        """Should handle errors during claim creation"""
        mock_warranty_service.create_warranty = AsyncMock(side_effect=Exception("DB error"))

        with patch('app.api.endpoints.sav.warranty_service', mock_warranty_service):
            response = client.post("/api/sav/create-claim", json={
                "customer_id": "customer@test.fr",
                "order_number": "CMD-1234-56789",
                "product_sku": "TEST-SKU",
                "product_name": "Test Product",
                "problem_description": "Test problem",
                "purchase_date": "2024-01-01T00:00:00Z",
                "delivery_date": "2024-01-15T00:00:00Z"
            })

            assert response.status_code == 500
            assert "Erreur" in response.json()["detail"]


# ============================================================================
# TESTS: POST /sav/add-evidence Endpoint
# ============================================================================

class TestAddEvidenceEndpoint:
    """Tests for add evidence endpoint"""

    def test_add_evidence_success(self, client, mock_sav_workflow_engine, mock_evidence_collector):
        """Should add evidence successfully"""
        with patch('app.api.endpoints.sav.sav_workflow_engine', mock_sav_workflow_engine), \
             patch('app.api.endpoints.sav.evidence_collector', mock_evidence_collector):

            response = client.post("/api/sav/add-evidence", json={
                "ticket_id": "SAV-TEST-001",
                "evidence_type": "photo",
                "evidence_url": "/uploads/photo.jpg",
                "file_size_bytes": 500000,
                "description": "Photo du mécanisme cassé",
                "metadata": {"width": 1920, "height": 1080}
            })

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["evidence_analysis"]["quality"] == "good"
            assert data["evidence_analysis"]["quality_score"] == 80
            assert data["completeness"]["is_complete"] is True
            assert data["ticket_status"] is not None

    def test_add_evidence_incomplete_set(self, client, mock_sav_workflow_engine, mock_evidence_collector):
        """Should indicate when evidence set is incomplete"""
        # Mock incomplete evidence
        mock_completeness = mock_evidence_collector.check_completeness.return_value
        mock_completeness.is_complete = False
        mock_completeness.completeness_score = 50
        mock_completeness.missing_items = ["1 vidéo requise"]
        mock_completeness.can_proceed = False

        with patch('app.api.endpoints.sav.sav_workflow_engine', mock_sav_workflow_engine), \
             patch('app.api.endpoints.sav.evidence_collector', mock_evidence_collector):

            response = client.post("/api/sav/add-evidence", json={
                "ticket_id": "SAV-TEST-001",
                "evidence_type": "photo",
                "evidence_url": "/uploads/photo.jpg",
                "file_size_bytes": 100000,
                "description": "Photo"
            })

            assert response.status_code == 200
            data = response.json()
            assert data["completeness"]["is_complete"] is False
            assert data["completeness"]["completeness_score"] == 50
            assert len(data["completeness"]["missing_items"]) > 0

    def test_add_evidence_ticket_not_found(self, client, mock_sav_workflow_engine, mock_evidence_collector):
        """Should return 404 when ticket not found"""
        mock_sav_workflow_engine.add_evidence = MagicMock(side_effect=ValueError("Ticket not found"))

        with patch('app.api.endpoints.sav.sav_workflow_engine', mock_sav_workflow_engine), \
             patch('app.api.endpoints.sav.evidence_collector', mock_evidence_collector):

            response = client.post("/api/sav/add-evidence", json={
                "ticket_id": "NONEXISTENT",
                "evidence_type": "photo",
                "evidence_url": "/uploads/photo.jpg",
                "file_size_bytes": 100000,
                "description": "Photo"
            })

            assert response.status_code == 404


# ============================================================================
# TESTS: GET /sav/ticket/{ticket_id} Endpoint
# ============================================================================

class TestGetTicketStatusEndpoint:
    """Tests for get ticket status endpoint"""

    def test_get_ticket_status_success(self, client, mock_sav_workflow_engine):
        """Should return ticket status"""
        with patch('app.api.endpoints.sav.sav_workflow_engine', mock_sav_workflow_engine):
            response = client.get("/api/sav/ticket/SAV-TEST-001")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "ticket" in data

    def test_get_ticket_status_not_found(self, client, mock_sav_workflow_engine):
        """Should return 404 when ticket not found"""
        mock_sav_workflow_engine.get_ticket_summary = MagicMock(return_value={"error": "Ticket not found"})

        with patch('app.api.endpoints.sav.sav_workflow_engine', mock_sav_workflow_engine):
            response = client.get("/api/sav/ticket/NONEXISTENT")

            assert response.status_code == 404


# ============================================================================
# TESTS: GET /sav/ticket/{ticket_id}/history Endpoint
# ============================================================================

class TestGetTicketHistoryEndpoint:
    """Tests for get ticket history endpoint"""

    def test_get_ticket_history_success(self, client, mock_sav_workflow_engine):
        """Should return ticket history"""
        # Add mock actions
        mock_action = MagicMock()
        mock_action.action_id = "ACT-001"
        mock_action.timestamp = datetime.now()
        mock_action.actor = "system"
        mock_action.action_type = "ticket_created"
        mock_action.description = "Ticket created"
        mock_action.metadata = {}

        mock_ticket = mock_sav_workflow_engine.active_tickets["SAV-TEST-001"]
        mock_ticket.actions = [mock_action]

        with patch('app.api.endpoints.sav.sav_workflow_engine', mock_sav_workflow_engine):
            response = client.get("/api/sav/ticket/SAV-TEST-001/history")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["ticket_id"] == "SAV-TEST-001"
            assert len(data["actions"]) == 1
            assert data["actions"][0]["action_type"] == "ticket_created"

    def test_get_ticket_history_not_found(self, client, mock_sav_workflow_engine):
        """Should return 404 when ticket not found"""
        with patch('app.api.endpoints.sav.sav_workflow_engine', mock_sav_workflow_engine):
            response = client.get("/api/sav/ticket/NONEXISTENT/history")

            assert response.status_code == 404


# ============================================================================
# TESTS: GET /sav/evidence-requirements/{problem_category} Endpoint
# ============================================================================

class TestGetEvidenceRequirementsEndpoint:
    """Tests for get evidence requirements endpoint"""

    def test_get_requirements_success(self, client, mock_evidence_collector):
        """Should return evidence requirements for category"""
        with patch('app.api.endpoints.sav.evidence_collector', mock_evidence_collector):
            response = client.get("/api/sav/evidence-requirements/structural?priority=P1")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "message" in data
            assert "requirements" in data
            assert data["requirements"]["min_photos"] == 3

    def test_get_requirements_default_priority(self, client, mock_evidence_collector):
        """Should use default priority P2 when not specified"""
        with patch('app.api.endpoints.sav.evidence_collector', mock_evidence_collector):
            response = client.get("/api/sav/evidence-requirements/mechanism")

            assert response.status_code == 200
            # Verify default priority was used
            mock_evidence_collector.generate_evidence_request_message.assert_called()


# ============================================================================
# TESTS: GET /sav/tickets Endpoint
# ============================================================================

class TestGetAllTicketsEndpoint:
    """Tests for get all tickets endpoint"""

    def test_get_all_tickets_success(self, client, mock_sav_workflow_engine):
        """Should return all tickets"""
        with patch('app.api.endpoints.sav.sav_workflow_engine', mock_sav_workflow_engine):
            response = client.get("/api/sav/tickets")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["total_tickets"] == 1
            assert len(data["tickets"]) == 1
            assert data["tickets"][0]["ticket_id"] == "SAV-TEST-001"

    def test_get_all_tickets_sorting(self, client, mock_sav_workflow_engine):
        """Should sort tickets by priority and date"""
        # Add multiple tickets with different priorities
        mock_ticket_p0 = MagicMock()
        mock_ticket_p0.ticket_id = "SAV-P0"
        mock_ticket_p0.priority = "P0"
        mock_ticket_p0.created_at = datetime.now()
        mock_ticket_p0.problem_category = "structural"
        mock_ticket_p0.priority_score = 95
        mock_ticket_p0.status = "open"
        mock_ticket_p0.auto_resolved = False
        mock_ticket_p0.customer_id = "test@test.fr"
        mock_ticket_p0.order_number = "CMD-001"
        mock_ticket_p0.product_name = "Product 1"
        mock_ticket_p0.problem_description = "P0 problem"
        mock_ticket_p0.evidences = []
        mock_ticket_p0.warranty_check_result = MagicMock(is_covered=True)
        mock_ticket_p0.sla_response_deadline = None
        mock_ticket_p0.tone_analysis = None
        mock_ticket_p0.client_summary = None

        mock_sav_workflow_engine.active_tickets = {
            "SAV-P0": mock_ticket_p0,
            "SAV-TEST-001": mock_sav_workflow_engine.active_tickets["SAV-TEST-001"]
        }

        with patch('app.api.endpoints.sav.sav_workflow_engine', mock_sav_workflow_engine):
            response = client.get("/api/sav/tickets")

            assert response.status_code == 200
            data = response.json()
            assert len(data["tickets"]) == 2
            # P0 should come first
            assert data["tickets"][0]["priority"] == "P0"


# ============================================================================
# TESTS: GET /sav/ticket/{ticket_id}/dossier Endpoint
# ============================================================================

class TestGenerateClientDossierEndpoint:
    """Tests for generate client dossier endpoint"""

    def test_generate_dossier_success(self, client, mock_sav_workflow_engine):
        """Should generate complete client dossier"""
        with patch('app.api.endpoints.sav.sav_workflow_engine', mock_sav_workflow_engine):
            response = client.get("/api/sav/ticket/SAV-TEST-001/dossier")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "dossier" in data

            dossier = data["dossier"]
            assert "ticket" in dossier
            assert "client" in dossier
            assert "produit" in dossier
            assert "probleme" in dossier
            assert "analyse_ton" in dossier
            assert "garantie" in dossier
            assert "preuves" in dossier
            assert "sla" in dossier
            assert "resolution" in dossier
            assert "recapitulatif" in dossier
            assert "historique" in dossier

    def test_generate_dossier_not_found(self, client, mock_sav_workflow_engine):
        """Should return 404 when ticket not found"""
        with patch('app.api.endpoints.sav.sav_workflow_engine', mock_sav_workflow_engine):
            response = client.get("/api/sav/ticket/NONEXISTENT/dossier")

            assert response.status_code == 404


# ============================================================================
# TESTS: Utility Function _generate_next_steps
# ============================================================================

class TestGenerateNextStepsFunction:
    """Tests for _generate_next_steps utility function"""

    def test_next_steps_auto_resolved_replacement(self):
        """Should generate next steps for auto-resolved replacement"""
        from app.api.endpoints.sav import _generate_next_steps

        ticket = MagicMock()
        ticket.auto_resolved = True
        ticket.resolution_type = "auto_replacement"
        ticket.resolution_description = "Pièce envoyée"
        ticket.ticket_id = "SAV-001"
        ticket.sla_intervention_deadline = datetime(2025, 1, 15, 12, 0)

        steps = _generate_next_steps(ticket)

        assert any("traitée automatiquement" in step for step in steps)
        assert any("pièce de remplacement" in step.lower() for step in steps)
        assert any("SAV-001" in step for step in steps)

    def test_next_steps_escalated(self):
        """Should generate next steps for escalated ticket"""
        from app.api.endpoints.sav import _generate_next_steps

        ticket = MagicMock()
        ticket.auto_resolved = False
        ticket.status = "escalated_to_human"
        ticket.ticket_id = "SAV-002"
        ticket.sla_response_deadline = datetime(2025, 1, 10, 14, 0)

        steps = _generate_next_steps(ticket)

        assert any("analyse approfondie" in step for step in steps)
        assert any("conseiller SAV" in step for step in steps)

    def test_next_steps_evidence_collection(self):
        """Should generate next steps for evidence collection"""
        from app.api.endpoints.sav import _generate_next_steps

        ticket = MagicMock()
        ticket.auto_resolved = False
        ticket.status = "evidence_collection"
        ticket.ticket_id = "SAV-003"

        steps = _generate_next_steps(ticket)

        assert any("preuves requises" in step for step in steps)
        assert any("photos/vidéos" in step.lower() for step in steps)
