#!/usr/bin/env python3
"""
Check which scraping sources are working
"""

import asyncio
import aiohttp
from app.services.job_scraper import JobScraperService

async def test_scraping_sources():
    """Test each scraping source individually"""
    print("🔍 Testing Individual Scraping Sources")
    print("=" * 50)
    
    scraper = JobScraperService()
    scraper.use_mock = False  # Force real scraping
    
    # Test sources
    sources = [
        ("RemoteOK", scraper._scrape_remoteok_jobs),
        ("WeWorkRemotely", scraper._scrape_weworkremotely_jobs),
        ("StackOverflow", scraper._scrape_stackoverflow_jobs),
        ("GitHub (Enhanced)", scraper._scrape_github_jobs),
    ]
    
    results = {}
    
    for source_name, scraper_func in sources:
        print(f"\n🧪 Testing {source_name}...")
        try:
            jobs = await scraper_func("Python", "Remote", 2)
            results[source_name] = {
                'status': 'success',
                'jobs_found': len(jobs),
                'sample_job': jobs[0] if jobs else None
            }
            
            if jobs:
                print(f"   ✅ Success: Found {len(jobs)} jobs")
                sample = jobs[0]
                print(f"   📋 Sample: {sample['title']} at {sample['company']}")
                print(f"   🔗 URL: {sample['url']}")
            else:
                print(f"   ⚠️  Success but no jobs found")
                
        except Exception as e:
            results[source_name] = {
                'status': 'failed',
                'error': str(e),
                'jobs_found': 0
            }
            print(f"   ❌ Failed: {str(e)}")
    
    await scraper.close()
    
    # Summary
    print(f"\n📊 Summary")
    print("=" * 30)
    
    working_sources = [name for name, result in results.items() if result['status'] == 'success' and result['jobs_found'] > 0]
    failed_sources = [name for name, result in results.items() if result['status'] == 'failed']
    empty_sources = [name for name, result in results.items() if result['status'] == 'success' and result['jobs_found'] == 0]
    
    print(f"✅ Working sources: {len(working_sources)}")
    for source in working_sources:
        print(f"   • {source}: {results[source]['jobs_found']} jobs")
    
    if failed_sources:
        print(f"\n❌ Failed sources: {len(failed_sources)}")
        for source in failed_sources:
            print(f"   • {source}: {results[source]['error']}")
    
    if empty_sources:
        print(f"\n⚠️  Empty sources: {len(empty_sources)}")
        for source in empty_sources:
            print(f"   • {source}: No jobs found")
    
    return results

async def test_url_accessibility():
    """Test if job board URLs are accessible"""
    print(f"\n🌐 Testing URL Accessibility")
    print("=" * 40)
    
    test_urls = [
        ("RemoteOK", "https://remoteok.io/remote-python-jobs"),
        ("WeWorkRemotely", "https://weworkremotely.com/remote-jobs/search?term=python"),
        ("StackOverflow", "https://stackoverflow.com/jobs?q=python&r=true"),
    ]
    
    async with aiohttp.ClientSession() as session:
        for name, url in test_urls:
            try:
                async with session.get(url, timeout=10) as response:
                    status = response.status
                    if status == 200:
                        print(f"   ✅ {name}: {status} (accessible)")
                    elif status == 403:
                        print(f"   🚫 {name}: {status} (blocked/forbidden)")
                    else:
                        print(f"   ⚠️  {name}: {status} (other)")
            except Exception as e:
                print(f"   ❌ {name}: Error - {str(e)}")

async def main():
    """Run all tests"""
    print("🧪 Job Scraping Source Diagnostic")
    print("=" * 50)
    
    # Test URL accessibility
    await test_url_accessibility()
    
    # Test scraping sources
    results = await test_scraping_sources()
    
    # Recommendations
    print(f"\n💡 Recommendations")
    print("=" * 30)
    
    working_count = sum(1 for r in results.values() if r['status'] == 'success' and r['jobs_found'] > 0)
    
    if working_count >= 2:
        print("✅ Multiple sources working - good diversity!")
    elif working_count == 1:
        print("⚠️  Only one source working - consider adding more")
    else:
        print("❌ No sources working - check network/firewall")
    
    print(f"\n🔧 Current Behavior:")
    print(f"   • Real scraping attempts: Multiple sources")
    print(f"   • Fallback on failure: Enhanced job generation")
    print(f"   • Result: Always returns jobs (real or realistic)")

if __name__ == "__main__":
    asyncio.run(main())