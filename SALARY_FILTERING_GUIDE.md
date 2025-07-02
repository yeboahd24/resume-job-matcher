# Salary Filtering Guide

This guide explains how to use the salary filtering feature in the Resume Job Matcher API.

## Overview

The salary filtering feature allows users to filter job matches based on salary requirements. This helps users focus on job opportunities that match their salary expectations, saving time and ensuring relevant results.

## Features

- **Explicit Salary Filtering**: Filter jobs by minimum and maximum salary
- **Profile-Based Filtering**: Use salary preferences stored in user profile
- **Salary Range Parsing**: Intelligent parsing of various salary formats
- **Hourly Rate Conversion**: Automatic conversion of hourly rates to annual salaries
- **Salary Statistics**: Access to common salary ranges by job level and type

## API Endpoints

### Job Matching with Salary Filtering

```http
POST /api/v1/jobs/match
Content-Type: multipart/form-data
Authorization: Bearer <token>

file=@resume.pdf
min_salary=80000
max_salary=150000
use_profile_salary=true
```

#### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `file` | File | Resume file (PDF or text) |
| `min_salary` | Integer | Minimum salary requirement (optional) |
| `max_salary` | Integer | Maximum salary consideration (optional) |
| `use_profile_salary` | Boolean | Whether to use salary preferences from user profile (default: false) |

### Salary Ranges Information

```http
GET /api/v1/jobs/salary-ranges
Authorization: Bearer <token>
```

Returns information about common salary ranges by job level and type.

## User Profile Salary Preferences

Users can set their salary preferences in their profile:

```http
POST /api/v1/auth/me/profile
Content-Type: application/json
Authorization: Bearer <token>

{
  "salary_min": 80000,
  "salary_max": 150000,
  "preferred_job_titles": ["Software Engineer", "Developer"],
  "preferred_locations": ["Remote", "New York"]
}
```

## How Salary Filtering Works

### 1. Salary Range Parsing

The system parses salary ranges from various formats:

- **Standard ranges**: "$80,000 - $120,000"
- **Hourly rates**: "$50/hour" (converted to annual)
- **Minimum only**: "From $90,000"
- **Maximum only**: "Up to $100,000"
- **K notation**: "$50-75k"

### 2. Filtering Logic

Jobs are filtered based on the following rules:

- If a job has a salary range (min-max), it's included if:
  - The job's maximum salary ≥ user's minimum requirement
  - The job's minimum salary ≤ user's maximum consideration

- If a job has only a minimum salary, it's included if:
  - The job's minimum salary ≤ user's maximum consideration (if specified)

- If a job has only a maximum salary, it's included if:
  - The job's maximum salary ≥ user's minimum requirement (if specified)

- Jobs with no salary information are excluded when filtering is applied

### 3. Hourly to Annual Conversion

Hourly rates are converted to annual salaries using:
- 40 hours per week
- 52 weeks per year
- 2,080 total hours per year

For example, "$50/hour" becomes $104,000 annually.

## Examples

### Example 1: Basic Salary Filtering

```python
import requests

# Upload resume with salary filter
files = {'file': open('resume.pdf', 'rb')}
params = {'min_salary': 100000}  # Only jobs with salaries ≥ $100k

response = requests.post(
    "http://localhost:8000/api/v1/jobs/match",
    files=files,
    params=params,
    headers={"Authorization": f"Bearer {token}"}
)
```

### Example 2: Using Profile Preferences

```python
# First, set profile preferences
profile_data = {
    "salary_min": 120000,
    "salary_max": 200000,
    "preferred_job_titles": ["Senior Developer"]
}

requests.post(
    "http://localhost:8000/api/v1/auth/me/profile",
    json=profile_data,
    headers={"Authorization": f"Bearer {token}"}
)

# Then use profile preferences for filtering
files = {'file': open('resume.pdf', 'rb')}
params = {'use_profile_salary': True}

response = requests.post(
    "http://localhost:8000/api/v1/jobs/match",
    files=files,
    params=params,
    headers={"Authorization": f"Bearer {token}"}
)
```

### Example 3: Get Salary Range Information

```python
response = requests.get(
    "http://localhost:8000/api/v1/jobs/salary-ranges",
    headers={"Authorization": f"Bearer {token}"}
)

salary_info = response.json()
print(f"Entry level range: {salary_info['salary_ranges_by_level']['entry_level']['range']}")
```

## Recommended Salary Ranges

| Level | Salary Range | Recommended Filter |
|-------|-------------|-------------------|
| Entry Level | $50,000 - $80,000 | min_salary=50000, max_salary=80000 |
| Mid Level | $80,000 - $120,000 | min_salary=80000, max_salary=120000 |
| Senior Level | $120,000 - $180,000 | min_salary=120000, max_salary=180000 |
| Management | $140,000 - $220,000 | min_salary=140000, max_salary=220000 |

## Testing the Feature

You can test the salary filtering feature using the provided test script:

```bash
python test_salary_filtering.py
```

This script will:
1. Test the salary ranges endpoint
2. Test salary parsing with various formats
3. Test job matching with explicit salary filters
4. Test profile-based salary filtering

## Implementation Details

The salary filtering feature is implemented across several components:

1. **API Endpoints**: Parameters for salary filtering in the job matching endpoint
2. **Salary Parser**: Utility for parsing and normalizing salary information
3. **Matching Service**: Integration with the job matching algorithm
4. **User Profile**: Storage of salary preferences

## Future Enhancements

Planned enhancements for the salary filtering feature:

1. **Salary Insights**: Market rate analysis for specific job titles
2. **Location Adjustment**: Salary adjustments based on cost of living
3. **Experience-Based Ranges**: Customized ranges based on years of experience
4. **Compensation Package Analysis**: Benefits, equity, bonuses consideration
5. **Salary Negotiation Tips**: Personalized advice based on market data

This salary filtering feature provides a powerful way for users to focus on job opportunities that match their financial expectations.