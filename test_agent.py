
"""
Test script for the AI Agent
"""

from app.agent import get_agent
from dotenv import load_dotenv
import time


def print_response(query: str, response: dict):
    """Pretty print the agent response"""
    print(f"\n{'-'*70}")
    print(f"USER: {query}")
    print('-'*70)
    print(f"ASSISTANT: {response['answer']}")
    
    if response.get('sources'):
        print(f"\nSources: {', '.join(response['sources'])}")
    
    if response.get('error'):
        print(f"\nError: {response['error']}")
    
    print('-'*70)


def test_basic_queries():
    """Test basic agent functionality"""
    load_dotenv()
    
    print("\n" + "-"*70)
    print("TESTING AI AGENT - BASIC QUERIES")
    print("-"*70)
    
    agent = get_agent()
    session_id = "test_session_1"
    
    # Test queries
    test_cases = [
        # General queries (should answer directly)
        "Hello! How are you?",
        "What can you help me with?",
        
        # Document-based queries (should use search_documents)
        "What is the remote work policy?",
        "How many vacation days do I get?",
        "How do I upload a file using the API?",
        "What are the health insurance options?",
        
        # Follow-up question (tests memory)
        "What about dental insurance?",
        
        # Date/time query (should use get_current_date)
        "What's today's date?",
    ]
    
    for query in test_cases:
        response = agent.chat(query, session_id=session_id)
        print_response(query, response)
        time.sleep(1)  # Avoid rate limits
    
    print("\nBasic queries test complete!")


def test_multi_session():
    """Test multiple sessions (memory isolation)"""
    load_dotenv()
    
    print("\n" + "="*70)
    print("TESTING AI AGENT - MULTI-SESSION MEMORY")
    print("="*70)
    
    agent = get_agent()
    
    # Session 1
    print("\n--- SESSION 1 ---")
    response1 = agent.chat("My name is Alice", session_id="session_1")
    print_response("My name is Alice", response1)
    
    response2 = agent.chat("What's my name?", session_id="session_1")
    print_response("What's my name?", response2)
    
    # Session 2 (should not know Alice's name)
    print("\n--- SESSION 2 ---")
    response3 = agent.chat("My name is Bob", session_id="session_2")
    print_response("My name is Bob", response3)
    
    response4 = agent.chat("What's my name?", session_id="session_2")
    print_response("What's my name?", response4)
    
    # Back to Session 1 (should still remember Alice)
    print("\n--- BACK TO SESSION 1 ---")
    response5 = agent.chat("Do you remember me?", session_id="session_1")
    print_response("Do you remember me?", response5)
    
    print(f"\nActive sessions: {agent.get_session_count()}")
    print("Multi-session test complete!")


def test_tool_usage():
    """Test specific tool usage"""
    load_dotenv()
    
    print("\n" + "-"*70)
    print("TESTING AI AGENT - TOOL USAGE")
    print("-"*70)
    
    agent = get_agent()
    
    # Test search_documents tool
    print("\n--- TESTING SEARCH_DOCUMENTS TOOL ---")
    queries_need_docs = [
        "What's the API endpoint for uploading files?",
        "Explain the 401k retirement plan",
        "How does CloudStorage Pro handle file versioning?",
    ]
    
    for query in queries_need_docs:
        response = agent.chat(query, session_id="tool_test")
        print_response(query, response)
        
        # Verify sources were found
        if response.get('sources'):
            print("Tool used correctly - sources found")
        else:
            print("Warning: No sources found, tool may not have been used")
        
        time.sleep(1)
    
    print("\nTool usage test complete!")

def interactive_mode():
    """Interactive chat mode"""
    load_dotenv()
    
    print("\n" + "-"*70)
    print("INTERACTIVE MODE - Chat with the Agent")
    print("Type 'quit' to exit, 'clear' to clear session")
    print("-"*70 + "\n")
    
    agent = get_agent()
    session_id = "interactive_session"
    
    while True:
        try:
            query = input("👤 You: ").strip()
            
            if not query:
                continue
            
            if query.lower() == 'quit':
                print("\nGoodbye!")
                break
            
            if query.lower() == 'clear':
                agent.clear_session(session_id)
                print("Session cleared!")
                continue
            
            response = agent.chat(query, session_id=session_id)
            
            print(f"\nAssistant: {response['answer']}")
            if response.get('sources'):
                print(f"Sources: {', '.join(response['sources'])}")
            print()
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}\n")


def main():
    """Run all tests"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        print("\nStarting AI Agent Tests...\n")
        
        # Run tests
        test_basic_queries()
        time.sleep(2)
        
        test_multi_session()
        time.sleep(2)
        
        test_tool_usage()
        
        print("\n" + "-"*70)
        print("ALL TESTS COMPLETED!")
        print("-"*70)
        print("\nTo try interactive mode, run:")
        print("  uv run python test_agent.py --interactive")


if __name__ == "__main__":
    main()