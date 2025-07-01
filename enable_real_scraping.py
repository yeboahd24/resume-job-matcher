#!/usr/bin/env python3
"""
Enable real web scraping instead of mock data
"""

import os
import shutil

def enable_real_scraping():
    """Switch from mock data to real web scraping"""
    print("🔧 Enabling Real Web Scraping")
    print("=" * 40)
    
    # Backup current .env
    if os.path.exists('.env'):
        print("📦 Backing up current .env to .env.backup...")
        shutil.copy('.env', '.env.backup')
    
    # Read current .env
    env_lines = []
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            env_lines = f.readlines()
    
    # Update the USE_MOCK_JOBS setting
    updated_lines = []
    mock_jobs_updated = False
    
    for line in env_lines:
        if line.startswith('USE_MOCK_JOBS='):
            updated_lines.append('USE_MOCK_JOBS=false\n')
            mock_jobs_updated = True
            print("✅ Changed USE_MOCK_JOBS from true to false")
        else:
            updated_lines.append(line)
    
    # If USE_MOCK_JOBS wasn't found, add it
    if not mock_jobs_updated:
        # Find the job scraping section and add it there
        for i, line in enumerate(updated_lines):
            if line.startswith('JOB_SCRAPING_ENABLED='):
                updated_lines.insert(i + 2, 'USE_MOCK_JOBS=false\n')
                mock_jobs_updated = True
                print("✅ Added USE_MOCK_JOBS=false to configuration")
                break
    
    # Write updated .env
    with open('.env', 'w') as f:
        f.writelines(updated_lines)
    
    print("✅ Configuration updated successfully!")
    
    print("\n📋 Real Scraping Sources Enabled:")
    print("   • RemoteOK.io - Remote job listings")
    print("   • WeWorkRemotely.com - Remote job board")
    print("   • StackOverflow Jobs - Developer jobs")
    print("   • GitHub Jobs - Fallback source")
    
    print("\n⚠️  Important Notes:")
    print("   • Real scraping takes longer (30-60 seconds)")
    print("   • Some sites may block requests occasionally")
    print("   • Rate limiting is applied to be respectful")
    print("   • Fallback to mock data if scraping fails")
    
    print("\n🔄 Next Steps:")
    print("   1. Restart your Celery worker")
    print("   2. Restart your FastAPI server")
    print("   3. Test with a resume upload")
    
    return True

def disable_real_scraping():
    """Switch back to mock data"""
    print("🔧 Disabling Real Web Scraping (Back to Mock Data)")
    print("=" * 50)
    
    # Read current .env
    env_lines = []
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            env_lines = f.readlines()
    
    # Update the USE_MOCK_JOBS setting
    updated_lines = []
    
    for line in env_lines:
        if line.startswith('USE_MOCK_JOBS='):
            updated_lines.append('USE_MOCK_JOBS=true\n')
            print("✅ Changed USE_MOCK_JOBS from false to true")
        else:
            updated_lines.append(line)
    
    # Write updated .env
    with open('.env', 'w') as f:
        f.writelines(updated_lines)
    
    print("✅ Switched back to mock data")
    return True

def show_current_status():
    """Show current scraping configuration"""
    print("📊 Current Job Scraping Configuration")
    print("=" * 40)
    
    # Read .env file
    use_mock = True  # default
    scraping_enabled = True  # default
    
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('USE_MOCK_JOBS='):
                    use_mock = line.strip().split('=')[1].lower() == 'true'
                elif line.startswith('JOB_SCRAPING_ENABLED='):
                    scraping_enabled = line.strip().split('=')[1].lower() == 'true'
    
    print(f"   Job Scraping Enabled: {'✅ Yes' if scraping_enabled else '❌ No'}")
    print(f"   Using Mock Data: {'✅ Yes' if use_mock else '❌ No'}")
    print(f"   Real Web Scraping: {'❌ No' if use_mock else '✅ Yes'}")
    
    if use_mock:
        print(f"\n📝 Currently using mock/fake job data")
        print(f"   • Faster response times")
        print(f"   • Consistent results for testing")
        print(f"   • No external dependencies")
    else:
        print(f"\n🌐 Currently using real web scraping")
        print(f"   • Slower response times (30-60s)")
        print(f"   • Real job listings from multiple sources")
        print(f"   • May occasionally fail due to site changes")
    
    return use_mock

if __name__ == "__main__":
    import sys
    
    print("🧪 Job Scraping Configuration Tool")
    print("=" * 50)
    
    # Show current status
    is_mock = show_current_status()
    
    print(f"\n🔧 Available Actions:")
    print(f"   1. Enable real web scraping")
    print(f"   2. Disable real web scraping (use mock data)")
    print(f"   3. Show current status")
    print(f"   4. Exit")
    
    if len(sys.argv) > 1:
        action = sys.argv[1].lower()
        if action in ['enable', 'real', 'true']:
            enable_real_scraping()
        elif action in ['disable', 'mock', 'false']:
            disable_real_scraping()
        elif action in ['status', 'show']:
            pass  # Already shown above
        else:
            print(f"❌ Unknown action: {action}")
    else:
        try:
            choice = input(f"\nEnter your choice (1-4): ").strip()
            
            if choice == '1':
                enable_real_scraping()
            elif choice == '2':
                disable_real_scraping()
            elif choice == '3':
                show_current_status()
            elif choice == '4':
                print("👋 Goodbye!")
            else:
                print("❌ Invalid choice")
        except KeyboardInterrupt:
            print(f"\n👋 Goodbye!")
        except EOFError:
            print(f"\n👋 Goodbye!")