#!/usr/bin/env python3
"""Test Azure OpenAI connection and list available models"""
import os
from dotenv import load_dotenv
import requests

load_dotenv()

endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
api_key = os.environ["AZURE_OPENAI_API_KEY"]
api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

# Try to list deployments
url = f"{endpoint}openai/deployments?api-version={api_version}"
headers = {
    "api-key": api_key
}

print(f"Testing connection to: {endpoint}")
print(f"API Version: {api_version}\n")

try:
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        deployments = response.json()
        print("✓ Connection successful!")
        print(f"\nAvailable deployments ({len(deployments.get('data', []))}):")
        print("-" * 60)
        for deployment in deployments.get('data', []):
            print(f"  • {deployment.get('id', 'N/A')}")
            print(f"    Model: {deployment.get('model', 'N/A')}")
            print(f"    Status: {deployment.get('status', 'N/A')}")
            print()
    else:
        print(f"✗ Error: {response.status_code}")
        print(f"Response: {response.text}")
except Exception as e:
    print(f"✗ Connection failed: {e}")
