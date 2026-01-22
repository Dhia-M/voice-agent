import requests
import json

print("Testing LM Studio connection...")

try:
    # Simple test request
    response = requests.post(
        "http://localhost:1234/v1/chat/completions",
        headers={"Content-Type": "application/json"},
        data=json.dumps({
            "model": "qwen2.5-7b-instruct-1m",
            "messages": [{"role": "user", "content": "Say hello in 3 words"}],
            "temperature": 0.7,
            "max_tokens": 50
        }),
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Parsed JSON: {json.dumps(data, indent=2)}")
        if 'choices' in data:
            print(f"LLM says: {data['choices'][0]['message']['content']}")
    else:
        print("❌ LM Studio returned error")
        
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to localhost:1234 - LM Studio not running?")
except Exception as e:
    print(f"❌ Error: {e}")

print("\nDone.")