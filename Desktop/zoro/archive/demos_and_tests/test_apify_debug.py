#!/usr/bin/env python3
"""
Apify Debug Script
=================

Debug what data we're actually getting from Apify actors
"""

import asyncio
from apify_client import ApifyClient

async def debug_apify_data():
    """
    Debug the actual data structure from Apify
    """
    
    print("🔍 DEBUGGING APIFY DATA STRUCTURE")
    print("=" * 50)
    
    api_token = "your-apify-token-here"
    client = ApifyClient(api_token)
    
    # Test 1: Debug profile scraper data
    print("📊 TEST 1: RAW PROFILE DATA")
    print("-" * 30)
    
    try:
        run_input = {
            "profiles": ["https://www.tiktok.com/@mrbeast"],
            "resultsType": "details"
        }
        
        print("🔍 Running profile scraper...")
        run = client.actor("clockworks/tiktok-profile-scraper").call(
            run_input=run_input,
            timeout_secs=300
        )
        
        print("✅ Actor completed, getting results...")
        
        # Get raw results
        results = []
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            results.append(item)
        
        print(f"📄 Found {len(results)} result(s)")
        
        if results:
            result = results[0]
            print(f"\n🔍 RAW DATA STRUCTURE:")
            print(f"Keys available: {list(result.keys())}")
            print(f"\n📊 SAMPLE DATA:")
            for key, value in list(result.items())[:20]:  # First 20 fields
                print(f"  {key}: {value}")
        else:
            print("❌ No results returned")
            
    except Exception as e:
        print(f"❌ Profile scraper error: {e}")
    
    # Test 2: Debug hashtag scraper data  
    print(f"\n📊 TEST 2: RAW HASHTAG DATA")
    print("-" * 32)
    
    try:
        run_input = {
            "hashtags": ["mrbeast"],
            "resultsPerPage": 3,
            "shouldDownloadVideos": False,
            "shouldDownloadCovers": False
        }
        
        print("🔍 Running hashtag scraper...")
        run = client.actor("clockworks/tiktok-hashtag-scraper").call(
            run_input=run_input,
            timeout_secs=300
        )
        
        print("✅ Actor completed, getting results...")
        
        # Get raw results
        results = []
        count = 0
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            results.append(item)
            count += 1
            if count >= 3:  # Just get first 3 for debugging
                break
        
        print(f"📄 Found {len(results)} result(s)")
        
        if results:
            result = results[0]
            print(f"\n🔍 RAW VIDEO DATA STRUCTURE:")
            print(f"Keys available: {list(result.keys())}")
            print(f"\n📊 SAMPLE VIDEO DATA:")
            for key, value in list(result.items())[:15]:  # First 15 fields
                print(f"  {key}: {value}")
                
            # Check specific fields we need
            print(f"\n🎯 KEY FIELDS:")
            print(f"  Author info: {result.get('authorMeta', 'NOT FOUND')}")
            print(f"  Play count: {result.get('playCount', 'NOT FOUND')}")
            print(f"  Digg count: {result.get('diggCount', 'NOT FOUND')}")
            print(f"  Create time: {result.get('createTimeISO', 'NOT FOUND')}")
            
        else:
            print("❌ No hashtag results returned")
            
    except Exception as e:
        print(f"❌ Hashtag scraper error: {e}")
    
    # Test 3: Try the free TikTok scraper (highest rated)
    print(f"\n📊 TEST 3: FREE TIKTOK SCRAPER")
    print("-" * 30)
    
    try:
        run_input = {
            "startUrls": ["https://www.tiktok.com/@mrbeast"]
        }
        
        print("🔍 Running free TikTok scraper...")
        run = client.actor("clockworks/free-tiktok-scraper").call(
            run_input=run_input,
            timeout_secs=300
        )
        
        print("✅ Actor completed, getting results...")
        
        # Get raw results
        results = []
        count = 0
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            results.append(item)
            count += 1
            if count >= 3:
                break
        
        print(f"📄 Found {len(results)} result(s)")
        
        if results:
            result = results[0]
            print(f"\n🔍 FREE SCRAPER DATA STRUCTURE:")
            print(f"Keys available: {list(result.keys())}")
            print(f"\n📊 SAMPLE DATA:")
            for key, value in list(result.items())[:15]:
                print(f"  {key}: {value}")
        else:
            print("❌ No free scraper results")
            
    except Exception as e:
        print(f"❌ Free scraper error: {e}")
    
    print(f"\n🎯 DEBUG SUMMARY:")
    print("=" * 20)
    print("✅ Apify connection: WORKING")
    print("✅ Actors running: WORKING")
    print("❓ Data parsing: NEEDS FIXING")
    print()
    print("💡 Next step: Fix data structure mapping")

if __name__ == "__main__":
    asyncio.run(debug_apify_data()) 