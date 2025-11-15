# BVM Sales Funnel - Local Business Listings Audit System

A Python-based sales funnel automation system for Best Version Media that generates inbound leads through free business listings audits, completely avoiding telemarketing law issues.

## 🎯 Overview

This application implements a 3-stage sales funnel:

1. **Awareness (TOFU)** - Landing page offering "Free Castle Hills Local Business Listings Audit"
2. **Interest/Conversion (MOFU)** - Automated audit + scheduling for 15-minute review session
3. **Decision (BOFU)** - Review call to present BVM solutions

## ✨ Features

- **Landing Page** - High-converting landing page with audit request form
- **Automated Listings Audit** - Checks Google My Business, Yelp, and Facebook
- **PDF Report Generation** - Professional audit reports with findings and recommendations
- **Email Automation** - Welcome emails, report delivery, and follow-up sequences
- **Lead Management** - CRM-style dashboard for tracking and managing leads
- **Scheduling Integration** - Ready for Calendly integration
- **API Endpoints** - RESTful API for lead data and statistics

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- pip package manager

### Installation

1. **Install dependencies:**
```bash
pip install -r requirements_funnel.txt
```

2. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

3. **Initialize the database:**
```bash
python app.py init_db
```

4. **Run the application:**
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 🔑 Configuration

### Required API Keys

1. **Google Places API** - For Google My Business listings
   - Get key: https://developers.google.com/maps/documentation/places/web-service/get-api-key
   
2. **Yelp Fusion API** - For Yelp listings
   - Get key: https://www.yelp.com/developers/documentation/v3/authentication
   
3. **Facebook Graph API** - For Facebook Business Pages
   - Get token: https://developers.facebook.com/docs/graph-api/get-started

4. **Email Service** - For sending emails
   - Gmail SMTP (recommended for testing)
   - SendGrid or Mailgun (recommended for production)

5. **Calendly API** (Optional) - For appointment scheduling
   - Get key: https://developer.calendly.com/

### Environment Variables

Edit `.env` file with your configuration:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here

# API Keys
GOOGLE_PLACES_API_KEY=your-google-api-key
YELP_API_KEY=your-yelp-api-key
FACEBOOK_ACCESS_TOKEN=your-facebook-token

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Calendly
CALENDLY_EVENT_TYPE_URL=https://calendly.com/your-username/15min

# Business Settings
BUSINESS_NAME=Best Version Media - Castle Hills
BUSINESS_PHONE=(555) 123-4567
BUSINESS_EMAIL=info@bvm-castlehills.com
```

## 📁 Project Structure

```
/vercel/sandbox/
├── app.py                  # Main Flask application
├── config.py               # Configuration management
├── models.py               # Database models
├── forms.py                # WTForms for form validation
├── lead_manager.py         # Lead management logic
├── listings_audit.py       # Listings audit engine
├── report_generator.py     # PDF report generation
├── email_service.py        # Email automation
├── requirements_funnel.txt # Python dependencies
├── .env.example            # Environment variables template
├── templates/              # HTML templates
│   ├── base.html
│   ├── index.html          # Landing page
│   ├── thank_you.html      # Thank you page
│   └── dashboard.html      # Admin dashboard
├── static/                 # Static files
│   ├── css/
│   └── js/
└── reports/                # Generated PDF reports
```

## 🎨 Key Components

### 1. Landing Page (`templates/index.html`)
- High-converting design with clear value proposition
- Audit request form with validation
- Social proof and testimonials
- Mobile-responsive

### 2. Listings Auditor (`listings_audit.py`)
- Checks business presence on Google, Yelp, Facebook
- Identifies issues: incorrect info, missing photos, poor reviews
- Calculates overall visibility score (0-100)
- Generates actionable recommendations

### 3. Report Generator (`report_generator.py`)
- Creates professional PDF reports using ReportLab
- Includes executive summary, platform analysis, issues, and recommendations
- Branded with BVM information and call-to-action

### 4. Email Service (`email_service.py`)
- Welcome email upon audit request
- Audit report delivery with PDF attachment
- Appointment reminders
- Follow-up sequences for non-responders

### 5. Lead Manager (`lead_manager.py`)
- Create and manage leads
- Track lead status (new, contacted, qualified, converted, lost)
- Calculate lead scores
- Activity tracking and notes

### 6. Dashboard (`templates/dashboard.html`)
- View all leads with filtering
- Statistics and metrics
- Lead status management
- Quick actions (email, view details)

## 🔄 Workflow

1. **Lead Capture**
   - Visitor lands on page (from ads, direct mail, etc.)
   - Fills out audit request form
   - Lead created in database

2. **Automated Audit**
   - System checks Google, Yelp, Facebook listings
   - Identifies issues and opportunities
   - Calculates visibility score

3. **Report Delivery**
   - Professional PDF report generated
   - Emailed to lead with findings
   - Follow-up email with scheduling link

4. **Appointment Scheduling**
   - Lead schedules 15-minute review session
   - Automated reminders sent
   - Lead status updated

5. **Review Call**
   - Discuss audit findings
   - Present BVM solutions
   - Convert to customer

## 📊 API Endpoints

### Get All Leads
```
GET /api/leads?status=new&limit=50
```

### Get Single Lead
```
GET /api/lead/<lead_id>
```

### Get Statistics
```
GET /api/stats
```

### Health Check
```
GET /health
```

## 🎯 Lead Scoring

Leads are automatically scored (0-100) based on:
- Complete contact information (+30)
- Audit completion (+20)
- Low audit score = high opportunity (+20)
- Appointment scheduled (+30)
- Recency (+10)

## 📧 Email Templates

The system includes pre-built email templates:
1. **Welcome Email** - Sent immediately after audit request
2. **Audit Report Email** - Sent with PDF report attached
3. **Appointment Reminder** - Sent before scheduled calls
4. **Follow-up Email** - Sent to leads who haven't scheduled

## 🚦 Testing

### Test the Application

1. **Run the app:**
```bash
python app.py
```

2. **Visit:** `http://localhost:5000`

3. **Submit a test audit request**

4. **Check the dashboard:** `http://localhost:5000/dashboard`

### Seed Test Data

```bash
python app.py seed_db
```

## 🔒 Legal Compliance

This system is designed to avoid telemarketing law issues:

✅ **Inbound Leads Only** - All contacts are opt-in
✅ **Express Permission** - Leads request the audit
✅ **Business Interest** - Clear, requested service
✅ **No Cold Calling** - All follow-up is consent-based

## 🎨 Customization

### Branding
- Update `BUSINESS_NAME`, `BUSINESS_PHONE`, `BUSINESS_EMAIL` in `.env`
- Add logo to `static/images/bvm_logo.png`
- Customize colors in `static/css/style.css`

### Communities
- Edit `COMMUNITIES` list in `config.py`
- Update footer in `templates/base.html`

### Email Templates
- Modify templates in `email_service.py`
- Add custom variables as needed

## 📈 Production Deployment

### Recommended Stack
- **Hosting:** Heroku, AWS, DigitalOcean, or Vercel
- **Database:** PostgreSQL (upgrade from SQLite)
- **Email:** SendGrid or Mailgun
- **Background Jobs:** Celery with Redis
- **Monitoring:** Sentry for error tracking

### Production Checklist
- [ ] Set `FLASK_ENV=production`
- [ ] Use strong `SECRET_KEY`
- [ ] Configure production database
- [ ] Set up SSL/HTTPS
- [ ] Configure email service
- [ ] Add API rate limiting
- [ ] Set up monitoring and logging
- [ ] Configure backups
- [ ] Add CAPTCHA to forms (prevent spam)

## 🤝 Support

For questions or issues:
- Email: info@bvm-castlehills.com
- Phone: (555) 123-4567

## 📝 License

This project is proprietary to Best Version Media.

---

**Built with ❤️ for Best Version Media - Bringing People Together**
