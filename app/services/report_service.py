"""
PDF Report Generation Service
"""

import os
import io
import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pathlib import Path

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white, grey
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics import renderPDF
from jinja2 import Environment, FileSystemLoader

from app.core.config import settings
from app.models.report import (
    ReportData, ReportRequest, ReportResponse, ReportMetadata,
    ReportFormat, ReportTheme, ReportSection
)

logger = logging.getLogger(__name__)


class ReportService:
    """Service for generating PDF and HTML reports"""
    
    def __init__(self):
        self.reports_dir = Path("data/reports")
        self.templates_dir = Path("app/templates/reports")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=True
        )
        
        # Theme configurations
        self.themes = {
            ReportTheme.PROFESSIONAL: {
                "primary_color": HexColor("#2c3e50"),
                "secondary_color": HexColor("#3498db"),
                "accent_color": HexColor("#e74c3c"),
                "text_color": black,
                "background_color": white,
                "font_family": "Helvetica"
            },
            ReportTheme.MODERN: {
                "primary_color": HexColor("#34495e"),
                "secondary_color": HexColor("#9b59b6"),
                "accent_color": HexColor("#f39c12"),
                "text_color": black,
                "background_color": white,
                "font_family": "Helvetica"
            },
            ReportTheme.MINIMAL: {
                "primary_color": HexColor("#2c3e50"),
                "secondary_color": HexColor("#95a5a6"),
                "accent_color": HexColor("#e67e22"),
                "text_color": black,
                "background_color": white,
                "font_family": "Helvetica"
            },
            ReportTheme.COLORFUL: {
                "primary_color": HexColor("#e74c3c"),
                "secondary_color": HexColor("#3498db"),
                "accent_color": HexColor("#2ecc71"),
                "text_color": black,
                "background_color": white,
                "font_family": "Helvetica"
            }
        }
    
    def generate_report(
        self,
        report_data: ReportData,
        report_request: ReportRequest
    ) -> ReportResponse:
        """Generate a report based on the request"""
        try:
            report_id = str(uuid.uuid4())
            
            if report_request.format == ReportFormat.PDF:
                file_path, file_size = self._generate_pdf_report(
                    report_data, report_request, report_id
                )
            else:
                file_path, file_size = self._generate_html_report(
                    report_data, report_request, report_id
                )
            
            # Create download URL (in production, this would be a signed URL)
            download_url = f"/api/v1/reports/{report_id}/download"
            
            # Set expiration (7 days for free users, 30 days for pro users)
            expires_days = 30 if report_data.subscription_tier in ["pro", "enterprise"] else 7
            expires_at = datetime.utcnow() + timedelta(days=expires_days)
            
            return ReportResponse(
                report_id=report_id,
                status="completed",
                download_url=download_url,
                file_size_bytes=file_size,
                expires_at=expires_at,
                generated_at=datetime.utcnow(),
                format=report_request.format,
                theme=report_request.theme
            )
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            raise ValueError(f"Failed to generate report: {str(e)}")
    
    def _generate_pdf_report(
        self,
        report_data: ReportData,
        report_request: ReportRequest,
        report_id: str
    ) -> tuple[str, int]:
        """Generate PDF report"""
        filename = f"job_match_report_{report_id}.pdf"
        file_path = self.reports_dir / filename
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(file_path),
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Get theme colors
        theme = self.themes[report_request.theme]
        
        # Build story (content)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=theme["primary_color"],
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=theme["primary_color"],
            borderWidth=1,
            borderColor=theme["secondary_color"],
            borderPadding=5
        )
        
        # Title
        title = report_request.custom_title or "Job Matching Report"
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 20))
        
        # Generate sections based on request
        for section in report_request.sections:
            if section == ReportSection.SUMMARY:
                story.extend(self._create_summary_section(report_data, styles, theme))
            elif section == ReportSection.MATCHED_JOBS:
                story.extend(self._create_jobs_section(report_data, styles, theme))
            elif section == ReportSection.SKILLS_ANALYSIS:
                story.extend(self._create_skills_section(report_data, styles, theme))
            elif section == ReportSection.RECOMMENDATIONS:
                story.extend(self._create_recommendations_section(report_data, styles, theme))
            elif section == ReportSection.SEARCH_QUERIES:
                story.extend(self._create_queries_section(report_data, styles, theme))
            elif section == ReportSection.STATISTICS:
                story.extend(self._create_statistics_section(report_data, styles, theme))
        
        # Footer
        story.append(PageBreak())
        story.extend(self._create_footer_section(report_data, styles, theme))
        
        # Build PDF
        doc.build(story)
        
        # Get file size
        file_size = file_path.stat().st_size
        
        return str(file_path), file_size
    
    def _create_summary_section(self, data: ReportData, styles, theme) -> List:
        """Create summary section"""
        content = []
        
        heading_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=theme["primary_color"]
        )
        
        content.append(Paragraph("Executive Summary", heading_style))
        
        # Summary table
        summary_data = [
            ["Resume File", data.resume_filename],
            ["Total Jobs Found", str(data.total_jobs_found)],
            ["Matched Jobs", str(len(data.matched_jobs))],
            ["Processing Time", f"{data.processing_time_seconds:.2f}s" if data.processing_time_seconds else "N/A"],
            ["Generated", data.generated_at.strftime("%Y-%m-%d %H:%M:%S")],
        ]
        
        if data.user_name:
            summary_data.insert(0, ["User", data.user_name])
        
        summary_table = Table(summary_data, colWidths=[2*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), theme["secondary_color"]),
            ('TEXTCOLOR', (0, 0), (0, -1), white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), HexColor("#f8f9fa")),
            ('GRID', (0, 0), (-1, -1), 1, HexColor("#dee2e6"))
        ]))
        
        content.append(summary_table)
        content.append(Spacer(1, 20))
        
        return content
    
    def _create_jobs_section(self, data: ReportData, styles, theme) -> List:
        """Create matched jobs section"""
        content = []
        
        heading_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=theme["primary_color"]
        )
        
        content.append(Paragraph("Matched Jobs", heading_style))
        
        if not data.matched_jobs:
            content.append(Paragraph("No matching jobs found.", styles['Normal']))
            content.append(Spacer(1, 20))
            return content
        
        # Sort jobs by similarity score
        sorted_jobs = sorted(data.matched_jobs, key=lambda x: x.similarity_score, reverse=True)
        
        for i, job in enumerate(sorted_jobs[:10], 1):  # Limit to top 10 jobs
            job_content = []
            
            # Job title and company
            job_title = f"{i}. {job.title} at {job.company}"
            job_content.append(Paragraph(job_title, styles['Heading3']))
            
            # Job details table
            job_data = [
                ["Location", job.location],
                ["Similarity Score", f"{job.similarity_score:.1%}"],
                ["Job Type", job.job_type or "Not specified"],
                ["Remote Allowed", "Yes" if job.remote_allowed else "No" if job.remote_allowed is not None else "Not specified"],
            ]
            
            if job.salary_range:
                job_data.append(["Salary Range", job.salary_range])
            
            if job.posted_date:
                job_data.append(["Posted Date", job.posted_date.strftime("%Y-%m-%d")])
            
            job_table = Table(job_data, colWidths=[1.5*inch, 3.5*inch])
            job_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), HexColor("#f8f9fa")),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, HexColor("#dee2e6"))
            ]))
            
            job_content.append(job_table)
            
            # Job description (truncated)
            description = job.description[:300] + "..." if len(job.description) > 300 else job.description
            job_content.append(Paragraph(f"<b>Description:</b> {description}", styles['Normal']))
            
            # Job URL
            job_content.append(Paragraph(f"<b>Apply:</b> <link href='{job.url}'>{job.url}</link>", styles['Normal']))
            
            content.append(KeepTogether(job_content))
            content.append(Spacer(1, 15))
        
        return content
    
    def _create_skills_section(self, data: ReportData, styles, theme) -> List:
        """Create skills analysis section"""
        content = []
        
        heading_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=theme["primary_color"]
        )
        
        content.append(Paragraph("Skills Analysis", heading_style))
        
        # Extracted skills
        if data.extracted_skills:
            content.append(Paragraph("<b>Skills Found in Your Resume:</b>", styles['Heading4']))
            skills_text = ", ".join(data.extracted_skills)
            content.append(Paragraph(skills_text, styles['Normal']))
            content.append(Spacer(1, 10))
        
        # Top skills from job matches
        if data.top_skills:
            content.append(Paragraph("<b>Most In-Demand Skills:</b>", styles['Heading4']))
            
            skills_data = [["Skill", "Frequency", "Relevance"]]
            for skill_info in data.top_skills[:10]:
                skills_data.append([
                    skill_info.get("skill", ""),
                    str(skill_info.get("frequency", 0)),
                    f"{skill_info.get('relevance', 0):.1%}"
                ])
            
            skills_table = Table(skills_data, colWidths=[2*inch, 1*inch, 1*inch])
            skills_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), theme["secondary_color"]),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('BACKGROUND', (0, 1), (-1, -1), HexColor("#f8f9fa")),
                ('GRID', (0, 0), (-1, -1), 1, HexColor("#dee2e6"))
            ]))
            
            content.append(skills_table)
            content.append(Spacer(1, 10))
        
        # Skill gaps
        if data.skill_gaps:
            content.append(Paragraph("<b>Skill Gaps to Consider:</b>", styles['Heading4']))
            gaps_text = ", ".join(data.skill_gaps)
            content.append(Paragraph(gaps_text, styles['Normal']))
            content.append(Spacer(1, 10))
        
        content.append(Spacer(1, 20))
        return content
    
    def _create_recommendations_section(self, data: ReportData, styles, theme) -> List:
        """Create recommendations section"""
        content = []
        
        heading_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=theme["primary_color"]
        )
        
        content.append(Paragraph("Recommendations", heading_style))
        
        if data.recommendations:
            for i, recommendation in enumerate(data.recommendations, 1):
                content.append(Paragraph(f"{i}. {recommendation}", styles['Normal']))
                content.append(Spacer(1, 5))
        
        if data.suggested_skills:
            content.append(Paragraph("<b>Suggested Skills to Learn:</b>", styles['Heading4']))
            skills_text = ", ".join(data.suggested_skills)
            content.append(Paragraph(skills_text, styles['Normal']))
            content.append(Spacer(1, 10))
        
        if data.career_tips:
            content.append(Paragraph("<b>Career Tips:</b>", styles['Heading4']))
            for tip in data.career_tips:
                content.append(Paragraph(f"• {tip}", styles['Normal']))
                content.append(Spacer(1, 3))
        
        content.append(Spacer(1, 20))
        return content
    
    def _create_queries_section(self, data: ReportData, styles, theme) -> List:
        """Create search queries section"""
        content = []
        
        heading_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=theme["primary_color"]
        )
        
        content.append(Paragraph("Search Queries Used", heading_style))
        
        if data.search_queries:
            for i, query in enumerate(data.search_queries, 1):
                content.append(Paragraph(f"{i}. {query}", styles['Normal']))
                content.append(Spacer(1, 5))
        else:
            content.append(Paragraph("No search queries available.", styles['Normal']))
        
        content.append(Spacer(1, 20))
        return content
    
    def _create_statistics_section(self, data: ReportData, styles, theme) -> List:
        """Create statistics section"""
        content = []
        
        heading_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=theme["primary_color"]
        )
        
        content.append(Paragraph("Statistics", heading_style))
        
        # Basic statistics
        stats_data = [
            ["Metric", "Value"],
            ["Total Jobs Analyzed", str(data.total_jobs_found)],
            ["Jobs Matched", str(len(data.matched_jobs))],
            ["Match Rate", f"{(len(data.matched_jobs) / max(data.total_jobs_found, 1)) * 100:.1f}%"],
            ["Average Similarity Score", f"{sum(job.similarity_score for job in data.matched_jobs) / max(len(data.matched_jobs), 1):.1%}"],
        ]
        
        stats_table = Table(stats_data, colWidths=[2.5*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), theme["secondary_color"]),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor("#f8f9fa")),
            ('GRID', (0, 0), (-1, -1), 1, HexColor("#dee2e6"))
        ]))
        
        content.append(stats_table)
        content.append(Spacer(1, 20))
        
        return content
    
    def _create_footer_section(self, data: ReportData, styles, theme) -> List:
        """Create footer section"""
        content = []
        
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=grey,
            alignment=TA_CENTER
        )
        
        content.append(Spacer(1, 50))
        content.append(Paragraph("Generated by Resume Job Matcher", footer_style))
        content.append(Paragraph(f"Report ID: {uuid.uuid4()}", footer_style))
        content.append(Paragraph(f"Generated on: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}", footer_style))
        
        return content
    
    def _generate_html_report(
        self,
        report_data: ReportData,
        report_request: ReportRequest,
        report_id: str
    ) -> tuple[str, int]:
        """Generate HTML report"""
        # This would use Jinja2 templates to generate HTML
        # For now, we'll create a simple HTML structure
        filename = f"job_match_report_{report_id}.html"
        file_path = self.reports_dir / filename
        
        html_content = self._create_html_content(report_data, report_request)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        file_size = file_path.stat().st_size
        return str(file_path), file_size
    
    def _create_html_content(self, data: ReportData, request: ReportRequest) -> str:
        """Create HTML content for the report"""
        # Simple HTML template - in production, use Jinja2 templates
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Job Matching Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .section {{ margin-bottom: 30px; }}
                .job {{ border: 1px solid #ddd; padding: 15px; margin-bottom: 15px; }}
                .similarity {{ color: #e74c3c; font-weight: bold; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{request.custom_title or 'Job Matching Report'}</h1>
                <p>Generated on: {data.generated_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="section">
                <h2>Summary</h2>
                <table>
                    <tr><td>Resume File</td><td>{data.resume_filename}</td></tr>
                    <tr><td>Total Jobs Found</td><td>{data.total_jobs_found}</td></tr>
                    <tr><td>Matched Jobs</td><td>{len(data.matched_jobs)}</td></tr>
                    <tr><td>Processing Time</td><td>{data.processing_time_seconds:.2f}s</td></tr>
                </table>
            </div>
            
            <div class="section">
                <h2>Matched Jobs</h2>
                {''.join([f'''
                <div class="job">
                    <h3>{job.title} at {job.company}</h3>
                    <p><strong>Location:</strong> {job.location}</p>
                    <p><strong>Similarity:</strong> <span class="similarity">{job.similarity_score:.1%}</span></p>
                    <p><strong>Description:</strong> {job.description[:200]}...</p>
                    <p><strong>Apply:</strong> <a href="{job.url}" target="_blank">{job.url}</a></p>
                </div>
                ''' for job in data.matched_jobs[:5]])}
            </div>
            
            <div class="section">
                <h2>Skills Analysis</h2>
                <p><strong>Skills found in your resume:</strong> {', '.join(data.extracted_skills)}</p>
            </div>
        </body>
        </html>
        """
        return html
    
    def get_report_file_path(self, report_id: str) -> Optional[Path]:
        """Get the file path for a report"""
        # Look for both PDF and HTML files
        pdf_path = self.reports_dir / f"job_match_report_{report_id}.pdf"
        html_path = self.reports_dir / f"job_match_report_{report_id}.html"
        
        if pdf_path.exists():
            return pdf_path
        elif html_path.exists():
            return html_path
        
        return None
    
    def cleanup_expired_reports(self):
        """Clean up expired report files"""
        try:
            current_time = datetime.utcnow()
            for file_path in self.reports_dir.glob("job_match_report_*.pdf"):
                # Check file age (default 7 days)
                file_age = current_time - datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_age.days > 7:
                    file_path.unlink()
                    logger.info(f"Deleted expired report: {file_path.name}")
            
            for file_path in self.reports_dir.glob("job_match_report_*.html"):
                file_age = current_time - datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_age.days > 7:
                    file_path.unlink()
                    logger.info(f"Deleted expired report: {file_path.name}")
                    
        except Exception as e:
            logger.error(f"Error cleaning up expired reports: {str(e)}")