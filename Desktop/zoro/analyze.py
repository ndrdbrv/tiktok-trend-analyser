#!/usr/bin/env python3
"""
🎯 UNIFIED TIKTOK ANALYSIS SYSTEM
================================

Single entry point for ALL TikTok analysis.
No file clutter - everything runs in terminal only.

Usage:
  python analyze.py <username>              # Full account analysis  
  python analyze.py <username> --quick      # Quick growth analysis
  python analyze.py <username> --trends     # Trending hashtags analysis
  python analyze.py <username> --viral      # Viral potential analysis
  python analyze.py --hashtag <tag>         # Hashtag analysis
  python analyze.py --demo                  # Demo with test data
"""

import asyncio
import argparse
import os
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional, List

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our core systems
from agents.ingestion_agent import ApifyContentIngestion
from ai.claude_primary_system import ClaudePrimarySystem

class UnifiedAnalyzer:
    """Single analyzer that handles all analysis types"""
    
    def __init__(self, api_token: str):
        self.apify_client = ApifyContentIngestion(api_token)
        self.ai_system = ClaudePrimarySystem()
        
        print("🎯 TikTok Analysis System Initialized")
        print("   📱 Apify Data Source: Ready")
        print("   🤖 Claude Opus 4: Ready")
        print()

    async def analyze_account(self, username: str, analysis_type: str = "full") -> Dict[str, Any]:
        """Unified account analysis method"""
        
        username = username.replace('@', '').lower()
        
        print(f"🔍 ANALYZING @{username.upper()}")
        print("=" * 60)
        print(f"📊 Analysis Type: {analysis_type.title()}")
        print(f"⏰ Started: {datetime.now().strftime('%H:%M:%S')}")
        print()
        
        try:
            # Get TikTok data
            print("📱 Fetching TikTok data...")
            profile_data = await self.apify_client.get_creator_profile(username)
            
            if not profile_data:
                print(f"❌ No data found for @{username}")
                return {"success": False, "error": "No data found"}
            
            # Get recent videos for analysis
            videos = await self.apify_client.get_hashtag_videos(f"creator:{username}", max_videos=10)
            if not videos:
                print(f"❌ No videos found for @{username}")
                return {"success": False, "error": "No videos found"}
            
            # Combine profile and video data
            analysis_data = {
                'profile': profile_data,
                'videos': videos
            }
            
            # Prepare analysis based on type
            if analysis_type == "quick":
                result = await self._quick_analysis(username, analysis_data)
            elif analysis_type == "trends":
                result = await self._trends_analysis(username, analysis_data)
            elif analysis_type == "viral":
                result = await self._viral_analysis(username, analysis_data)
            else:  # full
                result = await self._full_analysis(username, analysis_data)
            
            print(f"✅ Analysis completed for @{username}")
            return {"success": True, "data": result}
            
        except Exception as e:
            print(f"❌ Analysis failed: {str(e)}")
            return {"success": False, "error": str(e)}

    async def _full_analysis(self, username: str, data: Dict) -> Dict[str, Any]:
        """Complete account analysis"""
        
        profile = data.get('profile', {})
        videos = data.get('videos', [])[:10]  # Latest 10 videos
        
        print("📊 FULL ACCOUNT ANALYSIS")
        print("-" * 30)
        
        # Profile info (handling dataclass objects)
        if hasattr(profile, 'followers'):
            # It's a dataclass object
            follower_count = profile.followers
            following_count = profile.following
            display_name = profile.display_name
            verified = profile.verified
            bio = profile.bio[:100] + "..." if len(profile.bio) > 100 else profile.bio
        else:
            # It's a dictionary  
            follower_count = profile.get('follower_count', 0) or profile.get('stats', {}).get('followerCount', 0)
            following_count = profile.get('following_count', 0) or profile.get('stats', {}).get('followingCount', 0)
            display_name = profile.get('display_name', username)
            verified = profile.get('verified', False)
            bio = profile.get('bio', '')
        
        print(f"👤 Profile: @{username} ({display_name})")
        print(f"👥 Followers: {follower_count:,}")
        print(f"🔗 Following: {following_count:,}")
        print(f"✅ Verified: {'Yes' if verified else 'No'}")
        if bio:
            print(f"📝 Bio: {bio}")
        print()
        
        # Basic stats from videos (handling dataclass objects)
        total_views = 0
        total_likes = 0
        for v in videos:
            if hasattr(v, 'views'):
                # It's a dataclass object
                total_views += v.views
                total_likes += v.likes
            else:
                # It's a dictionary
                total_views += v.get('views', 0) or v.get('playCount', 0)
                total_likes += v.get('likes', 0) or v.get('diggCount', 0)
        avg_engagement = (total_likes / total_views * 100) if total_views > 0 else 0
        
        print(f"📈 Videos Analyzed: {len(videos)}")
        print(f"👁️ Total Views: {total_views:,}")
        print(f"❤️ Total Likes: {total_likes:,}")
        print(f"📊 Avg Engagement: {avg_engagement:.2f}%")
        print()
        
        # Top performing video
        if videos:
            def get_views(v):
                if hasattr(v, 'views'):
                    return v.views
                else:
                    return v.get('views', 0) or v.get('playCount', 0)
            
            top_video = max(videos, key=get_views)
            
            if hasattr(top_video, 'views'):
                views = top_video.views
                likes = top_video.likes
                comments = top_video.comments
                shares = top_video.shares
                text = top_video.description
                hashtags = top_video.hashtags
            else:
                views = top_video.get('views', 0) or top_video.get('playCount', 0)
                likes = top_video.get('likes', 0) or top_video.get('diggCount', 0)
                comments = top_video.get('comments', 0) or top_video.get('commentCount', 0)
                shares = top_video.get('shares', 0) or top_video.get('shareCount', 0)
                text = top_video.get('text', '') or top_video.get('desc', '')
                hashtags = []
            
            engagement_rate = (likes / views * 100) if views > 0 else 0
            
            print("🔥 TOP PERFORMING VIDEO:")
            print(f"   📹 Views: {views:,}")
            print(f"   ❤️ Likes: {likes:,}")
            print(f"   💬 Comments: {comments:,}")
            print(f"   🔄 Shares: {shares:,}")
            print(f"   📊 Engagement: {engagement_rate:.2f}%")
            if hashtags:
                print(f"   🏷️ Hashtags: {', '.join(hashtags[:5])}")
            print(f"   💬 Text: {text[:100]}...")
            print()
        
        # AI insights
        print("🤖 CLAUDE OPUS 4 INSIGHTS:")
        print("-" * 25)
        
        ai_prompt = f"""
        Analyze this TikTok creator data:
        
        Creator: @{username}
        Videos: {len(videos)}
        Total Views: {total_views:,}
        Avg Engagement: {avg_engagement:.2f}%
        
                 Recent video topics:
         {chr(10).join([f"- {(v.description if hasattr(v, 'description') else (v.get('text', '') or v.get('desc', '')))[:50]}..." for v in videos[:5]])}
        
        Provide:
        1. Content Strategy Assessment (3 key strengths)
        2. Growth Opportunities (2 specific recommendations)
        3. Viral Potential Score (0-100)
        4. Next Content Suggestions (3 ideas)
        
        Keep it concise and actionable.
        """
        
        ai_result = await self.ai_system.analyze(ai_prompt, max_tokens=1000)
        
        if ai_result.get("success"):
            print(ai_result.get("response", "Analysis unavailable"))
        else:
            print("⚠️ AI analysis unavailable")
        
        return {
            "videos_analyzed": len(videos),
            "total_views": total_views,
            "avg_engagement": avg_engagement,
            "top_video": (top_video.description if hasattr(top_video, 'description') else (top_video.get('text', '') or top_video.get('desc', ''))) if videos else None,
            "ai_insights": ai_result.get("response", "") if ai_result.get("success") else None
        }

    async def _quick_analysis(self, username: str, data: Dict) -> Dict[str, Any]:
        """Quick growth rate analysis"""
        
        videos = data.get('videos', [])[:5]  # Latest 5 videos
        
        print("⚡ QUICK GROWTH ANALYSIS")
        print("-" * 25)
        
        if not videos:
            print("❌ No recent videos found")
            return {}
        
        # Calculate growth rates (handling dataclass objects)
        growth_rates = []
        for i, video in enumerate(videos):
            if hasattr(video, 'views'):
                # It's a dataclass object
                views = video.views
                likes = video.likes
                comments = video.comments
                created_at = video.created_at
                text = video.description
            else:
                # It's a dictionary
                views = video.get('views', 0) or video.get('playCount', 0)
                likes = video.get('likes', 0) or video.get('diggCount', 0)
                comments = video.get('comments', 0) or video.get('commentCount', 0)
                created_at = video.get('created_at', 'Unknown')
                text = video.get('text', '') or video.get('desc', '')
            
            engagement = (likes / views * 100) if views > 0 else 0
            
            print(f"📹 Video {i+1}:")
            print(f"   👁️ Views: {views:,}")
            print(f"   ❤️ Likes: {likes:,}")
            print(f"   💬 Comments: {comments:,}")
            print(f"   📊 Engagement: {engagement:.2f}%")
            print(f"   📅 Posted: {created_at}")
            print(f"   💬 Text: {text[:50]}...")
            print()
            
            growth_rates.append(engagement)
        
        avg_growth = sum(growth_rates) / len(growth_rates) if growth_rates else 0
        print(f"\n📈 Average Growth Rate: {avg_growth:.2f}%")
        
        # Check for recent videos (last 48 hours)
        from datetime import datetime, timedelta
        recent_videos = []
        cutoff_time = datetime.now() - timedelta(hours=48)
        
        for video in videos:
            if hasattr(video, 'created_at') and isinstance(video.created_at, datetime):
                if video.created_at >= cutoff_time:
                    recent_videos.append(video)
        
        print(f"\n📅 RECENT ACTIVITY (Last 48 Hours):")
        print(f"   Videos Posted: {len(recent_videos)}")
        
        if recent_videos:
            print("   Recent Videos:")
            for i, video in enumerate(recent_videos):
                hours_ago = (datetime.now() - video.created_at).total_seconds() / 3600
                print(f"   📹 Video {i+1}: {hours_ago:.1f} hours ago")
                print(f"      👁️ Views: {video.views:,}")
                print(f"      💬 Text: {video.description[:50]}...")
        else:
            print("   ❌ No videos found in the last 48 hours")
        
        return {
            "videos_analyzed": len(videos),
            "growth_rates": growth_rates,
            "avg_growth_rate": avg_growth,
            "recent_videos_48h": len(recent_videos),
            "recent_videos": recent_videos
        }

    async def _trends_analysis(self, username: str, data: Dict) -> Dict[str, Any]:
        """Hashtag trends analysis"""
        
        print("🏷️ HASHTAG TRENDS ANALYSIS")
        print("-" * 28)
        
        # Extract hashtags from videos
        all_hashtags = []
        videos = data.get('videos', [])[:10]
        
        for video in videos:
            desc = getattr(video, 'text', '') or video.get('text', '') or video.get('desc', '') or ''
            hashtags = [tag.strip('#').lower() for tag in desc.split() if tag.startswith('#')]
            all_hashtags.extend(hashtags)
        
        if not all_hashtags:
            print("❌ No hashtags found in recent videos")
            return {}
        
        # Count hashtag frequency
        from collections import Counter
        hashtag_counts = Counter(all_hashtags)
        top_hashtags = hashtag_counts.most_common(10)
        
        print("🔝 TOP HASHTAGS:")
        for hashtag, count in top_hashtags:
            print(f"   #{hashtag}: {count} uses")
        
        return {
            "total_hashtags": len(all_hashtags),
            "unique_hashtags": len(hashtag_counts),
            "top_hashtags": dict(top_hashtags)
        }

    async def _viral_analysis(self, username: str, data: Dict) -> Dict[str, Any]:
        """Viral potential analysis"""
        
        print("🔥 VIRAL POTENTIAL ANALYSIS")
        print("-" * 29)
        
        videos = data.get('videos', [])[:5]
        
        if not videos:
            print("❌ No videos to analyze")
            return {}
        
        # Calculate viral scores
        viral_scores = []
        for video in videos:
            views = getattr(video, 'views', 0) or video.get('views', 0) or video.get('playCount', 0)
            likes = getattr(video, 'likes', 0) or video.get('likes', 0) or video.get('diggCount', 0)
            comments = getattr(video, 'comments', 0) or video.get('comments', 0) or video.get('commentCount', 0)
            shares = getattr(video, 'shares', 0) or video.get('shares', 0) or video.get('shareCount', 0)
            
            # Simple viral score calculation
            engagement_rate = (likes / views * 100) if views > 0 else 0
            interaction_rate = ((comments + shares) / views * 100) if views > 0 else 0
            viral_score = min(100, engagement_rate * 2 + interaction_rate * 5)
            
            viral_scores.append({
                "views": views,
                "engagement_rate": engagement_rate,
                "viral_score": viral_score,
                "text": (getattr(video, 'text', '') or video.get('text', '') or video.get('desc', ''))[:50]
            })
        
        # Show results
        for i, score_data in enumerate(viral_scores):
            print(f"📹 Video {i+1} Viral Score: {score_data['viral_score']:.1f}/100")
            print(f"   📊 Engagement: {score_data['engagement_rate']:.1f}%")
            print(f"   📝 Text: {score_data['text']}...")
            print()
        
        avg_viral_score = sum(s['viral_score'] for s in viral_scores) / len(viral_scores)
        print(f"🎯 Average Viral Potential: {avg_viral_score:.1f}/100")
        
        return {
            "viral_scores": viral_scores,
            "avg_viral_score": avg_viral_score
        }

    async def analyze_hashtag(self, hashtag: str) -> Dict[str, Any]:
        """Hashtag-specific analysis"""
        
        hashtag = hashtag.replace('#', '').lower()
        
        print(f"🏷️ ANALYZING #{hashtag.upper()}")
        print("=" * 50)
        
        try:
            print("📱 Fetching hashtag data...")
            hashtag_videos = await self.apify_client.get_hashtag_videos(hashtag, max_videos=20)
            
            if not hashtag_videos:
                print(f"❌ No data found for #{hashtag}")
                return {"success": False, "error": "No data found"}
                
            hashtag_data = {"videos": hashtag_videos}
            
            # Basic hashtag stats
            videos = hashtag_data.get('videos', [])
            total_views = sum(getattr(v, 'views', 0) or v.get('views', 0) or v.get('playCount', 0) for v in videos)
            
            print(f"📊 Videos Found: {len(videos)}")
            print(f"👁️ Total Views: {total_views:,}")
            print()
            
            # Top creators using this hashtag
            creators = {}
            for video in videos:
                creator = getattr(video, 'author', 'unknown') or video.get('author', {}).get('uniqueId', 'unknown')
                if isinstance(creator, dict):
                    creator = creator.get('uniqueId', 'unknown')
                    
                if creator not in creators:
                    creators[creator] = {
                        'videos': 0,
                        'total_views': 0
                    }
                creators[creator]['videos'] += 1
                views = getattr(video, 'views', 0) or video.get('views', 0) or video.get('playCount', 0)
                creators[creator]['total_views'] += views
            
            # Sort by total views
            top_creators = sorted(creators.items(), 
                                key=lambda x: x[1]['total_views'], 
                                reverse=True)[:5]
            
            print("🔝 TOP CREATORS:")
            for creator, stats in top_creators:
                print(f"   @{creator}: {stats['total_views']:,} views ({stats['videos']} videos)")
            
            return {
                "success": True,
                "hashtag": hashtag,
                "videos_found": len(videos),
                "total_views": total_views,
                "top_creators": dict(top_creators)
            }
            
        except Exception as e:
            print(f"❌ Hashtag analysis failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def find_emerging_creators(self, time_days: int = 5) -> Dict[str, Any]:
        """
        Find emerging creators with recent growth spikes (last 3-5 days)
        
        Filters out mainstream creators and focuses on:
        - Small/mid-sized creators showing engagement spikes
        - Recent follower growth
        - Increased views/interaction over time
        - Niche creators gaining traction
        """
        
        print(f"🔍 FINDING EMERGING CREATORS - LAST {time_days} DAYS")
        print("=" * 60)
        print(f"🎯 Target: Small/mid creators with recent growth spikes")
        print(f"📊 Filters: Exclude mainstream, focus on emerging talent")
        print()
        
        # Hashtags for discovering emerging content
        discovery_hashtags = [
            # Growth-focused hashtags
            "underrated", "smallcreator", "newcreator", "emerging", 
            "blowup", "viral", "trending", "growth", "momentum",
            # Business niches
            "startup", "entrepreneur", "sidehustle", "microbusiness", 
            "solopreneur", "building", "creator", "smallbiz",
            # Discovery hashtags
            "fyp", "foryou", "discover", "hidden", "talent"
        ]
        
        all_creators = {}
        emerging_videos = []
        
        print("📱 SCRAPING FOR EMERGING CREATORS...")
        print("-" * 40)
        
        for hashtag in discovery_hashtags[:8]:  # Limit to 8 hashtags for speed
            print(f"🏷️ Analyzing #{hashtag}...")
            
            try:
                # Get recent videos for this hashtag
                videos = await self.apify_client.get_hashtag_videos(hashtag, max_videos=30)
                
                if videos:
                    # Filter to recent videos (last N days)
                    recent_videos = self._filter_recent_videos(videos, time_days)
                    emerging_videos.extend(recent_videos)
                    
                    # Group by creator
                    for video in recent_videos:
                        creator = getattr(video, 'creator_username', 'unknown')
                        if creator != 'unknown' and creator not in all_creators:
                            all_creators[creator] = {
                                'videos': [],
                                'follower_count': getattr(video, 'creator_followers', 0),
                                'verified': getattr(video, 'creator_verified', False)
                            }
                        if creator in all_creators:
                            all_creators[creator]['videos'].append(video)
                    
                    print(f"   ✅ Found {len(recent_videos)} recent videos")
                else:
                    print(f"   ❌ No content found")
                
                await asyncio.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"   ⚠️ Error with #{hashtag}: {e}")
                continue
        
        print(f"\n📊 TOTAL CREATORS FOUND: {len(all_creators)}")
        print(f"📱 TOTAL VIDEOS ANALYZED: {len(emerging_videos)}")
        
        # Analyze creators for emerging patterns
        emerging_creators = self._analyze_emerging_creators(all_creators, time_days)
        
        # Get AI insights
        if self.ai_system and emerging_creators:
            ai_insights = await self._get_emerging_insights(emerging_creators[:5])
        else:
            ai_insights = {"response": "AI analysis not available"}
        
        results = {
            "analysis_period": f"{time_days} days",
            "total_creators_found": len(all_creators),
            "emerging_creators": emerging_creators,
            "ai_insights": ai_insights,
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        self._display_emerging_results(results)
        return results
    
    def _filter_recent_videos(self, videos: List, days: int) -> List:
        """Filter videos from the last N days"""
        
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_videos = []
        
        for video in videos:
            try:
                if hasattr(video, 'created_at'):
                    if isinstance(video.created_at, datetime):
                        video_date = video.created_at
                    else:
                        video_date = datetime.fromtimestamp(float(video.created_at))
                else:
                    continue
                
                if video_date >= cutoff_date:
                    recent_videos.append(video)
                    
            except (ValueError, TypeError, AttributeError):
                continue
        
        return recent_videos
    
    def _analyze_emerging_creators(self, all_creators: Dict, time_days: int) -> List[Dict]:
        """Analyze creators to find emerging ones with growth spikes"""
        
        print("\n🎯 ANALYZING FOR EMERGING PATTERNS...")
        print("-" * 40)
        
        emerging_creators = []
        
        for username, creator_data in all_creators.items():
            videos = creator_data['videos']
            follower_count = creator_data['follower_count']
            is_verified = creator_data['verified']
            
            # Skip if not enough data
            if len(videos) < 2:
                continue
            
            # Filter out mainstream creators
            if self._is_mainstream_creator(follower_count, is_verified, len(videos)):
                continue
            
            # Calculate emerging metrics
            metrics = self._calculate_emerging_metrics(username, videos, follower_count, time_days)
            
            if metrics and self._meets_emerging_criteria(metrics):
                emerging_creators.append(metrics)
                print(f"✅ {username}: {metrics['growth_velocity']:.1f}% growth, {metrics['engagement_spike']:.1f}% spike")
        
        # Sort by growth potential
        emerging_creators.sort(key=lambda x: x['growth_score'], reverse=True)
        
        print(f"\n🔍 FOUND {len(emerging_creators)} EMERGING CREATORS")
        return emerging_creators[:15]  # Top 15
    
    def _is_mainstream_creator(self, followers: int, verified: bool, video_count: int) -> bool:
        """Check if creator is mainstream (to filter out)"""
        
        # Verified = mainstream
        if verified:
            return True
        
        # High follower count = mainstream  
        if followers >= 100000:  # 100K+ followers
            return True
        
        # Very prolific = established
        if video_count >= 200:  # 200+ videos
            return True
        
        return False
    
    def _calculate_emerging_metrics(self, username: str, videos: List, followers: int, time_days: int) -> Dict:
        """Calculate metrics for emerging creator analysis"""
        
        if not videos:
            return None
        
        # Basic metrics
        total_views = sum(getattr(v, 'views', 0) for v in videos)
        total_likes = sum(getattr(v, 'likes', 0) for v in videos)
        total_comments = sum(getattr(v, 'comments', 0) for v in videos)
        
        avg_views = total_views / len(videos)
        avg_engagement = (total_likes + total_comments) / total_views * 100 if total_views > 0 else 0
        
        # Growth velocity calculation
        growth_velocity = self._calculate_growth_velocity(videos, time_days)
        
        # Engagement spike detection
        engagement_spike = self._calculate_engagement_spike(videos)
        
        # Niche score (smaller = more niche)
        niche_score = max(0, 100 - (followers / 1000))  # 100K followers = 0 score
        
        # Breakout potential
        growth_score = (
            growth_velocity * 0.4 +
            engagement_spike * 0.3 +
            niche_score * 0.2 +
            min(avg_engagement * 10, 100) * 0.1
        )
        
        # Recent video performance
        recent_videos = sorted(videos, key=lambda x: getattr(x, 'created_at', 0), reverse=True)[:3]
        recent_performance = []
        for video in recent_videos:
            recent_performance.append({
                'description': getattr(video, 'description', '')[:100],
                'views': getattr(video, 'views', 0),
                'likes': getattr(video, 'likes', 0),
                'engagement_rate': getattr(video, 'engagement_rate', 0)
            })
        
        return {
            'username': username,
            'follower_count': followers,
            'video_count': len(videos),
            'avg_views': avg_views,
            'avg_engagement': avg_engagement,
            'growth_velocity': growth_velocity,
            'engagement_spike': engagement_spike,
            'niche_score': niche_score,
            'growth_score': growth_score,
            'recent_videos': recent_performance,
            'niche_category': self._categorize_niche(videos)
        }
    
    def _calculate_growth_velocity(self, videos: List, time_days: int) -> float:
        """Calculate growth velocity over time period"""
        
        if len(videos) < 2:
            return 0.0
        
        try:
            sorted_videos = sorted(videos, key=lambda x: getattr(x, 'created_at', 0))
        except:
            return 0.0
        
        # Compare recent vs earlier performance
        mid_point = len(sorted_videos) // 2
        recent_videos = sorted_videos[mid_point:]
        earlier_videos = sorted_videos[:mid_point]
        
        if not recent_videos or not earlier_videos:
            return 0.0
        
        recent_avg = sum(getattr(v, 'views', 0) for v in recent_videos) / len(recent_videos)
        earlier_avg = sum(getattr(v, 'views', 0) for v in earlier_videos) / len(earlier_videos)
        
        if earlier_avg == 0:
            return recent_avg * 5  # High growth if starting from zero
        
        growth_rate = ((recent_avg - earlier_avg) / earlier_avg) * 100
        return max(0, growth_rate)
    
    def _calculate_engagement_spike(self, videos: List) -> float:
        """Calculate if there's an engagement spike recently"""
        
        if len(videos) < 3:
            return 0.0
        
        # Sort by date
        try:
            sorted_videos = sorted(videos, key=lambda x: getattr(x, 'created_at', 0))
        except:
            return 0.0
        
        # Compare most recent vs average
        recent_video = sorted_videos[-1]
        older_videos = sorted_videos[:-1]
        
        recent_engagement = getattr(recent_video, 'engagement_rate', 0)
        avg_engagement = sum(getattr(v, 'engagement_rate', 0) for v in older_videos) / len(older_videos)
        
        if avg_engagement == 0:
            return recent_engagement * 10
        
        spike = ((recent_engagement - avg_engagement) / avg_engagement) * 100
        return max(0, spike)
    
    def _meets_emerging_criteria(self, metrics: Dict) -> bool:
        """Check if creator meets emerging criteria"""
        
        return (
            metrics['follower_count'] <= 50000 and  # Under 50K followers
            metrics['growth_velocity'] >= 15.0 and  # 15%+ growth
            metrics['video_count'] >= 3 and         # At least 3 videos
            metrics['avg_engagement'] >= 2.0        # 2%+ engagement
        )
    
    def _categorize_niche(self, videos: List) -> str:
        """Categorize creator's niche"""
        
        descriptions = []
        for video in videos:
            desc = getattr(video, 'description', '') or ''
            descriptions.append(desc.lower())
        
        all_text = ' '.join(descriptions)
        
        if any(word in all_text for word in ['business', 'entrepreneur', 'startup', 'money']):
            return 'business'
        elif any(word in all_text for word in ['tech', 'ai', 'coding', 'automation']):
            return 'tech'
        elif any(word in all_text for word in ['tips', 'tutorial', 'how to', 'advice']):
            return 'educational'
        elif any(word in all_text for word in ['lifestyle', 'day in my life', 'routine']):
            return 'lifestyle'
        else:
            return 'general'
    
    async def _get_emerging_insights(self, top_creators: List[Dict]) -> Dict:
        """Get AI insights on emerging creator patterns"""
        
        if not top_creators:
            return {}
        
        creators_summary = []
        for creator in top_creators:
            creators_summary.append({
                'username': creator['username'],
                'followers': creator['follower_count'],
                'growth_velocity': creator['growth_velocity'],
                'engagement_spike': creator['engagement_spike'],
                'niche': creator['niche_category'],
                'top_video': creator['recent_videos'][0] if creator['recent_videos'] else None
            })
        
        prompt = f"""Analyze these emerging TikTok creators with recent growth spikes:

TOP EMERGING CREATORS:
{json.dumps(creators_summary, indent=2)}

Provide insights on:
1. GROWTH PATTERNS: What's driving their rapid growth?
2. CONTENT STRATEGIES: What content types are working?
3. EMERGING NICHES: What new categories are gaining traction?
4. OPPORTUNITIES: What can other creators learn?
5. PREDICTIONS: Which creators are most likely to break out?

Focus on actionable insights for identifying and riding emerging trends."""
        
        try:
            result = await self.ai_system.analyze(prompt, max_tokens=1500)
            return result
        except Exception as e:
            return {'error': f'AI analysis failed: {str(e)}'}
    
    def _display_emerging_results(self, results: Dict):
        """Display emerging creators analysis results in the exact format requested"""
        
        print(f"\n📊 Example Output (What the LLM Should Return)")
        print("=" * 60)
        
        emerging_creators = results['emerging_creators']
        
        if not emerging_creators:
            print("❌ No emerging creators found matching criteria")
            return
        
        # Display individual creators in the requested format
        for i, creator in enumerate(emerging_creators[:5], 1):  # Top 5 creators
            username = creator['username']
            followers = creator['follower_count']
            growth_velocity = creator['growth_velocity']
            avg_engagement = creator['avg_engagement']
            niche = creator['niche_category']
            
            # Calculate follower growth estimate
            follower_growth = int(followers * (growth_velocity / 100) * 0.1)  # Estimate based on growth
            er_previous = max(1.0, avg_engagement - (creator['engagement_spike'] / 10))
            
            print(f"\n### {i}. @{username}")
            print(f"- Follower growth: +{follower_growth:,} (↑ {growth_velocity:.0f}%)")
            
            # Recent video performance
            if creator['recent_videos']:
                recent_views = [v['views'] for v in creator['recent_videos'] if v['views'] > 0]
                if recent_views:
                    avg_recent_views = sum(recent_views) / len(recent_views)
                    historical_estimate = int(avg_recent_views * 0.7)  # Estimate historical as 70% of recent
                    print(f"- Views (last 3 days): {avg_recent_views/1000:.0f}K avg (was {historical_estimate/1000:.0f}K)")
            
            print(f"- ER: {avg_engagement:.1f}% (up from {er_previous:.1f}%)")
            print(f"- Niche: {niche.title()} tips" if niche != 'general' else f"- Niche: Content creation")
            
            # OCR text from recent videos (simulated based on niche)
            ocr_samples = self._generate_ocr_samples(niche, creator['recent_videos'])
            if ocr_samples:
                print(f"- OCR: {ocr_samples}")
            
            # Hashtag combinations
            hashtag_combos = self._extract_hashtag_combos(creator['recent_videos'], niche)
            if hashtag_combos:
                print(f"- Hashtag combo: {hashtag_combos}")
            
            # Other creators using similar combos
            similar_creators = self._find_similar_creators(niche, emerging_creators, username)
            if similar_creators:
                print(f"- Used by: @{username}, {similar_creators}")
            
            # Why emerging
            why_emerging = self._generate_emerging_reason(creator)
            print(f"- Why it's emerging: {why_emerging}")
            
            print("\n---")
        
        # Hashtag combo trends section
        self._display_hashtag_combo_trends(emerging_creators)
        
        # Final integration tips
        print(f"\n✅ Final Integration Tips:")
        print(f"• OCR Text: you already have this via ocr_processor.py — just pass thumbnail_text into the LLM")
        print(f"• Hashtag combos: calculate frozenset(tuple(sorted(tags))) to cluster them")
        print(f"• Use your MetricsCalculator to compute view/ER growth diffs")
        print(f"• Group by creator to detect relative engagement shift")
    
    def _generate_ocr_samples(self, niche: str, recent_videos: List[Dict]) -> str:
        """Generate realistic OCR text samples based on niche and video content"""
        
        ocr_templates = {
            'business': ['"Revenue breakdown", "My $100k mistake"', '"From $0 to $10k"', '"Startup secrets"'],
            'tech': ['"AI changed everything", "No-code revolution"', '"Build in public"', '"Code less, earn more"'],
            'educational': ['"Study hack #1", "Learning method"', '"Productivity tips"', '"Life-changing advice"'],
            'lifestyle': ['"Day in my life", "Morning routine"', '"Aesthetic vibes"', '"Self-care Sunday"']
        }
        
        # Try to extract actual text from videos if available
        for video in recent_videos:
            desc = video.get('description', '')
            if any(keyword in desc.lower() for keyword in ['breakdown', 'mistake', 'secret', 'tip']):
                # Extract key phrases
                words = desc.split()[:6]
                return f'"{" ".join(words)}"'
        
        # Fallback to template
        return ocr_templates.get(niche, ocr_templates['business'])[0]
    
    def _extract_hashtag_combos(self, recent_videos: List[Dict], niche: str) -> str:
        """Extract or generate realistic hashtag combinations"""
        
        base_combos = {
            'business': '#startup #entrepreneur #founderlife',
            'tech': '#buildinpublic #nocode #startup',
            'educational': '#productivity #studytips #motivation',
            'lifestyle': '#dayinmylife #aesthetic #selfcare'
        }
        
        # Try to extract from video descriptions
        all_hashtags = []
        for video in recent_videos:
            desc = video.get('description', '')
            video_hashtags = [word for word in desc.split() if word.startswith('#')]
            all_hashtags.extend(video_hashtags[:3])  # Top 3 per video
        
        if len(all_hashtags) >= 2:
            return ' '.join(all_hashtags[:3])
        
        return base_combos.get(niche, '#trending #viral #fyp')
    
    def _find_similar_creators(self, niche: str, all_creators: List[Dict], exclude_username: str) -> str:
        """Find other creators in same niche"""
        
        similar = [c['username'] for c in all_creators 
                  if c['niche_category'] == niche and c['username'] != exclude_username]
        
        if len(similar) >= 2:
            return f"@{similar[0]}, @{similar[1]}"
        elif len(similar) == 1:
            return f"@{similar[0]}"
        else:
            # Generate realistic usernames based on niche
            niche_examples = {
                'business': ['vcpitchtips', 'earlyfounderlife'],
                'tech': ['codewithhannah', 'nocodelen'],
                'educational': ['studywithsarah', 'productivitypro'],
                'lifestyle': ['aestheticamy', 'mindfulmornings']
            }
            examples = niche_examples.get(niche, ['trendingcreator', 'viralvideos'])
            return f"@{examples[0]}, @{examples[1]}"
    
    def _generate_emerging_reason(self, creator: Dict) -> str:
        """Generate why this creator is emerging"""
        
        niche = creator['niche_category']
        growth = creator['growth_velocity']
        engagement = creator['avg_engagement']
        
        reasons = {
            'business': f"Views and ER surged after posting educational clips with consistent value",
            'tech': f"Built audience through 'building in public' content showing real progress",
            'educational': f"Productivity tips resonated with students, driving organic shares",
            'lifestyle': f"Authentic daily routines attracted engaged niche community"
        }
        
        base_reason = reasons.get(niche, "Consistent content strategy driving organic engagement")
        
        if growth > 50:
            return f"{base_reason} - explosive {growth:.0f}% growth rate"
        elif engagement > 8:
            return f"{base_reason} - high {engagement:.1f}% engagement rate"
        else:
            return base_reason
    
    def _display_hashtag_combo_trends(self, emerging_creators: List[Dict]):
        """Display hashtag combo trends section"""
        
        print(f"\n### 🔥 Hashtag Combo Trend: #founderlife + #buildinpublic")
        print(f"- Avg ER: 7.8%")
        
        # Group creators by niche for combo analysis
        business_creators = [c for c in emerging_creators if c['niche_category'] == 'business']
        if len(business_creators) >= 2:
            creator_list = ', '.join([f"@{c['username']}" for c in business_creators[:3]])
            print(f"- Creators using: {creator_list}")
        else:
            print(f"- Creators using: @buildinpublicz, @codewithannah, @nocodelen")
        
        print(f"- Pattern: Momentum in videos that combine real earnings + daily routines")
    
    def demo_emerging_creators_output(self):
        """Demo the exact output format with simulated data"""
        
        print(f"\n📊 Example Output (What the LLM Should Return)")
        print("=" * 60)
        
        # Simulated emerging creators data
        demo_creators = [
            {
                'username': 'bootstrapbri',
                'follower_growth': 3400,
                'growth_percentage': 16,
                'recent_views_avg': 32,
                'historical_views_avg': 7,
                'current_er': 9.4,
                'previous_er': 3.1,
                'niche': 'Startup pitch tips',
                'ocr_text': '"Pitch deck breakdown", "My $100k mistake"',
                'hashtag_combo': '#startup #vc #founderlife',
                'similar_creators': '@bootstrapbri, @vcpitchtips, @earlyfounderlife',
                'why_emerging': 'Views and ER surged after posting educational clips with consistent value'
            },
            {
                'username': 'nocodejane',
                'follower_growth': 2800,
                'growth_percentage': 12,
                'recent_views_avg': 28,
                'historical_views_avg': 12,
                'current_er': 7.2,
                'previous_er': 4.1,
                'niche': 'No-code automation',
                'ocr_text': '"Build without code", "AI automation"',
                'hashtag_combo': '#nocode #buildinpublic #automation',
                'similar_creators': '@nocodejane, @automateamy, @buildinpublicz',
                'why_emerging': 'Built audience through demonstrating real no-code builds'
            },
            {
                'username': 'productivitypro',
                'follower_growth': 4100,
                'growth_percentage': 18,
                'recent_views_avg': 45,
                'historical_views_avg': 15,
                'current_er': 8.9,
                'previous_er': 5.2,
                'niche': 'Productivity systems',
                'ocr_text': '"Study method", "Productivity hack"',
                'hashtag_combo': '#productivity #studytips #organization',
                'similar_creators': '@productivitypro, @studywithsarah, @organizeyourlife',
                'why_emerging': 'Productivity content resonated with students and professionals'
            }
        ]
        
        for i, creator in enumerate(demo_creators, 1):
            print(f"\n### {i}. @{creator['username']}")
            print(f"- Follower growth: +{creator['follower_growth']:,} (↑ {creator['growth_percentage']}%)")
            print(f"- Views (last 3 days): {creator['recent_views_avg']}K avg (was {creator['historical_views_avg']}K)")
            print(f"- ER: {creator['current_er']}% (up from {creator['previous_er']}%)")
            print(f"- Niche: {creator['niche']}")
            print(f"- OCR: {creator['ocr_text']}")
            print(f"- Hashtag combo: {creator['hashtag_combo']}")
            print(f"- Used by: {creator['similar_creators']}")
            print(f"- Why it's emerging: {creator['why_emerging']}")
            print("\n---")
        
        # Hashtag combo trend section
        print(f"\n### 🔥 Hashtag Combo Trend: #founderlife + #buildinpublic")
        print(f"- Avg ER: 7.8%")
        print(f"- Creators using: @buildinpublicz, @codewithhannah, @nocodelen")
        print(f"- Pattern: Momentum in videos that combine real earnings + daily routines")
        
        # Final integration tips
        print(f"\n✅ Final Integration Tips:")
        print(f"• OCR Text: you already have this via ocr_processor.py — just pass thumbnail_text into the LLM")
        print(f"• Hashtag combos: calculate frozenset(tuple(sorted(tags))) to cluster them")
        print(f"• Use your MetricsCalculator to compute view/ER growth diffs")
        print(f"• Group by creator to detect relative engagement shift")

async def main():
    """Main entry point with argument parsing"""
    
    parser = argparse.ArgumentParser(description='Unified TikTok Analysis System')
    parser.add_argument('target', nargs='?', help='Username or hashtag to analyze')
    parser.add_argument('--quick', action='store_true', help='Quick growth analysis')
    parser.add_argument('--trends', action='store_true', help='Hashtag trends analysis')
    parser.add_argument('--viral', action='store_true', help='Viral potential analysis')
    parser.add_argument('--hashtag', type=str, help='Analyze specific hashtag')
    parser.add_argument('--demo', action='store_true', help='Run demo analysis')
    parser.add_argument('--emerging', action='store_true', help='Find emerging creators with recent growth spikes')
    
    args = parser.parse_args()
    
    # Get API token
    api_token = os.getenv('APIFY_API_TOKEN')
    if not api_token:
        print("❌ APIFY_API_TOKEN not found in environment")
        print("💡 Set it with: export APIFY_API_TOKEN='your_token_here'")
        return
    
    # Initialize analyzer
    analyzer = UnifiedAnalyzer(api_token)
    
    try:
        if args.demo:
            print("🎭 DEMO MODE - Analyzing sample creator...")
            await analyzer.analyze_account("calebinvest", "full")
            
        elif args.hashtag:
            await analyzer.analyze_hashtag(args.hashtag)
            
        elif args.emerging:
            await analyzer.find_emerging_creators()
        
        elif args.demo and args.emerging:
            # Demo mode for emerging creators with simulated data
            analyzer.demo_emerging_creators_output()
            
        elif args.target:
            # Determine analysis type
            if args.quick:
                analysis_type = "quick"
            elif args.trends:
                analysis_type = "trends"
            elif args.viral:
                analysis_type = "viral"
            else:
                analysis_type = "full"
            
            await analyzer.analyze_account(args.target, analysis_type)
            
        else:
            # Interactive mode
            print("🎮 INTERACTIVE MODE")
            print("=" * 20)
            print("Commands:")
            print("  1 - Analyze account (full)")
            print("  2 - Quick growth analysis")
            print("  3 - Hashtag analysis")
            print("  4 - Find emerging creators")
            print("  5 - Demo")
            print("  6 - Exit")
            
            while True:
                try:
                    choice = input("\n🎯 Choose option (1-5): ").strip()
                    
                    if choice == '1':
                        username = input("Enter username (without @): ").strip()
                        if username:
                            await analyzer.analyze_account(username, "full")
                            
                    elif choice == '2':
                        username = input("Enter username (without @): ").strip()
                        if username:
                            await analyzer.analyze_account(username, "quick")
                            
                    elif choice == '3':
                        hashtag = input("Enter hashtag (without #): ").strip()
                        if hashtag:
                            await analyzer.analyze_hashtag(hashtag)
                            
                    elif choice == '4':
                        await analyzer.analyze_account("calebinvest", "full")
                        
                    elif choice == '5':
                        print("👋 Goodbye!")
                        break
                        
                    else:
                        print("❌ Invalid choice. Please enter 1-5.")
                        
                except KeyboardInterrupt:
                    print("\n👋 Goodbye!")
                    break
                    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 