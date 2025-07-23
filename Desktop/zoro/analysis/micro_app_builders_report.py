#!/usr/bin/env python3
"""
Micro App Builders Intelligence Report
=====================================

Finds startup creators building apps with under 10k followers
and provides direct video links to their content.
"""

import asyncio
from agents.ingestion_agent import StartupContentIngestion

async def find_micro_app_builders():
    """Find micro-influencers building apps with under 10k followers"""
    
    print("🔍 MICRO APP BUILDERS INTELLIGENCE")
    print("=" * 60)
    print("Finding creators building apps with <10k followers")
    print()
    
    api_key = "MZTq3h5VIyi0CjKt"
    ingestion = StartupContentIngestion(api_key)
    
    # App-specific hashtags and keywords
    app_hashtags = [
        "app", "appdev", "appdevelopment", "mobileapp", "webapp", 
        "coding", "programming", "tech", "saas", "software"
    ]
    
    micro_app_builders = {}
    app_videos = []
    
    print("🔍 SCANNING APP-BUILDING HASHTAGS...")
    print("-" * 50)
    
    for hashtag in app_hashtags:
        print(f"📱 Analyzing #{hashtag}...")
        
        result = await ingestion.collect_startup_hashtag_data(hashtag, max_videos=20)
        
        if result.get("success"):
            videos = result.get("startup_videos", [])
            print(f"   ✅ {len(videos)} videos found")
            
            # Filter for app-building content
            for video in videos:
                description = video.description.lower()
                
                # Check if it's app-related content
                app_keywords = [
                    "app", "application", "mobile app", "web app", "coding", 
                    "programming", "developer", "dev", "software", "build", 
                    "launch", "mvp", "prototype", "beta", "ios", "android"
                ]
                
                is_app_content = any(keyword in description for keyword in app_keywords)
                
                if is_app_content:
                    creator = video.creator_username
                    
                    # Track this creator
                    if creator not in micro_app_builders:
                        micro_app_builders[creator] = {
                            "username": creator,
                            "videos": [],
                            "total_engagement": 0,
                            "follower_estimate": "Unknown",  # We'll estimate from engagement
                            "app_focus_score": 0
                        }
                    
                    # Add video with more details
                    video_data = {
                        "video_id": getattr(video, 'video_id', 'unknown'),
                        "description": video.description,
                        "views": video.views,
                        "likes": video.likes,
                        "comments": video.comments,
                        "shares": video.shares,
                        "engagement_rate": video.engagement_rate,
                        "duration": getattr(video, 'duration', 'unknown'),
                        "hashtag_source": hashtag,
                        "profile_link": f"https://www.tiktok.com/@{creator}",
                        "video_link": f"https://www.tiktok.com/@{creator}/video/{getattr(video, 'video_id', '')}" if getattr(video, 'video_id', None) else f"https://www.tiktok.com/@{creator}",
                        "app_keywords_found": [kw for kw in app_keywords if kw in description]
                    }
                    
                    micro_app_builders[creator]["videos"].append(video_data)
                    app_videos.append(video_data)
        
        await asyncio.sleep(0.5)  # Rate limiting
    
    # Calculate metrics and estimate follower counts
    for creator_data in micro_app_builders.values():
        videos = creator_data["videos"]
        if videos:
            creator_data["video_count"] = len(videos)
            creator_data["avg_engagement"] = sum(v["engagement_rate"] for v in videos) / len(videos)
            creator_data["total_views"] = sum(v["views"] for v in videos)
            creator_data["app_focus_score"] = sum(len(v["app_keywords_found"]) for v in videos) / len(videos)
            
            # Estimate follower count from engagement patterns
            avg_views = creator_data["total_views"] / len(videos)
            if avg_views < 1000:
                creator_data["follower_estimate"] = "<1k"
            elif avg_views < 5000:
                creator_data["follower_estimate"] = "1k-5k"
            elif avg_views < 20000:
                creator_data["follower_estimate"] = "5k-10k"
            elif avg_views < 100000:
                creator_data["follower_estimate"] = "10k-50k"
            else:
                creator_data["follower_estimate"] = "50k+"
    
    # Filter for likely micro-influencers (under 10k followers)
    micro_creators = {
        username: data for username, data in micro_app_builders.items()
        if data.get("follower_estimate") in ["<1k", "1k-5k", "5k-10k"]
    }
    
    print(f"\n🎯 MICRO APP BUILDERS (<10K FOLLOWERS)")
    print("=" * 60)
    print(f"Found {len(micro_creators)} micro app builders")
    print()
    
    # Sort by app focus and engagement
    top_micro_builders = sorted(
        micro_creators.items(),
        key=lambda x: x[1]["app_focus_score"] * x[1]["avg_engagement"],
        reverse=True
    )
    
    for i, (username, data) in enumerate(top_micro_builders[:15], 1):
        print(f"{i}. @{username}")
        print(f"   👥 Estimated followers: {data['follower_estimate']}")
        print(f"   📊 Avg engagement: {data['avg_engagement']:.1%}")
        print(f"   📱 App focus score: {data['app_focus_score']:.1f}/5")
        print(f"   📹 Videos analyzed: {data['video_count']}")
        print(f"   👀 Total views: {data['total_views']:,}")
        print(f"   🔗 Profile: {data['videos'][0]['profile_link']}")
        
        # Show their best app-related video
        best_video = max(data["videos"], key=lambda x: x["engagement_rate"])
        print(f"   \n   🎬 BEST APP VIDEO:")
        print(f"      📝 \"{best_video['description'][:80]}...\"")
        print(f"      📊 {best_video['engagement_rate']:.1%} engagement")
        print(f"      👀 {best_video['views']:,} views | ❤️ {best_video['likes']:,} likes")
        print(f"      🏷️ Keywords: {', '.join(best_video['app_keywords_found'][:3])}")
        print(f"      🔗 DIRECT VIDEO LINK: {best_video['video_link']}")
        print(f"      📱 Found via: #{best_video['hashtag_source']}")
        
        # Show all their videos if they have multiple
        if len(data["videos"]) > 1:
            print(f"   \n   📋 ALL VIDEOS:")
            for j, video in enumerate(data["videos"], 1):
                print(f"      {j}. \"{video['description'][:50]}...\"")
                print(f"         📊 {video['engagement_rate']:.1%} engagement, {video['views']:,} views")
                print(f"         🔗 {video['video_link']}")
        
        print("\n" + "-" * 60 + "\n")
    
    # Show trending app development topics
    print(f"🔥 TRENDING APP DEVELOPMENT TOPICS")
    print("=" * 50)
    
    all_keywords = []
    for video in app_videos:
        all_keywords.extend(video["app_keywords_found"])
    
    keyword_counts = {}
    for keyword in all_keywords:
        keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
    
    trending_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
    
    for i, (keyword, count) in enumerate(trending_keywords[:10], 1):
        print(f"{i}. 🔥 '{keyword}' - {count} mentions")
    
    print(f"\n💡 CONTENT OPPORTUNITIES")
    print("=" * 40)
    print("📱 App development tutorials")
    print("🚀 MVP launch stories")
    print("💰 Revenue from small apps")
    print("🛠️ No-code app building")
    print("📈 App growth strategies")
    
    print(f"\n📊 ANALYSIS SUMMARY")
    print("=" * 30)
    print(f"✅ {len(micro_creators)} micro app builders found")
    print(f"📱 {len(app_videos)} app-related videos analyzed")
    print(f"⚡ API units used: {ingestion.daily_units_used}/1500")

if __name__ == "__main__":
    asyncio.run(find_micro_app_builders()) 