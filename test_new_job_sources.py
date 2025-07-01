#!/usr/bin/env python3
"""
Test the new job sources
"""

import asyncio
from app.services.job_scraper import JobScraperService

async def test_all_new_sources():
    """Test all new job sources individually"""
    print("🧪 Testing New Job Sources")
    print("=" * 50)
    
    scraper = JobScraperService()
    scraper.use_mock = False  # Force real scraping
    
    # Test each new source
    new_sources = [
        ("JustRemote", scraper._scrape_justremote_jobs),
        ("Remote.co", scraper._scrape_remoteco_jobs),
        ("NoWhiteboard", scraper._scrape_nowhiteboard_jobs),
        ("Y Combinator", scraper._scrape_ycombinator_jobs),
        ("AngelList Style", scraper._scrape_angel_jobs),
        ("Freelancer", scraper._scrape_freelancer_jobs),
    ]
    
    all_results = {}
    
    for source_name, scraper_func in new_sources:
        print(f"\n🔍 Testing {source_name}...")
        try:
            jobs = await scraper_func("Python", "Remote", 3)
            all_results[source_name] = jobs
            
            if jobs:
                print(f"   ✅ Success: Found {len(jobs)} jobs")
                for i, job in enumerate(jobs, 1):
                    print(f"   {i}. {job['title']} at {job['company']}")
                    print(f"      📍 {job['location']}")
                    print(f"      💰 {job['salary_range']}")
                    print(f"      🔗 {job['url']}")
            else:
                print(f"   ⚠️  No jobs found")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            all_results[source_name] = []
    
    await scraper.close()
    
    # Summary
    print(f"\n📊 Summary")
    print("=" * 30)
    
    total_jobs = sum(len(jobs) for jobs in all_results.values())
    working_sources = sum(1 for jobs in all_results.values() if len(jobs) > 0)
    
    print(f"Total jobs found: {total_jobs}")
    print(f"Working sources: {working_sources}/{len(new_sources)}")
    
    # Show job diversity
    all_companies = set()
    all_job_types = set()
    
    for jobs in all_results.values():
        for job in jobs:
            all_companies.add(job['company'])
            all_job_types.add(job['job_type'])
    
    print(f"Unique companies: {len(all_companies)}")
    print(f"Job types: {', '.join(all_job_types)}")
    
    return all_results

async def test_combined_scraping():
    """Test the combined scraping with all sources"""
    print(f"\n🌐 Testing Combined Scraping")
    print("=" * 40)
    
    scraper = JobScraperService()
    scraper.use_mock = False
    
    # Test with different queries
    test_queries = ["Python", "JavaScript", "React", "Machine Learning"]
    
    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        try:
            jobs = await scraper.search_jobs(query, "Remote", limit=8)
            
            print(f"   📊 Found {len(jobs)} jobs")
            
            # Show diversity
            companies = set(job['company'] for job in jobs)
            locations = set(job['location'] for job in jobs)
            
            print(f"   🏢 Companies: {len(companies)}")
            print(f"   📍 Locations: {len(locations)}")
            
            # Show sample jobs
            print(f"   📋 Sample jobs:")
            for i, job in enumerate(jobs[:3], 1):
                print(f"      {i}. {job['title']} at {job['company']}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    await scraper.close()

async def main():
    """Run all tests"""
    print("🚀 New Job Sources Test Suite")
    print("=" * 50)
    
    # Test individual sources
    results = await test_all_new_sources()
    
    # Test combined scraping
    await test_combined_scraping()
    
    print(f"\n🎉 Testing Complete!")
    print(f"💡 The job matcher now has access to:")
    print(f"   • Original sources (RemoteOK, WeWorkRemotely)")
    print(f"   • 6 new job sources")
    print(f"   • Enhanced fallback generation")
    print(f"   • Much better job diversity!")

if __name__ == "__main__":
    asyncio.run(main())