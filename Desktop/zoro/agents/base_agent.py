"""
Base Agent Class for TikTok Trend Prediction Multi-Agent System
================================================================

This module defines the base agent class that all specialized agents inherit from.
Uses LangChain framework for agent capabilities.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import logging
import structlog
from enum import Enum

from langchain.agents import AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseMessage
from langchain_core.tools import BaseTool
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

# Import our configuration
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.definitions import AgentRole, SYSTEM_CADENCE

# =============================================================================
# AGENT STATUS & HEALTH
# =============================================================================

class AgentStatus(Enum):
    """Agent operational status"""
    IDLE = "idle"
    RUNNING = "running"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    STOPPED = "stopped"

@dataclass
class AgentHealth:
    """Health metrics for an agent"""
    status: AgentStatus = AgentStatus.IDLE
    last_execution: Optional[datetime] = None
    execution_count: int = 0
    error_count: int = 0
    average_execution_time: float = 0.0
    last_error: Optional[str] = None
    uptime_start: datetime = field(default_factory=datetime.now)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.execution_count == 0:
            return 100.0
        return ((self.execution_count - self.error_count) / self.execution_count) * 100

# =============================================================================
# AGENT TASK DEFINITIONS
# =============================================================================

class AgentTask(BaseModel):
    """Represents a task for an agent to execute"""
    task_id: str = Field(..., description="Unique task identifier")
    task_type: str = Field(..., description="Type of task to execute")
    priority: int = Field(default=1, description="Task priority (1=highest, 5=lowest)")
    data: Dict[str, Any] = Field(default_factory=dict, description="Task input data")
    created_at: datetime = Field(default_factory=datetime.now)
    scheduled_for: Optional[datetime] = Field(None, description="When to execute this task")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    timeout_seconds: int = Field(default=300, description="Task timeout in seconds")

class AgentResult(BaseModel):
    """Result from agent task execution"""
    task_id: str
    agent_name: str
    success: bool
    result_data: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
    execution_time_seconds: float
    completed_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

# =============================================================================
# BASE AGENT CLASS
# =============================================================================

class BaseAgent(ABC):
    """
    Abstract base class for all agents in the TikTok trend prediction system.
    
    Provides common functionality:
    - Health monitoring
    - Task execution framework
    - Logging and error handling
    - LangChain integration
    - Memory management
    """
    
    def __init__(
        self,
        agent_name: str,
        agent_role: AgentRole,
        llm=None,
        tools: List[BaseTool] = None,
        memory: ConversationBufferMemory = None,
        config: Dict[str, Any] = None
    ):
        self.agent_name = agent_name
        self.agent_role = agent_role
        self.config = config or {}
        self.health = AgentHealth()
        self.tools = tools or []
        self.memory = memory or ConversationBufferMemory(return_messages=True)
        
        # Set up structured logging
        self.logger = structlog.get_logger().bind(
            agent_name=agent_name,
            agent_role=agent_role.value
        )
        
        # LangChain components
        self.llm = llm
        self.agent_executor: Optional[AgentExecutor] = None
        
        # Task queue and execution state
        self.task_queue: List[AgentTask] = []
        self.current_task: Optional[AgentTask] = None
        self.is_running = False
        
        # Initialize the agent
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize LangChain agent executor if LLM is provided"""
        if self.llm and self.tools:
            try:
                # Create agent executor with tools
                self.agent_executor = AgentExecutor.from_agent_and_tools(
                    agent=self._create_agent(),
                    tools=self.tools,
                    memory=self.memory,
                    verbose=True,
                    handle_parsing_errors=True
                )
                self.logger.info("Agent initialized successfully")
            except Exception as e:
                self.logger.error("Failed to initialize agent", error=str(e))
                self.health.status = AgentStatus.ERROR
                self.health.last_error = str(e)
    
    @abstractmethod
    def _create_agent(self):
        """Create the specific LangChain agent implementation"""
        pass
    
    @abstractmethod
    async def execute_task(self, task: AgentTask) -> AgentResult:
        """Execute a specific task - must be implemented by subclasses"""
        pass
    
    # =============================================================================
    # TASK MANAGEMENT
    # =============================================================================
    
    def add_task(self, task: AgentTask) -> bool:
        """Add a task to the agent's queue"""
        try:
            # Check if we should execute immediately or queue
            if task.scheduled_for is None or task.scheduled_for <= datetime.now():
                self.task_queue.append(task)
                self.task_queue.sort(key=lambda t: t.priority)  # Sort by priority
                self.logger.info("Task added to queue", task_id=task.task_id, task_type=task.task_type)
                return True
            else:
                # Schedule for later (would integrate with scheduler in production)
                self.logger.info("Task scheduled for later", task_id=task.task_id, scheduled_for=task.scheduled_for)
                return True
        except Exception as e:
            self.logger.error("Failed to add task", task_id=task.task_id, error=str(e))
            return False
    
    async def process_next_task(self) -> Optional[AgentResult]:
        """Process the next task in the queue"""
        if not self.task_queue or self.health.status != AgentStatus.IDLE:
            return None
        
        task = self.task_queue.pop(0)
        self.current_task = task
        self.health.status = AgentStatus.RUNNING
        
        start_time = datetime.now()
        
        try:
            self.logger.info("Starting task execution", task_id=task.task_id, task_type=task.task_type)
            
            # Execute the task with timeout
            result = await asyncio.wait_for(
                self.execute_task(task),
                timeout=task.timeout_seconds
            )
            
            # Update health metrics
            execution_time = (datetime.now() - start_time).total_seconds()
            self.health.last_execution = datetime.now()
            self.health.execution_count += 1
            self._update_average_execution_time(execution_time)
            
            if result.success:
                self.logger.info("Task completed successfully", 
                               task_id=task.task_id, 
                               execution_time=execution_time)
            else:
                self.health.error_count += 1
                self.health.last_error = result.error_message
                self.logger.error("Task failed", 
                                task_id=task.task_id, 
                                error=result.error_message)
            
            return result
            
        except asyncio.TimeoutError:
            self.health.error_count += 1
            self.health.last_error = f"Task {task.task_id} timed out after {task.timeout_seconds}s"
            self.logger.error("Task timed out", task_id=task.task_id, timeout=task.timeout_seconds)
            
            return AgentResult(
                task_id=task.task_id,
                agent_name=self.agent_name,
                success=False,
                error_message=self.health.last_error,
                execution_time_seconds=(datetime.now() - start_time).total_seconds()
            )
            
        except Exception as e:
            self.health.error_count += 1
            self.health.last_error = str(e)
            self.logger.error("Task execution failed", task_id=task.task_id, error=str(e))
            
            return AgentResult(
                task_id=task.task_id,
                agent_name=self.agent_name,
                success=False,
                error_message=str(e),
                execution_time_seconds=(datetime.now() - start_time).total_seconds()
            )
            
        finally:
            self.current_task = None
            self.health.status = AgentStatus.IDLE
    
    # =============================================================================
    # HEALTH & MONITORING
    # =============================================================================
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status of the agent"""
        return {
            "agent_name": self.agent_name,
            "agent_role": self.agent_role.value,
            "status": self.health.status.value,
            "uptime_seconds": (datetime.now() - self.health.uptime_start).total_seconds(),
            "execution_count": self.health.execution_count,
            "error_count": self.health.error_count,
            "success_rate": self.health.success_rate,
            "average_execution_time": self.health.average_execution_time,
            "queue_length": len(self.task_queue),
            "last_execution": self.health.last_execution.isoformat() if self.health.last_execution else None,
            "last_error": self.health.last_error
        }
    
    def _update_average_execution_time(self, execution_time: float):
        """Update rolling average execution time"""
        if self.health.execution_count == 1:
            self.health.average_execution_time = execution_time
        else:
            # Simple moving average
            alpha = 0.1  # Weight for new measurement
            self.health.average_execution_time = (
                alpha * execution_time + 
                (1 - alpha) * self.health.average_execution_time
            )
    
    # =============================================================================
    # LANGCHAIN INTEGRATION HELPERS
    # =============================================================================
    
    async def run_llm_chain(self, prompt: str, **kwargs) -> str:
        """Run an LLM chain with the given prompt"""
        if not self.agent_executor:
            raise ValueError(f"Agent {self.agent_name} has no LLM executor configured")
        
        try:
            result = await self.agent_executor.arun(input=prompt, **kwargs)
            return result
        except Exception as e:
            self.logger.error("LLM chain execution failed", prompt=prompt[:100], error=str(e))
            raise
    
    def add_tool(self, tool: BaseTool):
        """Add a tool to the agent's toolkit"""
        self.tools.append(tool)
        if self.agent_executor:
            # Reinitialize agent executor with new tools
            self._initialize_agent()
    
    # =============================================================================
    # UTILITY METHODS
    # =============================================================================
    
    def start(self):
        """Start the agent"""
        self.is_running = True
        self.health.status = AgentStatus.IDLE
        self.logger.info("Agent started")
    
    def stop(self):
        """Stop the agent"""
        self.is_running = False
        self.health.status = AgentStatus.STOPPED
        self.logger.info("Agent stopped")
    
    def clear_queue(self):
        """Clear the task queue"""
        cleared_count = len(self.task_queue)
        self.task_queue.clear()
        self.logger.info("Task queue cleared", cleared_tasks=cleared_count)
    
    def get_queue_info(self) -> Dict[str, Any]:
        """Get information about the current task queue"""
        return {
            "queue_length": len(self.task_queue),
            "current_task": {
                "task_id": self.current_task.task_id,
                "task_type": self.current_task.task_type
            } if self.current_task else None,
            "next_tasks": [
                {"task_id": task.task_id, "task_type": task.task_type, "priority": task.priority}
                for task in self.task_queue[:5]  # Show next 5 tasks
            ]
        }
    
    def __repr__(self) -> str:
        return (f"BaseAgent(name={self.agent_name}, "
                f"role={self.agent_role.value}, "
                f"status={self.health.status.value}, "
                f"queue_length={len(self.task_queue)})")

# =============================================================================
# SPECIALIZED TASK TYPES
# =============================================================================

class IngestionTask(AgentTask):
    """Specialized task for data ingestion"""
    endpoint: str = Field(..., description="API endpoint to fetch from")
    parameters: Dict[str, Any] = Field(default_factory=dict)

class AnalysisTask(AgentTask):
    """Specialized task for data analysis"""
    data_source: str = Field(..., description="Source of data to analyze")
    metrics_to_compute: List[str] = Field(default_factory=list)

class SemanticTask(AgentTask):
    """Specialized task for semantic analysis"""
    content_type: str = Field(..., description="Type of content to analyze")
    prompt_template: str = Field(..., description="LLM prompt template to use")

# =============================================================================
# AGENT FACTORY
# =============================================================================

class AgentFactory:
    """Factory for creating different types of agents"""
    
    @staticmethod
    def create_agent(agent_role: AgentRole, config: Dict[str, Any] = None) -> BaseAgent:
        """Create an agent of the specified role"""
        # This will be expanded as we implement specific agent types
        from agents.ingestion_agent import IngestionAgent
        from agents.analyzer_agent import AnalyzerAgent
        from agents.semantic_agent import SemanticAgent
        
        agent_map = {
            AgentRole.INGESTION: IngestionAgent,
            AgentRole.ANALYZER: AnalyzerAgent,
            AgentRole.SEMANTIC: SemanticAgent,
            # Add more agents as implemented
        }
        
        if agent_role not in agent_map:
            raise ValueError(f"Agent role {agent_role} not implemented yet")
        
        agent_class = agent_map[agent_role]
        return agent_class(config=config)

if __name__ == "__main__":
    # Example usage
    import asyncio
    
    async def test_base_agent():
        # This would be a concrete implementation in practice
        class TestAgent(BaseAgent):
            def _create_agent(self):
                return None  # Simplified for test
            
            async def execute_task(self, task: AgentTask) -> AgentResult:
                # Simulate some work
                await asyncio.sleep(0.1)
                return AgentResult(
                    task_id=task.task_id,
                    agent_name=self.agent_name,
                    success=True,
                    result_data={"processed": True},
                    execution_time_seconds=0.1
                )
        
        # Create and test agent
        agent = TestAgent("test_agent", AgentRole.ANALYZER)
        agent.start()
        
        # Add a test task
        task = AgentTask(task_id="test_001", task_type="test_analysis")
        agent.add_task(task)
        
        # Process the task
        result = await agent.process_next_task()
        print(f"Task result: {result}")
        print(f"Agent health: {agent.get_health_status()}")
    
    asyncio.run(test_base_agent()) 