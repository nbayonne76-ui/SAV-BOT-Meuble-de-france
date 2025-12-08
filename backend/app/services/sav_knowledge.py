# backend/app/services/sav_knowledge.py
import json
import os
from typing import List, Dict, Optional
from pathlib import Path

class SAVKnowledgeBase:
    """
    Service to manage SAV scenarios and FAQ knowledge base
    """

    def __init__(self):
        self.base_path = Path(__file__).parent.parent.parent / "data"
        self.scenarios_path = self.base_path / "sav_scenarios.json"
        self.faq_path = self.base_path / "faq.json"

        self.scenarios = {}
        self.faq = {}
        self.load_knowledge()

    def load_knowledge(self):
        """Load SAV scenarios and FAQ from JSON files"""
        try:
            # Load SAV scenarios
            if self.scenarios_path.exists():
                with open(self.scenarios_path, 'r', encoding='utf-8') as f:
                    self.scenarios = json.load(f)

            # Load FAQ
            if self.faq_path.exists():
                with open(self.faq_path, 'r', encoding='utf-8') as f:
                    self.faq = json.load(f)

        except Exception as e:
            print(f"Error loading SAV knowledge: {e}")

    def search_scenario_by_keywords(self, query: str) -> List[Dict]:
        """
        Search scenarios by keywords in user query
        Returns list of matching scenarios sorted by relevance
        """
        query_lower = query.lower()
        matches = []

        for scenario in self.scenarios.get("scenarios", []):
            relevance_score = 0

            # Check keywords
            for keyword in scenario.get("keywords", []):
                if keyword.lower() in query_lower:
                    relevance_score += 2

            # Check title
            if any(word in scenario.get("title", "").lower() for word in query_lower.split()):
                relevance_score += 1

            # Check problem type
            if scenario.get("problem_type", "").lower() in query_lower:
                relevance_score += 3

            if relevance_score > 0:
                scenario_copy = scenario.copy()
                scenario_copy["relevance_score"] = relevance_score
                matches.append(scenario_copy)

        # Sort by relevance score
        matches.sort(key=lambda x: x["relevance_score"], reverse=True)

        return matches

    def get_scenario_by_id(self, scenario_id: str) -> Optional[Dict]:
        """Get a specific scenario by ID"""
        for scenario in self.scenarios.get("scenarios", []):
            if scenario.get("id") == scenario_id:
                return scenario
        return None

    def get_scenario_by_product(self, product_id: str) -> List[Dict]:
        """Get all scenarios related to a specific product"""
        matches = []
        for scenario in self.scenarios.get("scenarios", []):
            if scenario.get("product_id") == product_id:
                matches.append(scenario)
        return matches

    def get_scenarios_by_priority(self, priority: str) -> List[Dict]:
        """Get all scenarios with a specific priority (P0, P1, P2, P3)"""
        matches = []
        for scenario in self.scenarios.get("scenarios", []):
            if scenario.get("priority") == priority:
                matches.append(scenario)
        return matches

    def get_priority_info(self, priority: str) -> Optional[Dict]:
        """Get information about a priority level"""
        return self.scenarios.get("priority_definitions", {}).get(priority)

    def search_faq(self, query: str, category: Optional[str] = None) -> List[Dict]:
        """
        Search FAQ by query and optionally filter by category
        Returns list of matching questions sorted by relevance
        """
        query_lower = query.lower()
        matches = []

        categories = self.faq.get("faq", {}).get("categories", [])

        for cat in categories:
            # Skip if category filter doesn't match
            if category and cat.get("id") != category:
                continue

            for question in cat.get("questions", []):
                relevance_score = 0

                # Check keywords
                for keyword in question.get("keywords", []):
                    if keyword.lower() in query_lower:
                        relevance_score += 2

                # Check question text
                if any(word in question.get("question", "").lower() for word in query_lower.split()):
                    relevance_score += 3

                # Check answer text (lower weight)
                if any(word in question.get("answer", "").lower() for word in query_lower.split()):
                    relevance_score += 1

                if relevance_score > 0:
                    question_copy = question.copy()
                    question_copy["category"] = cat.get("name")
                    question_copy["category_icon"] = cat.get("icon")
                    question_copy["relevance_score"] = relevance_score
                    matches.append(question_copy)

        # Sort by relevance and popularity
        matches.sort(key=lambda x: (x["relevance_score"], x.get("popularity", 0)), reverse=True)

        return matches

    def get_faq_by_category(self, category_id: str) -> List[Dict]:
        """Get all FAQ questions for a specific category"""
        categories = self.faq.get("faq", {}).get("categories", [])

        for cat in categories:
            if cat.get("id") == category_id:
                return cat.get("questions", [])

        return []

    def get_all_faq_categories(self) -> List[Dict]:
        """Get list of all FAQ categories"""
        categories = self.faq.get("faq", {}).get("categories", [])
        return [
            {
                "id": cat.get("id"),
                "name": cat.get("name"),
                "icon": cat.get("icon"),
                "question_count": len(cat.get("questions", []))
            }
            for cat in categories
        ]

    def get_chatbot_guidelines(self) -> List[str]:
        """Get the list of chatbot guidelines for SAV"""
        return self.scenarios.get("chatbot_guidelines", [])

    def get_sav_context_for_chatbot(self, user_message: str) -> str:
        """
        Generate contextual SAV information for chatbot based on user message
        Returns formatted string to include in chatbot system prompt
        """
        # Search for relevant scenarios
        scenarios = self.search_scenario_by_keywords(user_message)[:3]  # Top 3

        # Search for relevant FAQ
        faq_items = self.search_faq(user_message)[:2]  # Top 2

        context = "# SAV KNOWLEDGE BASE\n\n"

        # Add relevant scenarios
        if scenarios:
            context += "## Scénarios SAV Pertinents:\n\n"
            for scenario in scenarios:
                context += f"**{scenario['title']}** (Priorité: {scenario['priority']})\n"
                context += f"- Première réponse: {scenario.get('first_response', '')}\n"

                if scenario.get('diagnostic_questions'):
                    context += f"- Questions diagnostic: {', '.join(scenario['diagnostic_questions'][:3])}\n"

                if scenario.get('quick_fix', {}).get('possible'):
                    context += f"- Solution rapide disponible\n"

                context += f"- Garantie: {'Oui' if scenario.get('warranty_coverage') else 'Non'}\n\n"

        # Add relevant FAQ
        if faq_items:
            context += "## FAQ Pertinentes:\n\n"
            for item in faq_items:
                context += f"**Q: {item['question']}**\n"
                # Truncate long answers
                answer = item['answer']
                if len(answer) > 300:
                    answer = answer[:300] + "..."
                context += f"A: {answer}\n\n"

        # Add guidelines
        guidelines = self.get_chatbot_guidelines()
        if guidelines:
            context += "## Guidelines SAV:\n"
            for guideline in guidelines[:5]:  # Top 5 guidelines
                context += f"- {guideline}\n"

        return context

    def update_faq_stats(self, question_id: str, helpful: bool):
        """Update FAQ statistics when user votes"""
        categories = self.faq.get("faq", {}).get("categories", [])

        for cat in categories:
            for question in cat.get("questions", []):
                if question.get("id") == question_id:
                    if helpful:
                        question["helpful_count"] = question.get("helpful_count", 0) + 1
                    else:
                        question["not_helpful_count"] = question.get("not_helpful_count", 0) + 1

                    # Save back to file
                    self._save_faq()
                    return True

        return False

    def add_faq_question(self, category_id: str, question: str, answer: str, keywords: List[str]) -> bool:
        """Add a new FAQ question"""
        categories = self.faq.get("faq", {}).get("categories", [])

        for cat in categories:
            if cat.get("id") == category_id:
                # Generate new ID
                existing_ids = [q.get("id") for q in cat.get("questions", [])]
                new_id = f"faq-{category_id}-{len(existing_ids) + 1:03d}"

                new_question = {
                    "id": new_id,
                    "question": question,
                    "answer": answer,
                    "keywords": keywords,
                    "related_scenarios": [],
                    "popularity": 1,
                    "helpful_count": 0,
                    "not_helpful_count": 0
                }

                cat["questions"].append(new_question)

                # Update metadata
                self.faq["faq"]["metadata"]["total_questions"] += 1
                self.faq["faq"]["metadata"]["last_updated"] = "2025-12-03"

                # Save
                self._save_faq()
                return True

        return False

    def _save_faq(self):
        """Save FAQ back to file"""
        try:
            with open(self.faq_path, 'w', encoding='utf-8') as f:
                json.dump(self.faq, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving FAQ: {e}")

    def get_all_scenarios_summary(self) -> str:
        """Get a summary of all scenarios for AI context"""
        scenarios = self.scenarios.get("scenarios", [])

        summary = f"# SAV SCENARIOS DATABASE ({len(scenarios)} scenarios)\n\n"

        # Group by priority
        by_priority = {}
        for scenario in scenarios:
            priority = scenario.get("priority", "P3")
            if priority not in by_priority:
                by_priority[priority] = []
            by_priority[priority].append(scenario)

        for priority in ["P0", "P1", "P2", "P3"]:
            if priority in by_priority:
                priority_info = self.get_priority_info(priority)
                summary += f"\n## {priority} - {priority_info.get('label')} ({len(by_priority[priority])} scenarios)\n"
                summary += f"Response time: {priority_info.get('response_time')}\n\n"

                for scenario in by_priority[priority]:
                    summary += f"- **{scenario['title']}** ({scenario['product_name']})\n"
                    summary += f"  Keywords: {', '.join(scenario.get('keywords', [])[:5])}\n"

        return summary


# Global instance
sav_kb = SAVKnowledgeBase()
