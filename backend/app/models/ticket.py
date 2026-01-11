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
    __table_args__ = (
        # Composite indexes for common query patterns
        {'comment': 'SAV service tickets with full history'},
    )

    # Primary key
    ticket_id = Column(String(50), primary_key=True, index=True)

    # Customer & Order info
    customer_id = Column(String(100), index=True)  # For customer ticket history
    customer_name = Column(String(200))
    order_number = Column(String(100), index=True)  # For order lookup
    product_sku = Column(String(100), index=True)  # For product issues tracking
    product_name = Column(String(200))

    # Problem details
    problem_description = Column(Text)
    problem_category = Column(String(100), index=True)  # For analytics and filtering
    problem_severity = Column(String(50), index=True)  # For priority filtering
    problem_confidence = Column(Float)

    # Warranty info
    warranty_id = Column(String(100), index=True)  # For warranty lookup
    warranty_status = Column(String(200))  # Increased from 50 to handle longer warranty messages

    # Priority
    priority = Column(String(20), index=True)  # For priority-based routing
    priority_score = Column(Integer)
    priority_factors = Column(JSON)  # List of factors

    # Status & Resolution
    status = Column(String(50), index=True)  # Most common filter
    auto_resolved = Column(Boolean, default=False, index=True)  # For resolution analytics
    resolution_type = Column(String(50))
    resolution_description = Column(Text)

    # Tone analysis
    tone_category = Column(String(50))
    tone_score = Column(Float)
    tone_keywords = Column(JSON)  # List of keywords

    # SLA & Timing
    created_at = Column(DateTime, default=datetime.now, index=True)  # For sorting and date ranges
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, index=True)  # For recent activity
    sla_response_deadline = Column(DateTime, index=True)  # For SLA monitoring
    sla_intervention_deadline = Column(DateTime, index=True)  # For SLA monitoring
    resolved_at = Column(DateTime, index=True)  # For resolution time analytics

    # Evidence & Attachments
    evidence = Column(JSON)  # List of evidence objects
    attachments = Column(JSON)  # List of attachment URLs

    # Actions & History
    actions = Column(JSON)  # List of action objects
    notes = Column(JSON)  # List of notes

    # Client Summary
    client_summary = Column(JSON)  # Client summary object

    # Source
    source = Column(String(50), default="chat", index=True)  # For channel analytics

    def __repr__(self):
        return f"<TicketDB {self.ticket_id} - {self.status}>"
