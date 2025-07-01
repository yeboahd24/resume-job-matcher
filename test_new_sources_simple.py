#!/usr/bin/env python3
"""
Simple test of new job sources with timeout protection
"""

import asyncio
from app.services.job_scraper import JobScraperService

async def test_source_with_timeout(source_name, scraper_func, query="Python", timeout=10):
    """Test a single source with timeout protection"""
    try:
        # Run with timeout
        jobs = await asyncio.wait_for(
            scraper_func(query, "Remote", 3), 
            timeout=timeout
        )
        
        if jobs:
            print(f"   ✅ {source_name}: Found {len(jobs)} jobs")
            for i, job in enumerate(jobs[:2], 1):  # Show first 2
                print(f"      {i}. {job['title']} at {job['company']}")
        else:
            print(f"   ⚠️  {source_name}: No jobs found")
        
        return len(jobs)
        
    except asyncio.TimeoutError:
        print(f"   ⏰ {source_name}: Timeout after {timeout}s")
        return 0
    except Exception as e:
        print(f"   ❌ {source_name}: Error - {str(e)[:50]}...")
        return 0

async def test_all_sources():
    """Test all job sources with timeout protection"""
    print("🧪 Testing All Job Sources (with timeout protection)")
    print("=" * 60)
    
    scraper = JobScraperService()
    scraper.use_mock = False
    
    # All sources to test
    sources = [
        ("JustRemote", scraper._scrape_justremote_jobs),
        ("Remote.co", scraper._scrape_remoteco_jobs),
        ("NoWhiteboard", scraper._scrape_nowhiteboard_jobs),
        ("Y Combinator", scraper._scrape_ycombinator_jobs),
        ("AngelList", scraper._scrape_angel_jobs),
        ("Freelancer", scraper._scrape_freelancer_jobs),
        ("GitHub Enhanced", scraper._scrape_github_jobs),
    ]
    
    total_jobs = 0
    working_sources = 0
    
    for source_name, scraper_func in sources:
        print(f"\n🔍 Testing {source_name}...")
        job_count = await test_source_with_timeout(source_name, scraper_func)
        
        if job_count > 0:
            working_sources += 1
            total_jobs += job_count
    
    await scraper.close()
    
    # Summary
    print(f"\n📊 Summary")
    print("=" * 30)
    print(f"Working sources: {working_sources}/{len(sources)}")
    print(f"Total jobs found: {total_jobs}")
    print(f"Average per source: {total_jobs/len(sources):.1f}")
    
    return working_sources, total_jobs

async def test_combined_search():
    """Test the combined search functionality"""
    print(f"\n🌐 Testing Combined Search")
    print("=" * 40)
    
    scraper = JobScraperService()
    scraper.use_mock = False
    
    test_queries = ["Python", "JavaScript", "React"]
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        try:
            # Test with timeout
            jobs = await asyncio.wait_for(
                scraper.search_jobs(query, "Remote", limit=6),
                timeout=30
            )
            
            companies = set(job['company'] for job in jobs)
            job_types = set(job['job_type'] for job in jobs)
            
            print(f"   📊 Found {len(jobs)} jobs from {len(companies)} companies")
            print(f"   💼 Job types: {', '.join(job_types)}")
            
            # Show sample
            for i, job in enumerate(jobs[:2], 1):
                print(f"   {i}. {job['title']} at {job['company']} ({job['location']})")
            
        except asyncio.TimeoutError:
            print(f"   ⏰ Timeout after 30s")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    await scraper.close()

async def main():
    """Run all tests"""
    print("🚀 Job Sources Test (Quick Version)")
    print("=" * 50)
    
    # Test individual sources
    working, total = await test_all_sources()
    
    # Test combined search
    await test_combined_search()
    
    print(f"\n🎉 Test Complete!")
    
    if working >= 4:
        print(f"✅ Excellent! {working} sources working")
    elif working >= 2:
        print(f"✅ Good! {working} sources working")
    else:
        print(f"⚠️  Only {working} sources working")
    
    print(f"💡 Your job matcher now has much better job diversity!")

if __name__ == "__main__":
    asyncio.run(main())