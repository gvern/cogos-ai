#!/usr/bin/env python3
"""
Test script to verify ingestion routes are working
"""
import requests
import json

def test_ingestion_endpoints():
    base_url = "http://localhost:8000"
    
    # Test endpoints
    endpoints = [
        "/ingestion/health",
        "/ingestion/collections", 
        "/ingestion/stats",
        "/ping"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            print(f"GET {endpoint}: {response.status_code}")
            if response.status_code == 200:
                print(f"  Response: {response.json()}")
            else:
                print(f"  Error: {response.text}")
        except Exception as e:
            print(f"GET {endpoint}: ERROR - {e}")
        print()

if __name__ == "__main__":
    test_ingestion_endpoints()
