from openai import OpenAI
import os
from dotenv import load_dotenv
import json

load_dotenv(override=True)

# Get OpenAI client
api_key = os.getenv('OPENAI_API_KEY')
print(f"API Key loaded: {api_key[:20]}..." if api_key else "No API key found")

client = OpenAI(api_key=api_key)

# Test GPT-5 mini with simple prompt
print("\n=== Testing GPT-5 mini ===\n")

try:
    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Generate a simple JSON with 3 predictions about student stress. Return format: {\"predictions\": [\"prediction1\", \"prediction2\", \"prediction3\"]}"}
        ],
        max_completion_tokens=2000,  # Increased for reasoning model
        response_format={"type": "json_object"}
    )

    print(f"Response object: {response}")
    print(f"\nResponse type: {type(response)}")
    print(f"\nResponse content: {response.choices[0].message.content}")

    # Try to parse JSON
    result = json.loads(response.choices[0].message.content)
    print(f"\nParsed JSON: {result}")
    print(f"\nPredictions: {result.get('predictions', [])}")

    print("\n✅ SUCCESS: GPT-5 mini is working!")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print(f"Error type: {type(e)}")
    import traceback
    traceback.print_exc()
