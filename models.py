from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Lead(db.Model):
    """Lead model for storing business contact information"""
    __tablename__ = 'leads'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Business Information
    business_name = db.Column(db.String(200), nullable=False)
    contact_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    zip_code = db.Column(db.String(10), nullable=False)
    address = db.Column(db.String(300), nullable=True)
    website = db.Column(db.String(200), nullable=True)
    
    # Lead Status
    status = db.Column(db.String(50), default='new')  # new, contacted, qualified, converted, lost
    lead_score = db.Column(db.Integer, default=0)
    source = db.Column(db.String(50), default='landing_page')  # landing_page, referral, direct
    
    # Audit Information
    audit_requested = db.Column(db.Boolean, default=True)
    audit_completed = db.Column(db.Boolean, default=False)
    audit_report_path = db.Column(db.String(300), nullable=True)
    audit_score = db.Column(db.Integer, nullable=True)  # 0-100 score
    
    # Scheduling
    appointment_scheduled = db.Column(db.Boolean, default=False)
    appointment_date = db.Column(db.DateTime, nullable=True)
    calendly_event_id = db.Column(db.String(100), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_contacted = db.Column(db.DateTime, nullable=True)
    
    # Notes and Follow-up
    notes = db.Column(db.Text, nullable=True)
    follow_up_date = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    audit_results = db.relationship('AuditResult', backref='lead', lazy=True, cascade='all, delete-orphan')
    activities = db.relationship('Activity', backref='lead', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Lead {self.business_name} - {self.email}>'
    
    def to_dict(self):
        """Convert lead to dictionary"""
        return {
            'id': self.id,
            'business_name': self.business_name,
            'contact_name': self.contact_name,
            'email': self.email,
            'phone': self.phone,
            'zip_code': self.zip_code,
            'status': self.status,
            'lead_score': self.lead_score,
            'audit_completed': self.audit_completed,
            'appointment_scheduled': self.appointment_scheduled,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class AuditResult(db.Model):
    """Store detailed audit results for each platform"""
    __tablename__ = 'audit_results'
    
    id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'), nullable=False)
    
    # Platform
    platform = db.Column(db.String(50), nullable=False)  # google, yelp, facebook, etc.
    
    # Findings
    is_listed = db.Column(db.Boolean, default=False)
    is_claimed = db.Column(db.Boolean, default=False)
    has_correct_info = db.Column(db.Boolean, default=False)
    has_photos = db.Column(db.Boolean, default=False)
    has_reviews = db.Column(db.Boolean, default=False)
    review_count = db.Column(db.Integer, default=0)
    average_rating = db.Column(db.Float, nullable=True)
    
    # Issues Found
    issues = db.Column(db.JSON, nullable=True)  # List of specific issues
    recommendations = db.Column(db.JSON, nullable=True)  # List of recommendations
    
    # Raw Data
    raw_data = db.Column(db.JSON, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AuditResult {self.platform} for Lead {self.lead_id}>'


class Activity(db.Model):
    """Track all activities and interactions with leads"""
    __tablename__ = 'activities'
    
    id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'), nullable=False)
    
    activity_type = db.Column(db.String(50), nullable=False)  # email, call, meeting, note
    subject = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(100), default='system')
    
    def __repr__(self):
        return f'<Activity {self.activity_type} for Lead {self.lead_id}>'


class EmailTemplate(db.Model):
    """Store email templates for automation"""
    __tablename__ = 'email_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    subject = db.Column(db.String(200), nullable=False)
    body_html = db.Column(db.Text, nullable=False)
    body_text = db.Column(db.Text, nullable=False)
    
    # Template Variables
    variables = db.Column(db.JSON, nullable=True)  # List of available variables
    
    # Automation
    trigger_event = db.Column(db.String(50), nullable=True)  # lead_created, audit_completed, etc.
    delay_hours = db.Column(db.Integer, default=0)  # Delay before sending
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<EmailTemplate {self.name}>'
