"""
TikTok Trend Prediction Multi-Agent System - Agents Module
==========================================================

This module contains all the specialized agents for the TikTok trend prediction system.
Each agent is responsible for a specific aspect of the data pipeline and analysis.
"""

from .base_agent import (
    BaseAgent,
    AgentTask,
    AgentResult,
    AgentStatus,
    AgentHealth,
    IngestionTask,
    AnalysisTask,
    SemanticTask,
    AgentFactory
)

from .ingestion_agent import (
    IngestionAgent,
    ApifyContentIngestion,
    StartupVideoData,
    HashtagTrendData
)

# Agent version information
__version__ = "1.0.0"
__author__ = "TikTok Trend Prediction Team"

# Available agent types
AVAILABLE_AGENTS = [
    "IngestionAgent",
    # "AnalyzerAgent",      # To be implemented
    # "SemanticAgent",      # To be implemented  
    # "PredictorAgent",     # To be implemented
    # "EvaluatorAgent",     # To be implemented
    # "ImprovementAgent",   # To be implemented
    # "GovernanceAgent",    # To be implemented
    # "NotificationAgent",  # To be implemented
]

__all__ = [
    # Base classes
    "BaseAgent",
    "AgentTask", 
    "AgentResult",
    "AgentStatus",
    "AgentHealth",
    "AgentFactory",
    
    # Task types
    "IngestionTask",
    "AnalysisTask", 
    "SemanticTask",
    
    # Concrete agents
    "IngestionAgent",
    
    # Utilities
    "ApifyContentIngestion",
    "DataValidator",
    
    # Module info
    "AVAILABLE_AGENTS",
    "__version__",
] 