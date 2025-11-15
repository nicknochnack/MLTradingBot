from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, DateTimeField
from wtforms.validators import DataRequired, Email, Length, Optional, Regexp

class LeadCaptureForm(FlaskForm):
    """Form for capturing leads on landing page"""
    business_name = StringField(
        'Business Name',
        validators=[
            DataRequired(message='Business name is required'),
            Length(min=2, max=200, message='Business name must be between 2 and 200 characters')
        ],
        render_kw={'placeholder': 'Your Business Name', 'class': 'form-control'}
    )
    
    contact_name = StringField(
        'Your Name',
        validators=[
            DataRequired(message='Your name is required'),
            Length(min=2, max=100, message='Name must be between 2 and 100 characters')
        ],
        render_kw={'placeholder': 'John Smith', 'class': 'form-control'}
    )
    
    email = StringField(
        'Email Address',
        validators=[
            DataRequired(message='Email is required'),
            Email(message='Please enter a valid email address')
        ],
        render_kw={'placeholder': 'john@business.com', 'class': 'form-control', 'type': 'email'}
    )
    
    phone = StringField(
        'Phone Number',
        validators=[
            Optional(),
            Regexp(r'^\+?1?\d{9,15}$', message='Please enter a valid phone number')
        ],
        render_kw={'placeholder': '(555) 123-4567', 'class': 'form-control', 'type': 'tel'}
    )
    
    zip_code = StringField(
        'ZIP Code',
        validators=[
            DataRequired(message='ZIP code is required'),
            Regexp(r'^\d{5}(-\d{4})?$', message='Please enter a valid ZIP code')
        ],
        render_kw={'placeholder': '75056', 'class': 'form-control'}
    )
    
    address = StringField(
        'Business Address',
        validators=[Optional(), Length(max=300)],
        render_kw={'placeholder': '123 Main St, City, State', 'class': 'form-control'}
    )


class LeadUpdateForm(FlaskForm):
    """Form for updating lead information in admin"""
    business_name = StringField(
        'Business Name',
        validators=[DataRequired(), Length(min=2, max=200)],
        render_kw={'class': 'form-control'}
    )
    
    contact_name = StringField(
        'Contact Name',
        validators=[DataRequired(), Length(min=2, max=100)],
        render_kw={'class': 'form-control'}
    )
    
    email = StringField(
        'Email',
        validators=[DataRequired(), Email()],
        render_kw={'class': 'form-control', 'type': 'email'}
    )
    
    phone = StringField(
        'Phone',
        validators=[Optional()],
        render_kw={'class': 'form-control', 'type': 'tel'}
    )
    
    zip_code = StringField(
        'ZIP Code',
        validators=[DataRequired()],
        render_kw={'class': 'form-control'}
    )
    
    address = StringField(
        'Address',
        validators=[Optional(), Length(max=300)],
        render_kw={'class': 'form-control'}
    )
    
    website = StringField(
        'Website',
        validators=[Optional(), Length(max=200)],
        render_kw={'class': 'form-control', 'type': 'url'}
    )
    
    status = SelectField(
        'Status',
        choices=[
            ('new', 'New'),
            ('contacted', 'Contacted'),
            ('qualified', 'Qualified'),
            ('converted', 'Converted'),
            ('lost', 'Lost')
        ],
        validators=[DataRequired()],
        render_kw={'class': 'form-select'}
    )
    
    lead_score = StringField(
        'Lead Score',
        validators=[Optional()],
        render_kw={'class': 'form-control', 'type': 'number', 'min': '0', 'max': '100'}
    )
    
    notes = TextAreaField(
        'Notes',
        validators=[Optional()],
        render_kw={'class': 'form-control', 'rows': '4'}
    )


class ActivityForm(FlaskForm):
    """Form for adding activities/notes to leads"""
    activity_type = SelectField(
        'Activity Type',
        choices=[
            ('note', 'Note'),
            ('email', 'Email'),
            ('call', 'Phone Call'),
            ('meeting', 'Meeting'),
            ('task', 'Task')
        ],
        validators=[DataRequired()],
        render_kw={'class': 'form-select'}
    )
    
    subject = StringField(
        'Subject',
        validators=[DataRequired(), Length(min=2, max=200)],
        render_kw={'class': 'form-control', 'placeholder': 'Brief description'}
    )
    
    description = TextAreaField(
        'Description',
        validators=[Optional()],
        render_kw={'class': 'form-control', 'rows': '4', 'placeholder': 'Detailed notes...'}
    )


class StatusUpdateForm(FlaskForm):
    """Form for updating lead status"""
    status = SelectField(
        'New Status',
        choices=[
            ('new', 'New'),
            ('contacted', 'Contacted'),
            ('qualified', 'Qualified'),
            ('converted', 'Converted'),
            ('lost', 'Lost')
        ],
        validators=[DataRequired()],
        render_kw={'class': 'form-select'}
    )
    
    note = TextAreaField(
        'Note (Optional)',
        validators=[Optional()],
        render_kw={'class': 'form-control', 'rows': '3', 'placeholder': 'Add a note about this status change...'}
    )


class AppointmentForm(FlaskForm):
    """Form for scheduling appointments"""
    appointment_date = DateTimeField(
        'Appointment Date & Time',
        validators=[DataRequired()],
        format='%Y-%m-%dT%H:%M',
        render_kw={'class': 'form-control', 'type': 'datetime-local'}
    )
    
    calendly_event_id = StringField(
        'Calendly Event ID',
        validators=[Optional()],
        render_kw={'class': 'form-control', 'placeholder': 'Optional'}
    )
    
    notes = TextAreaField(
        'Notes',
        validators=[Optional()],
        render_kw={'class': 'form-control', 'rows': '3'}
    )


class EmailTemplateForm(FlaskForm):
    """Form for creating/editing email templates"""
    name = StringField(
        'Template Name',
        validators=[DataRequired(), Length(min=2, max=100)],
        render_kw={'class': 'form-control', 'placeholder': 'welcome_email'}
    )
    
    subject = StringField(
        'Email Subject',
        validators=[DataRequired(), Length(min=2, max=200)],
        render_kw={'class': 'form-control', 'placeholder': 'Welcome to {{business_name}}'}
    )
    
    body_html = TextAreaField(
        'HTML Body',
        validators=[DataRequired()],
        render_kw={'class': 'form-control', 'rows': '10'}
    )
    
    body_text = TextAreaField(
        'Plain Text Body',
        validators=[DataRequired()],
        render_kw={'class': 'form-control', 'rows': '8'}
    )
    
    trigger_event = SelectField(
        'Trigger Event',
        choices=[
            ('', 'None (Manual)'),
            ('lead_created', 'Lead Created'),
            ('audit_completed', 'Audit Completed'),
            ('appointment_scheduled', 'Appointment Scheduled'),
            ('follow_up', 'Follow Up')
        ],
        validators=[Optional()],
        render_kw={'class': 'form-select'}
    )
    
    delay_hours = StringField(
        'Delay (Hours)',
        validators=[Optional()],
        render_kw={'class': 'form-control', 'type': 'number', 'min': '0', 'value': '0'}
    )
    
    is_active = BooleanField(
        'Active',
        default=True,
        render_kw={'class': 'form-check-input'}
    )
