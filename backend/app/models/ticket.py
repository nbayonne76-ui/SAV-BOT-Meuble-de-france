# backend/app/models/ticket.py
"""
SQLAlchemy models for SAV tickets with database persistence
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional, List, Dict

Base = declarative_base()


class TicketDB(Base):
    """Database model for SAV Tickets"""
    __tablename__ = "sav_tickets"

    # Primary key
    ticket_id = Column(String(50), primary_key=True, index=True)

    # Customer & Order info
    customer_id = Column(String(100), index=True)
    customer_name = Column(String(200))
    order_number = Column(String(100), index=True)
    product_sku = Column(String(100))
    product_name = Column(String(200))

    # Problem details
    problem_description = Column(Text)
    problem_category = Column(String(100))
    problem_severity = Column(String(50))
    problem_confidence = Column(Float)

    # Warranty info
    warranty_id = Column(String(100))
    warranty_status = Column(String(50))

    # Priority
    priority = Column(String(20), index=True)
    priority_score = Column(Integer)
    priority_factors = Column(JSON)  # List of factors

    # Status & Resolution
    status = Column(String(50), index=True)
    auto_resolved = Column(Boolean, default=False)
    resolution_type = Column(String(50))
    resolution_description = Column(Text)

    # Tone analysis
    tone_category = Column(String(50))
    tone_score = Column(Float)
    tone_keywords = Column(JSON)  # List of keywords

    # SLA & Timing
    created_at = Column(DateTime, default=datetime.now, index=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    sla_response_deadline = Column(DateTime)
    sla_intervention_deadline = Column(DateTime)
    resolved_at = Column(DateTime)

    # Evidence & Attachments
    evidence = Column(JSON)  # List of evidence objects
    attachments = Column(JSON)  # List of attachment URLs

    # Actions & History
    actions = Column(JSON)  # List of action objects
    notes = Column(JSON)  # List of notes

    # Client Summary
    client_summary = Column(JSON)  # Client summary object

    # Source
    source = Column(String(50), default="chat")  # chat, voice_chat, email, etc.

    def __repr__(self):
        return f"<TicketDB {self.ticket_id} - {self.status}>"
