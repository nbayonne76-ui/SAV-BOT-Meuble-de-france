# backend/tests/services/test_sav_workflow_engine.py
"""
Tests pour SAVWorkflowEngine - Moteur de workflow SAV
Coverage target: 80%+
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, AsyncMock

from app.services.sav_workflow_engine import (
    SAVWorkflowEngine,
    SAVTicket,
    TicketStatus,
    ResolutionType,
    Evidence
)
from app.models.warranty import Warranty, WarrantyCheck


# ==========================================
# Fixtures
# ==========================================

@pytest.fixture
def engine():
    """Create SAVWorkflowEngine instance"""
    return SAVWorkflowEngine()


@pytest.fixture
def mock_warranty():
    """Create mock warranty object"""
    warranty = MagicMock(spec=Warranty)
    warranty.warranty_id = "WARRANTY-12345"
    warranty.product_sku = "OSLO-3P-GREY"
    warranty.customer_id = "client@example.fr"
    warranty.purchase_date = datetime.now() - timedelta(days=30)
    warranty.expiration_date = datetime.now() + timedelta(days=700)
    warranty.is_active = True
    warranty.claims_history = []
    return warranty


@pytest.fixture
def mock_warranty_check_covered():
    """Mock warranty check result - covered"""
    check = MagicMock(spec=WarrantyCheck)
    check.is_covered = True
    check.component = "mécanisme"
    check.reason = "Défaut de fabrication sous garantie"
    check.days_remaining = 700
    check.requires_evidence = True
    return check


@pytest.fixture
def mock_warranty_check_not_covered():
    """Mock warranty check result - not covered"""
    check = MagicMock(spec=WarrantyCheck)
    check.is_covered = False
    check.component = None
    check.reason = "Garantie expirée"
    check.days_remaining = -30
    check.requires_evidence = False
    return check


@pytest.fixture
def mock_problem_detection():
    """Mock problem detector result"""
    result = MagicMock()
    result.primary_category = "mechanism"
    result.severity = "P1"
    result.confidence = 0.85
    result.matched_keywords = ["bloqué", "mécanisme", "ne fonctionne plus"]
    return result


@pytest.fixture
def mock_priority_result():
    """Mock priority scorer result"""
    result = MagicMock()
    result.priority = "P1"
    result.total_score = 65
    result.factors = ["mechanism", "under_warranty", "recent_purchase"]
    result.explanation = "Priorité HAUTE: Mécanisme défectueux sous garantie, achat récent"
    return result


@pytest.fixture
def mock_tone_analysis():
    """Mock tone analyzer result"""
    analysis = MagicMock()
    analysis.tone = "frustrated"
    analysis.urgency = "high"
    analysis.emotion_score = 0.7
    analysis.urgency_score = 0.8
    analysis.requires_human_empathy = True
    analysis.recommended_response_time = "< 24h"
    analysis.explanation = "Client frustré, urgence élevée détectée"
    return analysis


@pytest.fixture
def mock_client_summary():
    """Mock client summary generator result"""
    summary = MagicMock()
    summary.summary_id = "SUMMARY-12345"
    summary.validation_required = True
    summary.validation_link = "https://example.com/validate/12345"
    return summary


# ==========================================
# Test Class: Ticket Creation
# ==========================================

class TestCreateTicket:
    """Tests pour la création de tickets"""

    @pytest.mark.asyncio
    async def test_create_ticket_success(self, engine):
        """Should create ticket with correct format"""
        ticket = await engine._create_ticket(
            customer_id="client@example.fr",
            order_number="CMD-2025-001",
            product_sku="OSLO-3P-GREY",
            product_name="Canapé OSLO 3 places gris",
            problem_description="Le mécanisme est bloqué",
            warranty_id="WARRANTY-12345"
        )

        assert ticket is not None
        assert ticket.ticket_id.startswith("SAV-")
        assert ticket.customer_id == "client@example.fr"
        assert ticket.order_number == "CMD-2025-001"
        assert ticket.product_sku == "OSLO-3P-GREY"
        assert ticket.status == TicketStatus.NEW
        assert len(ticket.actions) == 1
        assert ticket.actions[0].action_type == "ticket_created"

    @pytest.mark.asyncio
    async def test_create_ticket_id_format(self, engine):
        """Should generate ticket ID with correct format SAV-YYYYMMDD-XXX"""
        ticket = await engine._create_ticket(
            customer_id="test@test.fr",
            order_number="CMD-2025-12345",
            product_sku="TEST-SKU",
            product_name="Test Product",
            problem_description="Test problem",
            warranty_id="WARRANTY-123"
        )

        # Format: SAV-YYYYMMDD-12345
        assert ticket.ticket_id.startswith("SAV-")
        parts = ticket.ticket_id.split("-")
        assert len(parts) == 3
        assert len(parts[1]) == 8  # YYYYMMDD
        assert parts[2] == "12345"  # Last part of order number


# ==========================================
# Test Class: Problem Analysis
# ==========================================

class TestAnalyzeProblem:
    """Tests pour l'analyse de problème"""

    @pytest.mark.asyncio
    async def test_analyze_problem_updates_ticket(self, engine, mock_problem_detection):
        """Should analyze problem and update ticket"""
        # Create ticket
        ticket = SAVTicket(
            ticket_id="SAV-TEST-001",
            customer_id="test@test.fr",
            order_number="CMD-001",
            product_sku="OSLO-3P",
            product_name="Canapé OSLO",
            problem_description="Le mécanisme ne fonctionne plus"
        )

        # Mock problem detector - patch where it's imported
        with patch('app.services.sav_workflow_engine.problem_detector') as mock_pd:
            mock_pd.detect_problem_type.return_value = mock_problem_detection

            result = await engine._analyze_problem(ticket, "Le mécanisme ne fonctionne plus")

            assert result.status == TicketStatus.PROBLEM_ANALYSIS
            assert result.problem_category == "mechanism"
            assert result.problem_severity == "P1"
            assert result.problem_confidence == 0.85
            assert len(result.actions) == 1
            assert result.actions[0].action_type == "problem_analyzed"


# ==========================================
# Test Class: Warranty Check
# ==========================================

class TestCheckWarranty:
    """Tests pour la vérification de garantie"""

    @pytest.mark.asyncio
    async def test_check_warranty_covered(self, engine, mock_warranty, mock_warranty_check_covered):
        """Should check warranty and mark as covered"""
        ticket = SAVTicket(
            ticket_id="SAV-TEST-001",
            customer_id="test@test.fr",
            order_number="CMD-001",
            product_sku="OSLO-3P",
            product_name="Canapé OSLO",
            problem_description="Problème mécanisme",
            problem_category="mechanism"
        )

        with patch('app.services.sav_workflow_engine.warranty_service') as mock_ws:
            mock_ws.check_warranty_coverage.return_value = mock_warranty_check_covered

            result = await engine._check_warranty(ticket, mock_warranty, "Problème mécanisme")

            assert result.status == TicketStatus.WARRANTY_CHECK
            assert result.warranty_check_result.is_covered is True
            assert result.warranty_check_result.component == "mécanisme"
            assert len(result.actions) == 1
            assert result.actions[0].action_type == "warranty_checked"

    @pytest.mark.asyncio
    async def test_check_warranty_not_covered(self, engine, mock_warranty, mock_warranty_check_not_covered):
        """Should check warranty and mark as not covered"""
        ticket = SAVTicket(
            ticket_id="SAV-TEST-001",
            customer_id="test@test.fr",
            order_number="CMD-001",
            product_sku="OSLO-3P",
            product_name="Canapé OSLO",
            problem_description="Usure normale"
        )

        with patch('app.services.sav_workflow_engine.warranty_service') as mock_ws:
            mock_ws.check_warranty_coverage.return_value = mock_warranty_check_not_covered

            result = await engine._check_warranty(ticket, mock_warranty, "Usure normale")

            assert result.warranty_check_result.is_covered is False
            assert result.warranty_check_result.reason == "Garantie expirée"


# ==========================================
# Test Class: Priority Calculation
# ==========================================

class TestCalculatePriority:
    """Tests pour le calcul de priorité"""

    @pytest.mark.asyncio
    async def test_calculate_priority_high(self, engine, mock_warranty, mock_warranty_check_covered, mock_priority_result):
        """Should calculate high priority"""
        ticket = SAVTicket(
            ticket_id="SAV-TEST-001",
            customer_id="test@test.fr",
            order_number="CMD-001",
            product_sku="OSLO-3P",
            product_name="Canapé OSLO",
            problem_description="Mécanisme cassé",
            problem_category="mechanism",
            problem_severity="P1",
            warranty_check_result=mock_warranty_check_covered
        )

        with patch('app.services.sav_workflow_engine.priority_scorer') as mock_ps:
            mock_ps.calculate_priority.return_value = mock_priority_result

            result = await engine._calculate_priority(
                ticket=ticket,
                warranty=mock_warranty,
                customer_tier="gold",
                product_value=1500.0
            )

            assert result.status == TicketStatus.PRIORITY_ASSESSMENT
            assert result.priority == "P1"
            assert result.priority_score == 65
            assert len(result.priority_factors) > 0
            assert len(result.actions) == 1
            assert result.actions[0].action_type == "priority_calculated"


# ==========================================
# Test Class: SLA Deadlines
# ==========================================

class TestSetSLADeadlines:
    """Tests pour la définition des SLA"""

    def test_set_sla_p0_critical(self, engine):
        """Should set 4h response SLA for P0"""
        ticket = SAVTicket(
            ticket_id="SAV-TEST-001",
            customer_id="test@test.fr",
            order_number="CMD-001",
            product_sku="OSLO-3P",
            product_name="Canapé OSLO",
            problem_description="Danger",
            priority="P0",
            created_at=datetime.now()
        )

        result = engine._set_sla_deadlines(ticket)

        assert result.sla_response_deadline is not None
        assert result.sla_intervention_deadline is not None
        # P0: 4h response, 24h intervention
        time_diff = (result.sla_response_deadline - result.created_at).total_seconds()
        assert time_diff == 4 * 3600  # 4 hours in seconds

    def test_set_sla_p3_low(self, engine):
        """Should set 7 days response SLA for P3"""
        ticket = SAVTicket(
            ticket_id="SAV-TEST-001",
            customer_id="test@test.fr",
            order_number="CMD-001",
            product_sku="OSLO-3P",
            product_name="Canapé OSLO",
            problem_description="Question",
            priority="P3",
            created_at=datetime.now()
        )

        result = engine._set_sla_deadlines(ticket)

        # P3: 168h (7 days) response
        time_diff = (result.sla_response_deadline - result.created_at).total_seconds()
        assert time_diff == 168 * 3600  # 7 days in seconds


# ==========================================
# Test Class: Evidence Requirements
# ==========================================

class TestEvidenceRequirements:
    """Tests pour la détermination des preuves requises"""

    def test_structural_problem_requires_video(self, engine):
        """Should require video for structural problems"""
        ticket = SAVTicket(
            ticket_id="SAV-TEST-001",
            customer_id="test@test.fr",
            order_number="CMD-001",
            product_sku="OSLO-3P",
            product_name="Canapé OSLO",
            problem_description="Structure cassée",
            problem_category="structural"
        )

        result = engine._determine_evidence_requirements(ticket)

        assert result.status == TicketStatus.EVIDENCE_COLLECTION
        assert len(result.actions) == 1
        action = result.actions[0]
        assert action.action_type == "evidence_requirements_set"
        assert action.metadata["require_video"] is True
        assert action.metadata["min_photos"] == 3

    def test_fabric_problem_no_video(self, engine):
        """Should not require video for fabric problems"""
        ticket = SAVTicket(
            ticket_id="SAV-TEST-001",
            customer_id="test@test.fr",
            order_number="CMD-001",
            product_sku="OSLO-3P",
            product_name="Canapé OSLO",
            problem_description="Tissu déchiré",
            problem_category="fabric"
        )

        result = engine._determine_evidence_requirements(ticket)

        action = result.actions[0]
        assert action.metadata["require_video"] is False
        assert action.metadata["min_photos"] == 2


# ==========================================
# Test Class: Auto-Resolve Conditions
# ==========================================

class TestCanAutoResolve:
    """Tests pour les conditions d'auto-résolution"""

    def test_can_auto_resolve_p2_fabric(self, engine, mock_warranty_check_covered):
        """Should allow auto-resolve for P2 fabric issue"""
        ticket = SAVTicket(
            ticket_id="SAV-TEST-001",
            customer_id="test@test.fr",
            order_number="CMD-001",
            product_sku="OSLO-3P",
            product_name="Canapé OSLO",
            problem_description="Petite tache",
            priority="P2",
            problem_category="fabric",
            problem_confidence=0.85,
            priority_score=45,
            warranty_check_result=mock_warranty_check_covered
        )

        result = engine._can_auto_resolve(ticket)

        assert result is True

    def test_cannot_auto_resolve_p0_critical(self, engine, mock_warranty_check_covered):
        """Should not allow auto-resolve for P0 critical"""
        ticket = SAVTicket(
            ticket_id="SAV-TEST-001",
            customer_id="test@test.fr",
            order_number="CMD-001",
            product_sku="OSLO-3P",
            product_name="Canapé OSLO",
            problem_description="Danger",
            priority="P0",
            problem_category="structural",
            problem_confidence=0.95,
            priority_score=95,
            warranty_check_result=mock_warranty_check_covered
        )

        result = engine._can_auto_resolve(ticket)

        assert result is False

    def test_cannot_auto_resolve_low_confidence(self, engine, mock_warranty_check_covered):
        """Should not allow auto-resolve for low confidence"""
        ticket = SAVTicket(
            ticket_id="SAV-TEST-001",
            customer_id="test@test.fr",
            order_number="CMD-001",
            product_sku="OSLO-3P",
            product_name="Canapé OSLO",
            problem_description="Problème",
            priority="P3",
            problem_category="fabric",
            problem_confidence=0.4,  # Too low
            priority_score=20,
            warranty_check_result=mock_warranty_check_covered
        )

        result = engine._can_auto_resolve(ticket)

        assert result is False


# ==========================================
# Test Class: Escalation Conditions
# ==========================================

class TestMustEscalate:
    """Tests pour les conditions d'escalade"""

    def test_must_escalate_p0(self, engine, mock_warranty_check_covered):
        """Should escalate P0 tickets"""
        ticket = SAVTicket(
            ticket_id="SAV-TEST-001",
            customer_id="test@test.fr",
            order_number="CMD-001",
            product_sku="OSLO-3P",
            product_name="Canapé OSLO",
            problem_description="Danger",
            priority="P0",
            problem_category="structural",
            problem_confidence=0.95,
            priority_score=95,
            warranty_check_result=mock_warranty_check_covered
        )

        result = engine._must_escalate_to_human(ticket)

        assert result is True

    def test_must_escalate_structural(self, engine, mock_warranty_check_covered):
        """Should escalate structural problems"""
        ticket = SAVTicket(
            ticket_id="SAV-TEST-001",
            customer_id="test@test.fr",
            order_number="CMD-001",
            product_sku="OSLO-3P",
            product_name="Canapé OSLO",
            problem_description="Structure cassée",
            priority="P1",
            problem_category="structural",
            problem_confidence=0.85,
            priority_score=70,
            warranty_check_result=mock_warranty_check_covered
        )

        result = engine._must_escalate_to_human(ticket)

        assert result is True

    def test_no_escalate_p3_covered(self, engine, mock_warranty_check_covered):
        """Should not escalate P3 covered tickets"""
        ticket = SAVTicket(
            ticket_id="SAV-TEST-001",
            customer_id="test@test.fr",
            order_number="CMD-001",
            product_sku="OSLO-3P",
            product_name="Canapé OSLO",
            problem_description="Petite tache",
            priority="P3",
            problem_category="fabric",
            problem_confidence=0.85,
            priority_score=25,
            warranty_check_result=mock_warranty_check_covered
        )

        result = engine._must_escalate_to_human(ticket)

        assert result is False


# ==========================================
# Test Class: Auto-Resolve
# ==========================================

class TestAutoResolve:
    """Tests pour l'auto-résolution"""

    @pytest.mark.asyncio
    async def test_auto_resolve_fabric_replacement(self, engine, mock_warranty_check_covered):
        """Should auto-resolve fabric issue with replacement"""
        ticket = SAVTicket(
            ticket_id="SAV-TEST-001",
            customer_id="test@test.fr",
            order_number="CMD-001",
            product_sku="OSLO-3P",
            product_name="Canapé OSLO",
            problem_description="Tissu déchiré",
            problem_category="fabric",
            warranty_check_result=mock_warranty_check_covered,
            created_at=datetime.now()
        )

        # Update mock to have component attribute
        mock_warranty_check_covered.component = "tissu"

        result = await engine._auto_resolve(ticket, MagicMock())

        assert result.status == TicketStatus.AUTO_RESOLVED
        assert result.auto_resolved is True
        assert result.resolution_type == ResolutionType.AUTO_REPLACEMENT
        assert result.time_to_resolution is not None
        assert len(result.actions) == 1

    @pytest.mark.asyncio
    async def test_auto_resolve_smell_education(self, engine, mock_warranty_check_covered):
        """Should auto-resolve smell issue with customer education"""
        ticket = SAVTicket(
            ticket_id="SAV-TEST-001",
            customer_id="test@test.fr",
            order_number="CMD-001",
            product_sku="OSLO-3P",
            product_name="Canapé OSLO",
            problem_description="Mauvaise odeur",
            problem_category="smell",
            warranty_check_result=mock_warranty_check_covered,
            created_at=datetime.now()
        )

        result = await engine._auto_resolve(ticket, MagicMock())

        assert result.resolution_type == ResolutionType.CUSTOMER_EDUCATION
        assert "Odeur normale" in result.resolution_description


# ==========================================
# Test Class: Escalate to Human
# ==========================================

class TestEscalateToHuman:
    """Tests pour l'escalade humaine"""

    @pytest.mark.asyncio
    async def test_escalate_to_human_p0(self, engine):
        """Should escalate P0 to human"""
        ticket = SAVTicket(
            ticket_id="SAV-TEST-001",
            customer_id="test@test.fr",
            order_number="CMD-001",
            product_sku="OSLO-3P",
            product_name="Canapé OSLO",
            problem_description="Danger",
            priority="P0",
            priority_score=95
        )

        result = await engine._escalate_to_human(ticket)

        assert result.status == TicketStatus.ESCALATED_TO_HUMAN
        assert result.auto_resolved is False
        assert len(result.actions) == 1
        assert result.actions[0].action_type == "escalated_to_human"


# ==========================================
# Test Class: Assign to Technician
# ==========================================

class TestAssignToTechnician:
    """Tests pour l'assignation technicien"""

    @pytest.mark.asyncio
    async def test_assign_to_technician(self, engine):
        """Should assign ticket to technician"""
        ticket = SAVTicket(
            ticket_id="SAV-TEST-001",
            customer_id="test@test.fr",
            order_number="CMD-001",
            product_sku="OSLO-3P",
            product_name="Canapé OSLO",
            problem_description="Réparation nécessaire",
            priority="P1",
            sla_intervention_deadline=datetime.now() + timedelta(hours=48)
        )

        result = await engine._assign_to_technician(ticket)

        assert result.status == TicketStatus.AWAITING_TECHNICIAN
        assert result.resolution_type == ResolutionType.TECHNICIAN_DISPATCH
        assert len(result.actions) == 1
        assert result.actions[0].action_type == "assigned_to_technician"


# ==========================================
# Test Class: Add Evidence
# ==========================================

class TestAddEvidence:
    """Tests pour l'ajout de preuves"""

    def test_add_photo_evidence(self, engine):
        """Should add photo evidence to ticket"""
        # Create ticket in engine
        ticket = SAVTicket(
            ticket_id="SAV-TEST-001",
            customer_id="test@test.fr",
            order_number="CMD-001",
            product_sku="OSLO-3P",
            product_name="Canapé OSLO",
            problem_description="Problème",
            problem_category="fabric"
        )
        engine.active_tickets["SAV-TEST-001"] = ticket

        result = engine.add_evidence(
            ticket_id="SAV-TEST-001",
            evidence_type="photo",
            evidence_url="https://example.com/photo1.jpg",
            description="Photo du problème"
        )

        assert len(result.evidences) == 1
        assert result.evidences[0].type == "photo"
        assert result.evidences[0].url == "https://example.com/photo1.jpg"
        assert result.evidences[0].evidence_id.startswith("SAV-TEST-001-EVD-")

    def test_add_evidence_marks_complete(self, engine):
        """Should mark evidence complete when requirements met"""
        ticket = SAVTicket(
            ticket_id="SAV-TEST-001",
            customer_id="test@test.fr",
            order_number="CMD-001",
            product_sku="OSLO-3P",
            product_name="Canapé OSLO",
            problem_description="Problème",
            problem_category="fabric"  # Requires 2 photos, no video
        )
        engine.active_tickets["SAV-TEST-001"] = ticket

        # Add first photo
        engine.add_evidence("SAV-TEST-001", "photo", "url1.jpg", "Photo 1")
        assert ticket.evidence_complete is False

        # Add second photo - should mark complete
        result = engine.add_evidence("SAV-TEST-001", "photo", "url2.jpg", "Photo 2")
        assert result.evidence_complete is True

    def test_add_evidence_invalid_ticket(self, engine):
        """Should raise error for invalid ticket ID"""
        with pytest.raises(ValueError, match="non trouvé"):
            engine.add_evidence(
                ticket_id="INVALID-ID",
                evidence_type="photo",
                evidence_url="url.jpg",
                description="Photo"
            )


# ==========================================
# Test Class: Tone Analysis
# ==========================================

class TestAnalyzeTone:
    """Tests pour l'analyse de ton"""

    def test_analyze_tone_frustrated(self, engine, mock_tone_analysis):
        """Should analyze frustrated tone"""
        ticket = SAVTicket(
            ticket_id="SAV-TEST-001",
            customer_id="test@test.fr",
            order_number="CMD-001",
            product_sku="OSLO-3P",
            product_name="Canapé OSLO",
            problem_description="C'est inacceptable!",
            created_at=datetime.now()
        )

        with patch('app.services.sav_workflow_engine.tone_analyzer') as mock_ta:
            mock_ta.analyze_tone.return_value = mock_tone_analysis

            result = engine._analyze_tone(ticket, "C'est inacceptable!")

            assert result.tone_analysis is not None
            assert result.tone_analysis.tone == "frustrated"
            assert result.tone_analysis.urgency == "high"
            assert len(result.actions) == 1

    def test_analyze_tone_critical_urgency_sets_sla(self, engine):
        """Should set SLA for critical urgency"""
        ticket = SAVTicket(
            ticket_id="SAV-TEST-001",
            customer_id="test@test.fr",
            order_number="CMD-001",
            product_sku="OSLO-3P",
            product_name="Canapé OSLO",
            problem_description="URGENT",
            created_at=datetime.now()
        )

        critical_tone = MagicMock()
        critical_tone.urgency = "critical"
        critical_tone.tone = "angry"
        critical_tone.emotion_score = 0.9
        critical_tone.urgency_score = 0.95
        critical_tone.requires_human_empathy = True
        critical_tone.recommended_response_time = "< 4h"
        critical_tone.explanation = "Urgence critique"

        with patch('app.services.sav_workflow_engine.tone_analyzer') as mock_ta:
            mock_ta.analyze_tone.return_value = critical_tone

            result = engine._analyze_tone(ticket, "URGENT")

            assert result.sla_response_deadline is not None
            # Should be 4h for critical
            time_diff = (result.sla_response_deadline - result.created_at).total_seconds()
            assert time_diff == 4 * 3600


# ==========================================
# Test Class: Generate Client Summary
# ==========================================

class TestGenerateClientSummary:
    """Tests pour la génération du récapitulatif client"""

    def test_generate_client_summary(self, engine, mock_client_summary, mock_warranty_check_covered):
        """Should generate client summary"""
        ticket = SAVTicket(
            ticket_id="SAV-TEST-001",
            customer_id="client@example.fr",
            order_number="CMD-001",
            product_sku="OSLO-3P",
            product_name="Canapé OSLO",
            problem_description="Problème mécanisme",
            status=TicketStatus.DECISION_PENDING,
            priority="P1",
            problem_category="mechanism",
            warranty_check_result=mock_warranty_check_covered,
            auto_resolved=False,
            resolution_type=None,
            resolution_description=None
        )

        with patch('app.services.sav_workflow_engine.client_summary_generator') as mock_csg:
            mock_csg.generate_summary.return_value = mock_client_summary

            result = engine._generate_client_summary(ticket)

            assert result.client_summary is not None
            assert result.client_summary.summary_id == "SUMMARY-12345"
            assert len(result.actions) == 1
            assert result.actions[0].action_type == "summary_generated"


# ==========================================
# Test Class: Get Ticket Summary
# ==========================================

class TestGetTicketSummary:
    """Tests pour la récupération du récapitulatif ticket"""

    def test_get_ticket_summary_success(self, engine, mock_warranty_check_covered):
        """Should return ticket summary"""
        ticket = SAVTicket(
            ticket_id="SAV-TEST-001",
            customer_id="test@test.fr",
            order_number="CMD-001",
            product_sku="OSLO-3P",
            product_name="Canapé OSLO",
            problem_description="Problème",
            status=TicketStatus.AUTO_RESOLVED,
            priority="P2",
            problem_category="fabric",
            warranty_check_result=mock_warranty_check_covered,
            auto_resolved=True,
            resolution_type=ResolutionType.AUTO_REPLACEMENT,
            resolution_description="Remplacement automatique",
            sla_response_deadline=datetime.now() + timedelta(hours=24),
            evidence_complete=True,
            created_at=datetime.now(),
            time_to_resolution=timedelta(hours=2)
        )
        ticket.actions.append(MagicMock())
        engine.active_tickets["SAV-TEST-001"] = ticket

        summary = engine.get_ticket_summary("SAV-TEST-001")

        assert summary["ticket_id"] == "SAV-TEST-001"
        assert summary["status"] == TicketStatus.AUTO_RESOLVED
        assert summary["priority"] == "P2"
        assert summary["warranty_covered"] is True
        assert summary["auto_resolved"] is True
        assert summary["evidence_complete"] is True
        assert summary["actions_count"] == 1

    def test_get_ticket_summary_not_found(self, engine):
        """Should return error for non-existent ticket"""
        summary = engine.get_ticket_summary("INVALID-ID")

        assert "error" in summary
        assert "non trouvé" in summary["error"]


# ==========================================
# Test Class: Priority Helpers
# ==========================================

class TestPriorityHelpers:
    """Tests pour les helpers de priorité"""

    def test_get_priority_label(self, engine):
        """Should return correct priority labels"""
        assert engine._get_priority_label("P0") == "CRITIQUE"
        assert engine._get_priority_label("P1") == "HAUTE"
        assert engine._get_priority_label("P2") == "MOYENNE"
        assert engine._get_priority_label("P3") == "BASSE"
        assert engine._get_priority_label("UNKNOWN") == "INCONNUE"

    def test_get_priority_emoji(self, engine):
        """Should return correct priority emojis"""
        assert engine._get_priority_emoji("P0") == "🔴"
        assert engine._get_priority_emoji("P1") == "🟠"
        assert engine._get_priority_emoji("P2") == "🟡"
        assert engine._get_priority_emoji("P3") == "🟢"
        assert engine._get_priority_emoji("UNKNOWN") == "⚪"


# ==========================================
# Test Class: Integration - Full Workflow
# ==========================================

class TestProcessNewClaimIntegration:
    """Tests d'intégration pour le workflow complet"""

    @pytest.mark.asyncio
    async def test_process_new_claim_full_workflow(
        self,
        engine,
        mock_warranty,
        mock_problem_detection,
        mock_warranty_check_covered,
        mock_priority_result,
        mock_tone_analysis,
        mock_client_summary
    ):
        """Should process complete claim workflow"""
        with patch('app.services.sav_workflow_engine.problem_detector') as mock_pd, \
             patch('app.services.sav_workflow_engine.warranty_service') as mock_ws, \
             patch('app.services.sav_workflow_engine.priority_scorer') as mock_ps, \
             patch('app.services.sav_workflow_engine.tone_analyzer') as mock_ta, \
             patch('app.services.sav_workflow_engine.client_summary_generator') as mock_csg:

            # Setup mocks
            mock_pd.detect_problem_type.return_value = mock_problem_detection
            mock_ws.check_warranty_coverage.return_value = mock_warranty_check_covered
            mock_ps.calculate_priority.return_value = mock_priority_result
            mock_ta.analyze_tone.return_value = mock_tone_analysis
            mock_csg.generate_summary.return_value = mock_client_summary

            # Process claim
            ticket = await engine.process_new_claim(
                customer_id="client@example.fr",
                order_number="CMD-2025-001",
                product_sku="OSLO-3P-GREY",
                product_name="Canapé OSLO 3 places gris",
                problem_description="Le mécanisme est bloqué",
                warranty=mock_warranty,
                customer_tier="gold",
                product_value=1500.0
            )

            # Verify ticket created
            assert ticket is not None
            assert ticket.ticket_id.startswith("SAV-")
            assert ticket.customer_id == "client@example.fr"

            # Verify problem analyzed
            assert ticket.problem_category == "mechanism"
            assert ticket.problem_severity == "P1"
            assert ticket.problem_confidence == 0.85

            # Verify warranty checked
            assert ticket.warranty_check_result.is_covered is True

            # Verify priority calculated
            assert ticket.priority == "P1"
            assert ticket.priority_score == 65

            # Verify SLA set
            assert ticket.sla_response_deadline is not None
            assert ticket.sla_intervention_deadline is not None

            # Verify tone analyzed
            assert ticket.tone_analysis is not None
            assert ticket.tone_analysis.tone == "frustrated"

            # Verify summary generated
            assert ticket.client_summary is not None

            # Verify ticket stored
            assert ticket.ticket_id in engine.active_tickets

    @pytest.mark.asyncio
    async def test_process_new_claim_auto_resolves_p3(
        self,
        engine,
        mock_warranty,
        mock_warranty_check_covered
    ):
        """Should auto-resolve P3 fabric issue"""
        # Mock P3 low priority fabric issue
        p3_problem = MagicMock()
        p3_problem.primary_category = "fabric"
        p3_problem.severity = "P3"
        p3_problem.confidence = 0.85
        p3_problem.matched_keywords = ["tache"]

        p3_priority = MagicMock()
        p3_priority.priority = "P3"
        p3_priority.total_score = 25
        p3_priority.factors = ["fabric", "under_warranty"]
        p3_priority.explanation = "Priorité basse"

        mock_tone = MagicMock()
        mock_tone.urgency = "low"
        mock_tone.tone = "neutral"
        mock_tone.emotion_score = 0.2
        mock_tone.urgency_score = 0.1
        mock_tone.requires_human_empathy = False
        mock_tone.recommended_response_time = "< 7 days"
        mock_tone.explanation = "Ton neutre"

        mock_summary = MagicMock()
        mock_summary.summary_id = "SUMMARY-123"
        mock_summary.validation_required = False

        with patch('app.services.sav_workflow_engine.problem_detector') as mock_pd, \
             patch('app.services.sav_workflow_engine.warranty_service') as mock_ws, \
             patch('app.services.sav_workflow_engine.priority_scorer') as mock_ps, \
             patch('app.services.sav_workflow_engine.tone_analyzer') as mock_ta, \
             patch('app.services.sav_workflow_engine.client_summary_generator') as mock_csg:

            mock_pd.detect_problem_type.return_value = p3_problem
            mock_ws.check_warranty_coverage.return_value = mock_warranty_check_covered
            mock_ps.calculate_priority.return_value = p3_priority
            mock_ta.analyze_tone.return_value = mock_tone
            mock_csg.generate_summary.return_value = mock_summary

            # Mock warranty_check_result to have component
            mock_warranty_check_covered.component = "tissu"

            ticket = await engine.process_new_claim(
                customer_id="client@example.fr",
                order_number="CMD-2025-001",
                product_sku="OSLO-3P-GREY",
                product_name="Canapé OSLO 3 places gris",
                problem_description="Petite tache sur le tissu",
                warranty=mock_warranty,
                customer_tier="standard",
                product_value=800.0
            )

            # Should be auto-resolved
            assert ticket.auto_resolved is True
            assert ticket.status == TicketStatus.AUTO_RESOLVED
            assert ticket.resolution_type == ResolutionType.AUTO_REPLACEMENT

    @pytest.mark.asyncio
    async def test_process_new_claim_escalates_p0(
        self,
        engine,
        mock_warranty,
        mock_warranty_check_covered
    ):
        """Should escalate P0 structural issue to human"""
        # Mock P0 critical structural issue
        p0_problem = MagicMock()
        p0_problem.primary_category = "structural"
        p0_problem.severity = "P0"
        p0_problem.confidence = 0.95
        p0_problem.matched_keywords = ["cassé", "danger"]

        p0_priority = MagicMock()
        p0_priority.priority = "P0"
        p0_priority.total_score = 95
        p0_priority.factors = ["structural", "critical"]
        p0_priority.explanation = "CRITIQUE: Danger structurel"

        critical_tone = MagicMock()
        critical_tone.urgency = "critical"
        critical_tone.tone = "angry"
        critical_tone.emotion_score = 0.9
        critical_tone.urgency_score = 0.95
        critical_tone.requires_human_empathy = True
        critical_tone.recommended_response_time = "< 4h"
        critical_tone.explanation = "Urgence critique"

        mock_summary = MagicMock()
        mock_summary.summary_id = "SUMMARY-123"
        mock_summary.validation_required = True

        with patch('app.services.sav_workflow_engine.problem_detector') as mock_pd, \
             patch('app.services.sav_workflow_engine.warranty_service') as mock_ws, \
             patch('app.services.sav_workflow_engine.priority_scorer') as mock_ps, \
             patch('app.services.sav_workflow_engine.tone_analyzer') as mock_ta, \
             patch('app.services.sav_workflow_engine.client_summary_generator') as mock_csg:

            mock_pd.detect_problem_type.return_value = p0_problem
            mock_ws.check_warranty_coverage.return_value = mock_warranty_check_covered
            mock_ps.calculate_priority.return_value = p0_priority
            mock_ta.analyze_tone.return_value = critical_tone
            mock_csg.generate_summary.return_value = mock_summary

            ticket = await engine.process_new_claim(
                customer_id="client@example.fr",
                order_number="CMD-2025-001",
                product_sku="OSLO-3P-GREY",
                product_name="Canapé OSLO 3 places gris",
                problem_description="Structure cassée, danger imminent!",
                warranty=mock_warranty,
                customer_tier="vip",
                product_value=2500.0
            )

            # Should be escalated to human
            assert ticket.auto_resolved is False
            assert ticket.status == TicketStatus.ESCALATED_TO_HUMAN
            assert ticket.priority == "P0"
