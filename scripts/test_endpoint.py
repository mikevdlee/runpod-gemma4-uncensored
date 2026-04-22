"""
Test script for RunPod Gemma 4 31B Uncensored endpoint.
Usage: python test_endpoint.py

Before running, set these environment variables:
  RUNPOD_API_KEY=your_runpod_api_key
  RUNPOD_ENDPOINT_ID=your_endpoint_id
"""

import os
import sys

def main():
    api_key = os.getenv("RUNPOD_API_KEY")
    endpoint_id = os.getenv("RUNPOD_ENDPOINT_ID")

    if not api_key or not endpoint_id:
        print("❌ Please set RUNPOD_API_KEY and RUNPOD_ENDPOINT_ID environment variables")
        print("   Example:")
        print("   set RUNPOD_API_KEY=your_key_here")
        print("   set RUNPOD_ENDPOINT_ID=your_endpoint_id")
        sys.exit(1)

    try:
        from openai import OpenAI
    except ImportError:
        print("❌ Please install openai: pip install openai")
        sys.exit(1)

    base_url = f"https://api.runpod.ai/v2/{endpoint_id}/openai/v1"
    client = OpenAI(api_key=api_key, base_url=base_url)

    print(f"🔗 Connecting to: {base_url}")
    print()

    # Test 1: List models
    print("=" * 60)
    print("TEST 1: List available models")
    print("=" * 60)
    try:
        models = client.models.list()
        for model in models.data:
            print(f"  ✅ Model: {model.id}")
    except Exception as e:
        print(f"  ❌ Failed: {e}")
    print()

    # Test 2: Basic chat completion
    print("=" * 60)
    print("TEST 2: Basic chat completion")
    print("=" * 60)
    try:
        response = client.chat.completions.create(
            model="gemma-4-31b-uncensored",
            messages=[
                {"role": "user", "content": "Hello! Introduce yourself in one sentence."}
            ],
            max_tokens=100,
            temperature=0.7,
        )
        print(f"  ✅ Response: {response.choices[0].message.content}")
        print(f"  📊 Tokens: {response.usage.prompt_tokens} in, {response.usage.completion_tokens} out")
    except Exception as e:
        print(f"  ❌ Failed: {e}")
    print()

    # Test 3: Reasoning / Thinking mode
    print("=" * 60)
    print("TEST 3: Reasoning mode (thinking)")
    print("=" * 60)
    try:
        response = client.chat.completions.create(
            model="gemma-4-31b-uncensored",
            messages=[
                {"role": "user", "content": "What is 17 * 23 + 45? Think step by step."}
            ],
            max_tokens=512,
            temperature=0.3,
        )
        msg = response.choices[0].message
        if hasattr(msg, 'reasoning_content') and msg.reasoning_content:
            print(f"  🧠 Reasoning: {msg.reasoning_content[:200]}...")
        print(f"  ✅ Answer: {msg.content}")
    except Exception as e:
        print(f"  ❌ Failed: {e}")
    print()

    # Test 4: Streaming
    print("=" * 60)
    print("TEST 4: Streaming")
    print("=" * 60)
    try:
        stream = client.chat.completions.create(
            model="gemma-4-31b-uncensored",
            messages=[
                {"role": "user", "content": "Count from 1 to 5."}
            ],
            max_tokens=50,
            stream=True,
        )
        print("  ✅ Stream: ", end="")
        for chunk in stream:
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="")
        print()
    except Exception as e:
        print(f"  ❌ Failed: {e}")
    print()

    print("=" * 60)
    print("🎉 All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
