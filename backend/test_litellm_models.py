import requests
import json

API_KEY = "sk-nn_jGQlwi-NXYdzhkc4BXw"
BASE_URL = "https://litellm.dev.asoclab.dev"

# Test different model variations
models_to_test = [
    "gpt-4o-mini",
    "azure/gpt-4o-mini",
    "gpt-4o",
    "gpt-3.5-turbo",
    "openai/gpt-4o-mini",
    "openai/gpt-3.5-turbo",
]

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {API_KEY}'
}

simple_message = {
    'messages': [{'role': 'user', 'content': 'Say hi'}],
    'max_tokens': 10
}

print("=" * 60)
print("TESTING LITELLM MODELS")
print("=" * 60)

for model in models_to_test:
    print(f"\n🔍 Testing: {model}")
    payload = {**simple_message, 'model': model}
    
    try:
        response = requests.post(
            f'{BASE_URL}/chat/completions',
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"✅ SUCCESS! Model '{model}' works!")
            print(f"Response: {response.json()['choices'][0]['message']['content'][:50]}")
            print("\n" + "=" * 60)
            print(f"✨ USE THIS MODEL: {model}")
            print("=" * 60)
            break
        else:
            error_msg = response.json().get('error', {}).get('message', response.text)
            print(f"❌ Failed: {error_msg[:100]}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)[:100]}")

print("\n\nIf no model worked, contact the API provider for the correct model name.")