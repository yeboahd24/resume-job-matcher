"""
Job scraping service
"""

import requests
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import logging
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)


class JobScraperService:
    """
    Service for scraping job listings from various sources
    """
    
    def __init__(self):
        self.timeout = settings.JOB_SCRAPING_TIMEOUT
        self.use_mock = settings.USE_MOCK_JOBS
        
    async def search_jobs(self, query: str, location: str = "", limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for jobs based on query and location
        
        Args:
            query: Search query (skills, job title, etc.)
            location: Location filter
            limit: Maximum number of jobs to return
            
        Returns:
            List of job dictionaries
        """
        if self.use_mock:
            return self._get_mock_jobs(query, location, limit)
        else:
            # In production, implement real job scraping or API calls
            return await self._scrape_indeed_jobs(query, location, limit)
    
    def _get_mock_jobs(self, query: str, location: str = "", limit: int = 5) -> List[Dict[str, Any]]:
        """
        Generate mock job listings for demo purposes
        
        Args:
            query: Search query
            location: Location filter
            limit: Number of jobs to generate
            
        Returns:
            List of mock job dictionaries
        """
        companies = [
            "Tech Corp", "Innovation Labs", "Digital Solutions", "StartupXYZ", 
            "Enterprise Inc", "Future Systems", "Cloud Dynamics", "Data Insights",
            "AI Innovations", "Web Solutions", "Mobile First", "Quantum Labs"
        ]
        
        locations = [
            "San Francisco, CA", "New York, NY", "Austin, TX", "Seattle, WA",
            "Chicago, IL", "Boston, MA", "Denver, CO", "Atlanta, GA",
            "Los Angeles, CA", "Portland, OR", "Remote", "Hybrid"
        ]
        
        job_types = [
            "Software Engineer", "Senior Developer", "Full Stack Developer",
            "Backend Engineer", "Frontend Developer", "DevOps Engineer",
            "Data Scientist", "Machine Learning Engineer", "Product Manager",
            "Technical Lead", "Principal Engineer", "Staff Engineer"
        ]
        
        mock_jobs = []
        
        for i in range(min(limit, 12)):  # Generate up to 12 different jobs
            company = companies[i % len(companies)]
            job_location = location if location else locations[i % len(locations)]
            job_type = job_types[i % len(job_types)]
            
            # Create job title that incorporates the query
            if query.lower() in job_type.lower():
                title = f"{job_type}"
            else:
                title = f"{job_type} - {query.title()}"
            
            # Generate description
            description = self._generate_job_description(query, job_type, company)
            
            job = {
                'title': title,
                'company': company,
                'location': job_location,
                'description': description,
                'url': f'https://example.com/jobs/{company.lower().replace(" ", "-")}-{i+1}',
                'posted_date': datetime.utcnow().isoformat(),
                'job_type': 'Full-time',
                'remote_allowed': 'Remote' in job_location or 'Hybrid' in job_location,
                'salary_range': self._generate_salary_range(job_type)
            }
            
            mock_jobs.append(job)
        
        return mock_jobs[:limit]
    
    def _generate_job_description(self, query: str, job_type: str, company: str) -> str:
        """Generate a realistic job description"""
        base_descriptions = {
            "Software Engineer": f"We are looking for a skilled software engineer with experience in {query}. "
                               f"Join our dynamic team at {company} and work on cutting-edge projects that impact millions of users.",
            
            "Senior Developer": f"Senior developer position requiring expertise in {query} and related technologies. "
                              f"At {company}, you'll lead technical initiatives and mentor junior developers.",
            
            "Full Stack Developer": f"Full stack developer with strong {query} skills needed for our growing team. "
                                  f"{company} offers great benefits and growth opportunities in a collaborative environment.",
            
            "Data Scientist": f"Data scientist role focusing on {query} and machine learning applications. "
                            f"Work with large datasets and build predictive models at {company}.",
            
            "DevOps Engineer": f"DevOps engineer position requiring knowledge of {query} and cloud infrastructure. "
                             f"Help scale our systems and improve deployment processes at {company}."
        }
        
        base_desc = base_descriptions.get(job_type, 
            f"Exciting opportunity for a {job_type} with {query} experience at {company}. "
            f"Join our innovative team and make a real impact.")
        
        additional_info = [
            f"\n\nKey Responsibilities:",
            f"• Develop and maintain applications using {query}",
            f"• Collaborate with cross-functional teams",
            f"• Participate in code reviews and technical discussions",
            f"• Contribute to architectural decisions",
            f"\nRequirements:",
            f"• Strong experience with {query}",
            f"• Bachelor's degree in Computer Science or related field",
            f"• Excellent problem-solving skills",
            f"• Strong communication abilities",
            f"\nBenefits:",
            f"• Competitive salary and equity",
            f"• Health, dental, and vision insurance",
            f"• Flexible work arrangements",
            f"• Professional development opportunities"
        ]
        
        return base_desc + "".join(additional_info)
    
    def _generate_salary_range(self, job_type: str) -> str:
        """Generate realistic salary range based on job type"""
        salary_ranges = {
            "Software Engineer": "$90,000 - $130,000",
            "Senior Developer": "$120,000 - $170,000",
            "Full Stack Developer": "$95,000 - $140,000",
            "Principal Engineer": "$160,000 - $220,000",
            "Staff Engineer": "$180,000 - $250,000",
            "Data Scientist": "$110,000 - $160,000",
            "Machine Learning Engineer": "$130,000 - $180,000",
            "DevOps Engineer": "$100,000 - $150,000",
            "Product Manager": "$120,000 - $170,000",
            "Technical Lead": "$140,000 - $190,000"
        }
        
        return salary_ranges.get(job_type, "$80,000 - $120,000")
    
    async def _scrape_indeed_jobs(self, query: str, location: str = "", limit: int = 5) -> List[Dict[str, Any]]:
        """
        Scrape jobs from Indeed (for production use with proper API)
        
        Note: This is a placeholder implementation. In production, you should:
        1. Use official APIs (Indeed API, LinkedIn API, etc.)
        2. Respect rate limits and terms of service
        3. Handle errors and retries properly
        """
        logger.warning("Real job scraping not implemented. Using mock data instead.")
        return self._get_mock_jobs(query, location, limit)
    
    async def scrape_multiple_sources(self, queries: List[str], location: str = "") -> List[Dict[str, Any]]:
        """
        Scrape jobs from multiple sources concurrently
        
        Args:
            queries: List of search queries
            location: Location filter
            
        Returns:
            Combined list of jobs from all sources
        """
        all_jobs = []
        
        # Create tasks for concurrent scraping
        tasks = []
        for query in queries:
            task = self.search_jobs(query, location, settings.MAX_JOBS_PER_SKILL)
            tasks.append(task)
        
        # Execute all tasks concurrently
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Job scraping failed: {result}")
                    continue
                
                if isinstance(result, list):
                    all_jobs.extend(result)
        
        except Exception as e:
            logger.error(f"Error in concurrent job scraping: {e}")
        
        # Remove duplicates based on title and company
        unique_jobs = []
        seen = set()
        
        for job in all_jobs:
            job_key = (job.get('title', ''), job.get('company', ''))
            if job_key not in seen:
                seen.add(job_key)
                unique_jobs.append(job)
        
        return unique_jobs