
"""
Test script for FastAPI endpoints
Run the API server first: uv run uvicorn app.main:app --reload
"""

import httpx
import json
import time
from typing import Dict, Any


API_BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """Print a section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def print_result(test_name: str, response: httpx.Response):
    """Print test result"""
    status_emoji = "✅" if response.status_code == 200 else "❌"
    print(f"\n{status_emoji} {test_name}")
    print(f"Status Code: {response.status_code}")
    
    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
    except:
        print(f"Response: {response.text}")
    
    print("-" * 70)


def test_root():
    """Test root endpoint"""
    print_section("TEST 1: Root Endpoint")
    
    try:
        response = httpx.get(f"{API_BASE_URL}/")
        print_result("GET /", response)
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_health():
    """Test health check endpoint"""
    print_section("TEST 2: Health Check")
    
    try:
        response = httpx.get(f"{API_BASE_URL}/health")
        print_result("GET /health", response)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n Health Details:")
            print(f"  Status: {data.get('status')}")
            print(f"  Agent Ready: {data.get('agent_ready')}")
            print(f"  RAG Ready: {data.get('rag_ready')}")
            print(f"  Active Sessions: {data.get('active_sessions')}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_ask_general():
    """Test /ask with general question"""
    print_section("TEST 3: General Question (No Documents)")
    
    try:
        payload = {
            "query": "Hello! How are you?",
            "session_id": "test_general"
        }
        
        response = httpx.post(
            f"{API_BASE_URL}/ask",
            json=payload,
            timeout=30.0
        )
        print_result("POST /ask (general)", response)
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_ask_document_based():
    """Test /ask with document-based questions"""
    print_section("TEST 4: Document-Based Questions")
    
    questions = [
        "What is the remote work policy?",
        "How many vacation days do employees get?",
        "How do I upload a file using the API?",
        "What are the health insurance options?"
    ]
    
    success_count = 0
    
    for i, question in enumerate(questions, 1):
        try:
            payload = {
                "query": question,
                "session_id": f"test_docs_{i}"
            }
            
            print(f"\nQuestion {i}/{len(questions)}: {question}")
            
            response = httpx.post(
                f"{API_BASE_URL}/ask",
                json=payload,
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"Status: {response.status_code}")
                print(f"Sources: {data.get('sources', [])}")
                print(f"Answer preview: {data.get('answer', '')[:150]}...")
                success_count += 1
            else:
                print(f"Status: {response.status_code}")
                print(f"Error: {response.text}")
            
            time.sleep(1)  # Avoid rate limits
            
        except Exception as e:
            print(f"Error: {e}")
    
    print(f"\nSuccess Rate: {success_count}/{len(questions)}")
    return success_count == len(questions)


def test_conversation_memory():
    """Test conversation memory with session_id"""
    print_section("TEST 5: Conversation Memory")
    
    try:
        session_id = "test_memory"
        
        # First message
        print("\n First message:")
        payload1 = {
            "query": "What is the vacation policy?",
            "session_id": session_id
        }
        response1 = httpx.post(
            f"{API_BASE_URL}/ask",
            json=payload1,
            timeout=30.0
        )
        print(f"Response: {response1.json().get('answer', '')[:100]}...")
        
        time.sleep(1)
        
        # Follow-up message (should have context)
        print("\n Follow-up message (testing memory):")
        payload2 = {
            "query": "What about sick leave?",
            "session_id": session_id
        }
        response2 = httpx.post(
            f"{API_BASE_URL}/ask",
            json=payload2,
            timeout=30.0
        )
        print(f"Response: {response2.json().get('answer', '')[:100]}...")
        
        return response1.status_code == 200 and response2.status_code == 200
        
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_session_isolation():
    """Test that different sessions are isolated"""
    print_section("TEST 6: Session Isolation")
    
    try:
        # Session 1
        print("\nSession 1:")
        payload1 = {
            "query": "My name is Alice",
            "session_id": "session_1"
        }
        response1 = httpx.post(f"{API_BASE_URL}/ask", json=payload1, timeout=30.0)
        print(f"Response: {response1.json().get('answer', '')[:100]}...")
        
        time.sleep(1)
        
        # Session 2
        print("\nSession 2:")
        payload2 = {
            "query": "What's my name?",
            "session_id": "session_2"
        }
        response2 = httpx.post(f"{API_BASE_URL}/ask", json=payload2, timeout=30.0)
        answer2 = response2.json().get('answer', '')
        print(f"Response: {answer2[:100]}...")
        
        # Session 2 should NOT know about Alice
        success = "alice" not in answer2.lower()
        print(f"\n{'✅' if success else '❌'} Sessions are {'isolated' if success else 'NOT isolated'}")
        
        return success
        
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_clear_session():
    """Test clearing a session"""
    print_section("TEST 7: Clear Session")
    
    try:
        session_id = "test_clear"
        
        # Create session with context
        print("\nCreating session context:")
        payload1 = {
            "query": "Remember that I like remote work",
            "session_id": session_id
        }
        httpx.post(f"{API_BASE_URL}/ask", json=payload1, timeout=30.0)
        
        time.sleep(1)
        
        # Clear session
        print("\nClearing session:")
        clear_payload = {"session_id": session_id}
        response = httpx.post(
            f"{API_BASE_URL}/clear-session",
            json=clear_payload,
            timeout=30.0
        )
        print_result("POST /clear-session", response)
        
        time.sleep(1)
        
        # Try to reference previous context (should not remember)
        print("\nTesting if memory was cleared:")
        payload2 = {
            "query": "What do I like?",
            "session_id": session_id
        }
        response2 = httpx.post(f"{API_BASE_URL}/ask", json=payload2, timeout=30.0)
        answer = response2.json().get('answer', '')
        print(f"Response: {answer[:150]}...")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_error_handling():
    """Test error handling"""
    print_section("TEST 8: Error Handling")
    
    try:
        # Test empty query
        print("\nEmpty query:")
        payload1 = {
            "query": "",
            "session_id": "test_error"
        }
        response1 = httpx.post(f"{API_BASE_URL}/ask", json=payload1, timeout=30.0)
        print(f"Status: {response1.status_code} (expected 422)")
        
        # Test invalid endpoint
        print("\nInvalid endpoint:")
        response2 = httpx.get(f"{API_BASE_URL}/invalid", timeout=30.0)
        print(f"Status: {response2.status_code} (expected 404)")
        
        return response1.status_code == 422 and response2.status_code == 404
        
    except Exception as e:
        print(f"Error: {e}")
        return False


def run_all_tests():
    """Run all API tests"""
    print("\n" + "-"*70)
    print("  FASTAPI ENDPOINT TESTING")
    print("-"*70)
    print("\n Make sure the API server is running:")
    print("   uv run uvicorn app.main:app --reload")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    input()
    
    # Check if server is running
    try:
        httpx.get(f"{API_BASE_URL}/", timeout=5.0)
    except Exception:
        print("\nError: API server is not running!")
        print("\nStart the server with:")
        print("  uv run uvicorn app.main:app --reload")
        return
    
    results = []
    
    # Run tests
    results.append(("Root Endpoint", test_root()))
    results.append(("Health Check", test_health()))
    results.append(("General Questions", test_ask_general()))
    results.append(("Document Questions", test_ask_document_based()))
    results.append(("Conversation Memory", test_conversation_memory()))
    results.append(("Session Isolation", test_session_isolation()))
    results.append(("Clear Session", test_clear_session()))
    results.append(("Error Handling", test_error_handling()))
    
    # Print summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\nAll tests passed!")
    else:
        print(f"\n{total - passed} test(s) failed")
    
    print("-"*70)


if __name__ == "__main__":
    run_all_tests()