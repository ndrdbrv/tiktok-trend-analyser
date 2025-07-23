#!/usr/bin/env python3
"""
Analyze Recent Video Growth Rates (Last 48 Hours)
================================================

Analyzes which videos have the highest growth rates in the last 48 hours
and what they're about based on thumbnail text and captions.
"""

import json
import os
from datetime import datetime, timedelta

def load_analysis_data(account_name):
    """Load the thumbnail analysis results for a specific account"""
    filename = f"{account_name}_thumbnail_analysis.json"
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ {filename} not found. Run the analysis first.")
        return []

def calculate_growth_rate(video_data):
    """Calculate growth rate based on views, likes, comments, shares"""
    views = video_data.get('views', 0)
    likes = video_data.get('likes', 0)
    comments = video_data.get('comments', 0)
    shares = video_data.get('shares', 0)
    
    if views == 0:
        return 0
    
    # Calculate engagement rate as a proxy for growth
    engagement_rate = ((likes + comments + shares) / views * 100)
    
    # Factor in recency (more recent videos get higher weight)
    created_at = video_data.get('created_at', '')
    if created_at and created_at != 'N/A':
        try:
            video_date = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
            days_ago = (datetime.now() - video_date).days
            if days_ago <= 2:  # Last 48 hours
                recency_boost = 1.5
            elif days_ago <= 7:  # Last week
                recency_boost = 1.2
            else:
                recency_boost = 1.0
        except:
            recency_boost = 1.0
    else:
        recency_boost = 1.0
    
    return engagement_rate * recency_boost

def analyze_recent_growth():
    """Analyze recent growth rates for both accounts"""
    
    print("🚀 RECENT VIDEO GROWTH ANALYSIS (Last 48 Hours)")
    print("=" * 60)
    
    # Analyze both accounts
    accounts = [
        ("calebinvest", "thumbnail_analysis.json"),
        ("neelyweely23", "neelyweely23_thumbnail_analysis.json")
    ]
    
    all_videos = []
    
    for account_name, filename in accounts:
        print(f"\n📊 ANALYZING @{account_name.upper()}")
        print("-" * 40)
        
        try:
            with open(filename, "r") as f:
                account_data = json.load(f)
        except FileNotFoundError:
            print(f"❌ {filename} not found. Skipping {account_name}.")
            continue
        
        # Calculate growth rates for each video
        for video in account_data:
            growth_rate = calculate_growth_rate(video)
            video['growth_rate'] = growth_rate
            video['account'] = account_name
            all_videos.append(video)
        
        # Show top 3 videos for this account
        account_videos = [v for v in all_videos if v['account'] == account_name]
        account_videos.sort(key=lambda x: x['growth_rate'], reverse=True)
        
        print(f"📈 Top 3 videos by growth rate:")
        for i, video in enumerate(account_videos[:3], 1):
            created_at = video.get('created_at', 'N/A')
            days_ago = "Unknown"
            if created_at and created_at != 'N/A':
                try:
                    video_date = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                    days_ago = (datetime.now() - video_date).days
                except:
                    pass
            
            print(f"\n   #{i} - {video.get('caption', 'N/A')[:50]}...")
            print(f"      📅 Posted: {days_ago} days ago")
            print(f"      👁️  Views: {video.get('views', 0):,}")
            print(f"      ❤️  Likes: {video.get('likes', 0):,}")
            print(f"      📊 Growth Rate: {video['growth_rate']:.2f}")
            
            # Show thumbnail text if available
            ocr_text = video.get('ocr_text', '').strip()
            if ocr_text:
                print(f"      📱 Thumbnail: \"{ocr_text[:60]}...\"")
            else:
                print(f"      📱 Thumbnail: No text detected")
    
    # Overall ranking across both accounts
    print(f"\n🏆 OVERALL TOP 10 VIDEOS BY GROWTH RATE")
    print("=" * 50)
    
    all_videos.sort(key=lambda x: x['growth_rate'], reverse=True)
    
    for i, video in enumerate(all_videos[:10], 1):
        account = video['account']
        created_at = video.get('created_at', 'N/A')
        days_ago = "Unknown"
        if created_at and created_at != 'N/A':
            try:
                video_date = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                days_ago = (datetime.now() - video_date).days
            except:
                pass
        
        print(f"\n#{i} - @{account.upper()}")
        print(f"   📝 Caption: {video.get('caption', 'N/A')[:60]}...")
        print(f"   📅 Posted: {days_ago} days ago")
        print(f"   👁️  Views: {video.get('views', 0):,}")
        print(f"   ❤️  Likes: {video.get('likes', 0):,}")
        print(f"   📊 Growth Rate: {video['growth_rate']:.2f}")
        
        # Show thumbnail text if available
        ocr_text = video.get('ocr_text', '').strip()
        if ocr_text:
            print(f"   📱 Thumbnail: \"{ocr_text[:60]}...\"")
        else:
            print(f"   📱 Thumbnail: No text detected")
    
    # Recent videos analysis (last 48 hours)
    print(f"\n⏰ VIDEOS FROM LAST 48 HOURS")
    print("=" * 40)
    
    recent_videos = []
    for video in all_videos:
        created_at = video.get('created_at', 'N/A')
        if created_at and created_at != 'N/A':
            try:
                video_date = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                days_ago = (datetime.now() - video_date).days
                if days_ago <= 2:  # Last 48 hours
                    video['days_ago'] = days_ago
                    recent_videos.append(video)
            except:
                continue
    
    if recent_videos:
        recent_videos.sort(key=lambda x: x['growth_rate'], reverse=True)
        
        for i, video in enumerate(recent_videos, 1):
            account = video['account']
            print(f"\n#{i} - @{account.upper()} ({video['days_ago']} days ago)")
            print(f"   📝 Caption: {video.get('caption', 'N/A')[:60]}...")
            print(f"   👁️  Views: {video.get('views', 0):,}")
            print(f"   ❤️  Likes: {video.get('likes', 0):,}")
            print(f"   📊 Growth Rate: {video['growth_rate']:.2f}")
            
            # Show thumbnail text if available
            ocr_text = video.get('ocr_text', '').strip()
            if ocr_text:
                print(f"   📱 Thumbnail: \"{ocr_text[:60]}...\"")
            else:
                print(f"   📱 Thumbnail: No text detected")
    else:
        print("❌ No videos found from the last 48 hours")
    
    # Content theme analysis for high-growth videos
    print(f"\n🎯 CONTENT THEMES IN HIGH-GROWTH VIDEOS")
    print("=" * 45)
    
    top_10_videos = all_videos[:10]
    
    # Analyze captions
    captions = [video.get('caption', '') for video in top_10_videos]
    all_caption_text = ' '.join(captions).lower()
    
    # Common themes
    themes = {
        'finance': all_caption_text.count('finance'),
        'daytrading': all_caption_text.count('daytrading'),
        'god': all_caption_text.count('god'),
        'cluely': all_caption_text.count('cluely'),
        'startup': all_caption_text.count('startup'),
        'money': all_caption_text.count('money'),
        'business': all_caption_text.count('business'),
        'fyp': all_caption_text.count('#fyp'),
        'viral': all_caption_text.count('#viral')
    }
    
    print("📝 Caption Themes in Top 10 Videos:")
    for theme, count in themes.items():
        if count > 0:
            print(f"   {theme.title()}: {count} mentions")
    
    # Analyze thumbnail text themes
    successful_ocr = [v for v in top_10_videos if v.get('ocr_text', '').strip()]
    
    if successful_ocr:
        all_ocr_text = ' '.join([v.get('ocr_text', '') for v in successful_ocr]).lower()
        
        # Theme detection in thumbnails
        thumbnail_themes = {
            'motivation': ['will', 'get', 'dream', 'car', 'crib', 'memory', 'trust', 'plan', 'bigger', 'ideas'],
            'startup': ['startup', 'founder', 'cluely', 'business', 'team'],
            'finance': ['money', 'month', 'dollars', 'income'],
            'work': ['work', 'life', 'another', 'maybe', 'cheating']
        }
        
        print(f"\n📱 Thumbnail Text Themes in Top 10 Videos:")
        for theme, keywords in thumbnail_themes.items():
            theme_count = sum(all_ocr_text.count(keyword) for keyword in keywords)
            if theme_count > 0:
                print(f"   {theme.title()}: {theme_count} mentions")
    
    # Growth insights
    print(f"\n💡 GROWTH INSIGHTS")
    print("-" * 20)
    
    avg_growth_rate = sum(v['growth_rate'] for v in all_videos) / len(all_videos) if all_videos else 0
    print(f"📊 Average Growth Rate: {avg_growth_rate:.2f}")
    
    # Account comparison
    calebinvest_videos = [v for v in all_videos if v['account'] == 'calebinvest']
    neelyweely23_videos = [v for v in all_videos if v['account'] == 'neelyweely23']
    
    if calebinvest_videos:
        caleb_avg = sum(v['growth_rate'] for v in calebinvest_videos) / len(calebinvest_videos)
        print(f"📈 @calebinvest Average Growth: {caleb_avg:.2f}")
    
    if neelyweely23_videos:
        neely_avg = sum(v['growth_rate'] for v in neelyweely23_videos) / len(neelyweely23_videos)
        print(f"📈 @neelyweely23 Average Growth: {neely_avg:.2f}")

if __name__ == "__main__":
    analyze_recent_growth() 