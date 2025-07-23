"""
LLM Analysis Component
=====================

Uses Claude Opus 4 for trending analysis and insights.
"""

import json
from typing import Dict, List, Any
import sys
import os

# Add parent directory to import Claude
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai.claude_primary_system import ClaudePrimarySystem

class LLMAnalyzer:
    """Handles AI analysis using Claude Opus 4"""
    
    def __init__(self):
        self.claude = ClaudePrimarySystem()
        
    async def analyze_trending_topics(self, videos: List[Dict]) -> Dict[str, Any]:
        """Analyze trending topics from video data"""
        
        # Prepare data for Claude
        video_data = []
        for video in videos[:20]:  # Top 20 for analysis
            video_data.append({
                'author': video.get('author', ''),
                'text': video.get('text', '')[:200],
                'ocr_text': video.get('ocr_text', ''),
                'views': video.get('views', 0),
                'engagement_rate': video.get('engagement_rate', 0),
                'hashtags': video.get('hashtags', [])[:5]
            })
        
        prompt = f"""Analyze these {len(video_data)} trending TikTok videos for topic trends:

VIDEO DATA:
{json.dumps(video_data, indent=2)}

Provide analysis on:

1. **TRENDING TOPICS**: What topics are gaining momentum?
2. **HASHTAG TRENDS**: Which hashtags are performing best?
3. **CONTENT PATTERNS**: What content types are viral?
4. **THUMBNAIL TEXT INSIGHTS**: What do thumbnails reveal about trends?
5. **AUDIENCE BEHAVIOR**: What's resonating with viewers?

Return structured insights with specific examples and data."""

        try:
            result = await self.claude.analyze(prompt, max_tokens=2000)
            
            if result["success"]:
                return {
                    'trending_analysis': result["response"],
                    'cost': result.get('cost', 0),
                    'response_time': result.get('response_time', 0),
                    'model_used': 'claude-opus-4'
                }
            else:
                return {'error': result.get('error', 'Analysis failed')}
                
        except Exception as e:
            return {'error': f'LLM analysis failed: {str(e)}'}
    
    async def analyze_hashtag_momentum(self, hashtag_data: Dict) -> Dict[str, Any]:
        """Analyze hashtag momentum and growth patterns"""
        
        prompt = f"""Analyze hashtag momentum from this data:

HASHTAG DATA:
{json.dumps(hashtag_data, indent=2)}

Provide insights on:

1. **MOMENTUM PATTERNS**: Which hashtags are growing fastest?
2. **USAGE TRENDS**: How are successful hashtags being used?
3. **COMBINATION STRATEGIES**: Which hashtag combos work best?
4. **TIMING INSIGHTS**: When do these hashtags perform best?
5. **PREDICTIONS**: Which hashtags will likely trend next?

Focus on actionable insights for content creators."""

        try:
            result = await self.claude.analyze(prompt, max_tokens=1500)
            
            if result["success"]:
                return {
                    'hashtag_analysis': result["response"],
                    'cost': result.get('cost', 0),
                    'model_used': 'claude-opus-4'
                }
            else:
                return {'error': result.get('error', 'Hashtag analysis failed')}
                
        except Exception as e:
            return {'error': f'Hashtag analysis failed: {str(e)}'}
    
    async def generate_content_recommendations(self, analysis_data: Dict) -> Dict[str, Any]:
        """Generate content creation recommendations"""
        
        prompt = f"""Based on this trending analysis, create specific content recommendations:

ANALYSIS DATA:
{json.dumps(analysis_data, indent=2)}

Generate:

1. **5 SPECIFIC VIDEO IDEAS** that would likely go viral
2. **OPTIMAL HASHTAG COMBOS** for each video idea  
3. **THUMBNAIL TEXT SUGGESTIONS** based on successful patterns
4. **POSTING TIMING** recommendations
5. **CONTENT HOOKS** that are currently working

Make recommendations specific and actionable."""

        try:
            result = await self.claude.analyze(prompt, max_tokens=2000)
            
            if result["success"]:
                return {
                    'recommendations': result["response"],
                    'cost': result.get('cost', 0),
                    'model_used': 'claude-opus-4'
                }
            else:
                return {'error': result.get('error', 'Recommendations failed')}
                
        except Exception as e:
            return {'error': f'Recommendations failed: {str(e)}'} 