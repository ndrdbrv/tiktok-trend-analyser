"""
Metrics Calculation Component
============================

Calculates engagement rates, viral scores, and growth metrics.
Enhanced with LLM analysis for semantic metrics.
"""

import sys
import os
from typing import Dict, List
from collections import Counter, defaultdict
from datetime import datetime, timedelta

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from ai.claude_primary_system import ClaudePrimarySystem
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("⚠️ LLM system not available for enhanced metrics")

class MetricsCalculator:
    """Handles all metrics calculations with LLM enhancement"""
    
    def __init__(self):
        self.llm = ClaudePrimarySystem() if LLM_AVAILABLE else None
        
    def calculate_engagement_metrics(self, videos: List[Dict]) -> List[Dict]:
        """Calculate engagement metrics for videos with LLM enhancement"""
        
        print("📊 Calculating enhanced metrics with Claude analysis...")
        
        for i, video in enumerate(videos):
            views = video.get('views', 0)
            likes = video.get('likes', 0)
            comments = video.get('comments', 0)
            shares = video.get('shares', 0)
            
            # Basic engagement metrics
            total_engagement = likes + comments + shares
            engagement_rate = (total_engagement / views * 100) if views > 0 else 0
            
            # Viral score (weighted engagement)
            like_weight = 1.0
            comment_weight = 3.0  # Comments are more valuable
            share_weight = 5.0    # Shares are most valuable
            
            weighted_engagement = (likes * like_weight + 
                                 comments * comment_weight + 
                                 shares * share_weight)
            
            viral_score = min((weighted_engagement / views * 100), 100) if views > 0 else 0
            
            # Add basic metrics
            video['engagement_rate'] = round(engagement_rate, 2)
            video['viral_score'] = round(viral_score, 2)
            video['total_engagement'] = total_engagement
            
            # LLM-Enhanced Semantic Metrics
            if self.llm and i < 10:  # Analyze top 10 videos for performance
                semantic_metrics = self._calculate_llm_metrics(video)
                video.update(semantic_metrics)
            
            if (i + 1) % 20 == 0:
                print(f"   Processed {i + 1}/{len(videos)} videos...")
        
        return videos
    
    def _calculate_llm_metrics(self, video: Dict) -> Dict:
        """Calculate LLM-enhanced semantic metrics"""
        
        try:
            # Prepare content for analysis
            description = video.get('text', '')
            ocr_text = video.get('ocr_text', '')
            author = video.get('author', '')
            engagement_rate = video.get('engagement_rate', 0)
            views = video.get('views', 0)
            
            # Quick LLM analysis prompt
            prompt = f"""Analyze this TikTok video content for viral patterns:

DESCRIPTION: {description[:200]}
THUMBNAIL TEXT: {ocr_text}
AUTHOR: @{author}
VIEWS: {views:,}
ENGAGEMENT: {engagement_rate}%

Provide ONLY a JSON response with these metrics:
{{
    "hook_strength": 0-10,
    "viral_pattern_score": 0-10,
    "content_category": "business|lifestyle|educational|entertainment|other",
    "click_bait_score": 0-10,
    "thumbnail_effectiveness": 0-10,
    "trending_potential": 0-10
}}

Focus on: hook strength, viral patterns, thumbnail text impact, and trending potential."""

            # Get LLM analysis (use sync version for speed)
            import asyncio
            try:
                result = asyncio.run(self.llm.analyze(prompt, max_tokens=200))
                
                if result.get("success"):
                    response = result["response"].strip()
                    # Extract JSON from response
                    import json
                    import re
                    
                    # Find JSON in response
                    json_match = re.search(r'\{.*\}', response, re.DOTALL)
                    if json_match:
                        metrics_data = json.loads(json_match.group())
                        
                        return {
                            'hook_strength': metrics_data.get('hook_strength', 5),
                            'viral_pattern_score': metrics_data.get('viral_pattern_score', 5),
                            'content_category': metrics_data.get('content_category', 'other'),
                            'click_bait_score': metrics_data.get('click_bait_score', 5),
                            'thumbnail_effectiveness': metrics_data.get('thumbnail_effectiveness', 5),
                            'trending_potential': metrics_data.get('trending_potential', 5),
                            'llm_cost': result.get('cost', 0)
                        }
                
            except Exception as e:
                print(f"   ⚠️ LLM analysis failed for video: {str(e)[:50]}")
                
        except Exception as e:
            print(f"   ⚠️ Metrics calculation failed: {str(e)[:50]}")
        
        # Return default metrics if LLM fails
        return {
            'hook_strength': 5,
            'viral_pattern_score': 5,
            'content_category': 'unknown',
            'click_bait_score': 5,
            'thumbnail_effectiveness': 5,
            'trending_potential': 5,
            'llm_cost': 0
        }
    
    def calculate_hashtag_metrics(self, videos: List[Dict]) -> Dict[str, Dict]:
        """Calculate hashtag performance metrics with LLM insights"""
        
        hashtag_data = defaultdict(lambda: {
            'count': 0,
            'total_views': 0,
            'total_engagement': 0,
            'avg_engagement_rate': 0,
            'top_creators': [],
            'viral_pattern_scores': [],
            'trending_potentials': []
        })
        
        # Collect hashtag data
        for video in videos:
            hashtags = video.get('hashtags', [])
            views = video.get('views', 0)
            engagement = video.get('total_engagement', 0)
            engagement_rate = video.get('engagement_rate', 0)
            author = video.get('author', '')
            
            # LLM metrics
            viral_pattern = video.get('viral_pattern_score', 5)
            trending_potential = video.get('trending_potential', 5)
            
            for hashtag in hashtags:
                data = hashtag_data[hashtag]
                data['count'] += 1
                data['total_views'] += views
                data['total_engagement'] += engagement
                data['viral_pattern_scores'].append(viral_pattern)
                data['trending_potentials'].append(trending_potential)
                
                if author not in data['top_creators']:
                    data['top_creators'].append(author)
        
        # Calculate averages and add LLM insights
        for hashtag, data in hashtag_data.items():
            if data['count'] > 0:
                data['avg_views'] = data['total_views'] / data['count']
                data['avg_engagement_rate'] = data['total_engagement'] / data['total_views'] * 100 if data['total_views'] > 0 else 0
                data['avg_viral_pattern'] = sum(data['viral_pattern_scores']) / len(data['viral_pattern_scores'])
                data['avg_trending_potential'] = sum(data['trending_potentials']) / len(data['trending_potentials'])
                
                # Momentum score (combines traditional + LLM metrics)
                momentum_score = (
                    data['avg_engagement_rate'] * 0.3 +
                    data['avg_viral_pattern'] * 0.4 +
                    data['avg_trending_potential'] * 0.3
                )
                data['momentum_score'] = round(momentum_score, 2)
        
        return dict(hashtag_data)
    
    def calculate_trending_metrics(self, videos: List[Dict]) -> Dict:
        """Calculate overall trending metrics with LLM insights"""
        
        if not videos:
            return {}
        
        total_videos = len(videos)
        total_views = sum(v.get('views', 0) for v in videos)
        total_engagement = sum(v.get('total_engagement', 0) for v in videos)
        
        avg_engagement_rate = sum(v.get('engagement_rate', 0) for v in videos) / total_videos
        avg_viral_score = sum(v.get('viral_score', 0) for v in videos) / total_videos
        
        # LLM-enhanced metrics
        avg_hook_strength = sum(v.get('hook_strength', 5) for v in videos) / total_videos
        avg_viral_pattern = sum(v.get('viral_pattern_score', 5) for v in videos) / total_videos
        avg_trending_potential = sum(v.get('trending_potential', 5) for v in videos) / total_videos
        
        # Content category distribution
        categories = [v.get('content_category', 'unknown') for v in videos]
        category_distribution = dict(Counter(categories))
        
        # Calculate trending momentum (LLM-enhanced)
        trending_momentum = (
            avg_engagement_rate * 0.25 +
            avg_viral_score * 0.25 +
            avg_hook_strength * 0.2 +
            avg_viral_pattern * 0.15 +
            avg_trending_potential * 0.15
        )
        
        return {
            'total_videos': total_videos,
            'total_views': total_views,
            'total_engagement': total_engagement,
            'avg_engagement_rate': round(avg_engagement_rate, 2),
            'avg_viral_score': round(avg_viral_score, 2),
            'avg_hook_strength': round(avg_hook_strength, 2),
            'avg_viral_pattern': round(avg_viral_pattern, 2),
            'avg_trending_potential': round(avg_trending_potential, 2),
            'trending_momentum': round(trending_momentum, 2),
            'category_distribution': category_distribution,
            'top_performing_video': max(videos, key=lambda x: x.get('viral_score', 0)) if videos else None
        } 