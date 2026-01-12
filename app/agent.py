# app/agent.py
"""
AI Agent implementation using LangGraph
"""

from typing import TypedDict, Annotated, Sequence, List, Dict, Any
import operator
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from app.tools import AVAILABLE_TOOLS
from app.config import settings


# Define the agent state
class AgentState(TypedDict):
    """State of the agent conversation"""
    messages: Annotated[Sequence[BaseMessage], operator.add]


class AIAgent:
    """AI Agent with tool calling and memory"""
    
    def __init__(self):
        """Initialize the AI agent"""
        # Initialize LLM with tool binding
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=0,
            streaming=False,
            api_key=settings.openai_api_key
        )
        
        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools(AVAILABLE_TOOLS)
        
        # Build the agent graph
        self.graph = self._build_graph()
        
        # Session memory storage (only user and assistant messages)
        self.sessions: Dict[str, List[BaseMessage]] = {}
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the agent"""
        return """You are a helpful AI assistant for TechCorp Inc.

Your role:
- Answer questions about company policies, benefits, and procedures
- Help users understand our products (CloudStorage Pro)
- Provide technical support using our API documentation
- Maintain a friendly, professional tone

Decision-making guidelines:
1. For questions about company policies, benefits, remote work, vacation, etc. → Use search_documents tool
2. For questions about CloudStorage Pro features, pricing, FAQ → Use search_documents tool  
3. For questions about API usage, endpoints, authentication → Use search_documents tool
4. For general questions, greetings, or small talk → Answer directly without tools
5. For current date/time questions → Use get_current_date tool

When using search_documents:
- Base your answer primarily on the retrieved context
- Cite the source documents
- If context doesn't fully answer the question, acknowledge limitations

Response format:
- Be concise and clear
- Use bullet points for lists when appropriate
- Include relevant details from documents
- Always mention sources when using retrieved information"""
    
    def _should_continue(self, state: AgentState) -> str:
        """Decide whether to continue or end"""
        messages = state["messages"]
        last_message = messages[-1]
        
        # If the LLM makes a tool call, route to tools
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools"
        
        # Otherwise end
        return "end"
    
    def _call_model(self, state: AgentState) -> Dict[str, Any]:
        """Call the LLM"""
        messages = state["messages"]
        
        # Add system message if this is the first message
        if not any(isinstance(msg, SystemMessage) for msg in messages):
            messages = [SystemMessage(content=self._get_system_prompt())] + list(messages)
        
        # Call LLM
        response = self.llm_with_tools.invoke(messages)
        
        return {"messages": [response]}
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        # Create the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("agent", self._call_model)
        workflow.add_node("tools", ToolNode(AVAILABLE_TOOLS))
        
        # Set entry point
        workflow.set_entry_point("agent")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "tools": "tools",
                "end": END
            }
        )
        
        # Add edge from tools back to agent
        workflow.add_edge("tools", "agent")
        
        # Compile the graph
        return workflow.compile()
    
    def _filter_messages_for_history(
        self, 
        messages: List[BaseMessage]
    ) -> List[BaseMessage]:
        """
        Filter messages to only keep user and assistant messages.
        Remove tool messages to avoid API errors.
        """
        filtered = []
        for msg in messages:
            if isinstance(msg, (HumanMessage, AIMessage)):
                # For AIMessage, create a clean copy without tool_calls
                if isinstance(msg, AIMessage):
                    # Create new AIMessage with just the content
                    filtered.append(AIMessage(content=msg.content))
                else:
                    filtered.append(msg)
            # Skip SystemMessage and ToolMessage
        return filtered
    
    def _get_session_history(self, session_id: str) -> List[BaseMessage]:
        """Get conversation history for a session"""
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        return self.sessions[session_id]
    
    def _update_session_history(
        self, 
        session_id: str, 
        messages: List[BaseMessage]
    ):
        """Update session history with filtered messages"""
        # Filter to only user and assistant messages
        filtered = self._filter_messages_for_history(messages)
        
        # Keep only the last 10 messages to avoid context overflow
        self.sessions[session_id] = filtered[-10:]
    
    def _extract_sources_from_messages(
        self, 
        messages: List[BaseMessage]
    ) -> List[str]:
        """Extract source documents from tool messages"""
        sources = []
        
        for msg in messages:
            if isinstance(msg, ToolMessage):
                # Tool message content might contain source information
                content = str(msg.content)
                if 'sources' in content:
                    # Try to extract sources from tool response
                    try:
                        import json
                        # Tool returns dict with sources
                        if content.startswith('{'):
                            data = json.loads(content)
                            if 'sources' in data:
                                sources.extend(data['sources'])
                    except:
                        pass
            
            # Also check regular message content for PDF mentions
            if hasattr(msg, 'content'):
                content = str(msg.content)
                import re
                found = re.findall(r'(\w+\.pdf)', content)
                sources.extend(found)
        
        return list(set(sources))  # Remove duplicates
    
    def chat(
        self, 
        query: str, 
        session_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Chat with the agent
        
        Args:
            query: User query
            session_id: Session identifier for memory
            
        Returns:
            Dictionary with answer and sources
        """
        try:
            # Get session history
            history = self._get_session_history(session_id)
            
            # Create new message
            new_message = HumanMessage(content=query)
            
            # Prepare initial state
            initial_state = {
                "messages": history + [new_message]
            }
            
            # Run the graph
            result = self.graph.invoke(initial_state)
            
            # Extract response
            messages = result["messages"]
            
            # Find the last AI message (final response)
            last_ai_message = None
            for msg in reversed(messages):
                if isinstance(msg, AIMessage) and msg.content:
                    last_ai_message = msg
                    break
            
            if last_ai_message is None:
                return {
                    "answer": "I'm sorry, I couldn't generate a response.",
                    "sources": [],
                    "session_id": session_id
                }
            
            answer = last_ai_message.content
            
            # Extract sources from tool messages
            sources = self._extract_sources_from_messages(messages)
            
            # Update session history (filtered)
            self._update_session_history(session_id, messages)
            
            return {
                "answer": answer,
                "sources": sources,
                "session_id": session_id
            }
            
        except Exception as e:
            return {
                "answer": f"I encountered an error: {str(e)}",
                "sources": [],
                "session_id": session_id,
                "error": str(e)
            }
    
    def clear_session(self, session_id: str):
        """Clear a session's history"""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def get_session_count(self) -> int:
        """Get number of active sessions"""
        return len(self.sessions)


# Singleton instance
_agent_instance = None

def get_agent() -> AIAgent:
    """Get or create agent instance"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = AIAgent()
    return _agent_instance