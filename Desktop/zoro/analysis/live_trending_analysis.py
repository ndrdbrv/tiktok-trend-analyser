#!/usr/bin/env python3
"""
Live Trending Analysis - Last 2 Days
====================================

Finds the hottest startup creators and content from the last 48 hours.
Includes video links, hashtag growth, and detailed performance metrics.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from agents.ingestion_agent import StartupContentIngestion
import time

class LiveTrendingAnalysis:
    """Analyzes trending startup content from the last 2 days"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.ingestion = StartupContentIngestion(api_key)
        self.current_time = time.time()
        self.two_days_ago = self.current_time - (2 * 24 * 3600)  # 48 hours ago
    
    async def find_trending_startup_creators(self) -> Dict[str, Any]:
        """Find trending startup creators and content from last 2 days"""
        
        print("🔥 LIVE TRENDING ANALYSIS - LAST 48 HOURS")
        print("=" * 60)
        print(f"Analysis time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Looking for content from: {datetime.fromtimestamp(self.two_days_ago).strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Hot startup hashtags to analyze
        hot_hashtags = [
            "startup", "entrepreneur", "businesstips", "startuplife", 
            "founder", "business", "saas", "funding", "growth", "marketing"
        ]
        
        all_trending_data = {
            "trending_creators": {},
            "viral_videos": [],
            "hot_hashtags": {},
            "trending_topics": {},
            "growth_analysis": {}
        }
        
        print("📊 ANALYZING HOT HASHTAGS...")
        print("-" * 40)
        
        for hashtag in hot_hashtags:
            print(f"🔍 Scanning #{hashtag} for trending content...")
            
            result = await self.ingestion.collect_startup_hashtag_data(hashtag, max_videos=20)
            
            if result.get("success"):
                videos = result.get("startup_videos", [])
                recent_videos = self.filter_recent_videos(videos)
                
                print(f"   ✅ Found {len(recent_videos)} recent videos out of {len(videos)} total")
                
                # Analyze this hashtag's performance
                hashtag_analysis = self.analyze_hashtag_performance(hashtag, recent_videos, videos)
                all_trending_data["hot_hashtags"][hashtag] = hashtag_analysis
                
                # Add to viral videos collection
                all_trending_data["viral_videos"].extend(recent_videos)
                
                # Track creators
                for video in recent_videos:
                    creator = video.creator_username
                    if creator not in all_trending_data["trending_creators"]:
                        all_trending_data["trending_creators"][creator] = {
                            "username": creator,
                            "videos": [],
                            "total_views": 0,
                            "total_engagement": 0,
                            "avg_business_relevance": 0,
                            "trending_score": 0
                        }
                    
                    all_trending_data["trending_creators"][creator]["videos"].append({
                        "video_id": video.video_id,
                        "description": video.description,
                        "views": video.views,
                        "likes": video.likes,
                        "comments": video.comments,
                        "shares": video.shares,
                        "engagement_rate": video.engagement_rate,
                        "duration": video.duration,
                        "created_at": video.created_at,
                        "business_relevance": video.business_relevance_score,
                        "hashtag_source": hashtag,
                        "tiktok_link": f"https://www.tiktok.com/@{creator}/video/{video.video_id}" if video.video_id else f"https://www.tiktok.com/@{creator}"
                    })
            
            await asyncio.sleep(1)  # Rate limiting
        
        # Calculate creator trending scores
        self.calculate_creator_trending_scores(all_trending_data["trending_creators"])
        
        # Analyze trending topics
        all_trending_data["trending_topics"] = self.extract_trending_topics(all_trending_data["viral_videos"])
        
        return all_trending_data
    
    def filter_recent_videos(self, videos: List) -> List:
        """Filter videos from the last 2 days"""
        recent_videos = []
        
        for video in videos:
            # Convert created_at to timestamp if it's a datetime object
            if hasattr(video.created_at, 'timestamp'):
                video_time = video.created_at.timestamp()
            else:
                # Assume it's already a timestamp
                video_time = float(video.created_at) if video.created_at else self.current_time
            
            # Check if video is from last 2 days
            if video_time >= self.two_days_ago:
                recent_videos.append(video)
        
        return recent_videos
    
    def analyze_hashtag_performance(self, hashtag: str, recent_videos: List, all_videos: List) -> Dict:
        """Analyze hashtag performance and growth"""
        
        if not recent_videos:
            return {
                "hashtag": hashtag,
                "recent_videos": 0,
                "growth_rate": 0,
                "avg_engagement": 0,
                "trending_score": 0
            }
        
        # Calculate performance metrics
        recent_engagement = sum(v.engagement_rate for v in recent_videos) / len(recent_videos)
        all_engagement = sum(v.engagement_rate for v in all_videos) / len(all_videos) if all_videos else 0
        
        # Growth calculation (simplified)
        growth_rate = (len(recent_videos) / len(all_videos)) * 100 if all_videos else 0
        
        # Trending score based on volume and engagement
        trending_score = (len(recent_videos) * 0.6) + (recent_engagement * 100 * 0.4)
        
        return {
            "hashtag": hashtag,
            "recent_videos": len(recent_videos),
            "total_videos": len(all_videos),
            "growth_rate": growth_rate,
            "avg_engagement": recent_engagement,
            "trending_score": trending_score,
            "status": "🔥 HOT" if trending_score > 5 else "📈 GROWING" if trending_score > 2 else "📊 STEADY"
        }
    
    def calculate_creator_trending_scores(self, creators: Dict) -> None:
        """Calculate trending scores for creators"""
        
        for creator_data in creators.values():
            videos = creator_data["videos"]
            if not videos:
                continue
                
            # Calculate metrics
            creator_data["total_views"] = sum(v["views"] for v in videos)
            creator_data["total_engagement"] = sum(v["engagement_rate"] for v in videos)
            creator_data["avg_engagement"] = creator_data["total_engagement"] / len(videos)
            creator_data["avg_business_relevance"] = sum(v["business_relevance"] for v in videos) / len(videos)
            creator_data["video_count"] = len(videos)
            
            # Trending score: engagement * video count * business relevance
            creator_data["trending_score"] = (
                creator_data["avg_engagement"] * 0.4 +
                min(len(videos) / 5, 1.0) * 0.3 +  # Video volume (capped)
                creator_data["avg_business_relevance"] * 0.3
            )
    
    def extract_trending_topics(self, videos: List) -> Dict[str, int]:
        """Extract trending topics from video descriptions"""
        
        topics = {}
        
        for video in videos:
            desc = video.description.lower()
            
            # Business topics
            if any(word in desc for word in ["ai", "artificial intelligence", "chatgpt", "automation"]):
                topics["AI/Tech"] = topics.get("AI/Tech", 0) + 1
            if any(word in desc for word in ["funding", "investment", "vc", "investor", "raise"]):
                topics["Funding"] = topics.get("Funding", 0) + 1
            if any(word in desc for word in ["remote", "wfh", "work from home", "digital nomad"]):
                topics["Remote Work"] = topics.get("Remote Work", 0) + 1
            if any(word in desc for word in ["saas", "software", "app", "platform"]):
                topics["SaaS/Software"] = topics.get("SaaS/Software", 0) + 1
            if any(word in desc for word in ["marketing", "social media", "content", "viral"]):
                topics["Marketing"] = topics.get("Marketing", 0) + 1
            if any(word in desc for word in ["failure", "mistake", "wrong", "failed", "lesson"]):
                topics["Failure/Lessons"] = topics.get("Failure/Lessons", 0) + 1
            if any(word in desc for word in ["success", "win", "achievement", "milestone"]):
                topics["Success Stories"] = topics.get("Success Stories", 0) + 1
            if any(word in desc for word in ["team", "hire", "employee", "culture", "staff"]):
                topics["Team Building"] = topics.get("Team Building", 0) + 1
        
        return topics
    
    def generate_trending_report(self, trending_data: Dict) -> None:
        """Generate comprehensive trending report"""
        
        print(f"\n🔥 TRENDING STARTUP CREATORS - LAST 48 HOURS")
        print("=" * 60)
        
        # Sort creators by trending score
        top_creators = sorted(
            trending_data["trending_creators"].items(),
            key=lambda x: x[1]["trending_score"],
            reverse=True
        )
        
        print(f"\n👑 TOP TRENDING CREATORS:")
        for i, (username, data) in enumerate(top_creators[:10], 1):
            if data["video_count"] > 0:
                print(f"\n{i}. @{username}")
                print(f"   🔥 Trending Score: {data['trending_score']:.2f}")
                print(f"   📊 {data['avg_engagement']:.1%} avg engagement")
                print(f"   📹 {data['video_count']} videos (last 48h)")
                print(f"   👀 {data['total_views']:,} total views")
                print(f"   🎯 {data['avg_business_relevance']:.1%} business relevance")
                
                # Show their top video
                top_video = max(data["videos"], key=lambda x: x["engagement_rate"])
                print(f"   🎬 TOP VIDEO: \"{top_video['description'][:60]}...\"")
                print(f"      📈 {top_video['engagement_rate']:.1%} engagement, {top_video['views']:,} views")
                print(f"      🔗 {top_video['tiktok_link']}")
        
        print(f"\n📊 HOTTEST HASHTAGS (LAST 48H):")
        hot_hashtags = sorted(
            trending_data["hot_hashtags"].items(),
            key=lambda x: x[1]["trending_score"],
            reverse=True
        )
        
                         for hashtag, data in hot_hashtags[:8]:
            status = data.get('status', '📊 STEADY')
            print(f"   {status} #{hashtag}")
            print(f"      📈 {data['recent_videos']} videos, {data['avg_engagement']:.1%} avg engagement")
            print(f"      🔥 Trending Score: {data['trending_score']:.1f}")
        
        print(f"\n🎭 TRENDING TOPICS:")
        sorted_topics = sorted(trending_data["trending_topics"].items(), key=lambda x: x[1], reverse=True)
        for topic, count in sorted_topics[:8]:
            print(f"   🔥 {topic}: {count} videos")
        
        # Show viral videos
        print(f"\n🚀 TOP VIRAL VIDEOS (LAST 48H):")
        viral_videos = sorted(trending_data["viral_videos"], key=lambda x: x.engagement_rate, reverse=True)
        
        for i, video in enumerate(viral_videos[:5], 1):
            print(f"\n{i}. @{video.creator_username}")
            print(f"   📝 \"{video.description[:80]}...\"")
            print(f"   📊 {video.engagement_rate:.1%} engagement")
            print(f"   👀 {video.views:,} views | ❤️ {video.likes:,} likes | 💬 {video.comments:,} comments")
            print(f"   ⏱️ {video.duration}s | 🎯 {video.business_relevance_score:.1%} business relevance")
            print(f"   🔗 https://www.tiktok.com/@{video.creator_username}/video/{video.video_id}")
        
        print(f"\n💡 ACTIONABLE INSIGHTS:")
        print(f"   🎯 Focus on: {', '.join([t[0] for t in sorted_topics[:3]])}")
        print(f"   🏷️ Use hashtags: {', '.join([f'#{h[0]}' for h in hot_hashtags[:3]])}")
        print(f"   👥 Study creators: {', '.join([f'@{c[0]}' for c in top_creators[:3]])}")
        
        # Generate content recommendations
        self.generate_content_recommendations(trending_data)
    
    def generate_content_recommendations(self, trending_data: Dict) -> None:
        """Generate specific content recommendations based on trending data"""
        
        print(f"\n🎬 CONTENT RECOMMENDATIONS FOR YOUR STARTUP:")
        print("=" * 60)
        
        top_creators = sorted(trending_data["trending_creators"].items(), key=lambda x: x[1]["trending_score"], reverse=True)
        hot_topics = sorted(trending_data["trending_topics"].items(), key=lambda x: x[1], reverse=True)
        
        recommendations = []
        
        # Based on trending topics
        for topic, count in hot_topics[:3]:
            if topic == "AI/Tech":
                recommendations.append({
                    "title": "How AI is Changing Our Startup",
                    "hook": "AI just transformed our entire business model",
                    "script": "Hook → Show before AI → AI implementation → Results → Future plans",
                    "hashtags": "#ai #startup #tech #entrepreneur",
                    "trend_source": f"Trending: {count} videos about AI"
                })
            elif topic == "Funding":
                recommendations.append({
                    "title": "Our Funding Journey - The Real Story",
                    "hook": "What VCs don't tell you about raising money",
                    "script": "Hook → Our funding goal → Rejections faced → What worked → Advice",
                    "hashtags": "#funding #vc #startup #entrepreneur",
                    "trend_source": f"Trending: {count} videos about funding"
                })
            elif topic == "Failure/Lessons":
                recommendations.append({
                    "title": "3 Startup Mistakes That Cost Us $30K",
                    "hook": "These mistakes almost killed our startup",
                    "script": "Hook → Mistake 1 + cost → Mistake 2 + cost → Mistake 3 + cost → Lessons",
                    "hashtags": "#startup #entrepreneur #businessmistakes #founder",
                    "trend_source": f"Trending: {count} videos about failures/lessons"
                })
        
        # Show recommendations
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. {rec['title']}")
            print(f"   🎯 Hook: \"{rec['hook']}\"")
            print(f"   📝 Script: {rec['script']}")
            print(f"   🏷️ Hashtags: {rec['hashtags']}")
            print(f"   📈 Why: {rec['trend_source']}")
        
        # Copy top creators
        if top_creators:
            top_creator = top_creators[0]
            creator_name = top_creator[0]
            creator_data = top_creator[1]
            
            print(f"\n🕵️ COPY @{creator_name} (TOP PERFORMER):")
            if creator_data["videos"]:
                top_video = max(creator_data["videos"], key=lambda x: x["engagement_rate"])
                print(f"   📝 Their winning video: \"{top_video['description'][:60]}...\"")
                print(f"   📊 {top_video['engagement_rate']:.1%} engagement")
                print(f"   🔗 Study: {top_video['tiktok_link']}")
                print(f"   💡 Adapt their format for your startup story")

async def run_live_trending_analysis():
    """Run the live trending analysis"""
    
    api_key = "MZTq3h5VIyi0CjKt"
    analyzer = LiveTrendingAnalysis(api_key)
    
    try:
        # Analyze trending content
        trending_data = await analyzer.find_trending_startup_creators()
        
        # Generate comprehensive report
        analyzer.generate_trending_report(trending_data)
        
        print(f"\n✅ LIVE TRENDING ANALYSIS COMPLETE!")
        print(f"📊 API Units Used: {analyzer.ingestion.daily_units_used}/1500")
        
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_live_trending_analysis()) 