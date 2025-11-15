from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import os
from typing import Dict

class AuditReportGenerator:
    """Generate professional PDF reports for business listings audits"""
    
    def __init__(self, output_dir: str = 'reports'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a365d'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2d3748'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Score style
        self.styles.add(ParagraphStyle(
            name='ScoreStyle',
            parent=self.styles['Normal'],
            fontSize=48,
            textColor=colors.HexColor('#2b6cb0'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Issue style
        self.styles.add(ParagraphStyle(
            name='IssueStyle',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#c53030'),
            leftIndent=20,
            spaceAfter=6
        ))
        
        # Recommendation style
        self.styles.add(ParagraphStyle(
            name='RecommendationStyle',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#2f855a'),
            leftIndent=20,
            spaceAfter=6
        ))
    
    def generate_report(self, lead_data: Dict, audit_data: Dict, 
                       filename: str = None) -> str:
        """
        Generate a comprehensive audit report
        
        Args:
            lead_data: Dictionary containing lead information
            audit_data: Dictionary containing audit results
            filename: Optional custom filename
            
        Returns:
            Path to the generated PDF file
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            business_name = lead_data.get('business_name', 'Business').replace(' ', '_')
            filename = f"{business_name}_Audit_{timestamp}.pdf"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Build content
        story = []
        
        # Header
        story.extend(self._build_header(lead_data))
        
        # Executive Summary
        story.extend(self._build_executive_summary(audit_data))
        
        # Overall Score
        story.extend(self._build_score_section(audit_data))
        
        # Platform Details
        story.extend(self._build_platform_details(audit_data))
        
        # Issues and Recommendations
        story.extend(self._build_issues_recommendations(audit_data))
        
        # Call to Action
        story.extend(self._build_cta())
        
        # Build PDF
        doc.build(story)
        
        return filepath
    
    def _build_header(self, lead_data: Dict) -> list:
        """Build report header"""
        elements = []
        
        # Title
        title = Paragraph(
            "Business Listings Audit Report",
            self.styles['CustomTitle']
        )
        elements.append(title)
        elements.append(Spacer(1, 0.2*inch))
        
        # Business information
        business_info = f"""
        <b>Business:</b> {lead_data.get('business_name', 'N/A')}<br/>
        <b>Contact:</b> {lead_data.get('contact_name', 'N/A')}<br/>
        <b>Location:</b> {lead_data.get('zip_code', 'N/A')}<br/>
        <b>Report Date:</b> {datetime.now().strftime('%B %d, %Y')}
        """
        
        info_para = Paragraph(business_info, self.styles['Normal'])
        elements.append(info_para)
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _build_executive_summary(self, audit_data: Dict) -> list:
        """Build executive summary section"""
        elements = []
        
        subtitle = Paragraph("Executive Summary", self.styles['CustomSubtitle'])
        elements.append(subtitle)
        
        summary_text = f"""
        We conducted a comprehensive audit of your business's online presence across 
        major platforms including Google My Business, Yelp, and Facebook. This report 
        identifies critical issues affecting your local visibility and provides 
        actionable recommendations to improve your online presence.
        """
        
        summary_para = Paragraph(summary_text, self.styles['Normal'])
        elements.append(summary_para)
        elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _build_score_section(self, audit_data: Dict) -> list:
        """Build overall score section"""
        elements = []
        
        score = audit_data.get('overall_score', 0)
        
        # Score display
        score_text = f"{score}/100"
        score_para = Paragraph(score_text, self.styles['ScoreStyle'])
        elements.append(score_para)
        
        # Score interpretation
        if score >= 80:
            interpretation = "Excellent! Your online presence is strong."
            color = colors.HexColor('#2f855a')
        elif score >= 60:
            interpretation = "Good, but there's room for improvement."
            color = colors.HexColor('#d69e2e')
        elif score >= 40:
            interpretation = "Fair. Several issues need attention."
            color = colors.HexColor('#dd6b20')
        else:
            interpretation = "Critical. Immediate action required."
            color = colors.HexColor('#c53030')
        
        interp_style = ParagraphStyle(
            'InterpStyle',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=color,
            alignment=TA_CENTER,
            spaceAfter=20
        )
        
        interp_para = Paragraph(interpretation, interp_style)
        elements.append(interp_para)
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _build_platform_details(self, audit_data: Dict) -> list:
        """Build platform-by-platform details"""
        elements = []
        
        subtitle = Paragraph("Platform Analysis", self.styles['CustomSubtitle'])
        elements.append(subtitle)
        elements.append(Spacer(1, 0.1*inch))
        
        # Create table data
        table_data = [['Platform', 'Listed', 'Claimed', 'Photos', 'Reviews', 'Score']]
        
        for platform_name, platform_data in audit_data.get('platforms', {}).items():
            row = [
                platform_data.get('platform', platform_name),
                '✓' if platform_data.get('is_listed') else '✗',
                '✓' if platform_data.get('is_claimed') else '✗',
                '✓' if platform_data.get('has_photos') else '✗',
                str(platform_data.get('review_count', 0)),
                f"{platform_data.get('score', 0)}/100"
            ]
            table_data.append(row)
        
        # Create table
        table = Table(table_data, colWidths=[2*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2b6cb0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')])
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _build_issues_recommendations(self, audit_data: Dict) -> list:
        """Build issues and recommendations sections"""
        elements = []
        
        # Issues section
        issues = audit_data.get('issues', [])
        if issues:
            subtitle = Paragraph("Critical Issues Found", self.styles['CustomSubtitle'])
            elements.append(subtitle)
            
            for issue in issues[:10]:  # Limit to top 10 issues
                issue_para = Paragraph(f"• {issue}", self.styles['IssueStyle'])
                elements.append(issue_para)
            
            elements.append(Spacer(1, 0.2*inch))
        
        # Recommendations section
        recommendations = audit_data.get('recommendations', [])
        if recommendations:
            subtitle = Paragraph("Recommended Actions", self.styles['CustomSubtitle'])
            elements.append(subtitle)
            
            for i, rec in enumerate(recommendations[:10], 1):  # Limit to top 10
                rec_para = Paragraph(f"{i}. {rec}", self.styles['RecommendationStyle'])
                elements.append(rec_para)
            
            elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _build_cta(self) -> list:
        """Build call-to-action section"""
        elements = []
        
        # Separator line
        elements.append(Spacer(1, 0.2*inch))
        
        # CTA box
        cta_text = """
        <b>Ready to Fix These Issues?</b><br/><br/>
        Best Version Media specializes in helping local businesses improve their online 
        presence and reach more customers in their community. Our integrated marketing 
        solutions include:<br/><br/>
        • Professional Online Presence Management<br/>
        • Local Print Magazine Advertising<br/>
        • Digital Marketing Solutions<br/>
        • Community Engagement Strategies<br/><br/>
        <b>Schedule your free 15-minute consultation to learn how we can help!</b><br/><br/>
        Contact: info@bvm-castlehills.com | (555) 123-4567
        """
        
        cta_style = ParagraphStyle(
            'CTAStyle',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#1a365d'),
            borderColor=colors.HexColor('#2b6cb0'),
            borderWidth=2,
            borderPadding=15,
            backColor=colors.HexColor('#ebf8ff'),
            spaceAfter=20
        )
        
        cta_para = Paragraph(cta_text, cta_style)
        elements.append(cta_para)
        
        # Footer
        footer_text = """
        <i>This report was generated by Best Version Media's automated listings audit system. 
        Data is collected from public sources and may not reflect real-time changes.</i>
        """
        
        footer_style = ParagraphStyle(
            'FooterStyle',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        
        footer_para = Paragraph(footer_text, footer_style)
        elements.append(Spacer(1, 0.2*inch))
        elements.append(footer_para)
        
        return elements
    
    def generate_simple_report(self, business_name: str, score: int, 
                              issues: list, recommendations: list) -> str:
        """
        Generate a simplified report (for testing or quick generation)
        
        Args:
            business_name: Name of the business
            score: Overall score
            issues: List of issues
            recommendations: List of recommendations
            
        Returns:
            Path to generated PDF
        """
        lead_data = {
            'business_name': business_name,
            'contact_name': 'Business Owner',
            'zip_code': 'N/A'
        }
        
        audit_data = {
            'overall_score': score,
            'issues': issues,
            'recommendations': recommendations,
            'platforms': {}
        }
        
        return self.generate_report(lead_data, audit_data)
