from models import db, Lead, AuditResult, Activity
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class LeadManager:
    """Manage leads and their lifecycle"""
    
    @staticmethod
    def create_lead(business_name: str, contact_name: str, email: str, 
                   phone: str = None, zip_code: str = None, **kwargs) -> Lead:
        """
        Create a new lead
        
        Args:
            business_name: Name of the business
            contact_name: Contact person name
            email: Email address
            phone: Phone number (optional)
            zip_code: ZIP code
            **kwargs: Additional lead attributes
            
        Returns:
            Created Lead object
        """
        lead = Lead(
            business_name=business_name,
            contact_name=contact_name,
            email=email,
            phone=phone,
            zip_code=zip_code,
            **kwargs
        )
        
        db.session.add(lead)
        db.session.commit()
        
        # Log activity
        LeadManager.add_activity(
            lead.id,
            'lead_created',
            'New Lead Created',
            f'Lead created from {kwargs.get("source", "landing_page")}'
        )
        
        return lead
    
    @staticmethod
    def get_lead(lead_id: int) -> Optional[Lead]:
        """Get lead by ID"""
        return Lead.query.get(lead_id)
    
    @staticmethod
    def get_lead_by_email(email: str) -> Optional[Lead]:
        """Get lead by email address"""
        return Lead.query.filter_by(email=email).first()
    
    @staticmethod
    def get_all_leads(status: str = None, limit: int = None) -> List[Lead]:
        """
        Get all leads, optionally filtered by status
        
        Args:
            status: Filter by lead status (new, contacted, qualified, converted, lost)
            limit: Maximum number of leads to return
            
        Returns:
            List of Lead objects
        """
        query = Lead.query
        
        if status:
            query = query.filter_by(status=status)
        
        query = query.order_by(Lead.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def update_lead(lead_id: int, **kwargs) -> Optional[Lead]:
        """
        Update lead information
        
        Args:
            lead_id: ID of the lead to update
            **kwargs: Fields to update
            
        Returns:
            Updated Lead object or None if not found
        """
        lead = Lead.query.get(lead_id)
        if not lead:
            return None
        
        for key, value in kwargs.items():
            if hasattr(lead, key):
                setattr(lead, key, value)
        
        lead.updated_at = datetime.utcnow()
        db.session.commit()
        
        return lead
    
    @staticmethod
    def update_lead_status(lead_id: int, new_status: str, note: str = None) -> Optional[Lead]:
        """
        Update lead status and log activity
        
        Args:
            lead_id: ID of the lead
            new_status: New status (new, contacted, qualified, converted, lost)
            note: Optional note about the status change
            
        Returns:
            Updated Lead object
        """
        lead = Lead.query.get(lead_id)
        if not lead:
            return None
        
        old_status = lead.status
        lead.status = new_status
        lead.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Log activity
        description = f'Status changed from {old_status} to {new_status}'
        if note:
            description += f': {note}'
        
        LeadManager.add_activity(
            lead_id,
            'status_change',
            'Status Updated',
            description
        )
        
        return lead
    
    @staticmethod
    def save_audit_results(lead_id: int, audit_data: Dict) -> bool:
        """
        Save audit results for a lead
        
        Args:
            lead_id: ID of the lead
            audit_data: Dictionary containing audit results
            
        Returns:
            True if successful, False otherwise
        """
        lead = Lead.query.get(lead_id)
        if not lead:
            return False
        
        # Update lead audit status
        lead.audit_completed = True
        lead.audit_score = audit_data.get('overall_score', 0)
        lead.updated_at = datetime.utcnow()
        
        # Save platform-specific results
        for platform_name, platform_data in audit_data.get('platforms', {}).items():
            audit_result = AuditResult(
                lead_id=lead_id,
                platform=platform_name,
                is_listed=platform_data.get('is_listed', False),
                is_claimed=platform_data.get('is_claimed', False),
                has_correct_info=platform_data.get('has_correct_info', False),
                has_photos=platform_data.get('has_photos', False),
                has_reviews=platform_data.get('has_reviews', False),
                review_count=platform_data.get('review_count', 0),
                average_rating=platform_data.get('average_rating', 0.0),
                issues=platform_data.get('issues', []),
                recommendations=audit_data.get('recommendations', []),
                raw_data=platform_data
            )
            db.session.add(audit_result)
        
        db.session.commit()
        
        # Log activity
        LeadManager.add_activity(
            lead_id,
            'audit_completed',
            'Listings Audit Completed',
            f'Overall score: {audit_data.get("overall_score", 0)}/100'
        )
        
        return True
    
    @staticmethod
    def schedule_appointment(lead_id: int, appointment_date: datetime, 
                           calendly_event_id: str = None) -> Optional[Lead]:
        """
        Schedule an appointment for a lead
        
        Args:
            lead_id: ID of the lead
            appointment_date: Date and time of appointment
            calendly_event_id: Optional Calendly event ID
            
        Returns:
            Updated Lead object
        """
        lead = Lead.query.get(lead_id)
        if not lead:
            return None
        
        lead.appointment_scheduled = True
        lead.appointment_date = appointment_date
        lead.calendly_event_id = calendly_event_id
        lead.updated_at = datetime.utcnow()
        
        # Update status if still new
        if lead.status == 'new':
            lead.status = 'contacted'
        
        db.session.commit()
        
        # Log activity
        LeadManager.add_activity(
            lead_id,
            'appointment_scheduled',
            'Appointment Scheduled',
            f'Scheduled for {appointment_date.strftime("%Y-%m-%d %H:%M")}'
        )
        
        return lead
    
    @staticmethod
    def add_activity(lead_id: int, activity_type: str, subject: str, 
                    description: str = None, created_by: str = 'system') -> Activity:
        """
        Add an activity/note to a lead
        
        Args:
            lead_id: ID of the lead
            activity_type: Type of activity (email, call, meeting, note, etc.)
            subject: Activity subject
            description: Detailed description
            created_by: Who created the activity
            
        Returns:
            Created Activity object
        """
        activity = Activity(
            lead_id=lead_id,
            activity_type=activity_type,
            subject=subject,
            description=description,
            created_by=created_by
        )
        
        db.session.add(activity)
        db.session.commit()
        
        return activity
    
    @staticmethod
    def get_lead_activities(lead_id: int, limit: int = None) -> List[Activity]:
        """
        Get all activities for a lead
        
        Args:
            lead_id: ID of the lead
            limit: Maximum number of activities to return
            
        Returns:
            List of Activity objects
        """
        query = Activity.query.filter_by(lead_id=lead_id).order_by(Activity.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def calculate_lead_score(lead: Lead) -> int:
        """
        Calculate lead score based on various factors
        
        Args:
            lead: Lead object
            
        Returns:
            Lead score (0-100)
        """
        score = 0
        
        # Base score for having complete information
        if lead.phone:
            score += 10
        if lead.website:
            score += 10
        if lead.address:
            score += 10
        
        # Audit completion
        if lead.audit_completed:
            score += 20
            # Lower audit score means more opportunity
            if lead.audit_score and lead.audit_score < 50:
                score += 20
        
        # Engagement
        if lead.appointment_scheduled:
            score += 30
        
        # Recency
        if lead.created_at:
            days_old = (datetime.utcnow() - lead.created_at).days
            if days_old < 7:
                score += 10
        
        return min(score, 100)
    
    @staticmethod
    def get_leads_needing_follow_up() -> List[Lead]:
        """
        Get leads that need follow-up
        
        Returns:
            List of leads needing attention
        """
        today = datetime.utcnow()
        
        # Leads with follow-up date in the past or today
        leads_with_followup = Lead.query.filter(
            Lead.follow_up_date <= today,
            Lead.status.in_(['new', 'contacted', 'qualified'])
        ).all()
        
        # Leads with audit completed but no appointment
        leads_no_appointment = Lead.query.filter(
            Lead.audit_completed == True,
            Lead.appointment_scheduled == False,
            Lead.status.in_(['new', 'contacted'])
        ).all()
        
        # Combine and deduplicate
        all_leads = list(set(leads_with_followup + leads_no_appointment))
        
        return sorted(all_leads, key=lambda x: x.created_at, reverse=True)
    
    @staticmethod
    def get_dashboard_stats() -> Dict:
        """
        Get statistics for dashboard
        
        Returns:
            Dictionary with various statistics
        """
        total_leads = Lead.query.count()
        new_leads = Lead.query.filter_by(status='new').count()
        qualified_leads = Lead.query.filter_by(status='qualified').count()
        converted_leads = Lead.query.filter_by(status='converted').count()
        
        audits_completed = Lead.query.filter_by(audit_completed=True).count()
        appointments_scheduled = Lead.query.filter_by(appointment_scheduled=True).count()
        
        # Leads created in last 7 days
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_leads = Lead.query.filter(Lead.created_at >= week_ago).count()
        
        # Conversion rate
        conversion_rate = (converted_leads / total_leads * 100) if total_leads > 0 else 0
        
        return {
            'total_leads': total_leads,
            'new_leads': new_leads,
            'qualified_leads': qualified_leads,
            'converted_leads': converted_leads,
            'audits_completed': audits_completed,
            'appointments_scheduled': appointments_scheduled,
            'recent_leads': recent_leads,
            'conversion_rate': round(conversion_rate, 2),
            'leads_needing_followup': len(LeadManager.get_leads_needing_follow_up())
        }
