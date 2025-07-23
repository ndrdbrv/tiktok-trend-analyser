#!/usr/bin/env python3
"""
Debug Creator Data Collection
============================

Debug script to see exactly what creator data we're collecting and why
the filtering might not be working.
"""

import asyncio
from agents.ingestion_agent import StartupContentIngestion

async def debug_creator_data():
    """Debug what creator data we're actually collecting"""
    
    print("🔍 DEBUGGING CREATOR DATA COLLECTION")
    print("=" * 50)
    
    api_key = "MZTq3h5VIyi0CjKt"
    ingestion = StartupContentIngestion(api_key)
    
    # Test with just one hashtag first
    result = await ingestion.collect_startup_hashtag_data("startup", max_videos=10)
    
    if result.get("success"):
        videos = result.get("startup_videos", [])
        print(f"✅ Found {len(videos)} videos for #startup")
        
        # Debug each video
        for i, video in enumerate(videos[:5], 1):
            print(f"\n{i}. Creator: @{video.creator_username}")
            print(f"   Followers: {video.creator_followers:,}")
            print(f"   Engagement: {video.engagement_rate:.1%}")
            print(f"   Business relevance: {video.business_relevance_score:.1%}")
            print(f"   Description: {video.description[:100]}...")
            print(f"   Views: {video.views:,}")
        
        # Check business relevance distribution
        business_scores = [v.business_relevance_score for v in videos]
        if business_scores:
            print(f"\n📊 Business Relevance Analysis:")
            print(f"   Min score: {min(business_scores):.1%}")
            print(f"   Max score: {max(business_scores):.1%}")
            print(f"   Avg score: {sum(business_scores)/len(business_scores):.1%}")
            print(f"   Videos >10% business: {sum(1 for s in business_scores if s > 0.1)}")
            print(f"   Videos >20% business: {sum(1 for s in business_scores if s > 0.2)}")
    
    else:
        print(f"❌ Error: {result.get('error')}")

if __name__ == "__main__":
    asyncio.run(debug_creator_data()) 