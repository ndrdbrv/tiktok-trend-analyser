#!/usr/bin/env python3
"""
Hashtag Discovery System
========================

Find related hashtags by analyzing content across different hashtags.
Discovers hashtag combinations and trending patterns.
"""

import asyncio
import re
from collections import Counter
from ensembledata.api import EDClient

class HashtagDiscoverySystem:
    """Discover related hashtags and hashtag combinations"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = EDClient(api_key, timeout=30)
        self.hashtag_combinations = {}
        self.hashtag_co_occurrence = Counter()
    
    def extract_hashtags_from_text(self, text: str) -> list:
        """Extract all hashtags from video description"""
        if not text:
            return []
        
        # Find all hashtags in text
        hashtags = re.findall(r'#(\w+)', text.lower())
        return list(set(hashtags))  # Remove duplicates
    
    async def discover_related_hashtags(self, seed_hashtag: str, max_videos: int = 100):
        """Discover hashtags related to a seed hashtag"""
        
        print(f"🔍 DISCOVERING HASHTAGS RELATED TO #{seed_hashtag}")
        print("=" * 60)
        
        try:
            # Get videos from seed hashtag
            result = self.client.tiktok.hashtag_search(hashtag=seed_hashtag, cursor=0)
            
            if not result.data or 'data' not in result.data:
                print(f"❌ No data found for #{seed_hashtag}")
                return {}
            
            videos = result.data['data'][:max_videos]
            
            print(f"📊 Analyzing {len(videos)} videos from #{seed_hashtag}...")
            
            all_related_hashtags = []
            hashtag_contexts = {}
            
            for video in videos:
                description = video.get('desc', '')
                hashtags_in_video = self.extract_hashtags_from_text(description)
                
                # Store context for each hashtag
                for hashtag in hashtags_in_video:
                    if hashtag != seed_hashtag:  # Exclude the seed hashtag
                        all_related_hashtags.append(hashtag)
                        
                        if hashtag not in hashtag_contexts:
                            hashtag_contexts[hashtag] = []
                        hashtag_contexts[hashtag].append({
                            'description': description[:100] + '...',
                            'creator': video.get('author', {}).get('uniqueId', 'unknown'),
                            'views': video.get('stats', {}).get('playCount', 0),
                            'likes': video.get('stats', {}).get('diggCount', 0)
                        })
                
                # Track hashtag combinations
                if len(hashtags_in_video) > 1:
                    combo = tuple(sorted(hashtags_in_video))
                    if combo not in self.hashtag_combinations:
                        self.hashtag_combinations[combo] = 0
                    self.hashtag_combinations[combo] += 1
            
            # Count frequency of related hashtags
            hashtag_frequency = Counter(all_related_hashtags)
            
            print(f"\n🎯 TOP 10 RELATED HASHTAGS:")
            print("-" * 30)
            
            discovery_results = {}
            
            for hashtag, count in hashtag_frequency.most_common(10):
                percentage = (count / len(videos)) * 100
                
                # Get sample contexts
                sample_contexts = hashtag_contexts[hashtag][:3]
                avg_views = sum(ctx['views'] for ctx in sample_contexts) / len(sample_contexts)
                
                print(f"#{hashtag}")
                print(f"  📊 Used in {count}/{len(videos)} videos ({percentage:.1f}%)")
                print(f"  👀 Avg views: {avg_views:,.0f}")
                print(f"  🎬 Sample creators: {', '.join([ctx['creator'] for ctx in sample_contexts[:3]])}")
                print()
                
                discovery_results[hashtag] = {
                    'frequency': count,
                    'percentage': percentage,
                    'avg_views': avg_views,
                    'sample_contexts': sample_contexts
                }
            
            return discovery_results
            
        except Exception as e:
            print(f"❌ Error discovering hashtags: {str(e)}")
            return {}
    
    async def find_hashtag_combinations(self, target_hashtags: list):
        """Find common hashtag combinations"""
        
        print(f"\n🔗 HASHTAG COMBINATION ANALYSIS")
        print("=" * 40)
        
        combination_analysis = {}
        
        for hashtag in target_hashtags:
            print(f"\n📊 Analyzing combinations with #{hashtag}...")
            
            try:
                result = self.client.tiktok.hashtag_search(hashtag=hashtag, cursor=0)
                
                if result.data and 'data' in result.data:
                    videos = result.data['data'][:50]  # Analyze 50 videos
                    
                    combinations_with_this_hashtag = []
                    
                    for video in videos:
                        description = video.get('desc', '')
                        hashtags_in_video = self.extract_hashtags_from_text(description)
                        
                        if len(hashtags_in_video) > 1:
                            # Find other hashtags used with this one
                            other_hashtags = [h for h in hashtags_in_video if h != hashtag]
                            for other in other_hashtags:
                                combinations_with_this_hashtag.append(other)
                    
                    # Count combinations
                    combo_counter = Counter(combinations_with_this_hashtag)
                    
                    print(f"  🎯 Top combinations with #{hashtag}:")
                    for combo_hashtag, count in combo_counter.most_common(5):
                        percentage = (count / len(videos)) * 100
                        print(f"    #{combo_hashtag} - {count} times ({percentage:.1f}%)")
                    
                    combination_analysis[hashtag] = combo_counter.most_common(10)
                
                await asyncio.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"  ❌ Error analyzing #{hashtag}: {str(e)}")
        
        return combination_analysis
    
    async def discover_trending_hashtag_clusters(self):
        """Discover clusters of hashtags that trend together"""
        
        print(f"\n🌟 TRENDING HASHTAG CLUSTERS")
        print("=" * 35)
        
        # Analyze multiple seed hashtags to find clusters
        seed_hashtags = ["startup", "entrepreneur", "business", "ai", "productivity"]
        
        hashtag_network = {}
        
        for seed in seed_hashtags:
            print(f"\n🔍 Building network from #{seed}...")
            
            related = await self.discover_related_hashtags(seed, max_videos=30)
            hashtag_network[seed] = related
            
            await asyncio.sleep(0.3)
        
        # Find clusters (hashtags that appear together frequently)
        print(f"\n🎯 HASHTAG CLUSTERS:")
        print("-" * 25)
        
        # Cluster 1: Business/Entrepreneurship
        business_cluster = set()
        for seed in ["startup", "entrepreneur", "business"]:
            if seed in hashtag_network:
                business_cluster.update(hashtag_network[seed].keys())
        
        print(f"📈 Business/Startup Cluster:")
        print(f"   {', '.join(['#' + h for h in list(business_cluster)[:10]])}")
        print()
        
        # Cluster 2: Tech/AI  
        tech_cluster = set()
        for seed in ["ai", "productivity"]:
            if seed in hashtag_network:
                tech_cluster.update(hashtag_network[seed].keys())
        
        print(f"🤖 Tech/AI Cluster:")
        print(f"   {', '.join(['#' + h for h in list(tech_cluster)[:10]])}")
        print()
        
        return {
            'business_cluster': business_cluster,
            'tech_cluster': tech_cluster,
            'full_network': hashtag_network
        }

async def demo_hashtag_discovery():
    """Demo the hashtag discovery system"""
    
    print("🎯 HASHTAG DISCOVERY SYSTEM DEMO")
    print("=" * 50)
    print("Find related hashtags and trending combinations!")
    print()
    
    api_key = "MZTq3h5VIyi0CjKt"
    discovery = HashtagDiscoverySystem(api_key)
    
    # Demo 1: Discover hashtags related to "startup"
    print("📊 PHASE 1: DISCOVER RELATED HASHTAGS")
    startup_related = await discovery.discover_related_hashtags("startup", max_videos=50)
    
    # Demo 2: Analyze hashtag combinations
    print("\n📊 PHASE 2: HASHTAG COMBINATIONS")
    target_hashtags = ["startup", "entrepreneur", "business"]
    combinations = await discovery.find_hashtag_combinations(target_hashtags)
    
    # Demo 3: Find trending clusters
    print("\n📊 PHASE 3: TRENDING CLUSTERS")
    clusters = await discovery.discover_trending_hashtag_clusters()
    
    # Summary
    print("\n🎉 DISCOVERY COMPLETE!")
    print("=" * 30)
    print(f"✅ Found {len(startup_related)} hashtags related to #startup")
    print(f"✅ Analyzed combinations for {len(target_hashtags)} hashtags")
    print(f"✅ Identified {len(clusters)} hashtag clusters")
    print()
    print("💡 USE CASES:")
    print("• Find new hashtags to target")
    print("• Discover trending combinations")
    print("• Build comprehensive hashtag strategies")
    print("• Track how hashtags evolve together")

if __name__ == "__main__":
    asyncio.run(demo_hashtag_discovery()) 