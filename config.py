import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///leads.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API Keys
    GOOGLE_PLACES_API_KEY = os.environ.get('GOOGLE_PLACES_API_KEY', '')
    YELP_API_KEY = os.environ.get('YELP_API_KEY', '')
    FACEBOOK_ACCESS_TOKEN = os.environ.get('FACEBOOK_ACCESS_TOKEN', '')
    
    # Email Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', '')
    
    # Calendly
    CALENDLY_API_KEY = os.environ.get('CALENDLY_API_KEY', '')
    CALENDLY_EVENT_TYPE_URL = os.environ.get('CALENDLY_EVENT_TYPE_URL', '')
    
    # Business Settings
    BUSINESS_NAME = os.environ.get('BUSINESS_NAME', 'Best Version Media - Castle Hills')
    BUSINESS_PHONE = os.environ.get('BUSINESS_PHONE', '(555) 123-4567')
    BUSINESS_EMAIL = os.environ.get('BUSINESS_EMAIL', 'info@bvm-castlehills.com')
    TARGET_ZIP_CODES = os.environ.get('TARGET_ZIP_CODES', '75056,75010').split(',')
    
    # Application Settings
    LEADS_PER_PAGE = int(os.environ.get('LEADS_PER_PAGE', 20))
    AUDIT_REPORT_LOGO = os.environ.get('AUDIT_REPORT_LOGO', 'static/images/bvm_logo.png')
    
    # Communities Served
    COMMUNITIES = [
        'Castle Hills', 'Addison', 'Bent Tree', 'Decatur', 'Heath', 
        'Keller', 'Light Farms', 'Lucas', 'Park Cities', 'Preston Hollow',
        'Rockwall', 'Southlake', 'Starwood', 'Trophy Club', 'Westover Hills',
        'Windsong Ranch'
    ]

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_leads.db'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
