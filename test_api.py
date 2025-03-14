#!/usr/bin/env python3
"""
Test script for the ZazenBot 5000 API
"""
import argparse
import requests
import json

def query_api(question, url="http://localhost:8000"):
    """
    Send a question to the ZazenBot 5000 API
    
    Args:
        question: The question to ask
        url: The base URL of the API
        
    Returns:
        The API response text
    """
    endpoint = f"{url}/query"
    headers = {"Content-Type": "application/json"}
    data = {"question": question}
    
    print(f"Sending question to {endpoint}: {question}")
    response = requests.post(endpoint, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        return response.text
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the ZazenBot 5000 API")
    parser.add_argument("question", type=str, help="The question to ask")
    parser.add_argument("--url", type=str, default="http://localhost:8000", 
                        help="The base URL of the API (default: http://localhost:8000)")
    
    args = parser.parse_args()
    
    response = query_api(args.question, args.url)
    if response:
        print("\nResponse:")
        print(response)
