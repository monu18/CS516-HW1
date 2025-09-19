"""
ML services for image analysis using Azure Computer Vision API.
Provides alt text generation and object detection for uploaded photos.
"""

import requests
import json
import os
from pathlib import Path
from typing import Dict, List, Optional

# API Configuration
try:
    from api_config import AZURE_VISION_ENDPOINT, AZURE_VISION_KEY
except ImportError:
    # Fallback to environment variables if api_config.py doesn't exist
    AZURE_VISION_ENDPOINT = os.environ.get('AZURE_VISION_ENDPOINT', '')
    AZURE_VISION_KEY = os.environ.get('AZURE_VISION_KEY', '')


def generate_alt_text(image_path: Path) -> Optional[str]:
    """
    Generate alternative text for an image using Azure Computer Vision API.

    Args:
        image_path: Path to the image file

    Returns:
        Generated alt text string or None if failed
    """
    if not AZURE_VISION_ENDPOINT or not AZURE_VISION_KEY:
        print("Warning: Azure Vision API credentials not configured")
        return "Image uploaded by user"  # Fallback alt text

    # Ensure endpoint has proper format
    endpoint = AZURE_VISION_ENDPOINT.rstrip('/')
    analyze_url = f"{endpoint}/vision/v3.2/analyze"

    headers = {
        'Ocp-Apim-Subscription-Key': AZURE_VISION_KEY,
        'Content-Type': 'application/octet-stream'
    }

    params = {
        'visualFeatures': 'Description',
        'language': 'en'
    }

    try:
        with open(image_path, 'rb') as image_data:
            response = requests.post(
                analyze_url,
                headers=headers,
                params=params,
                data=image_data,
                timeout=10
            )
            response.raise_for_status()

            analysis = response.json()
            if 'description' in analysis and analysis['description']['captions']:
                caption = analysis['description']['captions'][0]
                if caption['confidence'] > 0.3:  # Only use if reasonably confident
                    return caption['text'].capitalize()

    except requests.exceptions.RequestException as e:
        print(f"Network error generating alt text: {e}")
    except Exception as e:
        print(f"Error generating alt text: {e}")

    return "Image uploaded by user"  # Fallback alt text


def detect_objects(image_path: Path) -> List[str]:
    """
    Detect objects in an image using Azure Computer Vision API.

    Args:
        image_path: Path to the image file

    Returns:
        List of detected object names (lowercase)
    """
    if not AZURE_VISION_ENDPOINT or not AZURE_VISION_KEY:
        print("Warning: Azure Vision API credentials not configured")
        return []

    # Ensure endpoint has proper format
    endpoint = AZURE_VISION_ENDPOINT.rstrip('/')
    analyze_url = f"{endpoint}/vision/v3.2/analyze"

    headers = {
        'Ocp-Apim-Subscription-Key': AZURE_VISION_KEY,
        'Content-Type': 'application/octet-stream'
    }

    params = {
        'visualFeatures': 'Objects,Tags',
        'language': 'en'
    }

    try:
        with open(image_path, 'rb') as image_data:
            response = requests.post(
                analyze_url,
                headers=headers,
                params=params,
                data=image_data,
                timeout=10
            )
            response.raise_for_status()

            analysis = response.json()
            detected = []

            # Extract object names from objects detection
            if 'objects' in analysis:
                for obj in analysis['objects']:
                    if obj['confidence'] > 0.5:  # Only high-confidence detections
                        detected.append(obj['object'].lower())

            # Extract relevant tags
            if 'tags' in analysis:
                for tag in analysis['tags']:
                    if tag['confidence'] > 0.7:  # Higher threshold for tags
                        # Filter out overly generic tags
                        tag_name = tag['name'].lower()
                        if tag_name not in ['image', 'photo', 'picture', 'text']:
                            detected.append(tag_name)

            # Remove duplicates and return sorted list
            return sorted(list(set(detected)))

    except requests.exceptions.RequestException as e:
        print(f"Network error detecting objects: {e}")
    except Exception as e:
        print(f"Error detecting objects: {e}")

    return []


def process_uploaded_image(image_path: Path) -> Dict[str, any]:
    """
    Process an uploaded image to generate both alt text and detect objects.
    """
    print(f"Processing image: {image_path}")
    print(f"Endpoint configured: {AZURE_VISION_ENDPOINT[:30]}...")
    print(f"Key configured: {AZURE_VISION_KEY[:10]}...")

    alt_text = generate_alt_text(image_path)
    print(f"Generated alt text: {alt_text}")

    objects = detect_objects(image_path)
    print(f"Detected objects: {objects}")

    return {
        'alt_text': alt_text,
        'objects': objects
    }
