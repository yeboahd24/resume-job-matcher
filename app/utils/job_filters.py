"""
Job filtering utilities
"""

from typing import List, Dict, Any, Optional, Set, Tuple
import re
import logging

logger = logging.getLogger(__name__)


def filter_jobs_by_location(
    jobs: List[Dict[str, Any]], 
    locations: Optional[List[str]] = None,
    remote_only: bool = False
) -> List[Dict[str, Any]]:
    """
    Filter jobs by location
    
    Args:
        jobs: List of job dictionaries
        locations: List of preferred locations (cities, states, countries)
        remote_only: Whether to only include remote jobs
        
    Returns:
        Filtered list of jobs
    """
    if not locations and not remote_only:
        return jobs
    
    filtered_jobs = []
    
    for job in jobs:
        # Handle remote_only filter
        if remote_only:
            remote_allowed = job.get('remote_allowed')
            # Skip if remote is explicitly not allowed
            if remote_allowed is False:
                continue
            
            # If remote status is unknown but location contains remote keywords, consider it remote
            if remote_allowed is None:
                job_location = job.get('location', '').lower()
                if not any(keyword in job_location for keyword in ['remote', 'work from home', 'wfh', 'virtual']):
                    continue
        
        # If no specific locations are provided, include the job (already passed remote filter)
        if not locations:
            filtered_jobs.append(job)
            continue
        
        # Check if job location matches any preferred location
        job_location = job.get('location', '').lower()
        
        # Normalize locations for comparison
        normalized_job_location = _normalize_location(job_location)
        normalized_preferred_locations = [_normalize_location(loc) for loc in locations]
        
        # Check for location match
        if any(preferred_loc in normalized_job_location for preferred_loc in normalized_preferred_locations):
            filtered_jobs.append(job)
            continue
        
        # Check for remote with location preference
        if job.get('remote_allowed') and any('remote' in loc.lower() for loc in locations):
            filtered_jobs.append(job)
            continue
    
    return filtered_jobs


def filter_jobs_by_type(
    jobs: List[Dict[str, Any]], 
    job_types: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Filter jobs by job type
    
    Args:
        jobs: List of job dictionaries
        job_types: List of preferred job types (e.g., "Full-time", "Contract")
        
    Returns:
        Filtered list of jobs
    """
    if not job_types:
        return jobs
    
    # Normalize job types for comparison
    normalized_job_types = [job_type.lower().strip() for job_type in job_types]
    
    filtered_jobs = []
    
    for job in jobs:
        job_type = job.get('job_type')
        
        # If job type is not specified, check description for job type keywords
        if not job_type:
            job_description = job.get('description', '').lower()
            job_title = job.get('title', '').lower()
            
            # Extract potential job types from description and title
            extracted_types = _extract_job_types_from_text(job_description + " " + job_title)
            
            # Check if any extracted job type matches preferred types
            if any(extracted_type in normalized_job_types for extracted_type in extracted_types):
                filtered_jobs.append(job)
                continue
        else:
            # If job type is specified, check if it matches any preferred type
            if job_type.lower().strip() in normalized_job_types:
                filtered_jobs.append(job)
                continue
            
            # Check for partial matches (e.g., "Full-time" matches "Full")
            if any(job_type_pref in job_type.lower() for job_type_pref in normalized_job_types):
                filtered_jobs.append(job)
                continue
    
    return filtered_jobs


def _normalize_location(location: str) -> str:
    """
    Normalize location string for comparison
    
    Args:
        location: Location string
        
    Returns:
        Normalized location string
    """
    # Convert to lowercase
    normalized = location.lower()
    
    # Remove common prefixes/suffixes
    prefixes_suffixes = [
        'greater ', ' area', ' region', ' metropolitan', ' metro', ' county',
        ' city', ' district', ' province', ' state', ' territory'
    ]
    for ps in prefixes_suffixes:
        normalized = normalized.replace(ps, '')
    
    # Remove punctuation and extra whitespace
    normalized = re.sub(r'[^\w\s]', ' ', normalized)
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    
    # Handle common abbreviations
    state_abbr = {
        'al': 'alabama', 'ak': 'alaska', 'az': 'arizona', 'ar': 'arkansas',
        'ca': 'california', 'co': 'colorado', 'ct': 'connecticut', 'de': 'delaware',
        'fl': 'florida', 'ga': 'georgia', 'hi': 'hawaii', 'id': 'idaho',
        'il': 'illinois', 'in': 'indiana', 'ia': 'iowa', 'ks': 'kansas',
        'ky': 'kentucky', 'la': 'louisiana', 'me': 'maine', 'md': 'maryland',
        'ma': 'massachusetts', 'mi': 'michigan', 'mn': 'minnesota', 'ms': 'mississippi',
        'mo': 'missouri', 'mt': 'montana', 'ne': 'nebraska', 'nv': 'nevada',
        'nh': 'new hampshire', 'nj': 'new jersey', 'nm': 'new mexico', 'ny': 'new york',
        'nc': 'north carolina', 'nd': 'north dakota', 'oh': 'ohio', 'ok': 'oklahoma',
        'or': 'oregon', 'pa': 'pennsylvania', 'ri': 'rhode island', 'sc': 'south carolina',
        'sd': 'south dakota', 'tn': 'tennessee', 'tx': 'texas', 'ut': 'utah',
        'vt': 'vermont', 'va': 'virginia', 'wa': 'washington', 'wv': 'west virginia',
        'wi': 'wisconsin', 'wy': 'wyoming', 'dc': 'washington dc'
    }
    
    # Replace state abbreviations with full names
    words = normalized.split()
    for i, word in enumerate(words):
        if word in state_abbr:
            words[i] = state_abbr[word]
    
    normalized = ' '.join(words)
    
    return normalized


def _extract_job_types_from_text(text: str) -> Set[str]:
    """
    Extract job types from text
    
    Args:
        text: Text to extract job types from
        
    Returns:
        Set of extracted job types
    """
    job_type_keywords = {
        'full-time': ['full time', 'full-time', 'permanent', 'regular'],
        'part-time': ['part time', 'part-time'],
        'contract': ['contract', 'contractor', 'temporary', 'temp'],
        'freelance': ['freelance', 'freelancer'],
        'internship': ['intern', 'internship', 'co-op', 'coop'],
        'remote': ['remote', 'work from home', 'wfh', 'virtual', 'telecommute'],
        'hybrid': ['hybrid', 'flexible', 'partially remote']
    }
    
    extracted_types = set()
    
    for job_type, keywords in job_type_keywords.items():
        if any(keyword in text for keyword in keywords):
            extracted_types.add(job_type)
    
    return extracted_types


def apply_all_filters(
    jobs: List[Dict[str, Any]],
    locations: Optional[List[str]] = None,
    job_types: Optional[List[str]] = None,
    min_salary: Optional[int] = None,
    max_salary: Optional[int] = None,
    remote_only: bool = False
) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    """
    Apply all job filters
    
    Args:
        jobs: List of job dictionaries
        locations: List of preferred locations
        job_types: List of preferred job types
        min_salary: Minimum salary requirement
        max_salary: Maximum salary consideration
        remote_only: Whether to only include remote jobs
        
    Returns:
        Tuple of (filtered jobs list, filter stats)
    """
    from app.utils.salary_parser import filter_jobs_by_salary
    
    original_count = len(jobs)
    filter_stats = {
        'original_count': original_count,
        'after_location_filter': 0,
        'after_job_type_filter': 0,
        'after_salary_filter': 0,
        'final_count': 0
    }
    
    # Apply location filter
    if locations or remote_only:
        jobs = filter_jobs_by_location(jobs, locations, remote_only)
        filter_stats['after_location_filter'] = len(jobs)
    else:
        filter_stats['after_location_filter'] = original_count
    
    # Apply job type filter
    if job_types:
        jobs = filter_jobs_by_type(jobs, job_types)
        filter_stats['after_job_type_filter'] = len(jobs)
    else:
        filter_stats['after_job_type_filter'] = len(jobs)
    
    # Apply salary filter
    if min_salary is not None or max_salary is not None:
        jobs = filter_jobs_by_salary(jobs, min_salary, max_salary)
        filter_stats['after_salary_filter'] = len(jobs)
    else:
        filter_stats['after_salary_filter'] = len(jobs)
    
    filter_stats['final_count'] = len(jobs)
    
    return jobs, filter_stats