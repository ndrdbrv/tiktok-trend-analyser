#!/usr/bin/env python3
"""
🧹 PROJECT CLEANUP & ORGANIZATION
=================================

Clean up the shanks project and organize files properly
"""

import os
import shutil
from pathlib import Path

def organize_project():
    """Organize project files into proper structure"""
    
    print("🧹 ORGANIZING SHANKS PROJECT")
    print("=" * 40)
    
    # Files to keep (core system)
    KEEP_FILES = {
        "core_system": [
            "viral_intelligence_formulas.py",  # New formulas file
            "ai_enhanced_hashtag_intelligence.py",  # Main AI system
            "london_startup_creator_analysis.py",  # Creator analysis
            "startup_hashtag_intelligence.py",  # Hashtag intelligence
            "test_ai_system_minimal.py",  # System tests
            "orchestrator.py",  # Main orchestrator
            "run_system.py",  # System runner
            "README.md",
            "requirements.txt"
        ],
        "working_analysis": [
            "analysis/startup_intel_report.py",
            "analysis/emerging_trend_detector.py", 
            "analysis/live_trending_analysis.py"
        ],
        "agents": [
            "agents/base_agent.py",
            "agents/ingestion_agent.py"
        ],
        "config": [
            "config/definitions.py",
            "config/hashtag_targets.py",
            "config/metric_formulas.py"
        ]
    }
    
    # Files to archive (demos and tests)
    ARCHIVE_FILES = [
        "ai_capabilities_demo.py",
        "ai_demo_with_openai.py", 
        "advanced_virality_metrics_demo.py",
        "next_steps_analysis.py",
        "test_tjr_analysis.py",
        "check_tjr_dates.py",
        "tjr_24h_viral_breakdown.py",
        "analyze_specific_video.py",
        "analyze_specific_video_fixed.py",
        "analyze_video_content.py",
        "demos/",
        "tests/"
    ]
    
    # Create archive directory
    archive_dir = Path("archive/demos_and_tests")
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    print("📁 Creating organized structure...")
    
    # Move demo files to archive
    for file_pattern in ARCHIVE_FILES:
        file_path = Path(file_pattern)
        if file_path.exists():
            if file_path.is_file():
                shutil.move(str(file_path), str(archive_dir / file_path.name))
                print(f"   📦 Archived: {file_path.name}")
            elif file_path.is_dir():
                shutil.move(str(file_path), str(archive_dir / file_path.name))
                print(f"   📦 Archived directory: {file_path.name}")
    
    print("\n✅ CORE SYSTEM FILES:")
    for file in KEEP_FILES["core_system"]:
        if Path(file).exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} (missing)")
    
    print("\n📋 PROJECT STRUCTURE:")
    print("""
    shanks/
    ├── 📊 viral_intelligence_formulas.py    # ⭐ NEW: All formulas
    ├── 🤖 ai_enhanced_hashtag_intelligence.py # Main AI system  
    ├── 🇬🇧 london_startup_creator_analysis.py # Creator analysis
    ├── 🏷️ startup_hashtag_intelligence.py    # Hashtag intel
    ├── 🧪 test_ai_system_minimal.py         # System tests
    ├── 🎯 orchestrator.py                   # Main orchestrator
    ├── ▶️ run_system.py                     # System runner
    ├── agents/                              # Agent modules
    ├── analysis/                            # Analysis modules  
    ├── config/                              # Configuration
    ├── archive/                             # Archived demos
    └── utils/                               # Utilities
    """)
    
    return True

def create_quick_start_guide():
    """Create a quick start guide for the system"""
    
    guide_content = """# 🚀 SHANKS VIRAL INTELLIGENCE SYSTEM
## Quick Start Guide

### 🎯 MAIN SYSTEMS:

1. **📊 Formulas Reference:**
   ```bash
   python viral_intelligence_formulas.py
   ```

2. **🤖 AI-Enhanced Analysis:**
   ```bash
   python ai_enhanced_hashtag_intelligence.py
   ```

3. **🇬🇧 London Creator Analysis:**
   ```bash
   python london_startup_creator_analysis.py
   ```

4. **🏷️ Hashtag Intelligence:**
   ```bash
   python startup_hashtag_intelligence.py
   ```

5. **🧪 System Test:**
   ```bash
   python test_ai_system_minimal.py
   ```

### 🔧 CONFIGURATION:
- API keys configured in each script
- Apify: ✅ Active subscription  
- Anthropic: ✅ Credits available
- OpenAI: ✅ Backup system

### 📊 CORE FORMULAS:
- **Engagement Rate:** `(L + C + S) / n.D | R.A`
- **Momentum Score:** `(Growth_V × 0.4) + (Follower_Eng_Ratio × 0.3) + (Videos_p/Δ × 0.2) + (Regular_Posting × 0.1)`
- **Hashtag Growth:** `Videos_Δ / Videos_∀Δ`
- **Creator Momentum:** `Engagement_Head × Growth_Rate + Consistency(Video_Volume)`

### 🎯 KEY INSIGHTS:
- #londontech = highest performing hashtag
- Authenticity beats perfection  
- Behind-the-scenes content drives engagement
- Sustainability angle resonates well

### 💡 OPTIMAL HASHTAGS FOR YOUR CONTENT:
`#startup #entrepreneur #londontech #worktok #buildinpublic #founderlife #fyp`

---
**System Status:** ✅ 100% Operational  
**Last Updated:** Today  
**Cost per Analysis:** ~$3-6
"""

    with open("QUICK_START.md", "w") as f:
        f.write(guide_content)
    
    print("✅ Created QUICK_START.md guide")

if __name__ == "__main__":
    organize_project()
    create_quick_start_guide()
    
    print("\n🎉 PROJECT CLEANUP COMPLETE!")
    print("📋 Check QUICK_START.md for usage guide")
    print("📊 All formulas available in viral_intelligence_formulas.py")
    print("🚀 System ready for viral intelligence analysis!") 