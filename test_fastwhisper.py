#!/usr/bin/env python3
"""
Test script for FastWhisper API using the sample video file.
Tests transcription functionality and checks for common issues.
"""

import os
import sys
import requests
import time
import json
from pathlib import Path

# Configuration
FASTWHISPER_URL = "http://localhost:1990"
SAMPLE_VIDEO_PATH = "/home/mayurbt/PycharmProjects/vido_ht_m/FastWhisper/tests/sample/zYGDpG-pTho/video.mp4"
SHORT_VIDEO_PATH = "/home/mayurbt/PycharmProjects/vido_ht_m/FastWhisper/test_short.mp4"

def test_health_check():
    """Test if FastWhisper API is running and healthy."""
    print("Testing health check...")
    try:
        response = requests.get(f"{FASTWHISPER_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Health check passed: {data}")
            return True
        else:
            print(f"✗ Health check failed with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Health check failed: {e}")
        print("Make sure FastWhisper API is running on port 1990")
        return False

def test_transcription():
    """Test video transcription with the sample file."""
    print(f"\nTesting transcription with: {SAMPLE_VIDEO_PATH}")
    
    # Check if sample video exists
    if not os.path.exists(SAMPLE_VIDEO_PATH):
        print(f"✗ Sample video not found at: {SAMPLE_VIDEO_PATH}")
        return False
    
    print(f"✓ Sample video found ({os.path.getsize(SAMPLE_VIDEO_PATH)} bytes)")
    
    try:
        # Prepare file for upload
        with open(SAMPLE_VIDEO_PATH, 'rb') as video_file:
            files = {
                'file': ('video.mp4', video_file, 'video/mp4')
            }
            
            print("Sending transcription request...")
            start_time = time.time()
            
            response = requests.post(
                f"{FASTWHISPER_URL}/transcribe/",
                files=files,
                timeout=600  # 10 minutes timeout for large files
            )
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Transcription successful in {processing_time:.2f} seconds")
                print(f"Language detected: {data.get('language', 'N/A')}")
                print(f"Text length: {len(data.get('text', ''))}")
                print(f"Number of segments: {len(data.get('segments', []))}")
                
                # Print first few characters of transcription
                text = data.get('text', '')
                if text:
                    preview = text[:200] + "..." if len(text) > 200 else text
                    print(f"Transcription preview: {preview}")
                
                # Print segment details
                segments = data.get('segments', [])
                if segments:
                    print("\nFirst few segments:")
                    for i, segment in enumerate(segments[:3]):
                        print(f"  Segment {i+1}: {segment['start']:.2f}s - {segment['end']:.2f}s: {segment['text']}")
                
                return True
            else:
                print(f"✗ Transcription failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except requests.exceptions.Timeout:
        print("✗ Transcription timed out (>5 minutes)")
        return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Transcription request failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error during transcription: {e}")
        return False

def check_api_docs():
    """Check if API documentation is accessible."""
    print("\nChecking API documentation...")
    try:
        response = requests.get(f"{FASTWHISPER_URL}/docs", timeout=10)
        if response.status_code == 200:
            print("✓ API documentation accessible at http://localhost:1990/docs")
            return True
        else:
            print(f"✗ API docs not accessible (status {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Could not access API docs: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("FastWhisper API Test Suite")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Health check
    if test_health_check():
        tests_passed += 1
    
    # Test 2: API documentation
    if check_api_docs():
        tests_passed += 1
    
    # Test 3: Transcription
    if test_transcription():
        tests_passed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("✓ All tests passed! FastWhisper is working correctly.")
        return 0
    else:
        print("✗ Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())