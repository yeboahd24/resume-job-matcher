#!/usr/bin/env python3
"""
Test both mock and real scraping modes
"""

import asyncio
import time
from app.services.job_scraper import JobScraperService

async def test_mock_scraping():
    """Test mock job generation"""
    print("🧪 Testing Mock Job Generation")
    print("=" * 40)
    
    # Force mock mode
    scraper = JobScraperService()
    scraper.use_mock = True
    
    start_time = time.time()
    jobs = await scraper.search_jobs("Python", "Remote", limit=3)
    end_time = time.time()
    
    print(f"⏱️  Time taken: {end_time - start_time:.2f} seconds")
    print(f"📊 Jobs found: {len(jobs)}")
    
    for i, job in enumerate(jobs, 1):
        print(f"\n{i}. {job['title']} at {job['company']}")
        print(f"   📍 Location: {job['location']}")
        print(f"   🔗 URL: {job['url']}")
        print(f"   📝 Description: {job['description'][:100]}...")
    
    await scraper.close()
    return jobs

async def test_real_scraping():
    """Test real web scraping"""
    print("\n🌐 Testing Real Web Scraping")
    print("=" * 40)
    
    # Force real scraping mode
    scraper = JobScraperService()
    scraper.use_mock = False
    
    start_time = time.time()
    jobs = await scraper.search_jobs("Python", "Remote", limit=3)
    end_time = time.time()
    
    print(f"⏱️  Time taken: {end_time - start_time:.2f} seconds")
    print(f"📊 Jobs found: {len(jobs)}")
    
    for i, job in enumerate(jobs, 1):
        print(f"\n{i}. {job['title']} at {job['company']}")
        print(f"   📍 Location: {job['location']}")
        print(f"   🔗 URL: {job['url']}")
        print(f"   📝 Description: {job['description'][:100]}...")
    
    await scraper.close()
    return jobs

async def main():
    """Compare mock vs real scraping"""
    print("🔍 Job Scraping Comparison Tool")
    print("=" * 50)
    
    try:
        # Test mock scraping
        mock_jobs = await test_mock_scraping()
        
        # Test real scraping
        real_jobs = await test_real_scraping()
        
        # Summary
        print(f"\n📊 Summary")
        print("=" * 20)
        print(f"Mock jobs: {len(mock_jobs)} (fast, fake data)")
        print(f"Real jobs: {len(real_jobs)} (slow, real data)")
        
        # Check if real jobs have real URLs
        real_urls = [job for job in real_jobs if not job['url'].startswith('https://example.com')]
        print(f"Real URLs found: {len(real_urls)}")
        
        if real_urls:
            print("✅ Real scraping is working!")
        else:
            print("⚠️  Real scraping may have fallen back to mock data")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")

if __name__ == "__main__":
    asyncio.run(main())