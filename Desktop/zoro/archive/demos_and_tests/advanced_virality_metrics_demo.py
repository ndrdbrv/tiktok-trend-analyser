#!/usr/bin/env python3
"""
Advanced Virality Metrics Demo
==============================

Building on your formula: (likes + comments + shares + saves) / days

New metrics:
- Hashtag Growth Velocity: total_videos_using_hashtag / time_period
- Timing Correlation: correlation(posting_time, engagement)
- Content Length Optimization: engagement_rate_by_duration
"""

import asyncio
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from statistics import mean, correlation
from apify_client import ApifyClient

class AdvancedViralityMetrics:
    """Advanced metrics for viral prediction"""
    
    def __init__(self, api_token: str):
        self.client = ApifyClient(api_token)
        self.hashtag_timeline_data = defaultdict(list)
        self.timing_data = []
        self.content_length_data = []
    
    async def analyze_hashtag_growth_velocity(self, hashtags: list, days_back: int = 3):
        """
        Track hashtag usage growth over time periods
        Formula: videos_using_hashtag(today) / videos_using_hashtag(yesterday)
        """
        print("📈 HASHTAG GROWTH VELOCITY ANALYSIS")
        print("=" * 45)
        print(f"Analyzing {len(hashtags)} hashtags over {days_back} days")
        print()
        
        hashtag_data = {}
        
        for hashtag in hashtags:
            print(f"🔍 Analyzing #{hashtag}...")
            
            try:
                # Get recent videos for this hashtag
                run_input = {
                    "hashtags": [hashtag],
                    "resultsPerPage": 100,  # Get good sample size
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
                
                # Group videos by day
                daily_counts = defaultdict(int)
                total_engagement = 0
                
                cutoff_time = datetime.now() - timedelta(days=days_back)
                
                for video in videos:
                    create_time = video.get('createTime', 0)
                    if create_time:
                        video_date = datetime.fromtimestamp(create_time)
                        
                        if video_date >= cutoff_time:
                            day_key = video_date.strftime('%Y-%m-%d')
                            daily_counts[day_key] += 1
                            
                            # Calculate engagement
                            likes = video.get('diggCount', 0)
                            comments = video.get('commentCount', 0) 
                            shares = video.get('shareCount', 0)
                            total_engagement += likes + comments + shares
                
                # Calculate growth velocity
                sorted_days = sorted(daily_counts.keys())
                growth_velocity = 0
                
                if len(sorted_days) >= 2:
                    recent_count = daily_counts[sorted_days[-1]]  # Today
                    previous_count = daily_counts[sorted_days[-2]]  # Yesterday
                    
                    if previous_count > 0:
                        growth_velocity = (recent_count / previous_count) * 100
                
                hashtag_data[hashtag] = {
                    'daily_counts': dict(daily_counts),
                    'growth_velocity': growth_velocity,
                    'total_videos': len(videos),
                    'avg_daily_videos': mean(daily_counts.values()) if daily_counts else 0,
                    'total_engagement': total_engagement,
                    'engagement_per_video': total_engagement / len(videos) if videos else 0
                }
                
                print(f"   📊 Videos found: {len(videos)}")
                print(f"   📈 Growth velocity: {growth_velocity:.1f}%")
                print(f"   💫 Avg engagement/video: {hashtag_data[hashtag]['engagement_per_video']:,.0f}")
                print()
                
            except Exception as e:
                print(f"   ❌ Error analyzing #{hashtag}: {e}")
                hashtag_data[hashtag] = {'error': str(e)}
        
        # Find fastest growing hashtags
        print("🚀 FASTEST GROWING HASHTAGS:")
        print("-" * 30)
        
        valid_hashtags = [(h, data) for h, data in hashtag_data.items() 
                         if 'growth_velocity' in data and data['growth_velocity'] > 0]
        
        sorted_by_growth = sorted(valid_hashtags, 
                                key=lambda x: x[1]['growth_velocity'], 
                                reverse=True)
        
        for i, (hashtag, data) in enumerate(sorted_by_growth[:5], 1):
            velocity = data['growth_velocity']
            videos = data['total_videos']
            avg_engagement = data['engagement_per_video']
            
            if velocity > 200:
                status = "🔥 VIRAL POTENTIAL"
            elif velocity > 150:
                status = "📈 HIGH GROWTH"
            elif velocity > 110:
                status = "⚡ MODERATE GROWTH"
            else:
                status = "📊 STABLE"
            
            print(f"  {i}. #{hashtag}")
            print(f"     Growth: {velocity:.1f}% | Videos: {videos} | {status}")
            print(f"     Avg Engagement: {avg_engagement:,.0f}")
            print()
        
        return hashtag_data
    
    async def analyze_optimal_timing(self, hashtag: str = "startup"):
        """
        Find correlation between posting time and engagement
        Formula: correlation(posting_time, engagement_rate)
        """
        print("⏰ OPTIMAL TIMING ANALYSIS")
        print("=" * 35)
        print(f"Analyzing posting times for #{hashtag}")
        print()
        
        try:
            # Get videos for timing analysis
            run_input = {
                "hashtags": [hashtag],
                "resultsPerPage": 50,
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
            
            # Analyze timing vs engagement
            timing_data = []
            hourly_performance = defaultdict(list)
            
            for video in videos:
                create_time = video.get('createTime', 0)
                if create_time:
                    video_date = datetime.fromtimestamp(create_time)
                    hour = video_date.hour
                    
                    # Calculate engagement rate
                    views = video.get('playCount', 1)
                    likes = video.get('diggCount', 0)
                    comments = video.get('commentCount', 0)
                    shares = video.get('shareCount', 0)
                    
                    engagement_rate = ((likes + comments + shares) / views) * 100
                    
                    timing_data.append({
                        'hour': hour,
                        'engagement_rate': engagement_rate,
                        'views': views
                    })
                    
                    hourly_performance[hour].append(engagement_rate)
            
            # Calculate average performance by hour
            print("📊 PERFORMANCE BY HOUR:")
            print("-" * 25)
            
            best_hours = []
            for hour in range(24):
                if hour in hourly_performance:
                    avg_engagement = mean(hourly_performance[hour])
                    video_count = len(hourly_performance[hour])
                    
                    # Determine time period
                    if 6 <= hour < 12:
                        period = "🌅 Morning"
                    elif 12 <= hour < 17:
                        period = "☀️ Afternoon"
                    elif 17 <= hour < 21:
                        period = "🌇 Evening"
                    else:
                        period = "🌙 Night"
                    
                    best_hours.append((hour, avg_engagement, video_count, period))
                    
                    print(f"   {hour:2d}:00 | {avg_engagement:5.2f}% avg engagement | {video_count} videos | {period}")
            
            # Find optimal posting times
            best_hours.sort(key=lambda x: x[1], reverse=True)
            
            print(f"\n🎯 OPTIMAL POSTING TIMES:")
            print("-" * 25)
            
            for i, (hour, engagement, count, period) in enumerate(best_hours[:5], 1):
                print(f"  {i}. {hour:2d}:00 - {engagement:.2f}% engagement ({count} videos) {period}")
            
            return {
                'timing_data': timing_data,
                'hourly_averages': {h: mean(rates) for h, rates in hourly_performance.items()},
                'best_hours': best_hours[:5]
            }
            
        except Exception as e:
            print(f"❌ Error in timing analysis: {e}")
            return None
    
    async def analyze_content_length_optimization(self, hashtag: str = "entrepreneur"):
        """
        Find optimal video length for engagement
        Formula: engagement_rate_by_video_duration
        """
        print("🎬 CONTENT LENGTH OPTIMIZATION")
        print("=" * 40)
        print(f"Analyzing video length performance for #{hashtag}")
        print()
        
        try:
            # Get videos for length analysis
            run_input = {
                "hashtags": [hashtag],
                "resultsPerPage": 50,
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
            
            # Group by duration ranges
            duration_groups = {
                '0-15s': [],
                '16-30s': [],
                '31-60s': [],
                '60s+': []
            }
            
            for video in videos:
                # Note: videoDuration might not always be available
                duration = video.get('videoDuration', 30)  # Default to 30s if not available
                
                views = video.get('playCount', 1)
                likes = video.get('diggCount', 0)
                comments = video.get('commentCount', 0)
                shares = video.get('shareCount', 0)
                
                engagement_rate = ((likes + comments + shares) / views) * 100
                
                video_data = {
                    'duration': duration,
                    'engagement_rate': engagement_rate,
                    'views': views,
                    'total_engagement': likes + comments + shares
                }
                
                # Categorize by duration
                if duration <= 15:
                    duration_groups['0-15s'].append(video_data)
                elif duration <= 30:
                    duration_groups['16-30s'].append(video_data)
                elif duration <= 60:
                    duration_groups['31-60s'].append(video_data)
                else:
                    duration_groups['60s+'].append(video_data)
            
            # Calculate performance by duration
            print("📊 PERFORMANCE BY VIDEO LENGTH:")
            print("-" * 32)
            
            duration_performance = []
            
            for duration_range, video_list in duration_groups.items():
                if video_list:
                    avg_engagement = mean([v['engagement_rate'] for v in video_list])
                    avg_views = mean([v['views'] for v in video_list])
                    video_count = len(video_list)
                    
                    duration_performance.append({
                        'range': duration_range,
                        'avg_engagement': avg_engagement,
                        'avg_views': avg_views,
                        'video_count': video_count
                    })
                    
                    print(f"   {duration_range:8} | {avg_engagement:5.2f}% engagement | {avg_views:8,.0f} avg views | {video_count} videos")
            
            # Find optimal duration
            if duration_performance:
                best_duration = max(duration_performance, key=lambda x: x['avg_engagement'])
                
                print(f"\n🎯 OPTIMAL VIDEO LENGTH:")
                print(f"   {best_duration['range']} - {best_duration['avg_engagement']:.2f}% engagement")
                print(f"   Based on {best_duration['video_count']} videos")
            
            return duration_performance
            
        except Exception as e:
            print(f"❌ Error in content length analysis: {e}")
            return None

async def demo_advanced_metrics():
    """Demo the advanced virality metrics"""
    
    print("🚀 ADVANCED VIRALITY METRICS DEMO")
    print("=" * 50)
    print("Beyond basic engagement: Deep viral intelligence")
    print()
    
    api_token = "your-apify-token-here"
    analyzer = AdvancedViralityMetrics(api_token)
    
    # Test with startup/business hashtags
    test_hashtags = ["startup", "entrepreneur", "business", "productivity"]
    
    # Run all analyses
    await analyzer.analyze_hashtag_growth_velocity(test_hashtags)
    await analyzer.analyze_optimal_timing("startup")
    await analyzer.analyze_content_length_optimization("entrepreneur")
    
    print("✅ ADVANCED METRICS ANALYSIS COMPLETE!")
    print("=" * 40)
    print("These metrics can now feed into your viral prediction algorithms!")

if __name__ == "__main__":
    asyncio.run(demo_advanced_metrics()) 