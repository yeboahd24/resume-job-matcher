# Job Scraping Implementation Guide

## Overview

The Resume Job Matcher now includes a comprehensive free job scraping solution that can fetch real job listings from multiple sources while maintaining respectful scraping practices.

## Features

### 🆓 Free Job Sources
- **RemoteOK**: Remote job listings from a popular job board
- **We Work Remotely**: Another major remote job platform
- **Enhanced Fallback**: Intelligent job generation based on market data

### 🛡️ Respectful Scraping
- **Rate Limiting**: Configurable delays between requests (1-3 seconds)
- **User Agent Rotation**: Multiple browser user agents to avoid detection
- **Error Handling**: Graceful fallbacks when sources are unavailable
- **Session Management**: Proper connection pooling and cleanup

### ⚙️ Configuration Options
- **Toggle Sources**: Enable/disable individual job boards
- **Rate Limiting**: Customize request delays and retry limits
- **Fallback Behavior**: Control when to use enhanced job generation

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# Basic scraping settings
USE_MOCK_JOBS=false              # Set to false to enable real scraping
JOB_SCRAPING_ENABLED=true
JOB_SCRAPING_TIMEOUT=30

# Rate limiting (be respectful!)
SCRAPING_MIN_DELAY=1.0           # Minimum delay between requests
SCRAPING_MAX_DELAY=3.0           # Maximum delay between requests
SCRAPING_MAX_RETRIES=3           # Retry failed requests

# Job board toggles
ENABLE_REMOTEOK=true             # Enable RemoteOK scraping
ENABLE_WEWORKREMOTELY=true       # Enable We Work Remotely scraping
ENABLE_ENHANCED_FALLBACK=true    # Use enhanced job generation as fallback
```

## Usage

### Basic Usage

```python
from app.services.job_scraper import JobScraperService

# Initialize scraper
scraper = JobScraperService()

# Search for jobs
jobs = await scraper.search_jobs("python", "Remote", limit=5)

# Always close the session
await scraper.close()
```

### Multiple Sources

```python
# Search multiple skill sets
queries = ["react", "node.js", "python"]
jobs = await scraper.scrape_multiple_sources(queries, "Remote")
```

## Job Data Structure

Each job returned has the following structure:

```python
{
    'title': 'Python Developer',
    'company': 'Tech Company',
    'location': 'Remote',
    'description': 'Detailed job description...',
    'url': 'https://company.com/jobs/123',
    'posted_date': '2024-01-15T10:30:00',
    'job_type': 'Full-time',
    'remote_allowed': True,
    'salary_range': '$90,000 - $130,000'
}
```

## Implementation Details

### Rate Limiting Strategy

The scraper implements several rate limiting mechanisms:

1. **Per-domain tracking**: Separate rate limits for each job board
2. **Random delays**: Adds randomization to avoid detection patterns
3. **Exponential backoff**: Increases delays after failures

### Error Handling

The system gracefully handles various error scenarios:

- **Network timeouts**: Automatic retries with backoff
- **Blocked requests**: Falls back to other sources
- **Parsing errors**: Skips malformed job listings
- **No results**: Uses enhanced job generation

### Data Quality

To ensure high-quality job matches:

- **Deduplication**: Removes duplicate jobs based on title and company
- **Validation**: Ensures required fields are present
- **Relevance**: Filters jobs based on search query relevance

## Testing

### Quick Test

Run the test script to verify everything works:

```bash
python test_scraper.py
```

### Manual Testing

1. **Enable real scraping**:
   ```bash
   export USE_MOCK_JOBS=false
   ```

2. **Test the API**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/jobs/match" \
        -H "Content-Type: multipart/form-data" \
        -F "file=@sample_resume.pdf"
   ```

3. **Check logs** for scraping activity:
   ```bash
   tail -f logs/app.log | grep -i "scraping\|remoteok\|wework"
   ```

## Best Practices

### 🚫 Don't Do This
- Set delays below 1 second
- Scrape during peak hours
- Ignore robots.txt files
- Make concurrent requests to the same domain

### ✅ Do This
- Use reasonable delays (1-3 seconds)
- Monitor for rate limiting responses
- Implement proper error handling
- Respect website terms of service

### Legal Considerations

- **Check robots.txt**: Always respect robots.txt files
- **Terms of Service**: Review each site's ToS before scraping
- **Rate Limiting**: Be respectful with request frequency
- **Data Usage**: Only use data for legitimate matching purposes

## Troubleshooting

### Common Issues

1. **No jobs found**:
   - Check if `USE_MOCK_JOBS=false`
   - Verify network connectivity
   - Check if job boards are accessible

2. **Rate limiting errors**:
   - Increase `SCRAPING_MIN_DELAY`
   - Reduce concurrent requests
   - Check for IP blocking

3. **Parsing errors**:
   - Job board HTML structure may have changed
   - Check logs for specific parsing errors
   - Consider updating selectors

### Debugging

Enable debug logging:

```python
import logging
logging.getLogger('app.services.job_scraper').setLevel(logging.DEBUG)
```

## Future Enhancements

### Planned Features
- **More job boards**: Indeed, AngelList, Dice
- **Geographic filtering**: Better location-based search
- **Salary parsing**: Extract and normalize salary information
- **Company data**: Enrich with company information
- **Caching**: Cache results to reduce scraping frequency

### API Integration Options
- **Indeed Publisher API**: When budget allows
- **LinkedIn Talent Solutions**: For enterprise features
- **Third-party aggregators**: RapidAPI, JSearch, etc.

## Support

For issues or questions:

1. Check the logs for error messages
2. Verify configuration settings
3. Test with mock data first
4. Review the troubleshooting section
5. Open an issue on GitHub

## Contributing

To add new job boards:

1. Create a new `_scrape_[source]_jobs` method
2. Add configuration toggles
3. Update the scraper list in `_scrape_multiple_free_sources`
4. Add tests and documentation
5. Submit a pull request

---

**Remember**: Always scrape responsibly and respect website terms of service!