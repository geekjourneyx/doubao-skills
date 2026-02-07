#!/usr/bin/env python3
"""
Doubao TTS (Text-to-Speech) Script

Synthesizes speech from text using ByteDance Volcano Engine TTS V3 HTTP streaming API.

Usage:
    python tts.py --text "Hello world" --output output.mp3

Environment variables:
    DOUBAO_APPID: Application ID from Volcano Engine console
    DOUBAO_TOKEN: Access token from Volcano Engine console
"""

import argparse
import json
import os
import sys
import uuid

import requests


# TTS V3 HTTP streaming endpoint
TTS_ENDPOINT = "https://openspeech.bytedance.com/api/v3/tts/unidirectional"

# Error code descriptions
ERROR_CODES = {
    3000: "Success",
    3001: "Invalid request - check parameters",
    3003: "Concurrent limit exceeded - retry later",
    3005: "Server busy - retry later",
    3006: "Service interrupted - check reqid uniqueness",
    3010: "Text too long - split into smaller chunks",
    3011: "Invalid text - check text content",
    3030: "Processing timeout - retry",
    3031: "Processing error - retry",
    3050: "Voice type not found - check voice_type parameter",
}


def get_cluster(voice_type: str) -> str:
    """Determine cluster based on voice type."""
    if voice_type.startswith("S_"):
        return "volcano_icl"
    return "volcano_tts"


def check_config() -> tuple[str, str]:
    """Check and return configuration from environment variables."""
    appid = os.environ.get("DOUBAO_APPID")
    token = os.environ.get("DOUBAO_TOKEN")

    if not appid:
        print("Error: DOUBAO_APPID environment variable not set.")
        print("Please set it with: export DOUBAO_APPID='your-appid'")
        sys.exit(1)

    if not token:
        print("Error: DOUBAO_TOKEN environment variable not set.")
        print("Please set it with: export DOUBAO_TOKEN='your-token'")
        sys.exit(1)

    return appid, token


def synthesize_speech(
    text: str,
    voice_type: str = "zh_female_cancan_mars_bigtts",
    encoding: str = "mp3",
    speed_ratio: float = 1.0,
    emotion: str | None = None,
    output_path: str | None = None,
) -> str:
    """
    Synthesize speech from text.

    Args:
        text: Text to synthesize (max 1024 bytes, recommended <300 chars)
        voice_type: Voice ID
        encoding: Output format (mp3, wav, pcm, ogg_opus)
        speed_ratio: Speed ratio (0.1 - 2.0)
        emotion: Emotion for multi-emotion voices
        output_path: Output file path

    Returns:
        Path to the output audio file
    """
    appid, token = check_config()
    cluster = get_cluster(voice_type)

    # Generate unique request ID
    reqid = str(uuid.uuid4())
    uid = str(uuid.uuid4())

    # Build request payload
    request_payload = {
        "app": {
            "appid": appid,
            "token": token,
            "cluster": cluster,
        },
        "user": {
            "uid": uid,
        },
        "audio": {
            "voice_type": voice_type,
            "encoding": encoding,
            "speed_ratio": speed_ratio,
        },
        "request": {
            "reqid": reqid,
            "text": text,
            "operation": "submit",
        },
    }

    # Add emotion if specified
    if emotion:
        request_payload["audio"]["emotion"] = emotion
        request_payload["audio"]["enable_emotion"] = True

    # Set up headers
    headers = {
        "Authorization": f"Bearer; {token}",
        "Content-Type": "application/json",
    }

    # Determine output path
    if not output_path:
        output_path = f"output.{encoding}"

    try:
        # Make streaming request
        response = requests.post(
            TTS_ENDPOINT,
            headers=headers,
            json=request_payload,
            stream=True,
            timeout=60,
        )

        # Check for HTTP errors
        if response.status_code != 200:
            print(f"Error: HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"Message: {error_data.get('message', 'Unknown error')}")
            except Exception:
                print(f"Response: {response.text[:500]}")
            sys.exit(1)

        # Get logid for debugging
        logid = response.headers.get("X-Tt-Logid", "unknown")
        print(f"Request ID: {reqid}")
        print(f"Log ID: {logid}")

        # Stream audio data to file
        audio_data = bytearray()
        for chunk in response.iter_content(chunk_size=4096):
            if chunk:
                audio_data.extend(chunk)

        if not audio_data:
            print("Error: No audio data received")
            sys.exit(1)

        # Check if response is JSON error instead of audio
        try:
            # Try to parse as JSON (error response)
            error_response = json.loads(audio_data.decode("utf-8"))
            code = error_response.get("code", 0)
            message = error_response.get("message", "Unknown error")

            if code != 3000:
                error_desc = ERROR_CODES.get(code, "Unknown error")
                print(f"Error: {code} - {error_desc}")
                print(f"Message: {message}")
                sys.exit(1)
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Not JSON, it's audio data - this is expected
            pass

        # Save audio file
        with open(output_path, "wb") as f:
            f.write(audio_data)

        print(f"Audio saved to: {output_path}")
        print(f"Audio size: {len(audio_data)} bytes")
        return output_path

    except requests.exceptions.Timeout:
        print("Error: Request timed out. Please try again.")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("Error: Connection failed. Please check your network.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Synthesize speech from text using Doubao TTS API"
    )
    parser.add_argument(
        "--text",
        required=True,
        help="Text to synthesize (max 1024 bytes, recommended <300 chars)",
    )
    parser.add_argument(
        "--voice_type",
        default="zh_female_cancan_mars_bigtts",
        help="Voice type ID (default: zh_female_cancan_mars_bigtts)",
    )
    parser.add_argument(
        "--encoding",
        default="mp3",
        choices=["mp3", "wav", "pcm", "ogg_opus"],
        help="Output audio format (default: mp3)",
    )
    parser.add_argument(
        "--output",
        help="Output file path (default: output.<encoding>)",
    )
    parser.add_argument(
        "--speed_ratio",
        type=float,
        default=1.0,
        help="Speed ratio 0.1-2.0 (default: 1.0)",
    )
    parser.add_argument(
        "--emotion",
        help="Emotion for multi-emotion voices (e.g., happy, angry, sad)",
    )

    args = parser.parse_args()

    # Validate speed ratio
    if not 0.1 <= args.speed_ratio <= 2.0:
        print("Error: speed_ratio must be between 0.1 and 2.0")
        sys.exit(1)

    # Validate text length
    if len(args.text.encode("utf-8")) > 1024:
        print("Warning: Text exceeds 1024 bytes, may cause errors")

    synthesize_speech(
        text=args.text,
        voice_type=args.voice_type,
        encoding=args.encoding,
        speed_ratio=args.speed_ratio,
        emotion=args.emotion,
        output_path=args.output,
    )


if __name__ == "__main__":
    main()
