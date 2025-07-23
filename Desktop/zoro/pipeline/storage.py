"""
Data Storage Component
=====================

Handles saving and loading analysis results.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

class DataStorage:
    """Handles data storage and retrieval"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def save_analysis(self, data: Dict[str, Any], analysis_type: str = "trending") -> str:
        """Save analysis results with timestamp"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{analysis_type}_analysis_{timestamp}.json"
        filepath = os.path.join(self.data_dir, filename)
        
        # Add metadata
        data['metadata'] = {
            'timestamp': timestamp,
            'analysis_type': analysis_type,
            'created_at': datetime.now().isoformat()
        }
        
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            print(f"💾 Analysis saved: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ Save failed: {e}")
            return ""
    
    def load_latest_analysis(self, analysis_type: str = "trending") -> Dict[str, Any]:
        """Load the most recent analysis of given type"""
        
        try:
            # Find all files of this type
            files = [f for f in os.listdir(self.data_dir) 
                    if f.startswith(f"{analysis_type}_analysis_") and f.endswith('.json')]
            
            if not files:
                return {}
            
            # Get the most recent file
            latest_file = sorted(files)[-1]
            filepath = os.path.join(self.data_dir, latest_file)
            
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            print(f"📂 Loaded analysis: {latest_file}")
            return data
            
        except Exception as e:
            print(f"❌ Load failed: {e}")
            return {}
    
    def list_analyses(self) -> List[str]:
        """List all saved analyses"""
        
        try:
            files = [f for f in os.listdir(self.data_dir) if f.endswith('.json')]
            return sorted(files, reverse=True)  # Most recent first
            
        except Exception as e:
            print(f"❌ List failed: {e}")
            return []
    
    def export_summary(self, data: Dict[str, Any], filename: str = None) -> str:
        """Export a human-readable summary"""
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"trending_summary_{timestamp}.txt"
        
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            with open(filepath, 'w') as f:
                f.write("🚀 TIKTOK TRENDING ANALYSIS SUMMARY\n")
                f.write("=" * 50 + "\n\n")
                
                # Basic metrics
                if 'metrics' in data:
                    metrics = data['metrics']
                    f.write(f"📊 OVERVIEW:\n")
                    f.write(f"   Videos analyzed: {metrics.get('total_videos', 0)}\n")
                    f.write(f"   Total views: {metrics.get('total_views', 0):,}\n")
                    f.write(f"   Average engagement: {metrics.get('avg_engagement_rate', 0):.2f}%\n\n")
                
                # Top hashtags
                if 'hashtag_metrics' in data:
                    f.write(f"🏷️ TOP HASHTAGS:\n")
                    for i, (hashtag, metrics) in enumerate(list(data['hashtag_metrics'].items())[:10], 1):
                        f.write(f"   {i}. #{hashtag} - {metrics['momentum_score']:.0f} momentum\n")
                    f.write("\n")
                
                # LLM insights
                if 'llm_analysis' in data and 'trending_analysis' in data['llm_analysis']:
                    f.write(f"🤖 AI INSIGHTS:\n")
                    f.write(data['llm_analysis']['trending_analysis'])
                    f.write("\n\n")
            
            print(f"📄 Summary exported: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return "" 