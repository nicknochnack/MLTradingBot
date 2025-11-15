from flask_mail import Mail, Message
from flask import render_template_string
from models import EmailTemplate, Lead, Activity
from datetime import datetime
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class EmailService:
    """Handle email sending and automation"""
    
    def __init__(self, mail: Mail):
        self.mail = mail
    
    def send_email(self, to: str, subject: str, body_html: str, 
                   body_text: str = None, attachments: List[Dict] = None) -> bool:
        """
        Send an email
        
        Args:
            to: Recipient email address
            subject: Email subject
            body_html: HTML body content
            body_text: Plain text body (optional)
            attachments: List of attachment dicts with 'filename' and 'data' keys
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            msg = Message(
                subject=subject,
                recipients=[to],
                html=body_html,
                body=body_text or self._html_to_text(body_html)
            )
            
            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    msg.attach(
                        attachment['filename'],
                        'application/pdf',
                        attachment['data']
                    )
            
            self.mail.send(msg)
            logger.info(f"Email sent successfully to {to}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to}: {str(e)}")
            return False
    
    def send_welcome_email(self, lead: Lead) -> bool:
        """
        Send welcome email to new lead
        
        Args:
            lead: Lead object
            
        Returns:
            True if sent successfully
        """
        subject = "Thank You for Requesting Your Free Business Listings Audit!"
        
        body_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2b6cb0;">Hello {lead.contact_name}!</h2>
                
                <p>Thank you for requesting a free listings audit for <strong>{lead.business_name}</strong>.</p>
                
                <p>We're currently analyzing your business's online presence across Google, Yelp, Facebook, 
                and other major platforms. This process typically takes a few minutes.</p>
                
                <div style="background-color: #ebf8ff; border-left: 4px solid #2b6cb0; padding: 15px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #1a365d;">What Happens Next?</h3>
                    <ol style="margin-bottom: 0;">
                        <li>We'll complete your comprehensive listings audit</li>
                        <li>You'll receive a detailed PDF report via email</li>
                        <li>Schedule your free 15-minute review session to discuss the findings</li>
                    </ol>
                </div>
                
                <p>Your audit report will identify:</p>
                <ul>
                    <li>Missing or incorrect business information</li>
                    <li>Opportunities to improve your local visibility</li>
                    <li>Competitive insights for your area</li>
                    <li>Actionable recommendations to attract more customers</li>
                </ul>
                
                <p style="margin-top: 30px;">
                    <a href="mailto:info@bvm-castlehills.com" 
                       style="background-color: #2b6cb0; color: white; padding: 12px 24px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        Contact Us
                    </a>
                </p>
                
                <p style="margin-top: 30px; font-size: 14px; color: #666;">
                    Best regards,<br>
                    <strong>Best Version Media - Castle Hills</strong><br>
                    Serving Castle Hills and surrounding communities<br>
                    Phone: (555) 123-4567<br>
                    Email: info@bvm-castlehills.com
                </p>
                
                <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 30px 0;">
                
                <p style="font-size: 12px; color: #999; text-align: center;">
                    You're receiving this email because you requested a free business listings audit 
                    from Best Version Media.
                </p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(lead.email, subject, body_html)
    
    def send_audit_report_email(self, lead: Lead, report_path: str) -> bool:
        """
        Send audit report to lead
        
        Args:
            lead: Lead object
            report_path: Path to the PDF report
            
        Returns:
            True if sent successfully
        """
        subject = f"Your Business Listings Audit Report is Ready - {lead.business_name}"
        
        body_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2b6cb0;">Your Audit Report is Ready, {lead.contact_name}!</h2>
                
                <p>We've completed the comprehensive listings audit for <strong>{lead.business_name}</strong>.</p>
                
                <p>Please find your detailed audit report attached to this email. The report includes:</p>
                
                <ul>
                    <li><strong>Overall Online Presence Score</strong></li>
                    <li><strong>Platform-by-Platform Analysis</strong> (Google, Yelp, Facebook)</li>
                    <li><strong>Critical Issues</strong> affecting your visibility</li>
                    <li><strong>Actionable Recommendations</strong> to improve your listings</li>
                </ul>
                
                <div style="background-color: #fff5f5; border-left: 4px solid #c53030; padding: 15px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #742a2a;">Important Findings</h3>
                    <p style="margin-bottom: 0;">
                        Our audit revealed several opportunities to improve your local visibility and 
                        attract more customers in the Castle Hills area.
                    </p>
                </div>
                
                <h3 style="color: #1a365d;">Schedule Your Free 15-Minute Review Session</h3>
                
                <p>Let's discuss your audit results and how Best Version Media can help you:</p>
                <ul>
                    <li>Fix critical listing issues</li>
                    <li>Improve your local search rankings</li>
                    <li>Reach more customers in your community</li>
                    <li>Build a stronger online presence</li>
                </ul>
                
                <p style="margin-top: 30px;">
                    <a href="https://calendly.com/your-link/15min" 
                       style="background-color: #2f855a; color: white; padding: 12px 24px; 
                              text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                        Schedule Your Free Review Session
                    </a>
                </p>
                
                <p style="margin-top: 30px; font-size: 14px; color: #666;">
                    Questions? Reply to this email or call us at (555) 123-4567.
                </p>
                
                <p style="margin-top: 30px; font-size: 14px; color: #666;">
                    Best regards,<br>
                    <strong>Best Version Media - Castle Hills</strong><br>
                    Bringing People Together
                </p>
                
                <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 30px 0;">
                
                <p style="font-size: 12px; color: #999; text-align: center;">
                    Best Version Media | Serving Castle Hills, Addison, Keller, Southlake, and surrounding communities
                </p>
            </div>
        </body>
        </html>
        """
        
        # Read PDF file
        attachments = []
        try:
            with open(report_path, 'rb') as f:
                attachments.append({
                    'filename': f'{lead.business_name}_Audit_Report.pdf',
                    'data': f.read()
                })
        except Exception as e:
            logger.error(f"Failed to read report file {report_path}: {str(e)}")
            return False
        
        return self.send_email(lead.email, subject, body_html, attachments=attachments)
    
    def send_appointment_reminder(self, lead: Lead) -> bool:
        """
        Send appointment reminder email
        
        Args:
            lead: Lead object with scheduled appointment
            
        Returns:
            True if sent successfully
        """
        if not lead.appointment_date:
            return False
        
        appointment_time = lead.appointment_date.strftime('%B %d, %Y at %I:%M %p')
        
        subject = f"Reminder: Your Listings Review Session Tomorrow - {lead.business_name}"
        
        body_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2b6cb0;">Reminder: Your Review Session is Tomorrow!</h2>
                
                <p>Hi {lead.contact_name},</p>
                
                <p>This is a friendly reminder about your scheduled listings audit review session:</p>
                
                <div style="background-color: #ebf8ff; border: 2px solid #2b6cb0; padding: 20px; 
                            margin: 20px 0; border-radius: 8px; text-align: center;">
                    <h3 style="margin-top: 0; color: #1a365d;">Appointment Details</h3>
                    <p style="font-size: 18px; margin: 10px 0;">
                        <strong>{appointment_time}</strong>
                    </p>
                    <p style="margin-bottom: 0;">
                        Duration: 15 minutes
                    </p>
                </div>
                
                <h3 style="color: #1a365d;">What We'll Cover:</h3>
                <ul>
                    <li>Review your audit findings in detail</li>
                    <li>Discuss the impact on your business</li>
                    <li>Explore solutions to improve your online presence</li>
                    <li>Answer any questions you have</li>
                </ul>
                
                <p>Please have your audit report handy during our call.</p>
                
                <p style="margin-top: 30px;">
                    Need to reschedule? 
                    <a href="https://calendly.com/your-link/reschedule" style="color: #2b6cb0;">
                        Click here
                    </a>
                </p>
                
                <p style="margin-top: 30px; font-size: 14px; color: #666;">
                    Looking forward to speaking with you!<br><br>
                    <strong>Best Version Media - Castle Hills</strong><br>
                    Phone: (555) 123-4567
                </p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(lead.email, subject, body_html)
    
    def send_follow_up_email(self, lead: Lead, days_since_audit: int) -> bool:
        """
        Send follow-up email to leads who haven't scheduled
        
        Args:
            lead: Lead object
            days_since_audit: Number of days since audit was completed
            
        Returns:
            True if sent successfully
        """
        subject = f"Don't Miss Out on Improving Your Online Presence - {lead.business_name}"
        
        body_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2b6cb0;">Hi {lead.contact_name},</h2>
                
                <p>I wanted to follow up on the business listings audit we completed for 
                <strong>{lead.business_name}</strong> a few days ago.</p>
                
                <p>Have you had a chance to review the report? I noticed you haven't scheduled 
                your free 15-minute review session yet.</p>
                
                <div style="background-color: #fffaf0; border-left: 4px solid #d69e2e; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0;">
                        <strong>Quick reminder:</strong> The issues identified in your audit could be 
                        costing you customers right now. Local businesses that optimize their online 
                        presence see an average of 30% more customer inquiries.
                    </p>
                </div>
                
                <p>In just 15 minutes, we can:</p>
                <ul>
                    <li>Walk through your specific audit findings</li>
                    <li>Prioritize the most impactful fixes</li>
                    <li>Show you how Best Version Media can help</li>
                    <li>Answer any questions you have</li>
                </ul>
                
                <p style="margin-top: 30px; text-align: center;">
                    <a href="https://calendly.com/your-link/15min" 
                       style="background-color: #2b6cb0; color: white; padding: 12px 24px; 
                              text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                        Schedule Your Free Session Now
                    </a>
                </p>
                
                <p style="margin-top: 30px;">
                    Or if you prefer, just reply to this email with a good time to call you.
                </p>
                
                <p style="margin-top: 30px; font-size: 14px; color: #666;">
                    Best regards,<br>
                    <strong>Best Version Media - Castle Hills</strong><br>
                    Phone: (555) 123-4567<br>
                    Email: info@bvm-castlehills.com
                </p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(lead.email, subject, body_html)
    
    def _html_to_text(self, html: str) -> str:
        """
        Convert HTML to plain text (simple implementation)
        
        Args:
            html: HTML string
            
        Returns:
            Plain text version
        """
        # Simple HTML tag removal
        import re
        text = re.sub('<[^<]+?>', '', html)
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        return text.strip()
    
    def send_template_email(self, lead: Lead, template_name: str, 
                           custom_vars: Dict = None) -> bool:
        """
        Send email using a stored template
        
        Args:
            lead: Lead object
            template_name: Name of the email template
            custom_vars: Optional custom variables for template
            
        Returns:
            True if sent successfully
        """
        template = EmailTemplate.query.filter_by(name=template_name, is_active=True).first()
        
        if not template:
            logger.error(f"Email template '{template_name}' not found")
            return False
        
        # Prepare template variables
        variables = {
            'contact_name': lead.contact_name,
            'business_name': lead.business_name,
            'email': lead.email,
            'phone': lead.phone or 'N/A',
            'zip_code': lead.zip_code or 'N/A'
        }
        
        if custom_vars:
            variables.update(custom_vars)
        
        # Render template
        try:
            subject = render_template_string(template.subject, **variables)
            body_html = render_template_string(template.body_html, **variables)
            body_text = render_template_string(template.body_text, **variables)
            
            return self.send_email(lead.email, subject, body_html, body_text)
            
        except Exception as e:
            logger.error(f"Failed to render email template: {str(e)}")
            return False
