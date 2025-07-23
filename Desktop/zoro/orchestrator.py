"""
Multi-Agent Orchestrator for TikTok Trend Prediction System
===========================================================

This module implements the main orchestrator using LangGraph to coordinate
all agents in the TikTok trend prediction system. It manages workflow execution,
agent scheduling, and inter-agent communication.
"""

import asyncio
import logging
import structlog
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, TypedDict, Annotated
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid

# LangGraph imports
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from langchain_core.messages import BaseMessage, HumanMessage

# Our agent imports
from agents.base_agent import BaseAgent, AgentTask, AgentResult, AgentStatus
from agents.ingestion_agent import IngestionAgent
from config.definitions import AgentRole, SYSTEM_CADENCE
from config.ingestion_config import INGESTION_WORKFLOW

# =============================================================================
# WORKFLOW STATE MANAGEMENT
# =============================================================================

class WorkflowState(TypedDict):
    """State shared across all workflow nodes"""
    current_step: str
    workflow_id: str
    started_at: datetime
    last_updated: datetime
    
    # Agent states
    agents: Dict[str, Dict[str, Any]]
    
    # Task tracking
    pending_tasks: List[Dict[str, Any]]
    completed_tasks: List[Dict[str, Any]]
    failed_tasks: List[Dict[str, Any]]
    
    # Data flow
    ingested_data: Dict[str, Any]
    computed_metrics: Dict[str, Any]
    predictions: Dict[str, Any]
    
    # System health
    system_health: Dict[str, Any]
    alerts: List[Dict[str, Any]]
    
    # Configuration
    config: Dict[str, Any]

class WorkflowStep(Enum):
    """Workflow execution steps"""
    INITIALIZE = "initialize"
    DISCOVER_TRENDS = "discover_trends"
    ENRICH_DATA = "enrich_data"
    COMPUTE_METRICS = "compute_metrics"
    SEMANTIC_ANALYSIS = "semantic_analysis"
    GENERATE_PREDICTIONS = "generate_predictions"
    EVALUATE_RESULTS = "evaluate_results"
    CLEANUP = "cleanup"
    ERROR_HANDLING = "error_handling"

# =============================================================================
# AGENT REGISTRY
# =============================================================================

@dataclass
class AgentInfo:
    """Information about an agent in the system"""
    agent: BaseAgent
    last_health_check: datetime
    is_active: bool = True
    current_tasks: List[str] = field(default_factory=list)
    
class AgentRegistry:
    """Registry of all agents in the system"""
    
    def __init__(self):
        self.agents: Dict[str, AgentInfo] = {}
        self.logger = structlog.get_logger().bind(component="agent_registry")
    
    def register_agent(self, agent: BaseAgent) -> bool:
        """Register an agent in the system"""
        try:
            agent_info = AgentInfo(
                agent=agent,
                last_health_check=datetime.now()
            )
            self.agents[agent.agent_name] = agent_info
            self.logger.info("Agent registered", agent_name=agent.agent_name, role=agent.agent_role.value)
            return True
        except Exception as e:
            self.logger.error("Failed to register agent", agent_name=agent.agent_name, error=str(e))
            return False
    
    def get_agent(self, agent_name: str) -> Optional[BaseAgent]:
        """Get an agent by name"""
        agent_info = self.agents.get(agent_name)
        return agent_info.agent if agent_info else None
    
    def get_agents_by_role(self, role: AgentRole) -> List[BaseAgent]:
        """Get all agents with a specific role"""
        return [
            info.agent for info in self.agents.values()
            if info.agent.agent_role == role and info.is_active
        ]
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get health status of all agents"""
        health_data = {}
        for agent_name, agent_info in self.agents.items():
            health_data[agent_name] = {
                "health": agent_info.agent.get_health_status(),
                "is_active": agent_info.is_active,
                "current_tasks": agent_info.current_tasks,
                "last_health_check": agent_info.last_health_check.isoformat()
            }
        return health_data

# =============================================================================
# WORKFLOW NODES
# =============================================================================

class WorkflowOrchestrator:
    """Main orchestrator for the multi-agent workflow"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.agent_registry = AgentRegistry()
        self.logger = structlog.get_logger().bind(component="orchestrator")
        
        # Initialize workflow graph
        self.workflow_graph = self._create_workflow_graph()
        
        # Initialize agents
        self._initialize_agents()
        
        # Workflow state
        self.current_workflows: Dict[str, WorkflowState] = {}
    
    def _initialize_agents(self):
        """Initialize all agents in the system"""
        try:
            # Create and register ingestion agent
            ingestion_config = {
                'apify_api_token': self.config.get('apify_api_token', os.getenv('APIFY_API_TOKEN'))
            }
            ingestion_agent = IngestionAgent(config=ingestion_config)
            ingestion_agent.start()
            self.agent_registry.register_agent(ingestion_agent)
            
            # TODO: Add other agents as they're implemented
            # analyzer_agent = AnalyzerAgent(config=self.config)
            # semantic_agent = SemanticAgent(config=self.config)
            # etc.
            
            self.logger.info("All agents initialized successfully")
            
        except Exception as e:
            self.logger.error("Failed to initialize agents", error=str(e))
            raise
    
    def _create_workflow_graph(self) -> StateGraph:
        """Create the LangGraph workflow"""
        
        # Define the graph
        workflow = StateGraph(WorkflowState)
        
        # Add nodes for each workflow step
        workflow.add_node("initialize", self._initialize_workflow)
        workflow.add_node("discover_trends", self._discover_trends)
        workflow.add_node("enrich_data", self._enrich_data)
        workflow.add_node("compute_metrics", self._compute_metrics)
        workflow.add_node("semantic_analysis", self._semantic_analysis)
        workflow.add_node("generate_predictions", self._generate_predictions)
        workflow.add_node("evaluate_results", self._evaluate_results)
        workflow.add_node("cleanup", self._cleanup)
        workflow.add_node("error_handling", self._handle_errors)
        
        # Define the workflow edges
        workflow.set_entry_point("initialize")
        
        workflow.add_edge("initialize", "discover_trends")
        workflow.add_edge("discover_trends", "enrich_data")
        workflow.add_edge("enrich_data", "compute_metrics")
        workflow.add_edge("compute_metrics", "semantic_analysis")
        workflow.add_edge("semantic_analysis", "generate_predictions")
        workflow.add_edge("generate_predictions", "evaluate_results")
        workflow.add_edge("evaluate_results", "cleanup")
        workflow.add_edge("cleanup", END)
        
        # Error handling edges
        workflow.add_edge("error_handling", END)
        
        return workflow.compile()
    
    # =============================================================================
    # WORKFLOW NODE IMPLEMENTATIONS
    # =============================================================================
    
    async def _initialize_workflow(self, state: WorkflowState) -> WorkflowState:
        """Initialize a new workflow execution"""
        self.logger.info("Initializing workflow", workflow_id=state["workflow_id"])
        
        # Update state
        state["current_step"] = WorkflowStep.INITIALIZE.value
        state["last_updated"] = datetime.now()
        state["system_health"] = self.agent_registry.get_system_health()
        
        # Check agent health
        unhealthy_agents = []
        for agent_name, health_data in state["system_health"].items():
            if health_data["health"]["status"] not in ["idle", "running"]:
                unhealthy_agents.append(agent_name)
        
        if unhealthy_agents:
            state["alerts"].append({
                "type": "agent_health_warning",
                "message": f"Unhealthy agents detected: {unhealthy_agents}",
                "timestamp": datetime.now().isoformat(),
                "severity": "warning"
            })
        
        self.logger.info("Workflow initialized", 
                        workflow_id=state["workflow_id"],
                        healthy_agents=len(state["system_health"]) - len(unhealthy_agents))
        
        return state
    
    async def _discover_trends(self, state: WorkflowState) -> WorkflowState:
        """Discover trending hashtags using ingestion agent"""
        self.logger.info("Starting trend discovery", workflow_id=state["workflow_id"])
        
        state["current_step"] = WorkflowStep.DISCOVER_TRENDS.value
        state["last_updated"] = datetime.now()
        
        try:
            # Get ingestion agent
            ingestion_agent = self.agent_registry.get_agent("ingestion_agent")
            if not ingestion_agent:
                raise Exception("Ingestion agent not available")
            
            # Execute trending hashtags ingestion
            result = await ingestion_agent.ingest_trending_hashtags(count=100)
            
            if result.success:
                state["ingested_data"]["trending_hashtags"] = result.result_data
                state["completed_tasks"].append({
                    "task_id": result.task_id,
                    "step": "discover_trends",
                    "result": result.result_data,
                    "completed_at": datetime.now().isoformat()
                })
                
                self.logger.info("Trend discovery completed", 
                               workflow_id=state["workflow_id"],
                               hashtags_found=result.result_data.get("records_processed", 0))
            else:
                raise Exception(f"Trend discovery failed: {result.error_message}")
        
        except Exception as e:
            self.logger.error("Trend discovery failed", workflow_id=state["workflow_id"], error=str(e))
            state["failed_tasks"].append({
                "step": "discover_trends",
                "error": str(e),
                "failed_at": datetime.now().isoformat()
            })
            state["current_step"] = WorkflowStep.ERROR_HANDLING.value
        
        return state
    
    async def _enrich_data(self, state: WorkflowState) -> WorkflowState:
        """Enrich trending hashtags with additional data"""
        self.logger.info("Starting data enrichment", workflow_id=state["workflow_id"])
        
        state["current_step"] = WorkflowStep.ENRICH_DATA.value
        state["last_updated"] = datetime.now()
        
        try:
            ingestion_agent = self.agent_registry.get_agent("ingestion_agent")
            if not ingestion_agent:
                raise Exception("Ingestion agent not available")
            
            # Get top hashtags from discovery phase
            trending_data = state["ingested_data"].get("trending_hashtags", {})
            hashtag_count = trending_data.get("records_processed", 0)
            
            if hashtag_count == 0:
                raise Exception("No hashtags to enrich")
            
            # For demo purposes, enrich top 5 hashtags
            demo_hashtags = ["dance", "music", "trending", "viral", "fyp"]
            
            enrichment_results = []
            for hashtag in demo_hashtags[:5]:
                result = await ingestion_agent.ingest_hashtag_videos(hashtag, count=20)
                if result.success:
                    enrichment_results.append(result.result_data)
            
            state["ingested_data"]["hashtag_enrichment"] = enrichment_results
            state["completed_tasks"].append({
                "task_id": f"enrich_{uuid.uuid4().hex[:8]}",
                "step": "enrich_data",
                "result": {"enriched_hashtags": len(enrichment_results)},
                "completed_at": datetime.now().isoformat()
            })
            
            self.logger.info("Data enrichment completed", 
                           workflow_id=state["workflow_id"],
                           enriched_hashtags=len(enrichment_results))
        
        except Exception as e:
            self.logger.error("Data enrichment failed", workflow_id=state["workflow_id"], error=str(e))
            state["failed_tasks"].append({
                "step": "enrich_data",
                "error": str(e),
                "failed_at": datetime.now().isoformat()
            })
            state["current_step"] = WorkflowStep.ERROR_HANDLING.value
        
        return state
    
    async def _compute_metrics(self, state: WorkflowState) -> WorkflowState:
        """Compute quantitative metrics on the ingested data"""
        self.logger.info("Starting metrics computation", workflow_id=state["workflow_id"])
        
        state["current_step"] = WorkflowStep.COMPUTE_METRICS.value
        state["last_updated"] = datetime.now()
        
        try:
            # TODO: When AnalyzerAgent is implemented, use it here
            # For now, simulate metrics computation
            
            trending_data = state["ingested_data"].get("trending_hashtags", {})
            enrichment_data = state["ingested_data"].get("hashtag_enrichment", [])
            
            # Simulate computed metrics
            computed_metrics = {
                "velocity_scores": {"dance": 0.8, "music": 0.6, "trending": 0.9},
                "momentum_scores": {"dance": 0.75, "music": 0.55, "trending": 0.85},
                "engagement_efficiency": {"dance": 0.12, "music": 0.08, "trending": 0.15},
                "novelty_indices": {"dance": 0.3, "music": 0.4, "trending": 0.7},
                "computation_timestamp": datetime.now().isoformat(),
                "data_freshness_minutes": 15
            }
            
            state["computed_metrics"] = computed_metrics
            state["completed_tasks"].append({
                "task_id": f"metrics_{uuid.uuid4().hex[:8]}",
                "step": "compute_metrics",
                "result": {"metrics_computed": len(computed_metrics) - 2},  # Exclude timestamp fields
                "completed_at": datetime.now().isoformat()
            })
            
            self.logger.info("Metrics computation completed", 
                           workflow_id=state["workflow_id"],
                           metrics_computed=len(computed_metrics) - 2)
        
        except Exception as e:
            self.logger.error("Metrics computation failed", workflow_id=state["workflow_id"], error=str(e))
            state["failed_tasks"].append({
                "step": "compute_metrics",
                "error": str(e),
                "failed_at": datetime.now().isoformat()
            })
            state["current_step"] = WorkflowStep.ERROR_HANDLING.value
        
        return state
    
    async def _semantic_analysis(self, state: WorkflowState) -> WorkflowState:
        """Perform semantic analysis using LLM agents"""
        self.logger.info("Starting semantic analysis", workflow_id=state["workflow_id"])
        
        state["current_step"] = WorkflowStep.SEMANTIC_ANALYSIS.value
        state["last_updated"] = datetime.now()
        
        try:
            # TODO: When SemanticAgent is implemented, use it here
            # For now, simulate semantic analysis
            
            # Simulate semantic analysis results
            semantic_results = {
                "theme_clusters": {
                    "dance": {"theme": "movement_content", "confidence": 0.9},
                    "music": {"theme": "audio_content", "confidence": 0.8},
                    "trending": {"theme": "viral_content", "confidence": 0.95}
                },
                "trend_narratives": {
                    "dance": "High momentum due to new choreography viral spread",
                    "music": "Steady growth from popular artist collaborations",
                    "trending": "Explosive growth from cross-platform amplification"
                },
                "risk_flags": [],
                "analysis_timestamp": datetime.now().isoformat()
            }
            
            state["computed_metrics"]["semantic_analysis"] = semantic_results
            state["completed_tasks"].append({
                "task_id": f"semantic_{uuid.uuid4().hex[:8]}",
                "step": "semantic_analysis",
                "result": {"themes_identified": len(semantic_results["theme_clusters"])},
                "completed_at": datetime.now().isoformat()
            })
            
            self.logger.info("Semantic analysis completed", 
                           workflow_id=state["workflow_id"],
                           themes_identified=len(semantic_results["theme_clusters"]))
        
        except Exception as e:
            self.logger.error("Semantic analysis failed", workflow_id=state["workflow_id"], error=str(e))
            state["failed_tasks"].append({
                "step": "semantic_analysis",
                "error": str(e),
                "failed_at": datetime.now().isoformat()
            })
            state["current_step"] = WorkflowStep.ERROR_HANDLING.value
        
        return state
    
    async def _generate_predictions(self, state: WorkflowState) -> WorkflowState:
        """Generate viral predictions using ML models"""
        self.logger.info("Starting prediction generation", workflow_id=state["workflow_id"])
        
        state["current_step"] = WorkflowStep.GENERATE_PREDICTIONS.value
        state["last_updated"] = datetime.now()
        
        try:
            # TODO: When PredictorAgent is implemented, use it here
            # For now, simulate predictions
            
            metrics = state["computed_metrics"]
            
            # Simulate predictions based on computed metrics
            predictions = {
                "viral_probabilities": {
                    "dance": 0.85,
                    "music": 0.62,
                    "trending": 0.92
                },
                "prediction_horizon_hours": 24,
                "confidence_intervals": {
                    "dance": {"lower": 0.75, "upper": 0.95},
                    "music": {"lower": 0.52, "upper": 0.72},
                    "trending": {"lower": 0.87, "upper": 0.97}
                },
                "ranking": ["trending", "dance", "music"],
                "prediction_timestamp": datetime.now().isoformat(),
                "model_version": "v1.0_demo"
            }
            
            state["predictions"] = predictions
            state["completed_tasks"].append({
                "task_id": f"predict_{uuid.uuid4().hex[:8]}",
                "step": "generate_predictions",
                "result": {"predictions_generated": len(predictions["viral_probabilities"])},
                "completed_at": datetime.now().isoformat()
            })
            
            # Generate alerts for high-probability viral content
            high_viral_items = [
                item for item, prob in predictions["viral_probabilities"].items()
                if prob > 0.8
            ]
            
            if high_viral_items:
                state["alerts"].append({
                    "type": "high_viral_probability",
                    "message": f"High viral probability detected: {high_viral_items}",
                    "data": {item: predictions["viral_probabilities"][item] for item in high_viral_items},
                    "timestamp": datetime.now().isoformat(),
                    "severity": "info"
                })
            
            self.logger.info("Prediction generation completed", 
                           workflow_id=state["workflow_id"],
                           predictions_generated=len(predictions["viral_probabilities"]),
                           high_viral_items=len(high_viral_items))
        
        except Exception as e:
            self.logger.error("Prediction generation failed", workflow_id=state["workflow_id"], error=str(e))
            state["failed_tasks"].append({
                "step": "generate_predictions",
                "error": str(e),
                "failed_at": datetime.now().isoformat()
            })
            state["current_step"] = WorkflowStep.ERROR_HANDLING.value
        
        return state
    
    async def _evaluate_results(self, state: WorkflowState) -> WorkflowState:
        """Evaluate prediction results and update models"""
        self.logger.info("Starting results evaluation", workflow_id=state["workflow_id"])
        
        state["current_step"] = WorkflowStep.EVALUATE_RESULTS.value
        state["last_updated"] = datetime.now()
        
        try:
            # TODO: When EvaluatorAgent is implemented, use it here
            # For now, simulate evaluation
            
            evaluation_results = {
                "workflow_success": True,
                "total_execution_time_seconds": (datetime.now() - state["started_at"]).total_seconds(),
                "tasks_completed": len(state["completed_tasks"]),
                "tasks_failed": len(state["failed_tasks"]),
                "data_quality_score": 0.95,
                "prediction_confidence": 0.87,
                "evaluation_timestamp": datetime.now().isoformat()
            }
            
            state["completed_tasks"].append({
                "task_id": f"evaluate_{uuid.uuid4().hex[:8]}",
                "step": "evaluate_results",
                "result": evaluation_results,
                "completed_at": datetime.now().isoformat()
            })
            
            self.logger.info("Results evaluation completed", 
                           workflow_id=state["workflow_id"],
                           **{k: v for k, v in evaluation_results.items() if isinstance(v, (int, float, bool))})
        
        except Exception as e:
            self.logger.error("Results evaluation failed", workflow_id=state["workflow_id"], error=str(e))
            state["failed_tasks"].append({
                "step": "evaluate_results",
                "error": str(e),
                "failed_at": datetime.now().isoformat()
            })
            state["current_step"] = WorkflowStep.ERROR_HANDLING.value
        
        return state
    
    async def _cleanup(self, state: WorkflowState) -> WorkflowState:
        """Clean up workflow resources"""
        self.logger.info("Starting workflow cleanup", workflow_id=state["workflow_id"])
        
        state["current_step"] = WorkflowStep.CLEANUP.value
        state["last_updated"] = datetime.now()
        
        # Clean up temporary resources, close connections, etc.
        cleanup_actions = [
            "cleared_temporary_data",
            "released_agent_locks",
            "updated_metrics_cache",
            "logged_workflow_completion"
        ]
        
        for action in cleanup_actions:
            self.logger.debug("Cleanup action", action=action, workflow_id=state["workflow_id"])
        
        # Update workflow completion
        workflow_duration = (datetime.now() - state["started_at"]).total_seconds()
        
        state["completed_tasks"].append({
            "task_id": f"cleanup_{uuid.uuid4().hex[:8]}",
            "step": "cleanup",
            "result": {
                "cleanup_actions": len(cleanup_actions),
                "workflow_duration_seconds": workflow_duration
            },
            "completed_at": datetime.now().isoformat()
        })
        
        self.logger.info("Workflow cleanup completed", 
                        workflow_id=state["workflow_id"],
                        duration_seconds=workflow_duration)
        
        return state
    
    async def _handle_errors(self, state: WorkflowState) -> WorkflowState:
        """Handle workflow errors and attempt recovery"""
        self.logger.error("Handling workflow errors", workflow_id=state["workflow_id"])
        
        state["current_step"] = WorkflowStep.ERROR_HANDLING.value
        state["last_updated"] = datetime.now()
        
        # Log all failed tasks
        for failed_task in state["failed_tasks"]:
            self.logger.error("Failed task details", 
                            workflow_id=state["workflow_id"],
                            **failed_task)
        
        # Generate error summary alert
        state["alerts"].append({
            "type": "workflow_error",
            "message": f"Workflow {state['workflow_id']} encountered {len(state['failed_tasks'])} failures",
            "failed_tasks": state["failed_tasks"],
            "timestamp": datetime.now().isoformat(),
            "severity": "error"
        })
        
        return state
    
    # =============================================================================
    # PUBLIC METHODS
    # =============================================================================
    
    async def start_workflow(self, config: Dict[str, Any] = None) -> str:
        """Start a new workflow execution"""
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        # Initialize workflow state
        initial_state: WorkflowState = {
            "current_step": WorkflowStep.INITIALIZE.value,
            "workflow_id": workflow_id,
            "started_at": datetime.now(),
            "last_updated": datetime.now(),
            "agents": {},
            "pending_tasks": [],
            "completed_tasks": [],
            "failed_tasks": [],
            "ingested_data": {},
            "computed_metrics": {},
            "predictions": {},
            "system_health": {},
            "alerts": [],
            "config": config or {}
        }
        
        # Store workflow state
        self.current_workflows[workflow_id] = initial_state
        
        self.logger.info("Starting new workflow", workflow_id=workflow_id)
        
        try:
            # Execute the workflow
            final_state = await self.workflow_graph.ainvoke(initial_state)
            self.current_workflows[workflow_id] = final_state
            
            self.logger.info("Workflow completed", 
                           workflow_id=workflow_id,
                           final_step=final_state["current_step"],
                           tasks_completed=len(final_state["completed_tasks"]),
                           tasks_failed=len(final_state["failed_tasks"]))
            
            return workflow_id
            
        except Exception as e:
            self.logger.error("Workflow execution failed", workflow_id=workflow_id, error=str(e))
            
            # Update state with error
            if workflow_id in self.current_workflows:
                self.current_workflows[workflow_id]["failed_tasks"].append({
                    "step": "workflow_execution",
                    "error": str(e),
                    "failed_at": datetime.now().isoformat()
                })
            
            raise
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a workflow"""
        if workflow_id not in self.current_workflows:
            return None
        
        state = self.current_workflows[workflow_id]
        
        return {
            "workflow_id": workflow_id,
            "current_step": state["current_step"],
            "started_at": state["started_at"].isoformat(),
            "last_updated": state["last_updated"].isoformat(),
            "tasks_completed": len(state["completed_tasks"]),
            "tasks_failed": len(state["failed_tasks"]),
            "alerts": state["alerts"],
            "predictions": state.get("predictions", {}),
            "system_health": state.get("system_health", {})
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        return {
            "orchestrator_status": "running",
            "active_workflows": len(self.current_workflows),
            "agent_health": self.agent_registry.get_system_health(),
            "current_time": datetime.now().isoformat(),
            "workflows": {
                workflow_id: {
                    "current_step": state["current_step"],
                    "started_at": state["started_at"].isoformat(),
                    "tasks_completed": len(state["completed_tasks"]),
                    "tasks_failed": len(state["failed_tasks"])
                }
                for workflow_id, state in self.current_workflows.items()
            }
        }

# =============================================================================
# MAIN ORCHESTRATOR RUNNER
# =============================================================================

async def main():
    """Main function to run the orchestrator"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Configure logging
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
    
    # Create orchestrator
    config = {
        'apify_api_token': os.getenv('APIFY_API_TOKEN')
    }
    
    orchestrator = WorkflowOrchestrator(config=config)
    
    print("🚀 TikTok Trend Prediction Multi-Agent System Started!")
    print("=" * 60)
    
    # Get initial system status
    system_status = orchestrator.get_system_status()
    print(f"📊 System Status:")
    print(json.dumps(system_status, indent=2, default=str))
    
    # Start a workflow
    print("\n🔄 Starting workflow...")
    workflow_id = await orchestrator.start_workflow()
    
    # Get workflow results
    print(f"\n✅ Workflow completed: {workflow_id}")
    workflow_status = orchestrator.get_workflow_status(workflow_id)
    print(json.dumps(workflow_status, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(main()) 