# backend/app/services/evidence_collector.py
"""
Système de collecte et validation des preuves (photos, vidéos, documents)
Analyse la qualité et complétude des preuves fournies
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import hashlib
import re

logger = logging.getLogger(__name__)


class EvidenceType(str, Enum):
    """Types de preuves acceptées"""
    PHOTO = "photo"
    VIDEO = "video"
    DOCUMENT = "document"
    INVOICE = "invoice"


class EvidenceQuality(str, Enum):
    """Niveaux de qualité des preuves"""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    UNUSABLE = "unusable"


@dataclass
class EvidenceAnalysis:
    """Résultat d'analyse d'une preuve"""
    evidence_id: str
    quality: EvidenceQuality
    quality_score: float  # 0-100
    issues: List[str]
    strengths: List[str]
    recommendations: List[str]
    verified: bool
    analysis_timestamp: datetime


@dataclass
class CompletenessCheck:
    """Résultat de vérification de complétude"""
    is_complete: bool
    missing_items: List[str]
    completeness_score: float  # 0-100
    additional_requests: List[str]
    can_proceed: bool


class EvidenceCollector:
    """
    Système de collecte et validation des preuves
    """

    def __init__(self):
        # Configuration des exigences par catégorie de problème
        self.requirements_by_category = {
            "structural": {
                "min_photos": 3,
                "min_videos": 1,
                "required_angles": ["vue_ensemble", "zoom_probleme", "contexte"],
                "required_elements": ["structure_visible", "probleme_clair"],
                "description": "Photos de la structure affectée + vidéo montrant le problème"
            },
            "mechanism": {
                "min_photos": 2,
                "min_videos": 1,
                "required_angles": ["mecanisme_ferme", "mecanisme_ouvert"],
                "required_elements": ["mecanisme_visible", "demonstration_probleme"],
                "description": "Photos du mécanisme + vidéo démontrant le dysfonctionnement"
            },
            "fabric": {
                "min_photos": 3,
                "min_videos": 0,
                "required_angles": ["zoom_defaut", "vue_ensemble", "lumiere_naturelle"],
                "required_elements": ["defaut_visible", "zone_etendue"],
                "description": "Photos claires du défaut de tissu sous différents angles"
            },
            "cushions": {
                "min_photos": 2,
                "min_videos": 0,
                "required_angles": ["vue_dessus", "vue_profil"],
                "required_elements": ["affaissement_visible", "reference_hauteur"],
                "description": "Photos montrant l'affaissement et vue d'ensemble"
            },
            "delivery": {
                "min_photos": 4,
                "min_videos": 0,
                "required_angles": ["dommage", "emballage", "etiquette", "bon_livraison"],
                "required_elements": ["dommage_visible", "colis_intact_partiel"],
                "description": "Photos des dommages + emballage + documents de livraison"
            },
            "dimensions": {
                "min_photos": 3,
                "min_videos": 0,
                "required_angles": ["produit_complet", "mesure_largeur", "mesure_profondeur"],
                "required_elements": ["metre_visible", "dimensions_claires"],
                "description": "Photos avec mètre visible montrant les dimensions"
            }
        }

        # Règles de qualité pour les photos
        self.photo_quality_rules = {
            "min_file_size_kb": 50,  # Trop petite = mauvaise qualité
            "max_file_size_mb": 20,  # Trop grosse = problème upload
            "accepted_formats": [".jpg", ".jpeg", ".png", ".heic"],
            "min_description_length": 10
        }

        # Règles de qualité pour les vidéos
        self.video_quality_rules = {
            "min_duration_seconds": 5,
            "max_duration_seconds": 120,
            "max_file_size_mb": 100,
            "accepted_formats": [".mp4", ".mov", ".avi"]
        }

    def analyze_evidence(
        self,
        evidence_id: str,
        evidence_type: EvidenceType,
        file_url: str,
        file_size_bytes: int,
        description: str,
        metadata: Dict = None
    ) -> EvidenceAnalysis:
        """
        Analyse la qualité d'une preuve individuelle

        Args:
            evidence_id: ID de la preuve
            evidence_type: Type (photo, video, document)
            file_url: URL du fichier
            file_size_bytes: Taille du fichier
            description: Description fournie par le client
            metadata: Métadonnées additionnelles

        Returns:
            EvidenceAnalysis avec score de qualité
        """

        quality_score = 100.0
        issues = []
        strengths = []
        recommendations = []

        # Analyse selon le type
        if evidence_type == EvidenceType.PHOTO:
            quality_score, issues, strengths = self._analyze_photo(
                file_url, file_size_bytes, description, metadata
            )
        elif evidence_type == EvidenceType.VIDEO:
            quality_score, issues, strengths = self._analyze_video(
                file_url, file_size_bytes, description, metadata
            )
        elif evidence_type in [EvidenceType.DOCUMENT, EvidenceType.INVOICE]:
            quality_score, issues, strengths = self._analyze_document(
                file_url, file_size_bytes, description
            )

        # Déterminer la qualité globale
        if quality_score >= 90:
            quality = EvidenceQuality.EXCELLENT
        elif quality_score >= 75:
            quality = EvidenceQuality.GOOD
        elif quality_score >= 60:
            quality = EvidenceQuality.ACCEPTABLE
        elif quality_score >= 40:
            quality = EvidenceQuality.POOR
        else:
            quality = EvidenceQuality.UNUSABLE

        # Générer des recommandations
        if quality_score < 75:
            recommendations = self._generate_recommendations(evidence_type, issues)

        # Vérification automatique (basée sur score)
        verified = quality_score >= 60

        logger.info(
            f"📸 Preuve analysée {evidence_id}: {quality} "
            f"(score: {quality_score:.1f}/100)"
        )

        return EvidenceAnalysis(
            evidence_id=evidence_id,
            quality=quality,
            quality_score=quality_score,
            issues=issues,
            strengths=strengths,
            recommendations=recommendations,
            verified=verified,
            analysis_timestamp=datetime.now()
        )

    def _analyze_photo(
        self,
        file_url: str,
        file_size_bytes: int,
        description: str,
        metadata: Optional[Dict]
    ) -> Tuple[float, List[str], List[str]]:
        """Analyse une photo"""

        score = 100.0
        issues = []
        strengths = []

        # Vérifier la taille du fichier
        file_size_kb = file_size_bytes / 1024

        if file_size_kb < self.photo_quality_rules["min_file_size_kb"]:
            score -= 30
            issues.append(f"Fichier trop petit ({file_size_kb:.0f}KB) - qualité probablement insuffisante")
        elif file_size_kb > self.photo_quality_rules["max_file_size_mb"] * 1024:
            score -= 10
            issues.append(f"Fichier très volumineux ({file_size_kb / 1024:.1f}MB) - compression recommandée")
        else:
            strengths.append("Taille de fichier appropriée")

        # Vérifier le format
        file_extension = self._get_file_extension(file_url)
        if file_extension not in self.photo_quality_rules["accepted_formats"]:
            score -= 20
            issues.append(f"Format {file_extension} non optimal - préférer JPG ou PNG")
        else:
            strengths.append(f"Format {file_extension} accepté")

        # Vérifier la description
        if len(description) < self.photo_quality_rules["min_description_length"]:
            score -= 15
            issues.append("Description trop courte - détaillez ce qui est visible")
        else:
            strengths.append("Description fournie")

        # Vérifier les métadonnées (si disponibles)
        if metadata:
            if "width" in metadata and "height" in metadata:
                width = metadata["width"]
                height = metadata["height"]

                # Vérifier la résolution minimale
                if width < 640 or height < 480:
                    score -= 25
                    issues.append(f"Résolution trop faible ({width}x{height}) - minimum 640x480")
                elif width >= 1920 and height >= 1080:
                    strengths.append("Haute résolution")
                else:
                    strengths.append("Résolution acceptable")

            if "orientation" in metadata:
                strengths.append(f"Orientation: {metadata['orientation']}")

        return score, issues, strengths

    def _analyze_video(
        self,
        file_url: str,
        file_size_bytes: int,
        description: str,
        metadata: Optional[Dict]
    ) -> Tuple[float, List[str], List[str]]:
        """Analyse une vidéo"""

        score = 100.0
        issues = []
        strengths = []

        # Vérifier la taille du fichier
        file_size_mb = file_size_bytes / (1024 * 1024)

        if file_size_mb > self.video_quality_rules["max_file_size_mb"]:
            score -= 20
            issues.append(f"Vidéo très volumineuse ({file_size_mb:.1f}MB) - compression recommandée")
        else:
            strengths.append("Taille de vidéo acceptable")

        # Vérifier le format
        file_extension = self._get_file_extension(file_url)
        if file_extension not in self.video_quality_rules["accepted_formats"]:
            score -= 15
            issues.append(f"Format {file_extension} non optimal - préférer MP4")
        else:
            strengths.append(f"Format {file_extension} accepté")

        # Vérifier la durée (si disponible dans metadata)
        if metadata and "duration" in metadata:
            duration = metadata["duration"]  # en secondes

            if duration < self.video_quality_rules["min_duration_seconds"]:
                score -= 20
                issues.append(f"Vidéo trop courte ({duration}s) - minimum 5 secondes")
            elif duration > self.video_quality_rules["max_duration_seconds"]:
                score -= 10
                issues.append(f"Vidéo trop longue ({duration}s) - maximum 2 minutes")
            else:
                strengths.append(f"Durée appropriée ({duration}s)")

        # Vérifier la description
        if len(description) < 15:
            score -= 15
            issues.append("Description insuffisante - expliquez ce que montre la vidéo")
        else:
            strengths.append("Description fournie")

        return score, issues, strengths

    def _analyze_document(
        self,
        file_url: str,
        file_size_bytes: int,
        description: str
    ) -> Tuple[float, List[str], List[str]]:
        """Analyse un document (facture, bon de livraison, etc.)"""

        score = 100.0
        issues = []
        strengths = []

        file_extension = self._get_file_extension(file_url)

        # Vérifier le format
        accepted_doc_formats = [".pdf", ".jpg", ".jpeg", ".png"]
        if file_extension not in accepted_doc_formats:
            score -= 30
            issues.append(f"Format {file_extension} non accepté pour documents")
        else:
            strengths.append(f"Format {file_extension} accepté")

        # Vérifier la taille
        file_size_mb = file_size_bytes / (1024 * 1024)
        if file_size_mb > 10:
            score -= 10
            issues.append("Document volumineux - compression recommandée")
        else:
            strengths.append("Taille de document acceptable")

        # Vérifier description
        if len(description) < 5:
            score -= 20
            issues.append("Précisez le type de document (facture, bon de livraison, etc.)")
        else:
            strengths.append("Type de document précisé")

        return score, issues, strengths

    def check_completeness(
        self,
        problem_category: str,
        evidences: List[Dict],
        problem_severity: str = "P2"
    ) -> CompletenessCheck:
        """
        Vérifie si les preuves fournies sont complètes

        Args:
            problem_category: Catégorie du problème
            evidences: Liste des preuves fournies
            problem_severity: Sévérité du problème

        Returns:
            CompletenessCheck avec résultat de complétude
        """

        requirements = self.requirements_by_category.get(
            problem_category,
            {"min_photos": 2, "min_videos": 0, "required_angles": [], "required_elements": []}
        )

        missing_items = []
        additional_requests = []
        completeness_score = 0.0

        # Compter les preuves par type
        photo_count = sum(1 for e in evidences if e.get("type") == EvidenceType.PHOTO)
        video_count = sum(1 for e in evidences if e.get("type") == EvidenceType.VIDEO)

        # Vérifier le nombre minimum de photos
        min_photos = requirements["min_photos"]
        if photo_count < min_photos:
            missing_items.append(f"{min_photos - photo_count} photo(s) supplémentaire(s)")
            completeness_score += (photo_count / min_photos) * 50  # 50% du score
        else:
            completeness_score += 50

        # Vérifier le nombre minimum de vidéos
        min_videos = requirements["min_videos"]
        if video_count < min_videos:
            missing_items.append(f"{min_videos - video_count} vidéo(s)")
            completeness_score += (video_count / max(min_videos, 1)) * 30  # 30% du score
        else:
            completeness_score += 30

        # Vérifier la qualité globale des preuves
        good_quality_count = sum(
            1 for e in evidences
            if e.get("quality_score", 0) >= 70
        )
        quality_ratio = good_quality_count / max(len(evidences), 1)
        completeness_score += quality_ratio * 20  # 20% du score

        # Déterminer si on peut procéder
        is_complete = len(missing_items) == 0
        can_proceed = completeness_score >= 70 or problem_severity in ["P0", "P1"]

        # Générer des demandes additionnelles
        if not is_complete:
            additional_requests = self._generate_additional_requests(
                problem_category,
                requirements,
                missing_items
            )

        logger.info(
            f"✔️  Complétude des preuves: {completeness_score:.0f}% "
            f"({'Complet' if is_complete else 'Incomplet'})"
        )

        return CompletenessCheck(
            is_complete=is_complete,
            missing_items=missing_items,
            completeness_score=completeness_score,
            additional_requests=additional_requests,
            can_proceed=can_proceed
        )

    def _generate_recommendations(
        self,
        evidence_type: EvidenceType,
        issues: List[str]
    ) -> List[str]:
        """Génère des recommandations pour améliorer la qualité"""

        recommendations = []

        if evidence_type == EvidenceType.PHOTO:
            if any("trop petit" in issue.lower() for issue in issues):
                recommendations.append("Prenez une photo avec un appareil de meilleure qualité")
                recommendations.append("Assurez-vous d'avoir un bon éclairage")

            if any("résolution" in issue.lower() for issue in issues):
                recommendations.append("Utilisez l'appareil photo de votre smartphone (mode haute résolution)")

            if any("description" in issue.lower() for issue in issues):
                recommendations.append("Décrivez précisément ce qui est visible sur la photo")

        elif evidence_type == EvidenceType.VIDEO:
            if any("trop courte" in issue.lower() for issue in issues):
                recommendations.append("Filmez pendant au moins 10 secondes pour montrer le problème clairement")

            if any("trop longue" in issue.lower() for issue in issues):
                recommendations.append("Concentrez-vous sur le problème (max 2 minutes)")

        return recommendations

    def _generate_additional_requests(
        self,
        problem_category: str,
        requirements: Dict,
        missing_items: List[str]
    ) -> List[str]:
        """Génère des demandes spécifiques pour compléter les preuves"""

        requests = []

        if "photo" in " ".join(missing_items).lower():
            required_angles = requirements.get("required_angles", [])
            if required_angles:
                requests.append(
                    f"Veuillez fournir des photos sous ces angles: {', '.join(required_angles)}"
                )
            else:
                requests.append("Veuillez fournir des photos supplémentaires montrant le problème clairement")

        if "vidéo" in " ".join(missing_items).lower():
            if problem_category == "mechanism":
                requests.append(
                    "Veuillez fournir une vidéo montrant le mécanisme en action et le problème rencontré"
                )
            elif problem_category == "structural":
                requests.append(
                    "Veuillez fournir une vidéo montrant la structure et démontrant l'instabilité"
                )

        return requests

    def _get_file_extension(self, file_url: str) -> str:
        """Extrait l'extension du fichier depuis l'URL"""
        # Extraire l'extension (derniers caractères après le dernier point)
        match = re.search(r'\.[a-zA-Z0-9]+$', file_url.lower())
        if match:
            return match.group(0)
        return ""

    def generate_evidence_request_message(
        self,
        problem_category: str,
        priority: str
    ) -> str:
        """
        Génère un message demandant les preuves au client

        Args:
            problem_category: Catégorie du problème
            priority: Priorité du ticket

        Returns:
            Message formaté pour le client
        """

        requirements = self.requirements_by_category.get(
            problem_category,
            {"min_photos": 2, "min_videos": 0, "description": "Photos du problème"}
        )

        urgency = "🔴 URGENT" if priority == "P0" else "⚡ Important" if priority == "P1" else ""

        message = f"{urgency}\n\n" if urgency else ""
        message += "📸 **Preuves nécessaires pour traiter votre demande:**\n\n"
        message += f"✅ {requirements['min_photos']} photo(s) minimum\n"

        if requirements['min_videos'] > 0:
            message += f"✅ {requirements['min_videos']} vidéo(s)\n"

        message += f"\n💡 **Ce qu'il faut montrer:**\n{requirements['description']}\n"

        if "required_angles" in requirements and requirements["required_angles"]:
            message += f"\n📐 **Angles recommandés:**\n"
            for angle in requirements["required_angles"]:
                message += f"  • {angle.replace('_', ' ').title()}\n"

        message += "\n⚠️ **Conseils pour de bonnes preuves:**\n"
        message += "  • Éclairage suffisant (lumière naturelle de préférence)\n"
        message += "  • Photos nettes et en haute résolution\n"
        message += "  • Cadrage incluant le problème et son contexte\n"
        message += "  • Ajoutez une brève description pour chaque fichier\n"

        return message


# Instance globale
evidence_collector = EvidenceCollector()
