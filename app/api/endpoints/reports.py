"""
PDF Report generation endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import logging
import asyncio
from pathlib import Path
from datetime import datetime

from app.auth.manager import current_active_user
from app.models.user import User, SubscriptionTier
from app.models.report import (
    ReportRequest, ReportResponse, ReportData, ReportFormat, ReportTheme, ReportSection
)
from app.models.task import TaskStatusResponse
from app.services.report_service import ReportService
# Note: get_task_result function needs to be implemented in tasks service
# For now, we'll create a placeholder implementation
from app.db.database import get_async_session
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


def get_report_service() -> ReportService:
    """Dependency to get report service instance"""
    return ReportService()


async def get_task_result(task_id: str) -> Optional[TaskStatusResponse]:
    """
    Get task result from Celery
    This is a simplified implementation - in production, integrate with your Celery backend
    """
    try:
        from app.services.tasks import process_resume_and_match_jobs
        from celery.result import AsyncResult
        
        # Get task result from Celery
        result = AsyncResult(task_id, app=process_resume_and_match_jobs.app)
        
        if result.state == 'SUCCESS':
            # Mock successful result for testing
            return TaskStatusResponse(
                task_id=task_id,
                status="SUCCESS",
                result=[
                    # Mock job results
                    {
                        "title": "Senior Python Developer",
                        "company": "TechCorp Inc.",
                        "location": "San Francisco, CA",
                        "description": "We are looking for a Senior Python Developer with experience in FastAPI, Django, and machine learning. The ideal candidate will have 5+ years of experience building scalable web applications.",
                        "url": "https://example.com/jobs/senior-python-dev",
                        "similarity_score": 0.85,
                        "salary_range": "$120,000 - $160,000",
                        "job_type": "Full-time",
                        "remote_allowed": True
                    },
                    {
                        "title": "Machine Learning Engineer",
                        "company": "AI Innovations",
                        "location": "Remote",
                        "description": "Join our team to build cutting-edge ML models using Python, TensorFlow, and AWS. Experience with MLOps and data pipelines required.",
                        "url": "https://example.com/jobs/ml-engineer",
                        "similarity_score": 0.78,
                        "salary_range": "$130,000 - $170,000",
                        "job_type": "Full-time",
                        "remote_allowed": True
                    },
                    {
                        "title": "Full Stack Developer",
                        "company": "StartupXYZ",
                        "location": "New York, NY",
                        "description": "Looking for a full stack developer with Python/FastAPI backend and React frontend experience. Great opportunity to work with modern tech stack.",
                        "url": "https://example.com/jobs/fullstack-dev",
                        "similarity_score": 0.72,
                        "salary_range": "$100,000 - $140,000",
                        "job_type": "Full-time",
                        "remote_allowed": False
                    }
                ],
                completed_at=datetime.utcnow(),
                processing_time_seconds=15.5,
                metadata={
                    "resume_filename": "resume.txt",
                    "extracted_skills": ["Python", "FastAPI", "Machine Learning", "AWS", "Docker", "React", "PostgreSQL"],
                    "search_queries": ["Python Developer", "Machine Learning Engineer", "Full Stack Developer"],
                    "total_jobs_found": 25
                }
            )
        elif result.state == 'FAILURE':
            return TaskStatusResponse(
                task_id=task_id,
                status="FAILURE",
                error=str(result.result)
            )
        else:
            return TaskStatusResponse(
                task_id=task_id,
                status=result.state,
                progress=f"Task is {result.state.lower()}"
            )
            
    except Exception as e:
        logger.error(f"Error getting task result: {str(e)}")
        return None


@router.post("/generate", response_model=ReportResponse)
async def generate_report(
    report_request: ReportRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(current_active_user),
    report_service: ReportService = Depends(get_report_service),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Generate a PDF or HTML report for job matching results
    
    Requires Pro subscription or higher for PDF reports
    """
    try:
        # Check subscription permissions
        if report_request.format == ReportFormat.PDF:
            if user.subscription_tier not in [SubscriptionTier.PRO, SubscriptionTier.ENTERPRISE]:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail="PDF report generation requires Pro subscription or higher. Please upgrade your subscription."
                )
        
        # Get task result
        task_result = await get_task_result(report_request.task_id)
        if not task_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {report_request.task_id} not found or not completed"
            )
        
        if task_result.status != "SUCCESS":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Task {report_request.task_id} is not completed successfully. Status: {task_result.status}"
            )
        
        # Prepare report data
        report_data = await _prepare_report_data(
            task_result, user, report_request.task_id, session
        )
        
        # Generate report
        report_response = report_service.generate_report(report_data, report_request)
        
        # Schedule cleanup of old reports
        background_tasks.add_task(report_service.cleanup_expired_reports)
        
        logger.info(f"Generated {report_request.format} report for user {user.id}, task {report_request.task_id}")
        
        return report_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )


@router.get("/{report_id}/download")
async def download_report(
    report_id: str,
    user: User = Depends(current_active_user),
    report_service: ReportService = Depends(get_report_service)
):
    """
    Download a generated report
    """
    try:
        # Get report file path
        file_path = report_service.get_report_file_path(report_id)
        
        if not file_path or not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found or has expired"
            )
        
        # Determine content type based on file extension
        if file_path.suffix == '.pdf':
            media_type = 'application/pdf'
        elif file_path.suffix == '.html':
            media_type = 'text/html'
        else:
            media_type = 'application/octet-stream'
        
        logger.info(f"User {user.id} downloading report {report_id}")
        
        return FileResponse(
            path=str(file_path),
            filename=file_path.name,
            media_type=media_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading report {report_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to download report"
        )


@router.get("/formats")
async def get_available_formats(
    user: User = Depends(current_active_user)
):
    """
    Get available report formats based on user subscription
    """
    formats = ["html"]  # HTML is always available
    
    if user.subscription_tier in [SubscriptionTier.PRO, SubscriptionTier.ENTERPRISE]:
        formats.append("pdf")
    
    themes = ["professional", "modern", "minimal", "colorful"]
    
    sections = [
        "summary",
        "matched_jobs", 
        "skills_analysis",
        "recommendations",
        "search_queries",
        "statistics"
    ]
    
    return {
        "available_formats": formats,
        "available_themes": themes,
        "available_sections": sections,
        "subscription_tier": user.subscription_tier,
        "pdf_available": user.subscription_tier in [SubscriptionTier.PRO, SubscriptionTier.ENTERPRISE]
    }


@router.get("/templates")
async def get_report_templates():
    """
    Get available report templates and their descriptions
    """
    templates = {
        "professional": {
            "name": "Professional",
            "description": "Clean, business-oriented design with blue and gray color scheme",
            "best_for": "Corporate job applications, formal industries"
        },
        "modern": {
            "name": "Modern",
            "description": "Contemporary design with purple and orange accents",
            "best_for": "Tech companies, startups, creative industries"
        },
        "minimal": {
            "name": "Minimal",
            "description": "Simple, clean design with minimal colors",
            "best_for": "Any industry, focuses on content over design"
        },
        "colorful": {
            "name": "Colorful",
            "description": "Vibrant design with multiple accent colors",
            "best_for": "Creative industries, marketing, design roles"
        }
    }
    
    return {
        "templates": templates,
        "default_sections": [
            {
                "id": "summary",
                "name": "Executive Summary",
                "description": "Overview of the job matching results"
            },
            {
                "id": "matched_jobs",
                "name": "Matched Jobs",
                "description": "Detailed list of matching job opportunities"
            },
            {
                "id": "skills_analysis",
                "name": "Skills Analysis",
                "description": "Analysis of your skills vs. market demand"
            },
            {
                "id": "recommendations",
                "name": "Recommendations",
                "description": "Personalized career and skill recommendations"
            },
            {
                "id": "search_queries",
                "name": "Search Queries",
                "description": "Queries used to find matching jobs"
            },
            {
                "id": "statistics",
                "name": "Statistics",
                "description": "Detailed statistics about the job matching process"
            }
        ]
    }


async def _prepare_report_data(
    task_result: TaskStatusResponse,
    user: User,
    task_id: str,
    session: AsyncSession
) -> ReportData:
    """Prepare report data from task result and user info"""
    
    # Extract job matching results
    matched_jobs = task_result.result or []
    
    # Extract metadata
    metadata = task_result.metadata or {}
    
    # Prepare skills analysis
    extracted_skills = metadata.get("extracted_skills", [])
    search_queries = metadata.get("search_queries", [])
    
    # Generate insights and recommendations
    recommendations = _generate_recommendations(matched_jobs, extracted_skills, user)
    skill_gaps = _identify_skill_gaps(matched_jobs, extracted_skills)
    top_skills = _analyze_top_skills(matched_jobs)
    career_tips = _generate_career_tips(user.subscription_tier, len(matched_jobs))
    
    return ReportData(
        user_name=f"{user.first_name} {user.last_name}".strip() if user.first_name or user.last_name else None,
        user_email=user.email,
        subscription_tier=user.subscription_tier,
        generated_at=task_result.completed_at or task_result.started_at,
        resume_filename=metadata.get("resume_filename", "resume.txt"),
        extracted_skills=extracted_skills,
        matched_jobs=matched_jobs,
        total_jobs_found=metadata.get("total_jobs_found", len(matched_jobs)),
        search_queries=search_queries,
        processing_time_seconds=task_result.processing_time_seconds,
        top_skills=top_skills,
        skill_gaps=skill_gaps,
        recommendations=recommendations,
        suggested_skills=skill_gaps[:5],  # Top 5 skill gaps as suggestions
        career_tips=career_tips
    )


def _generate_recommendations(matched_jobs, extracted_skills, user) -> list[str]:
    """Generate personalized recommendations"""
    recommendations = []
    
    if not matched_jobs:
        recommendations.append("Consider broadening your search criteria or updating your resume with more relevant keywords.")
        recommendations.append("Review job descriptions in your field to identify commonly requested skills.")
    else:
        avg_similarity = sum(job.similarity_score for job in matched_jobs) / len(matched_jobs)
        
        if avg_similarity < 0.3:
            recommendations.append("Your current resume may benefit from optimization to better match job requirements.")
            recommendations.append("Consider adding more specific technical skills and industry keywords.")
        elif avg_similarity < 0.6:
            recommendations.append("You have good potential matches. Focus on tailoring your resume for specific roles.")
            recommendations.append("Highlight your most relevant experience and skills more prominently.")
        else:
            recommendations.append("Excellent job matching results! Your resume aligns well with market demands.")
            recommendations.append("Consider applying to the top-ranked positions as soon as possible.")
    
    # Subscription-based recommendations
    if user.subscription_tier == SubscriptionTier.FREE:
        recommendations.append("Upgrade to Pro for unlimited job matching and advanced filtering options.")
    
    return recommendations


def _identify_skill_gaps(matched_jobs, extracted_skills) -> list[str]:
    """Identify skills that appear in job descriptions but not in resume"""
    job_skills = set()
    
    # Extract skills from job descriptions (simplified)
    common_skills = [
        "Python", "JavaScript", "Java", "React", "Node.js", "SQL", "AWS", "Docker",
        "Kubernetes", "Git", "Agile", "Scrum", "Machine Learning", "Data Analysis",
        "Project Management", "Communication", "Leadership", "Problem Solving"
    ]
    
    for job in matched_jobs:
        description_lower = job.description.lower()
        for skill in common_skills:
            if skill.lower() in description_lower:
                job_skills.add(skill)
    
    # Find skills in jobs but not in resume
    resume_skills_lower = [skill.lower() for skill in extracted_skills]
    skill_gaps = [skill for skill in job_skills if skill.lower() not in resume_skills_lower]
    
    return list(skill_gaps)[:10]  # Return top 10 skill gaps


def _analyze_top_skills(matched_jobs) -> list[dict]:
    """Analyze most frequently mentioned skills in job matches"""
    skill_frequency = {}
    
    # Simplified skill extraction from job descriptions
    common_skills = [
        "Python", "JavaScript", "Java", "React", "Node.js", "SQL", "AWS", "Docker",
        "Kubernetes", "Git", "Agile", "Scrum", "Machine Learning", "Data Analysis"
    ]
    
    for job in matched_jobs:
        description_lower = job.description.lower()
        for skill in common_skills:
            if skill.lower() in description_lower:
                skill_frequency[skill] = skill_frequency.get(skill, 0) + 1
    
    # Convert to list of dicts with relevance scores
    top_skills = []
    total_jobs = len(matched_jobs)
    
    for skill, frequency in sorted(skill_frequency.items(), key=lambda x: x[1], reverse=True):
        relevance = frequency / total_jobs if total_jobs > 0 else 0
        top_skills.append({
            "skill": skill,
            "frequency": frequency,
            "relevance": relevance
        })
    
    return top_skills[:10]


def _generate_career_tips(subscription_tier, num_matches) -> list[str]:
    """Generate career tips based on user profile and results"""
    tips = [
        "Customize your resume for each application to improve match rates.",
        "Network with professionals in your target companies through LinkedIn.",
        "Keep your skills updated with the latest industry trends.",
        "Consider obtaining relevant certifications to stand out.",
        "Practice your interview skills with mock interviews."
    ]
    
    if subscription_tier == SubscriptionTier.FREE and num_matches > 3:
        tips.append("You're getting good results! Consider upgrading to Pro for unlimited matches.")
    
    if num_matches == 0:
        tips.append("Try using different keywords or expanding your location preferences.")
        tips.append("Consider roles that are one level below your target to build experience.")
    
    return tips[:5]