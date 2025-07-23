#!/usr/bin/env python3
"""
📱 COMPREHENSIVE TIKTOK CREATOR ANALYZER
=======================================

Analyzes any TikTok creator account across all content types
and provides detailed breakdown of their content strategy.
"""

import asyncio
import re
import os
from datetime import datetime
from typing import Dict, List, Any
from collections import defaultdict, Counter
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.ingestion_agent import StartupContentIngestion

class CreatorAccountAnalyzer:
    """Comprehensive TikTok creator account analyzer"""
    
    def __init__(self, api_key: str, target_creator: str):
        self.api_key = api_key
        self.ingestion = StartupContentIngestion(api_key)
        self.target_creator = target_creator.lower().replace('@', '')
        
        # Broad search hashtags to find the creator
        self.broad_hashtags = [
            # Popular general hashtags
            "fyp", "foryou", "viral", "trending", "tiktok",
            # Business/finance
            "money", "investing", "business", "entrepreneur", "finance", "wealth",
            "stocks", "crypto", "realestate", "passive income", "financialtok",
            # Lifestyle  
            "lifestyle", "motivation", "success", "mindset", "productivity",
            # Content creator hashtags
            "content", "creator", "influencer", "tips", "advice", "hack",
            # Educational
            "learn", "education", "tutorial", "howto", "guide",
            # Trending topics
            "2024", "2025", "new", "update", "news", "facts"
        ]
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        if not text:
            return []
        hashtags = re.findall(r'#(\w+)', text.lower())
        return list(set(hashtags))
    
    def _categorize_content(self, description: str) -> str:
        """Categorize content based on description"""
        if not description:
            return "Unknown"
        
        desc_lower = description.lower()
        
        # Finance/Business
        if any(term in desc_lower for term in ['money', 'invest', 'finance', 'wealth', 'rich', 'business', 'entrepreneur', 'stocks', 'crypto', 'passive', 'income']):
            return "Finance/Business"
        
        # Lifestyle/Motivation
        elif any(term in desc_lower for term in ['lifestyle', 'motivation', 'success', 'mindset', 'goals', 'habits', 'productivity']):
            return "Lifestyle/Motivation"
        
        # Educational/Tips
        elif any(term in desc_lower for term in ['how to', 'tutorial', 'guide', 'tips', 'learn', 'education', 'hack', 'secret']):
            return "Educational/Tips"
        
        # Entertainment
        elif any(term in desc_lower for term in ['funny', 'comedy', 'entertainment', 'meme', 'viral', 'trend']):
            return "Entertainment"
        
        # Personal/Vlog
        elif any(term in desc_lower for term in ['my', 'i am', 'daily', 'life', 'routine', 'day in', 'personal']):
            return "Personal/Vlog"
        
        else:
            return "General Content"
    
    async def find_creator_content(self) -> Dict[str, Any]:
        """Find all content from the target creator"""
        
        print(f"🔍 COMPREHENSIVE SEARCH FOR @{self.target_creator}")
        print("=" * 60)
        print("🎯 Searching across ALL content categories...")
        print()
        
        all_creator_videos = []
        search_results = {}
        
        # Search through broad hashtags
        for i, hashtag in enumerate(self.broad_hashtags, 1):
            print(f"📱 [{i:2d}/{len(self.broad_hashtags)}] Searching #{hashtag}...")
            
            try:
                result = await self.ingestion.collect_startup_hashtag_data(
                    hashtag, max_videos=50
                )
                
                if result.get("success"):
                    videos = result.get("startup_videos", [])
                    
                    # Filter for our target creator
                    creator_videos = [
                        v for v in videos 
                        if self.target_creator in v.creator_username.lower()
                    ]
                    
                    if creator_videos:
                        print(f"   ✅ Found {len(creator_videos)} videos via #{hashtag}")
                        all_creator_videos.extend(creator_videos)
                        search_results[hashtag] = len(creator_videos)
                    else:
                        print(f"   ❌ No videos found")
                
                await asyncio.sleep(0.2)  # Rate limiting
                
            except Exception as e:
                print(f"   ⚠️ Error searching #{hashtag}: {str(e)}")
        
        # Remove duplicates based on description
        unique_videos = []
        seen_descriptions = set()
        
        for video in all_creator_videos:
            video_key = f"{video.description}_{video.views}_{video.likes}"
            if video_key not in seen_descriptions:
                unique_videos.append(video)
                seen_descriptions.add(video_key)
        
        print(f"\n📊 SEARCH SUMMARY")
        print("=" * 30)
        print(f"🎯 Total videos found: {len(all_creator_videos)}")
        print(f"📱 Unique videos: {len(unique_videos)}")
        print(f"🔍 Hashtags with results: {len([h for h in search_results if search_results[h] > 0])}")
        
        return {
            'creator': self.target_creator,
            'videos': unique_videos,
            'search_results': search_results,
            'total_found': len(all_creator_videos),
            'unique_count': len(unique_videos)
        }
    
    async def analyze_creator_account(self) -> Dict[str, Any]:
        """Complete creator account analysis"""
        
        data = await self.find_creator_content()
        
        if not data['videos']:
            return {"error": f"No videos found for @{self.target_creator}"}
        
        videos = data['videos']
        
        # Sort by engagement and recency
        top_videos = sorted(videos, key=lambda x: x.engagement_rate, reverse=True)
        
        # Content analysis
        content_categories = defaultdict(int)
        hashtag_usage = defaultdict(int)
        performance_metrics = {
            'total_views': 0,
            'total_likes': 0,
            'total_comments': 0,
            'total_shares': 0,
            'avg_engagement': 0,
            'best_performing': None,
            'worst_performing': None
        }
        
        # Analyze each video
        for video in videos:
            # Content categorization
            category = self._categorize_content(video.description)
            content_categories[category] += 1
            
            # Hashtag analysis
            hashtags = self._extract_hashtags(video.description)
            for hashtag in hashtags:
                hashtag_usage[hashtag] += 1
            
            # Performance metrics
            performance_metrics['total_views'] += video.views
            performance_metrics['total_likes'] += video.likes
            performance_metrics['total_comments'] += video.comments
            performance_metrics['total_shares'] += video.shares
        
        # Calculate averages
        video_count = len(videos)
        performance_metrics['avg_views'] = performance_metrics['total_views'] // video_count
        performance_metrics['avg_likes'] = performance_metrics['total_likes'] // video_count
        performance_metrics['avg_engagement'] = sum(v.engagement_rate for v in videos) / video_count
        performance_metrics['best_performing'] = max(videos, key=lambda x: x.engagement_rate)
        performance_metrics['worst_performing'] = min(videos, key=lambda x: x.engagement_rate)
        
        return {
            'creator_info': {
                'username': self.target_creator,
                'total_videos_analyzed': video_count,
                'content_categories': dict(content_categories),
                'top_hashtags': dict(Counter(hashtag_usage).most_common(20))
            },
            'performance_metrics': performance_metrics,
            'top_videos': top_videos[:10],  # Top 10 by engagement
            'content_analysis': {
                'primary_category': max(content_categories.items(), key=lambda x: x[1])[0] if content_categories else "Unknown",
                'content_diversity': len(content_categories),
                'hashtag_diversity': len(hashtag_usage)
            },
            'search_data': data['search_results']
        }
    
    async def generate_creator_report(self) -> str:
        """Generate comprehensive creator analysis report"""
        
        analysis = await self.analyze_creator_account()
        
        if "error" in analysis:
            return f"❌ {analysis['error']}"
        
        creator_info = analysis['creator_info']
        performance = analysis['performance_metrics']
        content_analysis = analysis['content_analysis']
        
        report = f"""
📱 COMPREHENSIVE TIKTOK CREATOR ANALYSIS
=======================================
📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🎯 Creator: @{creator_info['username']}
📊 Videos Analyzed: {creator_info['total_videos_analyzed']}

🔥 ACCOUNT OVERVIEW
==================
📈 Performance Metrics:
• Total Views: {performance['total_views']:,}
• Total Likes: {performance['total_likes']:,}
• Total Comments: {performance['total_comments']:,}
• Average Engagement: {performance['avg_engagement']:.1%}
• Average Views per Video: {performance['avg_views']:,}
• Average Likes per Video: {performance['avg_likes']:,}

🎯 Content Strategy:
• Primary Content Category: {content_analysis['primary_category']}
• Content Categories Used: {content_analysis['content_diversity']}
• Hashtag Diversity: {content_analysis['hashtag_diversity']} unique hashtags

📊 CONTENT BREAKDOWN
===================
"""
        
        # Content categories
        if creator_info['content_categories']:
            report += "🎬 Content Categories:\n"
            for category, count in sorted(creator_info['content_categories'].items(), key=lambda x: x[1], reverse=True):
                percentage = (count / creator_info['total_videos_analyzed']) * 100
                report += f"• {category}: {count} videos ({percentage:.1f}%)\n"
            report += "\n"
        
        # Top hashtags
        if creator_info['top_hashtags']:
            report += "🏷️ Most Used Hashtags:\n"
            for hashtag, count in list(creator_info['top_hashtags'].items())[:15]:
                report += f"• #{hashtag}: {count} times\n"
            report += "\n"
        
        # Top performing videos
        report += "🏆 TOP PERFORMING VIDEOS\n"
        report += "=" * 30 + "\n"
        
        for i, video in enumerate(analysis['top_videos'][:8], 1):
            report += f"\n{i}. 📈 {video.engagement_rate:.1%} engagement\n"
            report += f"   👀 {video.views:,} views | ❤️ {video.likes:,} likes\n"
            report += f"   📝 \"{video.description[:80]}...\"\n"
            
            # Extract on-screen text/key message
            hashtags = self._extract_hashtags(video.description)
            if hashtags:
                top_hashtags = ', '.join([f"#{h}" for h in hashtags[:5]])
                report += f"   🏷️ Hashtags: {top_hashtags}\n"
            
            report += f"   🔗 https://www.tiktok.com/@{video.creator_username}\n"
        
        # Best vs worst performing
        best = performance['best_performing']
        worst = performance['worst_performing']
        
        report += f"\n📊 PERFORMANCE COMPARISON\n"
        report += "=" * 30 + "\n"
        report += f"🏆 Best Performing Video:\n"
        report += f"   📈 {best.engagement_rate:.1%} engagement\n"
        report += f"   👀 {best.views:,} views | ❤️ {best.likes:,} likes\n"
        report += f"   📝 \"{best.description[:60]}...\"\n\n"
        
        report += f"📉 Lowest Performing Video:\n"
        report += f"   📈 {worst.engagement_rate:.1%} engagement\n"
        report += f"   👀 {worst.views:,} views | ❤️ {worst.likes:,} likes\n"
        report += f"   📝 \"{worst.description[:60]}...\"\n"
        
        # Strategic insights
        engagement_range = best.engagement_rate - worst.engagement_rate
        report += f"\n💡 STRATEGIC INSIGHTS\n"
        report += "=" * 25 + "\n"
        report += f"📊 Engagement Range: {engagement_range:.1%} (shows content consistency)\n"
        report += f"🎯 Content Focus: {content_analysis['primary_category']}\n"
        report += f"📈 Average Performance: {performance['avg_engagement']:.1%} engagement\n"
        
        if performance['avg_engagement'] > 0.05:
            report += "🔥 HIGH ENGAGEMENT ACCOUNT - Strong audience connection\n"
        elif performance['avg_engagement'] > 0.02:
            report += "📈 GOOD ENGAGEMENT - Solid performance\n"
        else:
            report += "📊 GROWING ACCOUNT - Building audience\n"
        
        return report

async def main():
    """Run creator account analysis"""
    
    target_creator = input("📱 Enter TikTok creator username (without @): ").strip()
    
    if not target_creator:
        target_creator = "calebinvest"  # Default for testing
    
    print(f"\n🔍 ANALYZING @{target_creator}")
    print("=" * 60)
    
    # EnsembleData API key
    api_key = "MZTq3h5VIyi0CjKt"
    
    analyzer = CreatorAccountAnalyzer(api_key, target_creator)
    
    try:
        report = await analyzer.generate_creator_report()
        print(report)
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"{target_creator}_account_analysis_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n📄 Analysis saved to: {filename}")
        
    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 