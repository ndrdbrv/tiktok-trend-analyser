#!/usr/bin/env python3
"""
�� ENVIRONMENT LOADER (Claude Primary)
======================================

Loads environment variables from .env file for the TikTok trend analyzer.
Simplified for Claude Opus 4 primary system.
"""

import os
from pathlib import Path

def load_env_file(env_path: str = ".env"):
    """Load environment variables from .env file"""
    env_file = Path(env_path)
    
    if not env_file.exists():
        print(f"⚠️ .env file not found at {env_file.absolute()}")
        print("Create a .env file with your API keys")
        return False
    
    print(f"📁 Loading environment from {env_file.absolute()}")
    
    with open(env_file, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Parse KEY=VALUE format
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                
                # Set environment variable
                os.environ[key] = value
                print(f"✅ Loaded {key}: {value[:20]}...")
    
    return True

if __name__ == "__main__":
    print("🔧 Loading environment variables...")
    success = load_env_file()
    
    if success:
        print("\n📊 Current environment variables:")
        # Only check essential keys for Claude Primary system
        essential_keys = ['ANTHROPIC_API_KEY', 'APIFY_API_TOKEN']
        
        for key in essential_keys:
            value = os.getenv(key)
            if value:
                print(f"✅ {key}: {value[:20]}...")
            else:
                print(f"❌ {key}: Not set")
        
        print("\n🤖 System: Claude Primary (Simplified)")
        print("🎯 Ready for TikTok trend analysis!")
    else:
        print("❌ Failed to load .env file") 