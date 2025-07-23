#!/usr/bin/env python3
"""
Live Startup Content Ingestion Test
===================================

Test script to run live data ingestion for startup/entrepreneurship content
and generate real video recommendations.
"""

import asyncio
import json
from datetime import datetime
from agents.ingestion_agent import IngestionAgent

async def test_live_startup_ingestion():
    """Test live startup content ingestion"""
    
    print("🚀 LIVE STARTUP CONTENT INGESTION TEST")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Initialize agent with our validated API key
    config = {
        "ensemble_api_key": "MZTq3h5VIyi0CjKt"  # Our validated Wooden tier key
    }
    
    try:
        agent = IngestionAgent(config)
        print("✅ Ingestion Agent initialized successfully")
        
        # Test 1: Monitor top startup hashtags
        print("\n📊 STEP 1: Monitoring Top Startup Hashtags")
        print("-" * 40)
        
        startup_hashtags = ["startup", "entrepreneur", "businesstips", "startuplife", "founder"]
        result = await agent.ingest_startup_trends(startup_hashtags)
        
        if result.success:
            data = result.result_data
            trending_summary = data.get("trending_summary", {})
            
            print(f"✅ Found {trending_summary.get('total_startup_videos', 0)} startup videos")
            print(f"🏷️ Trending hashtags: {len(trending_summary.get('trending_hashtags', []))}")
            print(f"👥 Top creators: {len(trending_summary.get('top_creators', []))}")
            print(f"📈 Avg engagement: {trending_summary.get('avg_engagement_rate', 0):.1%}")
            
            # Show trending hashtags
            if trending_summary.get('trending_hashtags'):
                print(f"\n🔥 Top Trending Startup Hashtags:")
                for i, hashtag_data in enumerate(trending_summary['trending_hashtags'][:5], 1):
                    print(f"  {i}. #{hashtag_data['hashtag']} - Score: {hashtag_data['trending_score']:.2f}")
            
            # Show high potential videos
            if trending_summary.get('high_potential_videos'):
                print(f"\n🎯 High Potential Videos:")
                for i, video in enumerate(trending_summary['high_potential_videos'][:3], 1):
                    print(f"  {i}. @{video['creator']}: {video['description']}")
                    print(f"     📊 {video['engagement_rate']:.1%} engagement, {video['views']:,} views")
            
        else:
            print(f"❌ Error: {result.error_message}")
            return
        
        # Test 2: Get specific video recommendations
        print(f"\n🎬 STEP 2: Generating Video Recommendations")
        print("-" * 40)
        
        recommendations = await agent.get_startup_video_recommendations()
        
        if "error" not in recommendations:
            immediate_ops = recommendations.get("immediate_opportunities", [])
            optimal_hashtags = recommendations.get("optimal_hashtags", [])
            
            print(f"📋 Found {len(immediate_ops)} immediate opportunities")
            print(f"🏷️ Found {len(optimal_hashtags)} optimal hashtags")
            
            # Show immediate opportunities
            if immediate_ops:
                print(f"\n🔥 IMMEDIATE VIDEO OPPORTUNITIES:")
                for i, opp in enumerate(immediate_ops[:3], 1):
                    print(f"  {i}. {opp['why_viral']}")
                    print(f"     💡 Inspiration: {opp['inspiration']}")
                    print(f"     🎬 Format: {opp['format']}")
                    print()
            
            # Show optimal hashtags
            if optimal_hashtags:
                print(f"🏷️ OPTIMAL HASHTAGS TO USE:")
                for i, hashtag_data in enumerate(optimal_hashtags[:5], 1):
                    print(f"  {i}. {hashtag_data['hashtag']} - Score: {hashtag_data['trending_score']:.2f}")
        
        else:
            print(f"❌ Error getting recommendations: {recommendations['error']}")
        
        # Show API usage
        api_usage = data.get("api_usage", {})
        print(f"\n💰 API USAGE SUMMARY:")
        print(f"   Units used: {api_usage.get('total_units_used', 0)}/{api_usage.get('daily_limit', 1500)}")
        print(f"   Usage: {api_usage.get('usage_percentage', 0):.1f}% of daily limit")
        print(f"   Remaining: {api_usage.get('remaining_units', 0)} units")
        
        print(f"\n🎯 STARTUP CONTENT RECOMMENDATIONS:")
        print("=" * 60)
        
        # Generate specific video ideas based on what's trending
        if trending_summary.get('high_potential_videos'):
            print("📹 VIDEO IDEAS FOR YOUR STARTUP:")
            
            for i, video in enumerate(trending_summary['high_potential_videos'][:3], 1):
                print(f"\n{i}. Inspired by @{video['creator']}:")
                print(f"   🎬 Create: Similar content about your startup journey")
                print(f"   📝 Topic: {video['description'][:50]}...")
                print(f"   🎯 Why it works: {video['engagement_rate']:.1%} engagement rate")
                
                # Suggest hashtags based on trending ones
                if optimal_hashtags:
                    suggested_hashtags = [h['hashtag'] for h in optimal_hashtags[:3]]
                    print(f"   🏷️ Use hashtags: {', '.join(suggested_hashtags)}")
        
        print(f"\n✅ Live startup content ingestion completed!")
        
    except Exception as e:
        print(f"❌ Error during ingestion: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_specific_hashtag():
    """Test analysis of a specific hashtag"""
    
    print("\n🔍 TESTING SPECIFIC HASHTAG ANALYSIS")
    print("=" * 40)
    
    config = {"ensemble_api_key": "MZTq3h5VIyi0CjKt"}
    agent = IngestionAgent(config)
    
    # Test specific hashtag
    hashtag = "startup"
    result = await agent.ingest_hashtag_videos(hashtag, count=20)
    
    if result.success:
        data = result.result_data
        print(f"✅ Analyzed #{hashtag}")
        print(f"📊 Business relevant videos: {len(data.get('startup_videos', []))}")
        print(f"🎯 Business relevance filter: {data.get('business_relevance_filter', 'N/A')}")
    else:
        print(f"❌ Error analyzing #{hashtag}: {result.error_message}")

if __name__ == "__main__":
    print("🚀 Starting Live Startup Content Analysis...")
    
    # Run the tests
    asyncio.run(test_live_startup_ingestion())
    
    # Uncomment to test specific hashtag analysis
    # asyncio.run(test_specific_hashtag())
    
    print("\n🎉 Testing completed!") 