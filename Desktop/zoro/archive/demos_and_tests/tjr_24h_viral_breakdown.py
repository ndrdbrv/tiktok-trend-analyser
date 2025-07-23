#!/usr/bin/env python3
"""
@tjr 24-Hour Viral Content Breakdown
===================================

Detailed analysis of which specific videos went viral in last 24h and their topics
"""

import asyncio
from datetime import datetime, timedelta
from apify_client import ApifyClient

async def analyze_tjr_24h_viral_content():
    print("🔥 @TJR 24-HOUR VIRAL BREAKDOWN")
    print("=" * 50)
    print("🎯 Goal: Find which videos got most viral engagement in last 24h")
    print("📋 Focus: Likes + Comments + Shares = Total Engagement")
    print()
    
    api_token = "your-apify-token-here"
    client = ApifyClient(api_token)
    
    try:
        # Get more videos to ensure we capture full 24h
        run_input = {
            "profiles": ["https://www.tiktok.com/@tjr"],
            "resultsPerPage": 30,  # Get more to ensure 24h coverage
            "shouldDownloadVideos": False,
            "shouldDownloadCovers": False
        }
        
        print("🔍 Scraping @tjr recent videos...")
        
        run = client.actor("clockworks/tiktok-scraper").call(
            run_input=run_input,
            timeout_secs=300
        )
        
        # Get all results
        results = []
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            results.append(item)
        
        videos = [item for item in results if "authorMeta" in item]
        
        print(f"📹 Retrieved {len(videos)} videos")
        
        if not videos:
            print("❌ No videos found")
            return
        
        # Filter to last 24 hours
        now = datetime.now()
        cutoff_time = now - timedelta(hours=24)
        
        recent_videos = []
        for video in videos:
            create_time = video.get('createTime', 0)
            if create_time:
                video_date = datetime.fromtimestamp(create_time)
                if video_date >= cutoff_time:
                    recent_videos.append({
                        'video': video,
                        'date': video_date,
                        'total_engagement': video.get('diggCount', 0) + video.get('commentCount', 0) + video.get('shareCount', 0)
                    })
        
        # Sort by total engagement (most viral first)
        recent_videos.sort(key=lambda x: x['total_engagement'], reverse=True)
        
        print(f"\n📅 LAST 24 HOURS ANALYSIS:")
        print(f"⏰ Cutoff: {cutoff_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"🎬 Videos in last 24h: {len(recent_videos)}")
        
        if not recent_videos:
            print("❌ No videos found in last 24 hours")
            return
        
        # Calculate totals
        total_views_24h = sum(v['video'].get('playCount', 0) for v in recent_videos)
        total_engagement_24h = sum(v['total_engagement'] for v in recent_videos)
        
        print(f"📊 24h Totals: {total_views_24h:,} views | {total_engagement_24h:,} total engagement")
        print()
        
        # ============================================================================
        # TOP VIRAL VIDEOS BREAKDOWN
        # ============================================================================
        
        print("🔥 TOP VIRAL VIDEOS (Last 24h):")
        print("=" * 45)
        
        for i, item in enumerate(recent_videos[:10], 1):
            video = item['video']
            date = item['date']
            
            views = video.get('playCount', 0)
            likes = video.get('diggCount', 0)
            comments = video.get('commentCount', 0)
            shares = video.get('shareCount', 0)
            total_eng = item['total_engagement']
            
            engagement_rate = (total_eng / views * 100) if views > 0 else 0
            
            # Get video text/description
            description = video.get('text', '').strip()
            video_url = video.get('webVideoUrl', 'N/A')
            
            # Try to extract hashtags if any
            hashtags = video.get('hashtags', [])
            
            print(f"\n🏆 #{i} MOST VIRAL VIDEO:")
            print(f"📅 Posted: {date.strftime('%Y-%m-%d %H:%M')} ({(now - date).seconds//3600}h {((now - date).seconds//60)%60}m ago)")
            print(f"👀 Views: {views:,}")
            print(f"❤️ Likes: {likes:,}")
            print(f"💬 Comments: {comments:,}")
            print(f"🔄 Shares: {shares:,}")
            print(f"🔥 Total Engagement: {total_eng:,}")
            print(f"📈 Engagement Rate: {engagement_rate:.2f}%")
            
            # Analyze the content
            print(f"\n📝 CONTENT ANALYSIS:")
            if description:
                print(f"   📄 Description: \"{description}\"")
                
                # Try to infer topic from description
                description_lower = description.lower()
                potential_topics = []
                
                # Trading/Finance keywords
                if any(word in description_lower for word in ['trade', 'trading', 'profit', 'loss', 'market', 'stock', 'money', 'cash', 'pnl', 'day trading']):
                    potential_topics.append("💰 TRADING/FINANCE")
                
                # Motivational/Success keywords  
                if any(word in description_lower for word in ['success', 'grind', 'hustle', 'motivation', 'mindset', 'win', 'boss']):
                    potential_topics.append("🚀 MOTIVATION/SUCCESS")
                
                # Lifestyle keywords
                if any(word in description_lower for word in ['life', 'lifestyle', 'flex', 'rich', 'wealth', 'luxury']):
                    potential_topics.append("✨ LIFESTYLE")
                
                # Personal/Behind scenes
                if any(word in description_lower for word in ['me', 'my', 'personal', 'real', 'truth', 'honest']):
                    potential_topics.append("👤 PERSONAL")
                
                if potential_topics:
                    print(f"   🎯 Likely Topics: {' | '.join(potential_topics)}")
                else:
                    print(f"   🤔 Topic: UNCLEAR (minimal description)")
            else:
                print(f"   📄 Description: [NO TEXT - Video only content]")
                print(f"   🎯 Topic: VISUAL CONTENT (no description)")
            
            if hashtags:
                print(f"   🏷️ Hashtags: {', '.join([f'#{tag}' for tag in hashtags])}")
            else:
                print(f"   🏷️ Hashtags: None")
            
            print(f"   🔗 URL: {video_url}")
            
            # Performance tier
            if engagement_rate > 10:
                tier = "🔥 SUPER VIRAL"
            elif engagement_rate > 7:
                tier = "📈 HIGH VIRAL"
            elif engagement_rate > 4:
                tier = "⚡ MODERATE VIRAL"
            else:
                tier = "📊 STANDARD"
            
            print(f"   🏆 Performance: {tier}")
        
        # ============================================================================
        # CONTENT PATTERN ANALYSIS
        # ============================================================================
        
        print(f"\n🎯 CONTENT PATTERN ANALYSIS:")
        print("=" * 35)
        
        # Analyze all descriptions for patterns
        all_descriptions = [v['video'].get('text', '') for v in recent_videos if v['video'].get('text', '')]
        no_text_count = len([v for v in recent_videos if not v['video'].get('text', '')])
        
        print(f"📊 Content Breakdown:")
        print(f"   📝 Videos with text: {len(all_descriptions)}")
        print(f"   🎥 Videos without text: {no_text_count}")
        print(f"   📈 Text usage rate: {len(all_descriptions)/len(recent_videos)*100:.1f}%")
        
        # Topic frequency analysis
        topic_counts = {
            "💰 Trading/Finance": 0,
            "🚀 Motivation": 0, 
            "✨ Lifestyle": 0,
            "👤 Personal": 0,
            "🎥 Visual Only": 0
        }
        
        for video_item in recent_videos:
            desc = video_item['video'].get('text', '').lower()
            
            if not desc:
                topic_counts["🎥 Visual Only"] += 1
            else:
                if any(word in desc for word in ['trade', 'trading', 'profit', 'loss', 'market', 'stock', 'money']):
                    topic_counts["💰 Trading/Finance"] += 1
                elif any(word in desc for word in ['success', 'grind', 'hustle', 'motivation', 'mindset']):
                    topic_counts["🚀 Motivation"] += 1
                elif any(word in desc for word in ['life', 'lifestyle', 'flex', 'rich', 'wealth']):
                    topic_counts["✨ Lifestyle"] += 1
                else:
                    topic_counts["👤 Personal"] += 1
        
        print(f"\n🎯 Topic Distribution (Last 24h):")
        for topic, count in topic_counts.items():
            percentage = count / len(recent_videos) * 100
            print(f"   {topic}: {count} videos ({percentage:.1f}%)")
        
        # Find top performing topic
        topic_performance = {}
        for video_item in recent_videos:
            desc = video_item['video'].get('text', '').lower()
            engagement = video_item['total_engagement']
            
            if not desc:
                topic_performance.setdefault("Visual Only", []).append(engagement)
            elif any(word in desc for word in ['trade', 'trading', 'profit', 'loss', 'market']):
                topic_performance.setdefault("Trading", []).append(engagement)
            elif any(word in desc for word in ['success', 'grind', 'hustle', 'motivation']):
                topic_performance.setdefault("Motivation", []).append(engagement)
            else:
                topic_performance.setdefault("Other", []).append(engagement)
        
        print(f"\n🏆 TOP PERFORMING TOPIC:")
        best_topic = ""
        best_avg = 0
        for topic, engagements in topic_performance.items():
            if engagements:
                avg_engagement = sum(engagements) / len(engagements)
                print(f"   {topic}: {avg_engagement:,.0f} avg engagement ({len(engagements)} videos)")
                if avg_engagement > best_avg:
                    best_avg = avg_engagement
                    best_topic = topic
        
        if best_topic:
            print(f"🎯 WINNER: {best_topic} content performs best!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print(f"\n✅ 24-HOUR VIRAL ANALYSIS COMPLETE")

if __name__ == "__main__":
    asyncio.run(analyze_tjr_24h_viral_content()) 