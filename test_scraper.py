#!/usr/bin/env python3
"""
Test script for the enhanced job scraper
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from app.services.job_scraper import JobScraperService
from app.core.config import settings

async def test_job_scraper():
    """Test the job scraper with different configurations"""
    
    print("🔍 Testing Enhanced Job Scraper")
    print("=" * 50)
    
    # Test with mock data first
    print("\n1. Testing with MOCK data (USE_MOCK_JOBS=True)")
    settings.USE_MOCK_JOBS = True
    
    scraper = JobScraperService()
    
    try:
        jobs = await scraper.search_jobs("python", "Remote", 3)
        print(f"   Found {len(jobs)} mock jobs")
        
        if jobs:
            print(f"   Sample job: {jobs[0]['title']} at {jobs[0]['company']}")
    
    except Exception as e:
        print(f"   Error: {e}")
    
    finally:
        await scraper.close()
    
    # Test with real scraping
    print("\n2. Testing with REAL scraping (USE_MOCK_JOBS=False)")
    settings.USE_MOCK_JOBS = False
    
    scraper = JobScraperService()
    
    try:
        jobs = await scraper.search_jobs("javascript", "Remote", 2)
        print(f"   Found {len(jobs)} real/enhanced jobs")
        
        if jobs:
            print(f"   Sample job: {jobs[0]['title']} at {jobs[0]['company']}")
            print(f"   Job URL: {jobs[0]['url']}")
    
    except Exception as e:
        print(f"   Error: {e}")
    
    finally:
        await scraper.close()
    
    # Test multiple sources
    print("\n3. Testing multiple sources")
    scraper = JobScraperService()
    
    try:
        queries = ["react", "node.js"]
        jobs = await scraper.scrape_multiple_sources(queries, "Remote")
        print(f"   Found {len(jobs)} jobs from multiple sources")
        
        # Group by source type
        real_jobs = [j for j in jobs if 'remoteok.io' in j.get('url', '') or 'weworkremotely.com' in j.get('url', '')]
        enhanced_jobs = [j for j in jobs if j not in real_jobs]
        
        print(f"   Real scraped jobs: {len(real_jobs)}")
        print(f"   Enhanced fallback jobs: {len(enhanced_jobs)}")
    
    except Exception as e:
        print(f"   Error: {e}")
    
    finally:
        await scraper.close()
    
    print("\n✅ Job scraper testing completed!")

if __name__ == "__main__":
    asyncio.run(test_job_scraper())