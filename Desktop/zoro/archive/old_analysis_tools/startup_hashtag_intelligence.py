#!/usr/bin/env python3
"""
Startup Hashtag Intelligence System
===================================

Analyze hashtag patterns in the startup/business TikTok sector:
1. Find hashtags commonly used WITH #startup
2. Discover trending hashtags in startup/business content (last 24h)
3. Identify emerging hashtag combinations
4. Track hashtag co-occurrence patterns
"""

import asyncio
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from apify_client import ApifyClient

class StartupHashtagIntelligence:
    """Analyze hashtag patterns in startup/business TikTok content"""
    
    def __init__(self, api_token: str):
        self.client = ApifyClient(api_token)
        self.startup_hashtags = []
        self.hashtag_combinations = defaultdict(list)
        self.hashtag_timeline = defaultdict(list)
    
    def extract_hashtags_from_text(self, text: str) -> list:
        """Extract all hashtags from video description"""
        if not text:
            return []
        
        # Find all hashtags in text (case insensitive)
        hashtags = re.findall(r'#(\w+)', text.lower())
        return list(set(hashtags))  # Remove duplicates
    
    async def analyze_startup_hashtag_companions(self, max_videos: int = 100):
        """
        Find hashtags that people use TOGETHER with #startup
        """
        print("🔍 HASHTAGS USED WITH #STARTUP")
        print("=" * 40)
        print(f"Analyzing {max_videos} recent videos with #startup")
        print()
        
        try:
            # Get recent videos with #startup
            run_input = {
                "hashtags": ["startup"],
                "resultsPerPage": max_videos,
                "shouldDownloadVideos": False,
                "shouldDownloadCovers": False
            }
            
            print("📊 Scraping #startup videos...")
            
            run = self.client.actor("clockworks/tiktok-scraper").call(
                run_input=run_input,
                timeout_secs=300
            )
            
            videos = []
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                videos.append(item)
            
            print(f"✅ Found {len(videos)} videos with #startup")
            
            # Extract hashtags from each video
            companion_hashtags = Counter()
            startup_combinations = []
            recent_videos = []
            
            cutoff_time = datetime.now() - timedelta(hours=48)  # Last 48 hours for good sample
            
            for video in videos:
                create_time = video.get('createTime', 0)
                if create_time:
                    video_date = datetime.fromtimestamp(create_time)
                    
                    # Get video description
                    description = video.get('text', '')
                    hashtags = self.extract_hashtags_from_text(description)
                    
                    # Remove 'startup' itself from the list
                    companion_tags = [tag for tag in hashtags if tag != 'startup']
                    
                    if companion_tags:
                        # Count companion hashtags
                        for tag in companion_tags:
                            companion_hashtags[tag] += 1
                        
                        # Store combination
                        video_data = {
                            'hashtags': hashtags,
                            'companions': companion_tags,
                            'engagement': video.get('diggCount', 0) + video.get('commentCount', 0) + video.get('shareCount', 0),
                            'views': video.get('playCount', 0),
                            'date': video_date,
                            'url': video.get('webVideoUrl', ''),
                            'description': description[:100] + '...' if len(description) > 100 else description
                        }
                        
                        startup_combinations.append(video_data)
                        
                        # Track recent videos
                        if video_date >= cutoff_time:
                            recent_videos.append(video_data)
            
            # Show top companion hashtags
            print("🏷️ TOP HASHTAGS USED WITH #STARTUP:")
            print("-" * 38)
            
            for i, (hashtag, count) in enumerate(companion_hashtags.most_common(20), 1):
                percentage = (count / len(videos)) * 100
                print(f"  {i:2d}. #{hashtag:<20} | {count:3d} videos ({percentage:4.1f}%)")
            
            # Show powerful combinations
            print(f"\n🔥 MOST ENGAGING #STARTUP COMBINATIONS:")
            print("-" * 42)
            
            # Sort by engagement
            top_combinations = sorted(startup_combinations, 
                                    key=lambda x: x['engagement'], 
                                    reverse=True)[:10]
            
            for i, combo in enumerate(top_combinations, 1):
                hashtag_str = ', '.join([f'#{tag}' for tag in combo['hashtags'][:5]])
                engagement = combo['engagement']
                views = combo['views']
                
                print(f"  {i}. {hashtag_str}")
                print(f"     💫 {engagement:,} total engagement | 👀 {views:,} views")
                print(f"     📝 \"{combo['description']}\"")
                print()
            
            # Recent trending companions (last 48h)
            print(f"📈 TRENDING COMPANIONS (Last 48h):")
            print("-" * 35)
            
            recent_companions = Counter()
            for video in recent_videos:
                for tag in video['companions']:
                    recent_companions[tag] += 1
            
            for i, (hashtag, count) in enumerate(recent_companions.most_common(10), 1):
                print(f"  {i:2d}. #{hashtag} ({count} recent videos)")
            
            return {
                'companion_hashtags': dict(companion_hashtags.most_common(50)),
                'top_combinations': top_combinations,
                'recent_companions': dict(recent_companions.most_common(20)),
                'total_videos_analyzed': len(videos)
            }
            
        except Exception as e:
            print(f"❌ Error analyzing startup hashtag companions: {e}")
            return None
    
    async def analyze_trending_business_hashtags_24h(self):
        """
        Find the most used hashtags in startup/business sector (last 24h)
        """
        print("🔥 TRENDING BUSINESS HASHTAGS (LAST 24H)")
        print("=" * 50)
        print("Analyzing multiple business niches for trending hashtags")
        print()
        
        # Business/startup related hashtags to analyze
        business_hashtags = [
            "startup", "entrepreneur", "business", "productivity", 
            "marketing", "sales", "growth", "funding", "saas",
            "buildinpublic", "founders", "businesstips", "money"
        ]
        
        all_hashtags_24h = Counter()
        hashtag_engagement = defaultdict(list)
        trending_videos = []
        
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        for base_hashtag in business_hashtags:
            print(f"📊 Analyzing #{base_hashtag}...")
            
            try:
                run_input = {
                    "hashtags": [base_hashtag],
                    "resultsPerPage": 50,  # Good sample per hashtag
                    "shouldDownloadVideos": False,
                    "shouldDownloadCovers": False
                }
                
                run = self.client.actor("clockworks/tiktok-scraper").call(
                    run_input=run_input,
                    timeout_secs=300
                )
                
                videos = []
                for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                    videos.append(item)
                
                recent_count = 0
                
                for video in videos:
                    create_time = video.get('createTime', 0)
                    if create_time:
                        video_date = datetime.fromtimestamp(create_time)
                        
                        # Only analyze videos from last 24 hours
                        if video_date >= cutoff_time:
                            recent_count += 1
                            
                            description = video.get('text', '')
                            hashtags = self.extract_hashtags_from_text(description)
                            
                            # Track all hashtags found
                            for hashtag in hashtags:
                                all_hashtags_24h[hashtag] += 1
                                
                                # Track engagement for each hashtag
                                engagement = video.get('diggCount', 0) + video.get('commentCount', 0) + video.get('shareCount', 0)
                                hashtag_engagement[hashtag].append(engagement)
                            
                            # Store trending video data
                            trending_videos.append({
                                'hashtags': hashtags,
                                'engagement': engagement,
                                'views': video.get('playCount', 0),
                                'date': video_date,
                                'base_hashtag': base_hashtag,
                                'description': description[:80] + '...' if len(description) > 80 else description,
                                'url': video.get('webVideoUrl', '')
                            })
                
                print(f"   ✅ Found {recent_count} videos from last 24h")
                
                # Small delay to respect rate limits
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"   ❌ Error analyzing #{base_hashtag}: {e}")
        
        # Calculate trending scores
        hashtag_scores = {}
        for hashtag, count in all_hashtags_24h.items():
            if count >= 3:  # Minimum threshold
                avg_engagement = sum(hashtag_engagement[hashtag]) / len(hashtag_engagement[hashtag])
                # Trending score: frequency * average engagement
                hashtag_scores[hashtag] = {
                    'count': count,
                    'avg_engagement': avg_engagement,
                    'trending_score': count * (avg_engagement / 1000)  # Scale down engagement
                }
        
        print(f"\n📈 TOP TRENDING HASHTAGS (Last 24h):")
        print("-" * 38)
        print("   Rank | Hashtag              | Videos | Avg Engagement | Trending Score")
        print("   " + "-" * 70)
        
        # Sort by trending score
        sorted_hashtags = sorted(hashtag_scores.items(), 
                               key=lambda x: x[1]['trending_score'], 
                               reverse=True)
        
        for i, (hashtag, data) in enumerate(sorted_hashtags[:25], 1):
            count = data['count']
            avg_eng = data['avg_engagement']
            score = data['trending_score']
            
            print(f"   {i:2d}   | #{hashtag:<20} | {count:4d}   | {avg_eng:8,.0f}     | {score:8.1f}")
        
        # Find explosive hashtags (high engagement, emerging)
        print(f"\n🚀 EXPLOSIVE HASHTAGS (High Engagement + Emerging):")
        print("-" * 52)
        
        explosive_hashtags = []
        for hashtag, data in sorted_hashtags:
            if data['count'] >= 5 and data['avg_engagement'] > 2000:  # High engagement threshold
                explosive_hashtags.append((hashtag, data))
        
        for i, (hashtag, data) in enumerate(explosive_hashtags[:10], 1):
            count = data['count']
            avg_eng = data['avg_engagement']
            
            # Determine growth status
            if count >= 20:
                status = "🔥 VIRAL"
            elif count >= 10:
                status = "📈 TRENDING"
            else:
                status = "⚡ EMERGING"
            
            print(f"  {i}. #{hashtag} | {count} videos | {avg_eng:,.0f} avg engagement | {status}")
        
        # Show hashtag combinations that are trending
        print(f"\n💎 TRENDING HASHTAG COMBINATIONS:")
        print("-" * 35)
        
        # Find videos with multiple trending hashtags
        trending_combos = []
        top_trending = [h for h, _ in sorted_hashtags[:15]]  # Top 15 trending
        
        for video in trending_videos:
            video_trending_tags = [tag for tag in video['hashtags'] if tag in top_trending]
            if len(video_trending_tags) >= 2:  # Videos with 2+ trending hashtags
                trending_combos.append({
                    'hashtags': video_trending_tags,
                    'engagement': video['engagement'],
                    'description': video['description']
                })
        
        # Sort by engagement and show top combinations
        trending_combos.sort(key=lambda x: x['engagement'], reverse=True)
        
        for i, combo in enumerate(trending_combos[:8], 1):
            hashtag_str = ', '.join([f'#{tag}' for tag in combo['hashtags'][:4]])
            engagement = combo['engagement']
            
            print(f"  {i}. {hashtag_str}")
            print(f"     💫 {engagement:,} engagement | \"{combo['description']}\"")
            print()
        
        return {
            'trending_hashtags_24h': dict(all_hashtags_24h.most_common(50)),
            'hashtag_scores': hashtag_scores,
            'explosive_hashtags': explosive_hashtags,
            'trending_combinations': trending_combos[:20]
        }

async def run_startup_hashtag_intelligence():
    """Run complete startup hashtag intelligence analysis"""
    
    print("🧠 STARTUP HASHTAG INTELLIGENCE SYSTEM")
    print("=" * 55)
    print("Complete hashtag analysis for startup/business TikTok sector")
    print()
    
    api_token = "your-apify-token-here"
    analyzer = StartupHashtagIntelligence(api_token)
    
    # Analysis 1: What hashtags are used WITH #startup
    print("🎯 ANALYSIS 1: HASHTAG COMPANIONS")
    print("=" * 40)
    startup_companions = await analyzer.analyze_startup_hashtag_companions(max_videos=100)
    
    print("\n" + "="*60 + "\n")
    
    # Analysis 2: Trending hashtags in business sector (24h)
    print("🎯 ANALYSIS 2: 24H TRENDING BUSINESS HASHTAGS")
    print("=" * 50)
    trending_24h = await analyzer.analyze_trending_business_hashtags_24h()
    
    print("\n" + "="*60)
    print("✅ STARTUP HASHTAG INTELLIGENCE COMPLETE!")
    print("=" * 45)
    print("📊 Use this data to optimize your hashtag strategy")
    print("🚀 Focus on trending combinations for maximum reach")
    print("💡 Monitor explosive hashtags for early trend adoption")

if __name__ == "__main__":
    asyncio.run(run_startup_hashtag_intelligence()) 