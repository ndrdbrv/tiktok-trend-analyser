#!/usr/bin/env python3
"""
@tjr TikTok Account Analysis
===========================

Comprehensive analysis of @tjr using Apify TikTok Scraper
"""

import asyncio
import json
from datetime import datetime
from apify_client import ApifyClient

async def analyze_tjr_account():
    """
    Complete analysis of @tjr TikTok account
    """
    
    print("🔍 COMPREHENSIVE @TJR ANALYSIS")
    print("=" * 50)
    print("Account: https://www.tiktok.com/@tjr")
    print()
    
    api_token = "your-apify-token-here"
    client = ApifyClient(api_token)
    
    # ============================================================================
    # STEP 1: GET PROFILE DATA
    # ============================================================================
    
    print("📊 STEP 1: PROFILE ANALYSIS")
    print("-" * 30)
    
    try:
        # Get @tjr profile and recent videos
        run_input = {
            "profiles": ["https://www.tiktok.com/@tjr"],
            "resultsPerPage": 20,  # Get more videos for better analysis
            "shouldDownloadVideos": False,
            "shouldDownloadCovers": False
        }
        
        print("🔍 Scraping @tjr profile and videos...")
        
        run = client.actor("clockworks/tiktok-scraper").call(
            run_input=run_input,
            timeout_secs=300
        )
        
        print("✅ Profile scraping completed!")
        
        # Get all results
        results = []
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            results.append(item)
        
        print(f"📄 Retrieved {len(results)} items")
        
        if not results:
            print("❌ No data retrieved")
            return
        
        # Find profile data (usually first item has authorMeta with full profile)
        profile_data = None
        videos = []
        
        for item in results:
            if "authorMeta" in item:
                author = item["authorMeta"]
                
                # If this is detailed profile data
                if "fans" in author:  # Profile data has 'fans', video data might not
                    if profile_data is None:
                        profile_data = author
                
                # This is a video
                videos.append(item)
        
        # ============================================================================
        # STEP 2: PROFILE INSIGHTS
        # ============================================================================
        
        if profile_data:
            print(f"\n👤 @TJR PROFILE OVERVIEW:")
            print("=" * 35)
            print(f"📝 Display Name: {profile_data.get('nickName', 'N/A')}")
            print(f"👥 Followers: {profile_data.get('fans', 0):,}")
            print(f"👁️ Following: {profile_data.get('following', 0):,}")
            print(f"❤️ Total Likes: {profile_data.get('heart', 0):,}")
            print(f"🎬 Total Videos: {profile_data.get('video', 0):,}")
            print(f"✅ Verified: {'YES' if profile_data.get('verified', False) else 'NO'}")
            print(f"🔒 Private: {'YES' if profile_data.get('privateAccount', False) else 'NO'}")
            print(f"📄 Bio: {profile_data.get('signature', 'No bio')}")
            
            # Calculate key metrics
            followers = profile_data.get('fans', 0)
            total_likes = profile_data.get('heart', 0)
            total_videos = profile_data.get('video', 0)
            
            if followers > 0 and total_videos > 0:
                avg_likes_per_video = total_likes / total_videos
                engagement_rate = (total_likes / total_videos) / followers * 100 if followers > 0 else 0
                
                print(f"\n📈 ENGAGEMENT METRICS:")
                print(f"  📊 Avg Likes/Video: {avg_likes_per_video:,.0f}")
                print(f"  📊 Engagement Rate: {engagement_rate:.2f}%")
                
                # Determine creator tier
                if followers >= 1_000_000:
                    tier = "🌟 MEGA INFLUENCER"
                elif followers >= 100_000:
                    tier = "⭐ MACRO INFLUENCER"
                elif followers >= 10_000:
                    tier = "✨ MICRO INFLUENCER"
                else:
                    tier = "💫 NANO INFLUENCER"
                
                print(f"  🏆 Creator Tier: {tier}")
        
        # ============================================================================
        # STEP 3: VIDEO CONTENT ANALYSIS
        # ============================================================================
        
        print(f"\n🎬 VIDEO CONTENT ANALYSIS:")
        print("=" * 35)
        print(f"📹 Analyzing {len(videos)} recent videos...")
        
        if videos:
            # Sort videos by creation time (newest first)
            sorted_videos = sorted(videos, 
                                 key=lambda x: x.get('createTime', 0), 
                                 reverse=True)
            
            total_views = sum(v.get('playCount', 0) for v in videos)
            total_likes = sum(v.get('diggCount', 0) for v in videos)
            total_comments = sum(v.get('commentCount', 0) for v in videos)
            total_shares = sum(v.get('shareCount', 0) for v in videos)
            
            print(f"\n📊 RECENT CONTENT PERFORMANCE:")
            print(f"  👀 Total Views: {total_views:,}")
            print(f"  ❤️ Total Likes: {total_likes:,}")
            print(f"  💬 Total Comments: {total_comments:,}")
            print(f"  🔄 Total Shares: {total_shares:,}")
            
            if len(videos) > 0:
                avg_views = total_views / len(videos)
                avg_likes = total_likes / len(videos)
                avg_engagement_rate = (total_likes + total_comments + total_shares) / total_views * 100 if total_views > 0 else 0
                
                print(f"  📈 Avg Views/Video: {avg_views:,.0f}")
                print(f"  📈 Avg Likes/Video: {avg_likes:,.0f}")
                print(f"  📈 Avg Engagement Rate: {avg_engagement_rate:.2f}%")
            
            # ============================================================================
            # STEP 4: TOP PERFORMING VIDEOS
            # ============================================================================
            
            print(f"\n🔥 TOP PERFORMING VIDEOS:")
            print("-" * 30)
            
            # Sort by engagement (likes + comments + shares)
            for i, video in enumerate(sorted_videos[:5], 1):
                views = video.get('playCount', 0)
                likes = video.get('diggCount', 0)
                comments = video.get('commentCount', 0)
                shares = video.get('shareCount', 0)
                total_engagement = likes + comments + shares
                engagement_rate = (total_engagement / views * 100) if views > 0 else 0
                
                description = video.get('text', 'No description')[:80]
                video_url = video.get('webVideoUrl', 'N/A')
                
                print(f"\n{i}. 📹 VIDEO ANALYSIS:")
                print(f"   📝 \"{description}...\"")
                print(f"   👀 {views:,} views | ❤️ {likes:,} likes | 💬 {comments:,} comments")
                print(f"   📊 {engagement_rate:.2f}% engagement rate")
                print(f"   🔗 {video_url}")
                
                # Analyze hashtags
                hashtags = video.get('hashtags', [])
                if hashtags:
                    print(f"   🏷️ Hashtags: {', '.join([f'#{tag}' for tag in hashtags[:5]])}")
            
            # ============================================================================
            # STEP 5: CONTENT THEMES & HASHTAG ANALYSIS
            # ============================================================================
            
            print(f"\n🎯 CONTENT THEMES ANALYSIS:")
            print("-" * 30)
            
            # Analyze all hashtags
            all_hashtags = []
            startup_keywords = ['startup', 'business', 'entrepreneur', 'app', 'tech', 'advice', 'tips']
            startup_content_count = 0
            
            for video in videos:
                hashtags = video.get('hashtags', [])
                all_hashtags.extend(hashtags)
                
                # Check for startup/business content
                text = video.get('text', '').lower()
                if any(keyword in text for keyword in startup_keywords):
                    startup_content_count += 1
            
            # Count hashtag frequency
            hashtag_counts = {}
            for tag in all_hashtags:
                hashtag_counts[tag] = hashtag_counts.get(tag, 0) + 1
            
            # Top hashtags
            top_hashtags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            print(f"🏷️ TOP HASHTAGS:")
            for hashtag, count in top_hashtags:
                print(f"  #{hashtag}: {count} videos")
            
            # Startup content analysis
            startup_percentage = (startup_content_count / len(videos) * 100) if videos else 0
            print(f"\n🚀 STARTUP CONTENT ANALYSIS:")
            print(f"  📊 {startup_content_count}/{len(videos)} videos contain startup/business keywords")
            print(f"  📈 {startup_percentage:.1f}% of content is startup-related")
            
            # ============================================================================
            # STEP 6: VIRAL POTENTIAL ASSESSMENT
            # ============================================================================
            
            print(f"\n🔮 VIRAL POTENTIAL ASSESSMENT:")
            print("-" * 35)
            
            if videos:
                # Find top performing video for viral analysis
                top_video = max(videos, key=lambda x: x.get('diggCount', 0) + x.get('commentCount', 0) + x.get('shareCount', 0))
                
                top_views = top_video.get('playCount', 0)
                top_likes = top_video.get('diggCount', 0)
                top_comments = top_video.get('commentCount', 0)
                top_shares = top_video.get('shareCount', 0)
                top_engagement = (top_likes + top_comments + top_shares) / top_views * 100 if top_views > 0 else 0
                
                print(f"🏆 BEST PERFORMING VIDEO:")
                print(f"  📝 \"{top_video.get('text', '')[:60]}...\"")
                print(f"  📊 {top_engagement:.2f}% engagement rate")
                print(f"  👀 {top_views:,} views")
                
                # Viral indicators
                viral_indicators = []
                if top_engagement > 5:
                    viral_indicators.append("✅ High engagement rate")
                if top_shares > top_views * 0.01:  # >1% share rate
                    viral_indicators.append("✅ Strong shareability")
                if len(top_video.get('hashtags', [])) >= 3:
                    viral_indicators.append("✅ Good hashtag usage")
                
                if viral_indicators:
                    print(f"\n🚀 VIRAL INDICATORS:")
                    for indicator in viral_indicators:
                        print(f"  {indicator}")
                
                # Overall assessment
                if top_engagement > 8:
                    viral_assessment = "🔥 HIGH viral potential"
                elif top_engagement > 4:
                    viral_assessment = "📈 MEDIUM viral potential" 
                else:
                    viral_assessment = "📊 STANDARD performance"
                
                print(f"\n🎯 OVERALL ASSESSMENT: {viral_assessment}")
        
        else:
            print("❌ No video data found")
    
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
    
    print(f"\n✅ @TJR ANALYSIS COMPLETE")
    print("=" * 30)
    print("🔍 Ready to analyze any other accounts!")

if __name__ == "__main__":
    asyncio.run(analyze_tjr_account()) 