#!/usr/bin/env python3
"""
Ingestion Agent for TikTok Trend Prediction Multi-Agent System
==============================================================

This agent is responsible for fetching data from Apify APIs for real TikTok data
and storing it for analysis. Focused on startup/entrepreneurship content monitoring.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import uuid
import structlog
import time
from dataclasses import dataclass

from langchain_core.tools import BaseTool, tool
from pydantic import BaseModel, Field

# Apify client for TikTok scraping
from apify_client import ApifyClient

from agents.base_agent import BaseAgent, AgentTask, AgentResult, IngestionTask
from config.definitions import AgentRole
from config.hashtag_targets import get_priority_hashtags, HashtagCategory, STARTUP_ENTREPRENEURSHIP_HASHTAGS

# =============================================================================
# APIFY-BASED DATA STRUCTURES  
# =============================================================================

@dataclass
class TikTokCreatorData:
    """Real TikTok creator data from Apify"""
    username: str
    display_name: str
    followers: int
    following: int
    likes: int
    videos: int
    verified: bool
    bio: str
    avatar_url: str
    is_private: bool

@dataclass
class TikTokVideoData:
    """Real TikTok video data from Apify"""
    video_id: str
    creator_username: str
    description: str
    views: int
    likes: int
    comments: int
    shares: int
    created_at: datetime
    video_url: str
    hashtags: List[str]
    music_title: str
    duration: int

@dataclass
class StartupVideoData:
    """Structured data for startup-related TikTok videos from Apify"""
    video_id: str
    hashtags: List[str]
    creator_username: str
    creator_followers: int
    creator_verified: bool
    views: int
    likes: int
    comments: int
    shares: int
    engagement_rate: float
    description: str
    duration: int
    created_at: datetime
    growth_velocity: float
    viral_score: float
    business_relevance_score: float

@dataclass
class HashtagTrendData:
    """Structured data for hashtag trend analysis"""
    hashtag: str
    total_posts: int
    posts_last_hour: int
    posts_last_24h: int
    growth_velocity: float
    acceleration: float
    top_creators: List[str]
    avg_engagement_rate: float
    trending_score: float

# =============================================================================
# APIFY SDK CLIENT
# =============================================================================

class ApifyContentIngestion:
    """
    High-quality TikTok content ingestion using Apify actors
    """
    
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.client = ApifyClient(api_token)
        self.logger = structlog.get_logger().bind(component="apify_ingestion")
        
        # Top-rated Apify TikTok actors
        self.actors = {
            "profile_scraper": "clockworks/tiktok-profile-scraper",  # 9.7K users, 4.8★
            "hashtag_scraper": "clockworks/tiktok-hashtag-scraper",  # 5.2K users, 4.6★
            "data_extractor": "clockworks/free-tiktok-scraper",      # 29K users, 4.8★
            "video_scraper": "clockworks/tiktok-video-scraper",      # 3.5K users, 4.8★
        }
        
        # Cache for avoiding duplicate requests
        self.hashtag_cache = {}
        self.last_cache_clear = datetime.now()
    
    def _safe_int(self, value):
        """Safely convert values to int"""
        try:
            return int(value) if value else 0
        except (ValueError, TypeError):
            return 0
    
    def _calculate_engagement_rate(self, likes: int, comments: int, shares: int, views: int) -> float:
        """Calculate engagement rate"""
        if views == 0:
            return 0.0
        return (likes + comments + shares) / views
    
    def _calculate_growth_velocity(self, current_posts: int, previous_posts: int) -> float:
        """Calculate growth velocity"""
        if previous_posts == 0:
            return float('inf') if current_posts > 0 else 0.0
        return (current_posts - previous_posts) / previous_posts
    
    def _calculate_viral_score(self, views: int, likes: int, comments: int, shares: int, creator_followers: int) -> float:
        """Calculate viral score based on metrics"""
        if creator_followers == 0:
            return 0.0
        
        # Engagement rate
        engagement_rate = self._calculate_engagement_rate(likes, comments, shares, views)
        
        # View-to-follower ratio (viral reach)
        reach_ratio = views / creator_followers if creator_followers > 0 else 0
        
        # Shareability score
        share_score = shares / max(views, 1)
        
        # Combine metrics (0-100 scale)
        viral_score = min(100, (engagement_rate * 100 * 0.4) + (reach_ratio * 20) + (share_score * 100 * 0.4))
        
        return viral_score
    
    async def get_creator_profile(self, username: str) -> Optional[TikTokCreatorData]:
        """Get real creator profile data using Apify TikTok Profile Scraper"""
        try:
            self.logger.info("Fetching creator profile", username=username)
            
            run_input = {
                "profiles": [f"https://www.tiktok.com/@{username}"],
                "resultsType": "details"
            }
            
            # Run the actor
            run = self.client.actor(self.actors["profile_scraper"]).call(
                run_input=run_input,
                timeout_secs=300
            )
            
            # Get the results
            results = []
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                results.append(item)
            
            if results:
                profile = results[0]
                
                # Based on debug output, the profile data structure is different
                # Let's extract from the authorMeta structure that we see in video results
                author_meta = profile.get("authorMeta", {})
                
                creator_data = TikTokCreatorData(
                    username=author_meta.get("name", username),
                    display_name=author_meta.get("nickName", ""),
                    followers=self._safe_int(author_meta.get("fans", 0)),
                    following=self._safe_int(author_meta.get("following", 0)), 
                    likes=self._safe_int(author_meta.get("heart", 0)),
                    videos=self._safe_int(author_meta.get("video", 0)),
                    verified=author_meta.get("verified", False),
                    bio=author_meta.get("signature", ""),
                    avatar_url=author_meta.get("avatar", ""),
                    is_private=author_meta.get("privateAccount", False)
                )
                
                self.logger.info("Successfully fetched creator profile", 
                               username=username, 
                               followers=creator_data.followers,
                               verified=creator_data.verified)
                
                return creator_data
            else:
                self.logger.warning("No data returned for creator", username=username)
                return None
                
        except Exception as e:
            self.logger.error("Error fetching creator profile", username=username, error=str(e))
            return None
    
    async def get_hashtag_videos(self, hashtag: str, max_videos: int = 50) -> List[TikTokVideoData]:
        """Get real videos for a hashtag using Apify TikTok Hashtag Scraper"""
        try:
            self.logger.info("Fetching hashtag videos", hashtag=hashtag, max_videos=max_videos)
            
            run_input = {
                "hashtags": [hashtag],
                "resultsPerPage": max_videos,
                "shouldDownloadVideos": False,
                "shouldDownloadCovers": False
            }
            
            # Run the actor
            run = self.client.actor(self.actors["hashtag_scraper"]).call(
                run_input=run_input,
                timeout_secs=600
            )
            
            # Get the results
            videos = []
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                
                # Extract hashtags from description
                desc = item.get("text", "")
                hashtags = []
                words = desc.split()
                for word in words:
                    if word.startswith("#"):
                        hashtags.append(word[1:])  # Remove #
                
                video_data = TikTokVideoData(
                    video_id=item.get("id", ""),
                    creator_username=item.get("authorMeta", {}).get("name", ""),
                    description=desc,
                    views=self._safe_int(item.get("playCount", 0)),
                    likes=self._safe_int(item.get("diggCount", 0)),
                    comments=self._safe_int(item.get("commentCount", 0)),
                    shares=self._safe_int(item.get("shareCount", 0)),
                    created_at=datetime.fromtimestamp(item.get("createTime", 0)) if item.get("createTime") else datetime.now(),
                    video_url=item.get("webVideoUrl", ""),
                    hashtags=hashtags,
                    music_title=item.get("musicMeta", {}).get("musicName", ""),
                    duration=self._safe_int(item.get("videoMeta", {}).get("duration", 0))
                )
                videos.append(video_data)
            
            self.logger.info("Successfully fetched hashtag videos", 
                           hashtag=hashtag, 
                           videos_found=len(videos))
            return videos
            
        except Exception as e:
            self.logger.error("Error fetching hashtag videos", hashtag=hashtag, error=str(e))
            return []

    async def collect_startup_hashtag_data(self, hashtag: str, max_videos: int = 50) -> Dict[str, Any]:
        """Collect and analyze startup-related hashtag data"""
        try:
            # Get videos for the hashtag
            videos = await self.get_hashtag_videos(hashtag, max_videos)
            
            if not videos:
                return {
                    "success": False,
                    "error": f"No videos found for #{hashtag}",
                    "hashtag": hashtag
                }
            
            # Process videos into startup data format
            startup_videos = []
            for video in videos:
                # Get creator data for follower count
                creator_data = await self.get_creator_profile(video.creator_username)
                creator_followers = creator_data.followers if creator_data else 0
                creator_verified = creator_data.verified if creator_data else False
                
                # Calculate metrics
                engagement_rate = self._calculate_engagement_rate(
                    video.likes, video.comments, video.shares, video.views
                )
                viral_score = self._calculate_viral_score(
                    video.views, video.likes, video.comments, video.shares, creator_followers
                )
                
                # Business relevance score (simple keyword matching for now)
                business_keywords = ['startup', 'business', 'entrepreneur', 'money', 'success', 'growth']
                business_relevance = sum(1 for keyword in business_keywords 
                                       if keyword.lower() in video.description.lower()) / len(business_keywords)
                
                startup_video = StartupVideoData(
                    video_id=video.video_id,
                    hashtags=video.hashtags,
                    creator_username=video.creator_username,
                    creator_followers=creator_followers,
                    creator_verified=creator_verified,
                    views=video.views,
                    likes=video.likes,
                    comments=video.comments,
                    shares=video.shares,
                    engagement_rate=engagement_rate,
                    description=video.description,
                    duration=video.duration,
                    created_at=video.created_at,
                    growth_velocity=0.0,  # Would need historical data
                    viral_score=viral_score,
                    business_relevance_score=business_relevance
                )
                startup_videos.append(startup_video)
            
            # Sort by viral score
            startup_videos.sort(key=lambda x: x.viral_score, reverse=True)
            
            return {
                "success": True,
                "hashtag": hashtag,
                "total_videos": len(startup_videos),
                "startup_videos": startup_videos,
                "collection_timestamp": datetime.now(),
                "avg_viral_score": sum(v.viral_score for v in startup_videos) / len(startup_videos),
                "top_creators": list(set([v.creator_username for v in startup_videos[:10]]))
            }
            
        except Exception as e:
            self.logger.error("Error collecting startup hashtag data", hashtag=hashtag, error=str(e))
            return {
                "success": False,
                "error": str(e),
                "hashtag": hashtag
            }

# =============================================================================
# LANGCHAIN TOOLS FOR STARTUP MONITORING
# =============================================================================

@tool
def monitor_startup_trends(hashtag_list: List[str]) -> str:
    """Monitor trending startup hashtags for viral potential"""
    try:
        # This would be called by LangChain agent
        return f"Monitoring {len(hashtag_list)} startup hashtags: {', '.join(hashtag_list)}"
    except Exception as e:
        return f"Error monitoring trends: {e}"

@tool  
def analyze_startup_video(video_url: str) -> str:
    """Analyze individual startup video for viral elements"""
    try:
        # This would be called by LangChain agent
        return f"Analyzing startup video: {video_url}"
    except Exception as e:
        return f"Error analyzing video: {e}"

# =============================================================================
# UPDATED INGESTION AGENT
# =============================================================================

class IngestionAgent(BaseAgent):
    """
    Agent responsible for ingesting startup/business content from TikTok via Apify APIs
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        # Get configuration
        config = config or {}
        api_token = config.get('apify_api_token', os.getenv('APIFY_API_TOKEN'))
        
        if not api_token:
            raise ValueError("APIFY_API_TOKEN is required")
        
        # Initialize Apify content ingestion
        self.apify_ingestion = ApifyContentIngestion(api_token)
        
        # LangChain tools for startup monitoring
        tools = [monitor_startup_trends, analyze_startup_video]
        
        # Initialize base agent
        super().__init__(
            agent_name="ingestion_agent",
            agent_role=AgentRole.INGESTION,
            tools=tools,
            config=config
        )
        
        self.logger.info("Apify Ingestion Agent initialized", api_token_length=len(api_token))
    
    def _create_agent(self):
        """Create LangChain agent for startup content ingestion"""
        # For now, return None since we're using the SDK directly
        # In future, this could create a LangChain agent with LLM reasoning
        return None
    
    async def execute_task(self, task) -> AgentResult:
        """Execute ingestion task"""
        if hasattr(task, 'task_type'):
            if task.task_type == "startup_trends":
                return await self.ingest_startup_trends(task.parameters.get('hashtag_list'))
            elif task.task_type == "hashtag_analysis":
                hashtag = task.parameters.get('hashtag')
                count = task.parameters.get('count', 50)
                return await self.ingest_hashtag_videos(hashtag, count)
        
        # Default: ingest startup trends
        return await self.ingest_startup_trends()
    
    async def ingest_startup_trends(self, hashtag_list: List[str] = None) -> AgentResult:
        """Ingest trending startup content"""
        try:
            if not hashtag_list:
                hashtag_list = get_priority_hashtags(HashtagCategory.STARTUP_BASIC)
            
            all_results = {}
            
            for hashtag in hashtag_list[:5]:  # Limit to 5 hashtags to avoid rate limits
                result = await self.apify_ingestion.collect_startup_hashtag_data(hashtag, max_videos=20)
                
                if result.get("success"):
                    all_results[hashtag] = result
                    self.logger.info("Successfully ingested hashtag", 
                                   hashtag=hashtag, 
                                   videos=result.get("total_videos", 0))
                else:
                    self.logger.warning("Failed to ingest hashtag", 
                                      hashtag=hashtag, 
                                      error=result.get("error"))
            
            return AgentResult(
                agent_name=self.agent_name,
                task_id=str(uuid.uuid4()),
                success=len(all_results) > 0,
                data=all_results,
                metadata={
                    "hashtags_processed": len(all_results),
                    "total_hashtags_attempted": len(hashtag_list),
                    "timestamp": datetime.now()
                }
            )
            
        except Exception as e:
            self.logger.error("Error in startup trends ingestion", error=str(e))
            return AgentResult(
                agent_name=self.agent_name,
                task_id=str(uuid.uuid4()),
                success=False,
                error=str(e)
            )
    
    async def ingest_hashtag_videos(self, hashtag: str, count: int = 50) -> AgentResult:
        """Ingest videos for a specific hashtag"""
        try:
            result = await self.apify_ingestion.collect_startup_hashtag_data(hashtag, max_videos=count)
            
            return AgentResult(
                agent_name=self.agent_name,
                task_id=str(uuid.uuid4()),
                success=result.get("success", False),
                data=result,
                metadata={
                    "hashtag": hashtag,
                    "videos_requested": count,
                    "videos_found": result.get("total_videos", 0),
                    "timestamp": datetime.now()
                }
            )
            
        except Exception as e:
            self.logger.error("Error in hashtag video ingestion", hashtag=hashtag, error=str(e))
            return AgentResult(
                agent_name=self.agent_name,
                task_id=str(uuid.uuid4()),
                success=False,
                error=str(e)
            )

# =============================================================================
# TESTING & EXAMPLES
# =============================================================================

async def test_apify_ingestion():
    """Test the Apify ingestion system"""
    
    print("🚀 TESTING APIFY INGESTION SYSTEM")
    print("=" * 50)
    
    # Test configuration
    config = {"apify_api_token": os.getenv('APIFY_API_TOKEN')}
    
    # Create agent
    agent = IngestionAgent(config=config)
    
    # Test startup trends ingestion
    print("📊 Testing startup trends ingestion...")
    trends_task = IngestionTask(
        task_type="startup_trends",
        parameters={"hashtag_list": ["entrepreneur", "startup"]}
    )
    
    result = await agent.execute_task(trends_task)
    
    if result.success:
        print("✅ Startup trends ingestion: SUCCESS")
        print(f"   Hashtags processed: {result.metadata.get('hashtags_processed')}")
        for hashtag, data in result.data.items():
            print(f"   #{hashtag}: {data.get('total_videos', 0)} videos")
    else:
        print(f"❌ Startup trends ingestion: FAILED - {result.error}")

if __name__ == "__main__":
    import os
    asyncio.run(test_apify_ingestion())
