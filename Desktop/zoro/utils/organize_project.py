#!/usr/bin/env python3
"""
Project Organization Script
===========================
Clean up and organize the shanks project structure
"""

import os
import shutil
from pathlib import Path

def organize_project():
    """Organize project files into clean directory structure"""
    
    print("🧹 ORGANIZING PROJECT STRUCTURE")
    print("=" * 40)
    
    # Define the clean directory structure
    directories = {
        "demos/": "Demo and example files",
        "analysis/": "Analysis and reporting tools", 
        "integrations/": "Third-party integrations",
        "ai/": "AI and LLM related files",
        "utils/": "Utility and helper scripts",
        "archive/": "Old/deprecated files"
    }
    
    # Create directories
    print("📁 Creating directory structure...")
    for directory, description in directories.items():
        Path(directory).mkdir(exist_ok=True)
        print(f"   ✅ {directory} - {description}")
    
    print()
    
    # Define file movements
    file_moves = {
        # Demo files
        "demos/": [
            "comprehensive_video_analyzer.py",
            "ensembledata_full_capabilities.py", 
            "hashtag_discovery_system.py",
            "simple_hook_demo.py",
            "debug_creator_data.py"
        ],
        
        # Analysis tools
        "analysis/": [
            "micro_app_builders_report.py",
            "viral_metrics_explained.py",
            "video_hook_analyzer.py",
            "current_project_status.py",
            "project_status_report.py",
            "live_trending_analysis.py",
            "startup_intel_report.py",
            "targeted_cta_hunter.py",
            "working_creator_spy.py"
        ],
        
        # Integrations
        "integrations/": [
            "apify_enhancement_plan.py",
            "apify_integration_plan.py", 
            "apify_integration_setup.py",
            "ensemble_data_breakdown.py"
        ],
        
        # AI/LLM files
        "ai/": [
            "llamaindex_integration.py",
            "llamaindex_claude_integration.py",
            "claude_only_system.py",
            "setup_llm_integration.py",
            "llm_comparison_analysis.py"
        ],
        
        # Utility files
        "utils/": [
            "organize_project.py",  # This file
            "test_startup_ingestion.py"
        ]
    }
    
    # Move files
    print("📦 Moving files to organized structure...")
    
    moved_count = 0
    for target_dir, files in file_moves.items():
        if files:
            print(f"\n📂 Moving to {target_dir}:")
            
        for file in files:
            if Path(file).exists():
                try:
                    shutil.move(file, target_dir + file)
                    print(f"   ✅ {file}")
                    moved_count += 1
                except Exception as e:
                    print(f"   ❌ {file} - Error: {e}")
            else:
                print(f"   ⚠️ {file} - Not found")
    
    # Clean up root directory - keep only essential files
    print(f"\n📋 ESSENTIAL FILES REMAINING IN ROOT:")
    print("-" * 35)
    
    essential_files = [
        "agents/",
        "config/", 
        "docs/",
        "tests/",
        "demos/",
        "analysis/", 
        "integrations/",
        "ai/",
        "utils/",
        "run_system.py",
        "orchestrator.py", 
        "requirements.txt",
        "README.md",
        ".venv/",
        ".gitignore"
    ]
    
    for item in essential_files:
        if Path(item).exists():
            if Path(item).is_dir():
                print(f"   📁 {item}")
            else:
                print(f"   📄 {item}")
    
    print(f"\n✅ Moved {moved_count} files into organized structure!")
    
    # Create a clean README for the new structure
    create_organized_readme()
    
    print("\n🎯 PROJECT IS NOW ORGANIZED!")
    print("=" * 30)
    print("📁 demos/ - Try the system capabilities")
    print("📊 analysis/ - Run viral analysis reports") 
    print("🔌 integrations/ - Add Apify, Claude, etc.")
    print("🤖 ai/ - LLM and AI-powered features")
    print("🛠️ utils/ - Helper scripts and tools")

def create_organized_readme():
    """Create README for the organized structure"""
    
    readme_content = """# 🚀 TikTok Viral Analysis System

## 📁 Project Structure

### 🎯 Quick Start
```bash
# Test the system
python demos/comprehensive_video_analyzer.py

# Run viral analysis
python analysis/micro_app_builders_report.py

# Main system
python run_system.py
```

### 📂 Directories

**📁 `demos/`** - Try system capabilities
- `comprehensive_video_analyzer.py` - Full system demo
- `hashtag_discovery_system.py` - Find related hashtags
- `ensembledata_full_capabilities.py` - All API features

**📊 `analysis/`** - Viral analysis tools  
- `micro_app_builders_report.py` - Find micro-influencers
- `video_hook_analyzer.py` - Analyze viral hooks
- `viral_metrics_explained.py` - Understand metrics

**🔌 `integrations/`** - Third-party connections
- `apify_integration_setup.py` - Add visual analysis
- `ensemble_data_breakdown.py` - API capabilities

**🤖 `ai/`** - AI-powered features
- `llamaindex_claude_integration.py` - Claude 3.5 Sonnet
- `claude_only_system.py` - Pure Claude system
- `setup_llm_integration.py` - LLM setup

**🛠️ `utils/`** - Helper tools
- `organize_project.py` - Clean up structure

**⚙️ `agents/`** - Core system agents
- `ingestion_agent.py` - Data collection
- `base_agent.py` - Agent framework

**📋 `config/`** - Configuration files
- `definitions.py` - System definitions
- `hashtag_targets.py` - Target hashtags

## 🚀 Usage

1. **Test the system**: `python demos/comprehensive_video_analyzer.py`
2. **Run analysis**: `python analysis/micro_app_builders_report.py`  
3. **Add AI**: Set API keys and run `python ai/claude_only_system.py`
4. **Full system**: `python run_system.py`

## 📊 Status: 95% Complete - Ready for API keys!
"""
    
    with open("README.md", "w") as f:
        f.write(readme_content)
    
    print("   ✅ Created organized README.md")

if __name__ == "__main__":
    organize_project() 