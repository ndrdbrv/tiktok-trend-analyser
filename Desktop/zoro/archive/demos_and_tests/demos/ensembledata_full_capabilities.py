#!/usr/bin/env python3
"""
EnsembleData API - FULL CAPABILITIES DEMO
==========================================

Shows ALL available search methods, not just hashtags:
- 🎵 Music/Sound trends  
- 👤 User/Creator analysis
- 🔍 Keyword searches
- #️⃣ Hashtag monitoring
- 🎬 Video analysis
- 💬 Comment analysis
"""

import asyncio
from ensembledata.api import EDClient
from datetime import datetime

class EnsembleDataFullDemo:
    """Demonstrate all EnsembleData API capabilities"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = EDClient(api_key, timeout=30)
        self.total_units_used = 0
    
    def _safe_int(self, value):
        """Safely convert units to int"""
        try:
            return int(value) if value else 0
        except (ValueError, TypeError):
            return 0
    
    def _track_units(self, result):
        """Track API units used"""
        units = self._safe_int(result.units_charged)
        self.total_units_used += units
        return units
    
    async def demo_music_trends(self):
        """🎵 MUSIC/SOUND TREND ANALYSIS"""
        print("🎵 MUSIC/SOUND TREND ANALYSIS")
        print("=" * 40)
        print("Find viral sounds and music trending in different niches")
        print()
        
        music_queries = ["motivational", "startup", "business", "viral beat", "trending"]
        
        for query in music_queries:
            try:
                print(f"🎼 Searching music: '{query}'")
                result = self.client.tiktok.music_search(keyword=query, sorting="0", filter_by="0")
                units = self._track_units(result)
                
                if result.data and 'data' in result.data:
                    sounds = result.data['data'][:3]  # Top 3 results
                    
                    for i, sound in enumerate(sounds, 1):
                        print(f"   {i}. 🎵 {sound.get('title', 'Unknown')}")
                        print(f"      Author: {sound.get('author', 'Unknown')}")
                        print(f"      Play URL: {sound.get('play_url', 'N/A')}")
                        print(f"      Duration: {sound.get('duration', 0)} seconds")
                        print()
                
                print(f"   📊 Units used: {units}")
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
        
        print()
    
    async def demo_user_analysis(self):
        """👤 USER/CREATOR ANALYSIS"""
        print("👤 USER/CREATOR ANALYSIS")
        print("=" * 30)
        print("Analyze creators, their followers, and content performance")
        print()
        
        # Analyze popular business/startup creators
        creators = ["mrbeast", "garyvee", "alexhormozi", "theofficialselfmade"]
        
        for creator in creators:
            try:
                print(f"👤 Analyzing creator: @{creator}")
                
                # Get user info
                user_info = self.client.tiktok.user_info_from_username(username=creator)
                units1 = self._track_units(user_info)
                
                if user_info.data:
                    user_data = user_info.data
                    print(f"   📊 Followers: {user_data.get('followerCount', 0):,}")
                    print(f"   📹 Videos: {user_data.get('videoCount', 0):,}")
                    print(f"   ❤️ Total Likes: {user_data.get('heartCount', 0):,}")
                    print(f"   ✅ Verified: {user_data.get('verified', False)}")
                    
                    # Get recent posts
                    print(f"   🎬 Recent posts:")
                    user_posts = self.client.tiktok.user_posts_from_username(username=creator, depth=1)
                    units2 = self._track_units(user_posts)
                    
                    if user_posts.data and 'data' in user_posts.data:
                        posts = user_posts.data['data'][:3]  # Latest 3 posts
                        
                        for i, post in enumerate(posts, 1):
                            stats = post.get('stats', {})
                            print(f"      {i}. Views: {stats.get('playCount', 0):,}")
                            print(f"         Likes: {stats.get('diggCount', 0):,}")
                            print(f"         Comments: {stats.get('commentCount', 0):,}")
                            print(f"         Description: {post.get('desc', '')[:60]}...")
                            print()
                
                print(f"   📊 Total units used: {units1 + units2}")
                await asyncio.sleep(0.8)
                
            except Exception as e:
                print(f"   ❌ Error analyzing {creator}: {str(e)}")
        
        print()
    
    async def demo_keyword_search(self):
        """🔍 KEYWORD SEARCH ANALYSIS"""
        print("🔍 KEYWORD SEARCH ANALYSIS")
        print("=" * 35)
        print("Search for ANY keyword/topic across all TikTok content")
        print()
        
        keywords = [
            "artificial intelligence",
            "startup advice", 
            "day in the life entrepreneur",
            "passive income",
            "digital marketing",
            "cryptocurrency"
        ]
        
        for keyword in keywords:
            try:
                print(f"🔍 Searching keyword: '{keyword}'")
                result = self.client.tiktok.keyword_search(keyword=keyword, period="7")
                units = self._track_units(result)
                
                if result.data and 'data' in result.data:
                    videos = result.data['data'][:3]  # Top 3 results
                    
                    for i, video in enumerate(videos, 1):
                        stats = video.get('stats', {})
                        author_info = video.get('author', {})
                        
                        print(f"   {i}. 👤 @{author_info.get('uniqueId', 'unknown')}")
                        print(f"      📊 {stats.get('playCount', 0):,} views")
                        print(f"      ❤️ {stats.get('diggCount', 0):,} likes")
                        print(f"      📝 {video.get('desc', '')[:50]}...")
                        print()
                
                print(f"   📊 Units used: {units}")
                await asyncio.sleep(0.6)
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
        
        print()
    
    async def demo_hashtag_analysis(self):
        """#️⃣ HASHTAG ANALYSIS (Enhanced)"""
        print("#️⃣ HASHTAG ANALYSIS (Enhanced)")
        print("=" * 40)
        print("Deep dive into hashtag performance and trends")
        print()
        
        hashtags = ["startup", "entrepreneur", "ai", "productivity", "motivation"]
        
        for hashtag in hashtags:
            try:
                print(f"#️⃣ Analyzing hashtag: #{hashtag}")
                
                # Get hashtag data
                result = self.client.tiktok.hashtag_search(hashtag=hashtag, cursor=0)
                units = self._track_units(result)
                
                if result.data and 'data' in result.data:
                    videos = result.data['data'][:5]  # Top 5 videos
                    
                    total_views = sum(video.get('stats', {}).get('playCount', 0) for video in videos)
                    total_likes = sum(video.get('stats', {}).get('diggCount', 0) for video in videos)
                    avg_engagement = (total_likes / max(total_views, 1)) * 100
                    
                    print(f"   📊 Sample size: {len(videos)} videos")
                    print(f"   👀 Total views: {total_views:,}")
                    print(f"   ❤️ Total likes: {total_likes:,}")
                    print(f"   📈 Avg engagement: {avg_engagement:.2f}%")
                    
                    print(f"   🎬 Top performing videos:")
                    for i, video in enumerate(videos[:3], 1):
                        stats = video.get('stats', {})
                        author = video.get('author', {})
                        views = stats.get('playCount', 0)
                        likes = stats.get('diggCount', 0)
                        engagement = (likes / max(views, 1)) * 100
                        
                        print(f"      {i}. @{author.get('uniqueId', 'unknown')}")
                        print(f"         📊 {views:,} views, {likes:,} likes ({engagement:.1f}%)")
                        print(f"         📝 {video.get('desc', '')[:40]}...")
                        print()
                
                print(f"   📊 Units used: {units}")
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
        
        print()
    
    async def demo_video_deep_dive(self):
        """🎬 VIDEO DEEP DIVE ANALYSIS"""
        print("🎬 VIDEO DEEP DIVE ANALYSIS")
        print("=" * 35)
        print("Get detailed info about specific videos and their comments")
        print()
        
        # First, get a video ID from hashtag search
        try:
            print("🔍 Finding a viral startup video for deep analysis...")
            result = self.client.tiktok.hashtag_search(hashtag="startup", cursor=0)
            self._track_units(result)
            
            if result.data and 'data' in result.data:
                video = result.data['data'][0]  # Get first video
                video_id = video.get('id')
                
                if video_id:
                    print(f"🎬 Analyzing video ID: {video_id}")
                    
                    # Get detailed video info
                    video_info = self.client.tiktok.video_info(video_id=video_id)
                    units1 = self._track_units(video_info)
                    
                    if video_info.data:
                        v_data = video_info.data
                        stats = v_data.get('stats', {})
                        author = v_data.get('author', {})
                        
                        print(f"   👤 Creator: @{author.get('uniqueId', 'unknown')}")
                        print(f"   📊 Views: {stats.get('playCount', 0):,}")
                        print(f"   ❤️ Likes: {stats.get('diggCount', 0):,}")
                        print(f"   💬 Comments: {stats.get('commentCount', 0):,}")
                        print(f"   🔄 Shares: {stats.get('shareCount', 0):,}")
                        print(f"   📝 Description: {v_data.get('desc', '')}")
                        print(f"   🕐 Created: {v_data.get('createTime', 'Unknown')}")
                        print()
                        
                        # Get comments for sentiment analysis
                        print("   💬 Sample comments:")
                        try:
                            comments = self.client.tiktok.video_comments(video_id=video_id, cursor=0)
                            units2 = self._track_units(comments)
                            
                            if comments.data and 'data' in comments.data:
                                comment_list = comments.data['data'][:5]  # Top 5 comments
                                
                                for i, comment in enumerate(comment_list, 1):
                                    comment_text = comment.get('text', '')
                                    like_count = comment.get('digg_count', 0)
                                    print(f"      {i}. {comment_text[:60]}... ({like_count} likes)")
                                
                                print(f"   📊 Comment analysis units: {units2}")
                            
                        except Exception as e:
                            print(f"   ❌ Comment analysis error: {str(e)}")
                        
                        print(f"   📊 Total units used: {units1}")
        
        except Exception as e:
            print(f"❌ Video deep dive error: {str(e)}")
        
        print()
    
    async def demo_comprehensive_creator_spy(self):
        """🕵️ COMPREHENSIVE CREATOR SPY"""
        print("🕵️ COMPREHENSIVE CREATOR SPY")
        print("=" * 40)
        print("Find creators by niche and analyze their complete strategy")
        print()
        
        # Search for creators in specific niches
        niches = ["startup coach", "business mentor", "entrepreneur"]
        
        for niche in niches:
            try:
                print(f"🔍 Finding '{niche}' creators...")
                
                # Use keyword search to find creators
                result = self.client.tiktok.keyword_search(keyword=niche, period="30")
                units = self._track_units(result)
                
                if result.data and 'data' in result.data:
                    videos = result.data['data'][:3]  # Top 3 videos
                    
                    creators_analyzed = set()
                    
                    for video in videos:
                        author = video.get('author', {})
                        username = author.get('uniqueId', '')
                        
                        if username and username not in creators_analyzed:
                            creators_analyzed.add(username)
                            
                            print(f"   🎯 Found creator: @{username}")
                            print(f"      📊 Followers: {author.get('followerCount', 0):,}")
                            print(f"      ✅ Verified: {author.get('verified', False)}")
                            
                            # Get their content strategy
                            video_stats = video.get('stats', {})
                            views = video_stats.get('playCount', 0)
                            likes = video_stats.get('diggCount', 0)
                            engagement = (likes / max(views, 1)) * 100
                            
                            print(f"      📈 Sample video: {views:,} views, {engagement:.1f}% engagement")
                            print(f"      📝 Content: {video.get('desc', '')[:50]}...")
                            print()
                
                print(f"   📊 Units used: {units}")
                await asyncio.sleep(0.7)
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
        
        print()
    
    async def run_full_demo(self):
        """Run complete demonstration of ALL EnsembleData capabilities"""
        
        print("🚀 ENSEMBLEDATA API - COMPLETE CAPABILITIES DEMO")
        print("=" * 70)
        print("🎯 Showing ALL available data sources beyond just hashtags!")
        print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        try:
            # Demo all capabilities
            await self.demo_music_trends()
            await self.demo_user_analysis()
            await self.demo_keyword_search()
            await self.demo_hashtag_analysis()
            await self.demo_video_deep_dive()
            await self.demo_comprehensive_creator_spy()
            
            # Final summary
            print("📊 DEMO SUMMARY")
            print("=" * 20)
            print(f"✅ Total API units used: {self.total_units_used}")
            print(f"🎯 Data sources demonstrated:")
            print(f"   • 🎵 Music/Sound trends")
            print(f"   • 👤 Creator/User analysis") 
            print(f"   • 🔍 Keyword searches")
            print(f"   • #️⃣ Hashtag monitoring")
            print(f"   • 🎬 Video deep analysis")
            print(f"   • 💬 Comment sentiment")
            print(f"   • 🕵️ Creator discovery")
            print()
            print("🎉 EnsembleData can track ANY type of viral content!")
            print("   Not limited to hashtags - full TikTok ecosystem access!")
            
        except Exception as e:
            print(f"❌ Demo error: {str(e)}")

async def main():
    """Run the complete EnsembleData capabilities demo"""
    
    api_key = "MZTq3h5VIyi0CjKt"
    demo = EnsembleDataFullDemo(api_key)
    
    await demo.run_full_demo()

if __name__ == "__main__":
    asyncio.run(main()) 