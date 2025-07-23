#!/usr/bin/env python3
"""
TikTok Trend Prediction Multi-Agent System - Main Runner
========================================================

This script demonstrates how to run the complete TikTok trend prediction
multi-agent system powered by Apify and LangChain.

Usage:
    python run_system.py
    python run_system.py --demo
    python run_system.py --config config.yaml
"""

import asyncio
import sys
import os
import json
import argparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging first
import structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

from orchestrator import WorkflowOrchestrator
from agents import IngestionAgent, AVAILABLE_AGENTS

# =============================================================================
# CONFIGURATION
# =============================================================================

def load_config(config_path: str = None) -> dict:
    """Load configuration from environment and config file"""
    
    # Try to load from .env file first
    load_dotenv()
    
    config = {
        # API Configuration - Use your real API key!
        'apify_api_token': os.getenv('APIFY_API_TOKEN'),
        
        # LLM Configuration
        'openai_api_key': os.getenv('OPENAI_API_KEY'),
        'anthropic_api_key': os.getenv('ANTHROPIC_API_KEY'),
        
        # System Configuration
        'environment': os.getenv('ENVIRONMENT', 'development'),
        'log_level': os.getenv('LOG_LEVEL', 'INFO'),
        'max_concurrent_workflows': int(os.getenv('MAX_CONCURRENT_WORKFLOWS', '3')),
        'workflow_timeout_minutes': int(os.getenv('WORKFLOW_TIMEOUT_MINUTES', '30')),
        
        # Feature Flags
        'enable_semantic_analysis': os.getenv('ENABLE_SEMANTIC_ANALYSIS', 'false').lower() == 'true',
        'enable_real_time_alerts': os.getenv('ENABLE_REAL_TIME_ALERTS', 'true').lower() == 'true',
        'enable_demo_mode': False,  # Now using real data!
    }
    
    # Load from config file if provided
    if config_path and Path(config_path).exists():
        import yaml
        with open(config_path, 'r') as f:
            file_config = yaml.safe_load(f)
            config.update(file_config)
    
    return config

# =============================================================================
# DEMO SCENARIOS
# =============================================================================

async def run_demo_scenario(orchestrator: WorkflowOrchestrator):
    """Run a demonstration scenario"""
    print("\n🎭 Running Demo Scenario: TikTok Trend Discovery")
    print("=" * 60)
    
    # Start a demo workflow
    print("🚀 Starting trend prediction workflow...")
    workflow_id = await orchestrator.start_workflow({
        'demo_mode': True,
        'target_hashtags': ['dance', 'music', 'comedy', 'tutorial', 'trending']
    })
    
    print(f"✅ Workflow started: {workflow_id}")
    
    # Get and display results
    await asyncio.sleep(2)  # Give workflow time to complete
    
    workflow_status = orchestrator.get_workflow_status(workflow_id)
    if workflow_status:
        print(f"\n📊 Workflow Results:")
        print(f"   Status: {workflow_status['current_step']}")
        print(f"   Tasks Completed: {workflow_status['tasks_completed']}")
        print(f"   Tasks Failed: {workflow_status['tasks_failed']}")
        print(f"   Alerts: {len(workflow_status['alerts'])}")
        
        # Display predictions if available
        predictions = workflow_status.get('predictions', {})
        if predictions and 'viral_probabilities' in predictions:
            print(f"\n🔮 Viral Predictions:")
            for hashtag, prob in predictions['viral_probabilities'].items():
                emoji = "🔥" if prob > 0.8 else "📈" if prob > 0.6 else "📊"
                print(f"   {emoji} #{hashtag}: {prob:.1%} viral probability")
        
        # Display alerts
        if workflow_status['alerts']:
            print(f"\n🚨 System Alerts:")
            for alert in workflow_status['alerts']:
                severity_emoji = "🔴" if alert['severity'] == 'error' else "🟡" if alert['severity'] == 'warning' else "🔵"
                print(f"   {severity_emoji} {alert['message']}")
    
    return workflow_id

async def run_continuous_monitoring(orchestrator: WorkflowOrchestrator, duration_minutes: int = 10):
    """Run continuous monitoring simulation"""
    print(f"\n⏰ Running Continuous Monitoring (for {duration_minutes} minutes)")
    print("=" * 60)
    
    end_time = datetime.now().timestamp() + (duration_minutes * 60)
    workflow_count = 0
    
    while datetime.now().timestamp() < end_time:
        try:
            print(f"\n🔄 Starting monitoring cycle {workflow_count + 1}")
            
            # Start a workflow
            workflow_id = await orchestrator.start_workflow({
                'monitoring_mode': True,
                'cycle_number': workflow_count + 1
            })
            
            workflow_count += 1
            print(f"✅ Workflow {workflow_count} completed: {workflow_id}")
            
            # Get system status
            system_status = orchestrator.get_system_status()
            print(f"📊 System: {system_status['active_workflows']} active workflows")
            
            # Wait before next cycle (simulate 15-minute intervals)
            await asyncio.sleep(30)  # 30 seconds in demo mode
            
        except KeyboardInterrupt:
            print("\n⛔ Monitoring stopped by user")
            break
        except Exception as e:
            print(f"❌ Error in monitoring cycle: {e}")
            await asyncio.sleep(10)
    
    print(f"\n✅ Continuous monitoring completed. Total workflows: {workflow_count}")

# =============================================================================
# HEALTH CHECKS
# =============================================================================

def check_dependencies():
    """Check if all required dependencies are available"""
    print("🔍 Checking system dependencies...")
    
    issues = []
    
    # Check required packages
    try:
        import langchain
        import langgraph
        import aiohttp
        import pandas
        import numpy
        print("✅ All required packages are installed")
    except ImportError as e:
        issues.append(f"Missing package: {e}")
    
    # Check configuration
    config = load_config()
    if config['ensemble_api_key'] == 'MZTq3h5VIyi0CjKt':
        print("✅ Using your EnsembleData Trial API key")
    
    if not config.get('openai_api_key') and not config.get('anthropic_api_key'):
        print("⚠️  No LLM API key configured. Some features may be limited.")
    
    if issues:
        print("❌ Issues found:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    
    print("✅ All dependencies are ready")
    return True

# =============================================================================
# MAIN FUNCTIONS
# =============================================================================

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='TikTok Trend Prediction Multi-Agent System')
    parser.add_argument('--demo', action='store_true', help='Run demo scenario')
    parser.add_argument('--monitor', type=int, metavar='MINUTES', help='Run continuous monitoring for N minutes')
    parser.add_argument('--config', type=str, help='Configuration file path')
    parser.add_argument('--check-deps', action='store_true', help='Check dependencies and exit')
    
    args = parser.parse_args()
    
    # Check dependencies
    if args.check_deps:
        check_dependencies()
        return
    
    if not check_dependencies():
        print("❌ Dependency check failed. Please install missing packages.")
        sys.exit(1)
    
    # Load configuration
    config = load_config(args.config)
    
    print("🚀 TikTok Trend Prediction Multi-Agent System")
    print("=" * 60)
    print(f"Environment: {config['environment']}")
    print(f"Available Agents: {', '.join(AVAILABLE_AGENTS)}")
    print(f"Demo Mode: {'Enabled' if config['enable_demo_mode'] else 'Disabled'}")
    
    # Initialize orchestrator
    try:
        orchestrator = WorkflowOrchestrator(config=config)
        print("✅ Orchestrator initialized successfully")
        
        # Get initial system status
        system_status = orchestrator.get_system_status()
        print(f"📊 System Health: {len(system_status['agent_health'])} agents registered")
        
        # Run based on arguments
        if args.demo:
            await run_demo_scenario(orchestrator)
        elif args.monitor:
            await run_continuous_monitoring(orchestrator, args.monitor)
        else:
            # Interactive mode
            print("\n🎮 Interactive Mode")
            print("Commands:")
            print("  1 - Run demo scenario")
            print("  2 - Start single workflow") 
            print("  3 - Show system status")
            print("  4 - Exit")
            
            while True:
                try:
                    choice = input("\nEnter command (1-4): ").strip()
                    
                    if choice == '1':
                        await run_demo_scenario(orchestrator)
                    elif choice == '2':
                        workflow_id = await orchestrator.start_workflow()
                        print(f"✅ Workflow started: {workflow_id}")
                    elif choice == '3':
                        status = orchestrator.get_system_status()
                        print(json.dumps(status, indent=2, default=str))
                    elif choice == '4':
                        print("👋 Goodbye!")
                        break
                    else:
                        print("❌ Invalid choice. Please enter 1-4.")
                        
                except KeyboardInterrupt:
                    print("\n👋 Goodbye!")
                    break
                except Exception as e:
                    print(f"❌ Error: {e}")
    
    except Exception as e:
        print(f"❌ Failed to initialize system: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)
    
    # Run the system
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 System stopped by user")
    except Exception as e:
        print(f"❌ System error: {e}")
        sys.exit(1) 