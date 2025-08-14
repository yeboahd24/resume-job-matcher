"""
Salary parsing utilities
"""

import re
from typing import Optional, Tuple, Dict, Any


def parse_salary_range(salary_range: Optional[str]) -> Tuple[Optional[int], Optional[int]]:
    """
    Parse a salary range string into minimum and maximum values
    
    Args:
        salary_range: String representation of salary range (e.g., "$80,000 - $120,000")
        
    Returns:
        Tuple of (min_salary, max_salary) in integer format
    """
    if not salary_range:
        return None, None
    
    # Convert to lowercase for consistency
    salary_text = salary_range.lower()
    
    # Handle hourly rates
    if 'hour' in salary_text or '/hr' in salary_text or '/h' in salary_text:
        return _parse_hourly_rate(salary_text)
    
    # Handle "competitive" or other non-numeric descriptions
    if any(term in salary_text for term in ['competitive', 'negotiable', 'doe', 'depends']):
        return None, None
    
    # Extract all numbers from the string
    numbers = re.findall(r'[\d,]+', salary_text)
    numbers = [int(n.replace(',', '')) for n in numbers]
    
    if not numbers:
        return None, None
    
    # If only one number is found
    if len(numbers) == 1:
        # Check if it's a minimum salary
        if 'from' in salary_text or 'min' in salary_text or 'starting' in salary_text:
            return numbers[0], None
        # Check if it's a maximum salary
        elif 'up to' in salary_text or 'max' in salary_text:
            return None, numbers[0]
        # Otherwise assume it's both min and max
        else:
            return numbers[0], numbers[0]
    
    # If multiple numbers, assume first is min and last is max
    return min(numbers), max(numbers)


def _parse_hourly_rate(hourly_text: str) -> Tuple[Optional[int], Optional[int]]:
    """
    Parse hourly rate and convert to annual salary
    
    Args:
        hourly_text: String with hourly rate information
        
    Returns:
        Tuple of (min_annual_salary, max_annual_salary)
    """
    # Extract hourly rates
    rates = re.findall(r'\$?(\d+(?:\.\d+)?)', hourly_text)
    
    if not rates:
        return None, None
    
    # Convert to float
    rates = [float(rate) for rate in rates]
    
    # Assume 2080 hours per year (40 hours/week * 52 weeks)
    hours_per_year = 2080
    
    if len(rates) == 1:
        # Single rate
        annual = int(rates[0] * hours_per_year)
        return annual, annual
    else:
        # Range of rates
        min_annual = int(min(rates) * hours_per_year)
        max_annual = int(max(rates) * hours_per_year)
        return min_annual, max_annual


def normalize_salary_data(jobs: list) -> list:
    """
    Add min_salary and max_salary fields to job dictionaries
    
    Args:
        jobs: List of job dictionaries
        
    Returns:
        List of job dictionaries with normalized salary fields
    """
    for job in jobs:
        if 'salary_range' in job and job['salary_range']:
            min_salary, max_salary = parse_salary_range(job['salary_range'])
            job['min_salary'] = min_salary
            job['max_salary'] = max_salary
    
    return jobs


def filter_jobs_by_salary(jobs: list, min_salary: Optional[int] = None, max_salary: Optional[int] = None) -> list:
    """
    Filter jobs by salary range
    
    Args:
        jobs: List of job dictionaries
        min_salary: Minimum salary requirement (None for no minimum)
        max_salary: Maximum salary consideration (None for no maximum)
        
    Returns:
        Filtered list of jobs
    """
    if min_salary is None and max_salary is None:
        return jobs
    
    # Normalize salary data first
    jobs = normalize_salary_data(jobs)
    
    filtered_jobs = []
    for job in jobs:
        job_min = job.get('min_salary')
        job_max = job.get('max_salary')
        
        # Skip jobs with no salary information
        if job_min is None and job_max is None:
            continue
        
        # Apply minimum salary filter if specified
        if min_salary is not None:
            # If job has a max salary, it must be >= min_salary
            if job_max is not None and job_max < min_salary:
                continue
            # If job only has min salary, it must be >= min_salary
            if job_max is None and job_min is not None and job_min < min_salary:
                continue
        
        # Apply maximum salary filter if specified
        if max_salary is not None:
            # If job has a min salary, it must be <= max_salary
            if job_min is not None and job_min > max_salary:
                continue
        
        filtered_jobs.append(job)
    
    return filtered_jobs