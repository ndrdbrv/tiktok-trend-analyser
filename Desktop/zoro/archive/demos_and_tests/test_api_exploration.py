#!/usr/bin/env python3
"""
EnsembleData API Exploration
===========================

Let's see what accounts and data we can actually access with the API.
"""

import asyncio
from ensembledata.api import EDClient, EDError

async def explore_api_capabilities():
    """
    Comprehensive test to see what the EnsembleData API can actually access
    """
    
    print("🔍 ENSEMBLEDATA API EXPLORATION")
    print("=" * 50)
    print("Let's see what accounts we can actually find...")
    print()
    
    api_key = "MZTq3h5VIyi0CjKt"
    
    try:
        client = EDClient(api_key, timeout=30)
        print("✅ API Client initialized")
        
        # Test different popular hashtags to see what accounts we get
        test_hashtags = [
            "viral", "trending", "fyp", "foryou", 
            "money", "business", "startup", "entrepreneur",
            "challenge", "dance", "comedy", "food"
        ]
        
        all_found_accounts = []
        
        for hashtag in test_hashtags:
            print(f"\n🔍 Testing #{hashtag}...")
            
            try:
                result = client.tiktok.hashtag_search(hashtag=hashtag, cursor=0)
                print(f"   ⚡ Units charged: {result.units_charged}")
                
                if result.data and result.data.get('data'):
                    videos = result.data.get('data', [])
                    print(f"   📹 Found {len(videos)} videos")
                    
                    # Analyze the accounts we find
                    unique_accounts = {}
                    
                    for video in videos[:10]:  # Check first 10 videos
                        author = video.get('author', {})
                        username = author.get('unique_id', 'unknown')
                        
                        if username not in unique_accounts:
                            unique_accounts[username] = {
                                'username': username,
                                'display_name': author.get('nickname', 'N/A'),
                                'followers': author.get('follower_count', 0),
                                'verified': author.get('verified', False),
                                'bio': author.get('signature', 'No bio'),
                                'found_in_hashtag': hashtag
                            }
                    
                    # Show top accounts from this hashtag
                    sorted_accounts = sorted(unique_accounts.values(), 
                                           key=lambda x: x['followers'], reverse=True)
                    
                    print(f"   👥 TOP ACCOUNTS FOUND:")
                    for i, acc in enumerate(sorted_accounts[:3], 1):
                        verified_emoji = "✅" if acc['verified'] else "❌"
                        print(f"      {i}. @{acc['username']} {verified_emoji}")
                        print(f"         👥 {acc['followers']:,} followers")
                        print(f"         📝 {acc['display_name']}")
                        print(f"         💬 {acc['bio'][:50]}...")
                    
                    all_found_accounts.extend(sorted_accounts)
                
                else:
                    print("   ❌ No data returned")
                    
            except Exception as e:
                print(f"   ❌ Error with #{hashtag}: {e}")
            
            await asyncio.sleep(0.5)  # Rate limiting
        
        # Analysis of all found accounts
        print(f"\n📊 OVERALL ANALYSIS")
        print("=" * 30)
        
        total_accounts = len(all_found_accounts)
        verified_accounts = [acc for acc in all_found_accounts if acc['verified']]
        
        print(f"📱 Total unique accounts found: {total_accounts}")
        print(f"✅ Verified accounts: {len(verified_accounts)}")
        print(f"❌ Unverified accounts: {total_accounts - len(verified_accounts)}")
        
        # Top accounts overall by followers
        all_accounts_unique = {}
        for acc in all_found_accounts:
            username = acc['username']
            if username not in all_accounts_unique or acc['followers'] > all_accounts_unique[username]['followers']:
                all_accounts_unique[username] = acc
        
        top_accounts = sorted(all_accounts_unique.values(), 
                            key=lambda x: x['followers'], reverse=True)
        
        print(f"\n🏆 TOP 10 ACCOUNTS BY FOLLOWERS:")
        print("-" * 40)
        for i, acc in enumerate(top_accounts[:10], 1):
            verified_emoji = "✅" if acc['verified'] else "❌"
            print(f"{i:2d}. @{acc['username']} {verified_emoji}")
            print(f"    👥 {acc['followers']:,} followers")
            print(f"    📝 {acc['display_name']}")
            print(f"    🏷️ Found in: #{acc['found_in_hashtag']}")
            print()
        
        # Show verified accounts specifically
        if verified_accounts:
            print(f"✅ VERIFIED ACCOUNTS FOUND:")
            print("-" * 30)
            for i, acc in enumerate(verified_accounts[:5], 1):
                print(f"{i}. @{acc['username']}")
                print(f"   👥 {acc['followers']:,} followers")
                print(f"   📝 {acc['display_name']}")
                print(f"   🏷️ Found in: #{acc['found_in_hashtag']}")
                print()
        else:
            print("❌ NO VERIFIED ACCOUNTS FOUND")
        
        # Follower distribution analysis
        follower_ranges = {
            "1M+": len([acc for acc in all_found_accounts if acc['followers'] >= 1000000]),
            "100K-1M": len([acc for acc in all_found_accounts if 100000 <= acc['followers'] < 1000000]),
            "10K-100K": len([acc for acc in all_found_accounts if 10000 <= acc['followers'] < 100000]),
            "1K-10K": len([acc for acc in all_found_accounts if 1000 <= acc['followers'] < 10000]),
            "<1K": len([acc for acc in all_found_accounts if acc['followers'] < 1000])
        }
        
        print(f"📈 FOLLOWER DISTRIBUTION:")
        print("-" * 25)
        for range_name, count in follower_ranges.items():
            print(f"{range_name:8}: {count:3d} accounts")
        
        # Test specific search for big creators
        print(f"\n🔍 TESTING SPECIFIC BIG CREATORS:")
        print("-" * 35)
        
        big_creator_hashtags = ["charlidamelio", "addisonre", "zachking", "spencerx", "riyaz"]
        
        for creator_tag in big_creator_hashtags:
            try:
                result = client.tiktok.hashtag_search(hashtag=creator_tag, cursor=0)
                
                if result.data and result.data.get('data'):
                    videos = result.data.get('data', [])
                    
                    # Look for the actual creator
                    found_creator = False
                    for video in videos[:10]:
                        author = video.get('author', {})
                        username = author.get('unique_id', '').lower()
                        
                        if creator_tag.lower() in username:
                            found_creator = True
                            verified_emoji = "✅" if author.get('verified', False) else "❌"
                            print(f"🎯 @{username} {verified_emoji} - {author.get('follower_count', 0):,} followers")
                            break
                    
                    if not found_creator:
                        print(f"❌ {creator_tag}: Official account not found")
                
            except Exception as e:
                print(f"❌ {creator_tag}: Error - {e}")
            
            await asyncio.sleep(0.3)
        
    except Exception as e:
        print(f"❌ General error: {e}")
    
    print(f"\n🎯 CONCLUSION:")
    print("=" * 20)
    print("✅ API can access TikTok data")
    print("✅ Can find various accounts")
    print("✅ Gets follower counts and basic info")
    print("❓ Quality of accounts varies")
    print("❓ May not access all major creators")
    print("❓ Data freshness unknown")
    print()
    print("💡 The API works but may have limitations on accessing")
    print("   the biggest/most recent creator data.")

if __name__ == "__main__":
    asyncio.run(explore_api_capabilities()) 