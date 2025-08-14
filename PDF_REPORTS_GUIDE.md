# PDF Report Generation Guide

This guide explains how to use the PDF report generation system in the Resume Job Matcher API.

## Overview

The PDF report generation system allows users to create professional, downloadable reports of their job matching results. The system supports both PDF and HTML formats with multiple themes and customizable sections.

## Features

### 🎨 **Multiple Themes**
- **Professional**: Clean, business-oriented design with blue and gray colors
- **Modern**: Contemporary design with purple and orange accents  
- **Minimal**: Simple, clean design focusing on content
- **Colorful**: Vibrant design with multiple accent colors

### 📄 **Multiple Formats**
- **HTML**: Available for all users, great for web viewing
- **PDF**: Professional format, requires Pro subscription or higher

### 📊 **Customizable Sections**
- **Executive Summary**: Overview of job matching results
- **Matched Jobs**: Detailed list of matching opportunities
- **Skills Analysis**: Analysis of resume skills vs. market demand
- **Recommendations**: Personalized career advice
- **Search Queries**: Queries used to find jobs
- **Statistics**: Detailed metrics and analytics

## API Endpoints

### Generate Report
```http
POST /api/v1/reports/generate
Authorization: Bearer <token>
Content-Type: application/json

{
  "task_id": "abc123-def456-ghi789",
  "format": "pdf",
  "theme": "professional",
  "sections": ["summary", "matched_jobs", "skills_analysis", "recommendations"],
  "include_charts": true,
  "custom_title": "My Job Matching Report"
}
```

**Response:**
```json
{
  "report_id": "report-uuid-123",
  "status": "completed",
  "download_url": "/api/v1/reports/report-uuid-123/download",
  "file_size_bytes": 245760,
  "expires_at": "2024-01-15T10:30:00Z",
  "generated_at": "2024-01-08T10:30:00Z",
  "format": "pdf",
  "theme": "professional"
}
```

### Download Report
```http
GET /api/v1/reports/{report_id}/download
Authorization: Bearer <token>
```

Returns the generated report file for download.

### Get Available Formats
```http
GET /api/v1/reports/formats
Authorization: Bearer <token>
```

Returns available formats, themes, and sections based on user subscription.

### Get Report Templates
```http
GET /api/v1/reports/templates
Authorization: Bearer <token>
```

Returns detailed information about available themes and sections.

## Subscription Requirements

| Feature | Free | Student | Pro | Enterprise |
|---------|------|---------|-----|------------|
| HTML Reports | ✅ | ✅ | ✅ | ✅ |
| PDF Reports | ❌ | ❌ | ✅ | ✅ |
| All Themes | ✅ | ✅ | ✅ | ✅ |
| All Sections | ✅ | ✅ | ✅ | ✅ |
| Custom Titles | ✅ | ✅ | ✅ | ✅ |
| Report Expiry | 7 days | 7 days | 30 days | 30 days |

## Usage Examples

### 1. Basic HTML Report
```python
import requests

# Generate HTML report (available for all users)
report_request = {
    "task_id": "your-task-id",
    "format": "html",
    "theme": "modern",
    "sections": ["summary", "matched_jobs"]
}

response = requests.post(
    "http://localhost:8000/api/v1/reports/generate",
    json=report_request,
    headers={"Authorization": f"Bearer {token}"}
)

if response.status_code == 200:
    report = response.json()
    print(f"Report generated: {report['download_url']}")
```

### 2. Professional PDF Report
```python
# Generate PDF report (requires Pro subscription)
report_request = {
    "task_id": "your-task-id",
    "format": "pdf",
    "theme": "professional",
    "sections": [
        "summary",
        "matched_jobs", 
        "skills_analysis",
        "recommendations",
        "statistics"
    ],
    "include_charts": True,
    "custom_title": "Senior Developer Job Search Report"
}

response = requests.post(
    "http://localhost:8000/api/v1/reports/generate",
    json=report_request,
    headers={"Authorization": f"Bearer {token}"}
)
```

### 3. Download Generated Report
```python
# Download the report
report_id = "report-uuid-123"
response = requests.get(
    f"http://localhost:8000/api/v1/reports/{report_id}/download",
    headers={"Authorization": f"Bearer {token}"}
)

if response.status_code == 200:
    with open("job_report.pdf", "wb") as f:
        f.write(response.content)
    print("Report downloaded successfully!")
```

## Testing the System

### 1. Using the Test Script
```bash
python test_pdf_reports.py
```

This comprehensive test script will:
- Register and login a test user
- Upgrade to Pro subscription
- Submit a job matching task
- Wait for completion
- Generate both PDF and HTML reports
- Download the generated reports

### 2. Using the Web Interface
Open `pdf_reports_test.html` in your browser to:
- Login and manage subscription
- Upload resumes for job matching
- Generate reports with different themes
- Download generated reports
- Track report history

### 3. Manual API Testing
```bash
# 1. Login and get token
curl -X POST "http://localhost:8000/api/v1/auth/jwt/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=password123"

# 2. Check available formats
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/reports/formats"

# 3. Generate report
curl -X POST "http://localhost:8000/api/v1/reports/generate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "your-task-id",
    "format": "pdf",
    "theme": "professional",
    "sections": ["summary", "matched_jobs"]
  }'

# 4. Download report
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/reports/REPORT_ID/download" \
  -o "report.pdf"
```

## Report Content Details

### Executive Summary
- User information and resume details
- Total jobs found and matched
- Processing time and generation date
- Key metrics overview

### Matched Jobs Section
- Top 10 matching job opportunities
- Job details: title, company, location
- Similarity scores and relevance
- Job descriptions and application links
- Salary information (when available)

### Skills Analysis
- Skills extracted from resume
- Most in-demand skills from job matches
- Skill frequency and relevance scores
- Identified skill gaps and recommendations

### Recommendations
- Personalized career advice
- Suggested skills to learn
- Job search tips and strategies
- Subscription-specific recommendations

### Statistics
- Detailed matching metrics
- Success rates and averages
- Visual charts and graphs (PDF only)
- Comparative analysis

## Customization Options

### Themes
Each theme provides different visual styling:

```python
# Theme examples
themes = {
    "professional": {
        "colors": ["#2c3e50", "#3498db", "#e74c3c"],
        "style": "Corporate, clean, business-oriented"
    },
    "modern": {
        "colors": ["#34495e", "#9b59b6", "#f39c12"], 
        "style": "Contemporary, tech-focused"
    },
    "minimal": {
        "colors": ["#2c3e50", "#95a5a6", "#e67e22"],
        "style": "Simple, content-focused"
    },
    "colorful": {
        "colors": ["#e74c3c", "#3498db", "#2ecc71"],
        "style": "Vibrant, creative industries"
    }
}
```

### Custom Sections
You can include/exclude sections based on needs:

```python
# Minimal report
sections = ["summary", "matched_jobs"]

# Comprehensive report  
sections = [
    "summary",
    "matched_jobs",
    "skills_analysis", 
    "recommendations",
    "search_queries",
    "statistics"
]
```

## File Management

### Storage
- Reports are stored in `data/reports/` directory
- Files are named with unique UUIDs
- Both PDF and HTML formats supported

### Expiration
- **Free/Student**: Reports expire after 7 days
- **Pro/Enterprise**: Reports expire after 30 days
- Automatic cleanup removes expired files

### Security
- Reports are tied to user accounts
- Download URLs require authentication
- No public access to report files

## Error Handling

### Common Errors

1. **Task Not Found (404)**
```json
{
  "detail": "Task abc123 not found or not completed"
}
```

2. **Subscription Required (402)**
```json
{
  "detail": "PDF report generation requires Pro subscription or higher"
}
```

3. **Invalid Sections (400)**
```json
{
  "detail": "At least one section must be included"
}
```

### Error Resolution
- Ensure task is completed successfully before generating reports
- Upgrade subscription for PDF access
- Verify all required parameters are provided
- Check authentication token validity

## Performance Considerations

### Generation Time
- **HTML Reports**: ~1-3 seconds
- **PDF Reports**: ~3-10 seconds (depending on content)
- **Large Reports**: May take longer with many jobs/sections

### File Sizes
- **HTML**: 50-200 KB typically
- **PDF**: 200KB-2MB depending on content and images
- **Charts**: Add ~50-100KB to PDF files

### Optimization Tips
- Limit matched jobs to top 10-20 for faster generation
- Use minimal sections for quick reports
- Consider HTML for immediate viewing, PDF for formal sharing

## Integration Examples

### Frontend Integration
```javascript
// Generate and download report
async function generateReport(taskId, format = 'pdf') {
    const response = await fetch('/api/v1/reports/generate', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            task_id: taskId,
            format: format,
            theme: 'professional',
            sections: ['summary', 'matched_jobs', 'skills_analysis']
        })
    });
    
    if (response.ok) {
        const report = await response.json();
        // Redirect to download
        window.open(report.download_url, '_blank');
    }
}
```

### Email Integration
```python
# Send report via email
def send_report_email(user_email, report_url):
    subject = "Your Job Matching Report is Ready"
    body = f"""
    Your personalized job matching report has been generated.
    
    Download your report: {report_url}
    
    This link will expire in 7 days.
    """
    # Send email implementation
```

## Future Enhancements

### Planned Features
- **Interactive Charts**: Clickable visualizations in PDF
- **Company Logos**: Automatic logo inclusion for matched companies
- **Multi-language**: Support for different languages
- **Batch Reports**: Generate multiple reports at once
- **Report Templates**: Pre-defined industry-specific templates

### Advanced Customization
- **Custom Branding**: Company logos and colors
- **White-label**: Remove "Resume Job Matcher" branding
- **API Integration**: Embed reports in external systems
- **Real-time Updates**: Live report updates as new jobs are found

This PDF report generation system provides a professional way for users to document and share their job search results, with flexible customization options and subscription-based feature access.