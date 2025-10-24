#!/usr/bin/env python3
"""
Test script to verify the model selection functionality works correctly.
This script tests all four RL algorithms available in the practice backend.
"""

import requests
import json
import time

def test_algorithm(algorithm_type, base_url="http://localhost:8000"):
    """Test a specific RL algorithm"""
    print(f"\n🧪 Testing {algorithm_type.upper()} algorithm...")
    
    # Test data - simple 2-link scenario
    test_data = {
        "links": [
            {"tx_position": {"x": 0, "y": 25}, "rx_position": {"x": 100, "y": 25}},
            {"tx_position": {"x": 0, "y": 75}, "rx_position": {"x": 100, "y": 75}}
        ],
        "algorithm_type": algorithm_type
    }
    
    try:
        start_time = time.time()
        response = requests.post(f"{base_url}/optimize", json=test_data, timeout=30)
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {algorithm_type.upper()} - Success!")
            print(f"   Total Capacity: {result['total_capacity']:.4f} Gbps")
            print(f"   Training Time: {result['training_time']:.2f} seconds")
            print(f"   Algorithm Used: {result['algorithm_type']}")
            print(f"   Link 1 Capacity: {result['results'][0]['capacity']:.4f} Gbps")
            print(f"   Link 2 Capacity: {result['results'][1]['capacity']:.4f} Gbps")
            return True
        else:
            print(f"❌ {algorithm_type.upper()} - HTTP Error {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ {algorithm_type.upper()} - Request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ {algorithm_type.upper()} - Unexpected error: {e}")
        return False

def main():
    """Run tests for all algorithms"""
    print("🚀 Starting RL Algorithm Tests")
    print("=" * 50)
    
    algorithms = ["q_learning", "sarsa", "double_q", "expected_sarsa"]
    results = {}
    
    for algo in algorithms:
        results[algo] = test_algorithm(algo)
        time.sleep(1)  # Brief pause between tests
    
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    successful = sum(results.values())
    total = len(results)
    
    for algo, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {algo.upper()}: {status}")
    
    print(f"\n🎯 Overall: {successful}/{total} algorithms passed")
    
    if successful == total:
        print("🎉 All tests passed! Model selection is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the backend logs for details.")

if __name__ == "__main__":
    main()
