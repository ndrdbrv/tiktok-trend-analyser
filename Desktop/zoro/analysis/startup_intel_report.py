#!/usr/bin/env python3
"""
Startup Intelligence Report
==========================

Shows top performing startup creators, their viral videos, and trending hashtags
with direct TikTok links and performance metrics.
"""

import asyncio
from agents.ingestion_agent import StartupContentIngestion

async def generate_startup_intel_report():
    """Generate startup intelligence report with top creators and trending content"""
    
    print("🕵️ STARTUP INTELLIGENCE REPORT")
    print("=" * 60)
    print("Live analysis of top performing startup creators and content")
    print()
    
    api_key = "MZTq3h5VIyi0CjKt"
    ingestion = StartupContentIngestion(api_key)
    
    # Analyze hot startup hashtags
    hot_hashtags = ["startup", "entrepreneur", "businesstips", "founder", "growth", "business"]
    
    all_creators = {}
    viral_videos = []
    hashtag_performance = {}
    
    print("📊 ANALYZING TOP STARTUP HASHTAGS...")
    print("-" * 40)
    
    for hashtag in hot_hashtags:
        print(f"🔍 #{hashtag}...")
        
        result = await ingestion.collect_startup_hashtag_data(hashtag, max_videos=15)
        
        if result.get("success"):
            videos = result.get("startup_videos", [])
            print(f"   ✅ {len(videos)} videos found")
            
            # Track hashtag performance
            if videos:
                avg_engagement = sum(v.engagement_rate for v in videos) / len(videos)
                total_views = sum(v.views for v in videos)
                
                hashtag_performance[hashtag] = {
                    "video_count": len(videos),
                    "avg_engagement": avg_engagement,
                    "total_views": total_views,
                    "trending_score": avg_engagement * len(videos)
                }
            
            # Collect viral videos and creators
            for video in videos:
                if video.engagement_rate > 0.10:  # 10%+ engagement = viral
                    viral_videos.append(video)
                
                creator = video.creator_username
                if creator not in all_creators:
                    all_creators[creator] = {
                        "username": creator,
                        "videos": [],
                        "total_views": 0,
                        "avg_engagement": 0,
                        "business_score": 0
                    }
                
                all_creators[creator]["videos"].append({
                    "description": video.description,
                    "views": video.views,
                    "likes": video.likes,
                    "comments": video.comments,
                    "shares": video.shares,
                    "engagement_rate": video.engagement_rate,
                    "business_relevance": video.business_relevance_score,
                    "tiktok_link": f"https://www.tiktok.com/@{creator}",
                    "hashtag_source": hashtag
                })
        
        await asyncio.sleep(0.5)  # Rate limiting
    
    # Calculate creator performance
    for creator_data in all_creators.values():
        videos = creator_data["videos"]
        if videos:
            creator_data["total_views"] = sum(v["views"] for v in videos)
            creator_data["avg_engagement"] = sum(v["engagement_rate"] for v in videos) / len(videos)
            creator_data["business_score"] = sum(v["business_relevance"] for v in videos) / len(videos)
            creator_data["video_count"] = len(videos)
    
    # Generate report
    print(f"\n🎯 TOP PERFORMING STARTUP CREATORS")
    print("=" * 60)
    
    # Sort creators by performance
    top_creators = sorted(
        all_creators.items(),
        key=lambda x: x[1]["avg_engagement"] * x[1]["business_score"],
        reverse=True
    )
    
    for i, (username, data) in enumerate(top_creators[:10], 1):
        if data["video_count"] > 0:
            print(f"\n{i}. @{username}")
            print(f"   📊 Performance: {data['avg_engagement']:.1%} avg engagement")
            print(f"   🎯 Business Focus: {data['business_score']:.1%}")
            print(f"   📹 Content: {data['video_count']} videos analyzed")
            print(f"   👀 Reach: {data['total_views']:,} total views")
            
            # Show their best video
            best_video = max(data["videos"], key=lambda x: x["engagement_rate"])
            print(f"   🔥 TOP VIDEO: \"{best_video['description'][:70]}...\"")
            print(f"      📈 {best_video['engagement_rate']:.1%} engagement")
            print(f"      👀 {best_video['views']:,} views | ❤️ {best_video['likes']:,} likes")
            print(f"      🔗 LINK: {best_video['tiktok_link']}")
            print(f"      🏷️ Found via: #{best_video['hashtag_source']}")
    
    print(f"\n🔥 HOTTEST HASHTAGS RIGHT NOW")
    print("=" * 40)
    
    # Sort hashtags by trending score
    trending_hashtags = sorted(
        hashtag_performance.items(),
        key=lambda x: x[1]["trending_score"],
        reverse=True
    )
    
    for i, (hashtag, data) in enumerate(trending_hashtags, 1):
        status = "🔥 HOT" if data["trending_score"] > 2 else "📈 GROWING"
        print(f"{i}. {status} #{hashtag}")
        print(f"   📊 {data['video_count']} videos, {data['avg_engagement']:.1%} avg engagement")
        print(f"   👀 {data['total_views']:,} total views")
        print(f"   🔥 Trending Score: {data['trending_score']:.1f}")
        print()
    
    print(f"\n🚀 MOST VIRAL STARTUP VIDEOS")
    print("=" * 40)
    
    # Sort by engagement rate
    top_viral = sorted(viral_videos, key=lambda x: x.engagement_rate, reverse=True)
    
    for i, video in enumerate(top_viral[:8], 1):
        print(f"\n{i}. @{video.creator_username}")
        print(f"   📝 \"{video.description[:80]}...\"")
        print(f"   📊 {video.engagement_rate:.1%} engagement")
        print(f"   👀 {video.views:,} views | ❤️ {video.likes:,} likes | 💬 {video.comments:,} comments")
        print(f"   🎯 Business relevance: {video.business_relevance_score:.1%}")
        print(f"   🔗 WATCH: https://www.tiktok.com/@{video.creator_username}")
    
    # Analysis insights
    print(f"\n💡 KEY INSIGHTS FOR YOUR STARTUP CONTENT")
    print("=" * 60)
    
    if trending_hashtags:
        top_hashtag = trending_hashtags[0][0]
        print(f"🏷️ USE THESE HOT HASHTAGS: #{top_hashtag}")
        for hashtag, _ in trending_hashtags[1:4]:
            print(f"   #{hashtag}")
    
    if top_creators:
        print(f"\n👥 STUDY THESE TOP CREATORS:")
        for username, data in top_creators[:3]:
            print(f"   @{username} - {data['avg_engagement']:.1%} engagement")
    
    if top_viral:
        print(f"\n🎬 CONTENT PATTERNS TO COPY:")
        for video in top_viral[:3]:
            hook = video.description.split('.')[0].split('!')[0][:50]
            print(f"   🎯 \"{hook}...\" ({video.engagement_rate:.1%} engagement)")
    
    print(f"\n📊 API Usage: {ingestion.daily_units_used}/1500 units")
    print(f"✅ ANALYSIS COMPLETE - {len(all_creators)} creators analyzed")

if __name__ == "__main__":
    asyncio.run(generate_startup_intel_report()) 