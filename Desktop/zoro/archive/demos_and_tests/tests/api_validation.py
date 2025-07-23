#!/usr/bin/env python3
"""
EnsembleData API Validation Test
Validates API reliability across multiple TikTok endpoints for the multi-agent system
"""

from ensembledata.api import EDClient, EDError
from datetime import datetime
import time

API_KEY = "MZTq3h5VIyi0CjKt"

def validate_api():
    """Validate EnsembleData API across all required endpoints"""
    
    print("🔍 EnsembleData API Validation for Multi-Agent System")
    print("=" * 60)
    print(f"Testing API reliability for trend analysis")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    client = EDClient(API_KEY, timeout=30)
    results = {}
    total_units = 0
    
    def safe_int(value):
        """Safely convert units to int"""
        try:
            return int(value) if value else 0
        except (ValueError, TypeError):
            return 0
    
    # Test required endpoints for the multi-agent system
    test_scenarios = [
        ("user_info", "User Info Endpoint", [
            ("cristiano", "charlidamelio", "mrbeast")
        ]),
        ("hashtag_search", "Hashtag Monitoring", [
            ("fyp", "football", "cooking", "ai")
        ]),
        ("keyword_search", "Keyword Trend Analysis", [
            ("tesla", "pizza", "dance", "news")
        ]),
        ("user_posts", "Content Analysis", [
            ("cristiano", "charlidamelio")
        ]),
        ("music_search", "Music Trend Tracking", [
            ("pop", "classical")
        ])
    ]
    
    for endpoint_type, description, test_data in test_scenarios:
        print(f"🔧 TESTING: {description}")
        print("-" * 40)
        
        endpoint_results = []
        
        for item in test_data:
            try:
                if endpoint_type == "user_info":
                    result = client.tiktok.user_info_from_username(username=item)
                    
                elif endpoint_type == "hashtag_search":
                    result = client.tiktok.hashtag_search(hashtag=item, cursor=0)
                    
                elif endpoint_type == "keyword_search":
                    result = client.tiktok.keyword_search(keyword=item, period="30")
                    
                elif endpoint_type == "user_posts":
                    result = client.tiktok.user_posts_from_username(username=item, depth=1)
                    
                elif endpoint_type == "music_search":
                    result = client.tiktok.music_search(keyword=item, sorting="0", filter_by="0")
                
                units = safe_int(result.units_charged)
                print(f"   ✅ {item}: Success ({units} units)")
                endpoint_results.append(True)
                total_units += units
                
            except Exception as e:
                print(f"   ❌ {item}: {str(e)[:50]}...")
                endpoint_results.append(False)
            
            time.sleep(0.5)  # Be nice to the API
        
        results[endpoint_type] = endpoint_results
        success_rate = sum(endpoint_results) / len(endpoint_results) * 100
        print(f"   📊 Success Rate: {success_rate:.1f}%")
        print()
    
    # Summary
    print("=" * 60)
    print("📋 VALIDATION SUMMARY")
    print("=" * 60)
    
    all_tests = []
    for endpoint_results in results.values():
        all_tests.extend(endpoint_results)
    
    overall_success = sum(all_tests) / len(all_tests) * 100
    
    print(f"🎯 Overall Success Rate: {overall_success:.1f}%")
    print(f"🔢 Total Units Used: {total_units}/1500")
    print(f"📊 Estimated Daily Capacity: ~{1500 // (total_units // sum(all_tests)) if sum(all_tests) > 0 else 'Unknown'} calls")
    
    if overall_success >= 90:
        print("\n🚀 READY FOR PRODUCTION!")
        print("   ✅ All endpoints working reliably")
        print("   ✅ Multi-agent system can proceed")
    elif overall_success >= 70:
        print("\n✅ GOOD TO PROCEED")
        print("   ⚠️  Some endpoints may need retry logic")
    else:
        print("\n❌ REQUIRES ATTENTION")
        print("   🔧 Significant issues need addressing")
    
    return overall_success, total_units, results

if __name__ == "__main__":
    validate_api() 