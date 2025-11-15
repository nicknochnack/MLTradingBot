from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_mail import Mail
from config import config
from models import db, Lead
from forms import AuditRequestForm
from lead_manager import LeadManager
from listings_audit import ListingsAuditor
from report_generator import AuditReportGenerator
from email_service import EmailService
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Load configuration
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Initialize extensions
db.init_app(app)
mail = Mail(app)

# Initialize services
email_service = EmailService(mail)

# Create database tables
with app.app_context():
    db.create_all()
    logger.info("Database tables created successfully")


@app.route('/')
def index():
    """Landing page with audit request form"""
    form = AuditRequestForm()
    return render_template('index.html', form=form)


@app.route('/audit', methods=['GET'])
def audit_page():
    """Dedicated audit request page"""
    form = AuditRequestForm()
    return render_template('index.html', form=form)


@app.route('/submit-audit', methods=['POST'])
def submit_audit_request():
    """Handle audit request form submission"""
    form = AuditRequestForm()
    
    if form.validate_on_submit():
        try:
            # Check if lead already exists
            existing_lead = LeadManager.get_lead_by_email(form.email.data)
            
            if existing_lead:
                flash('You already have an audit request. Check your email for the report!', 'info')
                return redirect(url_for('thank_you', lead_id=existing_lead.id))
            
            # Create new lead
            lead = LeadManager.create_lead(
                business_name=form.business_name.data,
                contact_name=form.contact_name.data,
                email=form.email.data,
                phone=form.phone.data,
                zip_code=form.zip_code.data,
                address=form.address.data,
                source='landing_page'
            )
            
            logger.info(f"New lead created: {lead.business_name} ({lead.email})")
            
            # Send welcome email
            try:
                email_service.send_welcome_email(lead)
                logger.info(f"Welcome email sent to {lead.email}")
            except Exception as e:
                logger.error(f"Failed to send welcome email: {str(e)}")
            
            # Perform audit in background (simplified - in production use Celery/RQ)
            try:
                perform_audit(lead)
            except Exception as e:
                logger.error(f"Audit failed for lead {lead.id}: {str(e)}")
            
            return redirect(url_for('thank_you', lead_id=lead.id))
            
        except Exception as e:
            logger.error(f"Error processing audit request: {str(e)}")
            flash('An error occurred. Please try again or contact us directly.', 'danger')
            return redirect(url_for('index'))
    
    # Form validation failed
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'{error}', 'danger')
    
    return render_template('index.html', form=form)


def perform_audit(lead: Lead):
    """
    Perform the listings audit and generate report
    
    Args:
        lead: Lead object to audit
    """
    try:
        # Initialize auditor
        auditor = ListingsAuditor(app.config)
        
        # Perform audit
        logger.info(f"Starting audit for {lead.business_name}")
        audit_results = auditor.audit_business(
            business_name=lead.business_name,
            zip_code=lead.zip_code,
            address=lead.address
        )
        
        # Save audit results to database
        LeadManager.save_audit_results(lead.id, audit_results)
        logger.info(f"Audit completed for {lead.business_name}. Score: {audit_results['overall_score']}")
        
        # Generate PDF report
        report_generator = AuditReportGenerator(output_dir='reports')
        lead_data = {
            'business_name': lead.business_name,
            'contact_name': lead.contact_name,
            'email': lead.email,
            'zip_code': lead.zip_code
        }
        
        report_path = report_generator.generate_report(lead_data, audit_results)
        logger.info(f"Report generated: {report_path}")
        
        # Update lead with report path
        LeadManager.update_lead(lead.id, audit_report_path=report_path)
        
        # Send report via email
        try:
            email_service.send_audit_report_email(lead, report_path)
            logger.info(f"Audit report emailed to {lead.email}")
        except Exception as e:
            logger.error(f"Failed to send audit report email: {str(e)}")
        
        # Update lead score
        lead_score = LeadManager.calculate_lead_score(lead)
        LeadManager.update_lead(lead.id, lead_score=lead_score)
        
    except Exception as e:
        logger.error(f"Error performing audit for lead {lead.id}: {str(e)}")
        raise


@app.route('/thank-you/<int:lead_id>')
def thank_you(lead_id):
    """Thank you page after audit request"""
    lead = LeadManager.get_lead(lead_id)
    
    if not lead:
        flash('Lead not found', 'danger')
        return redirect(url_for('index'))
    
    return render_template('thank_you.html', lead=lead)


@app.route('/dashboard')
def dashboard():
    """Admin dashboard for managing leads"""
    status_filter = request.args.get('status')
    
    # Get leads
    if status_filter:
        leads = LeadManager.get_all_leads(status=status_filter)
    else:
        leads = LeadManager.get_all_leads(limit=100)
    
    # Get statistics
    stats = LeadManager.get_dashboard_stats()
    
    return render_template('dashboard.html', leads=leads, stats=stats, status_filter=status_filter)


@app.route('/lead/<int:lead_id>')
def lead_detail(lead_id):
    """Detailed view of a single lead"""
    lead = LeadManager.get_lead(lead_id)
    
    if not lead:
        flash('Lead not found', 'danger')
        return redirect(url_for('dashboard'))
    
    activities = LeadManager.get_lead_activities(lead_id, limit=20)
    
    return render_template('lead_detail.html', lead=lead, activities=activities)


@app.route('/api/leads', methods=['GET'])
def api_get_leads():
    """API endpoint to get leads"""
    status = request.args.get('status')
    limit = request.args.get('limit', 50, type=int)
    
    leads = LeadManager.get_all_leads(status=status, limit=limit)
    
    return jsonify({
        'success': True,
        'count': len(leads),
        'leads': [lead.to_dict() for lead in leads]
    })


@app.route('/api/lead/<int:lead_id>', methods=['GET'])
def api_get_lead(lead_id):
    """API endpoint to get a single lead"""
    lead = LeadManager.get_lead(lead_id)
    
    if not lead:
        return jsonify({'success': False, 'error': 'Lead not found'}), 404
    
    return jsonify({
        'success': True,
        'lead': lead.to_dict()
    })


@app.route('/api/stats', methods=['GET'])
def api_get_stats():
    """API endpoint to get dashboard statistics"""
    stats = LeadManager.get_dashboard_stats()
    
    return jsonify({
        'success': True,
        'stats': stats
    })


@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')


@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'database': 'connected' if db.engine else 'disconnected'
    })


@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    logger.error(f"Internal server error: {str(error)}")
    db.session.rollback()
    return render_template('500.html'), 500


# CLI commands
@app.cli.command()
def init_db():
    """Initialize the database"""
    db.create_all()
    print("Database initialized successfully!")


@app.cli.command()
def seed_db():
    """Seed the database with sample data"""
    # Create sample lead
    lead = LeadManager.create_lead(
        business_name="Sample Restaurant",
        contact_name="John Doe",
        email="john@example.com",
        phone="(555) 123-4567",
        zip_code="75056",
        source="test"
    )
    print(f"Sample lead created: {lead.business_name}")


if __name__ == '__main__':
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(host='0.0.0.0', port=port, debug=debug)
