#!/usr/bin/env python3
"""
Doubao ASR (Automatic Speech Recognition) Script

Transcribes audio files to text using ByteDance Volcano Engine ASR WebSocket API.

Usage:
    python asr.py --audio_path recording.wav

Environment variables:
    DOUBAO_APPID: Application ID from Volcano Engine console
    DOUBAO_TOKEN: Access token from Volcano Engine console
    DOUBAO_CLUSTER: Cluster name from Volcano Engine console
"""

import argparse
import asyncio
import gzip
import json
import os
import sys
import uuid
import wave
from io import BytesIO

import websockets


# ASR WebSocket endpoint
ASR_ENDPOINT = "wss://openspeech.bytedance.com/api/v2/asr"

# Protocol constants
PROTOCOL_VERSION = 0b0001
DEFAULT_HEADER_SIZE = 0b0001

# Message types
CLIENT_FULL_REQUEST = 0b0001
CLIENT_AUDIO_ONLY_REQUEST = 0b0010
SERVER_FULL_RESPONSE = 0b1001
SERVER_ACK = 0b1011
SERVER_ERROR_RESPONSE = 0b1111

# Message flags
NO_SEQUENCE = 0b0000
NEG_SEQUENCE = 0b0010

# Serialization/Compression
JSON_SERIAL = 0b0001
GZIP_COMPRESS = 0b0001

# Workflow presets
WORKFLOWS = {
    "default": "audio_in,resample,partition,vad,fe,decode",
    "itn": "audio_in,resample,partition,vad,fe,decode,itn",
    "punctuate": "audio_in,resample,partition,vad,fe,decode,nlu_punctuate",
    "smooth": "audio_in,resample,partition,vad,fe,decode,nlu_ddc",
    "full": "audio_in,resample,partition,vad,fe,decode,itn,nlu_ddc,nlu_punctuate",
}

# Error code descriptions
ERROR_CODES = {
    1000: "Success",
    1001: "Invalid parameters - check request format",
    1002: "Authentication failed - verify token",
    1003: "Rate limit exceeded - reduce request frequency",
    1004: "Quota exceeded - check account quota",
    1005: "Server busy - retry later",
    1010: "Audio too long - use shorter audio",
    1012: "Invalid audio format - check audio file",
    1013: "Silent audio - no speech detected",
    1020: "Recognition timeout - retry",
    1022: "Recognition error - retry",
}


def check_config() -> tuple[str, str, str]:
    """Check and return configuration from environment variables."""
    appid = os.environ.get("DOUBAO_APPID")
    token = os.environ.get("DOUBAO_TOKEN")
    cluster = os.environ.get("DOUBAO_CLUSTER")

    if not appid:
        print("Error: DOUBAO_APPID environment variable not set.")
        print("Please set it with: export DOUBAO_APPID='your-appid'")
        sys.exit(1)

    if not token:
        print("Error: DOUBAO_TOKEN environment variable not set.")
        print("Please set it with: export DOUBAO_TOKEN='your-token'")
        sys.exit(1)

    if not cluster:
        print("Error: DOUBAO_CLUSTER environment variable not set.")
        print("Please set it with: export DOUBAO_CLUSTER='your-cluster'")
        sys.exit(1)

    return appid, token, cluster


def generate_header(
    message_type=CLIENT_FULL_REQUEST,
    message_flags=NO_SEQUENCE,
) -> bytearray:
    """Generate binary protocol header."""
    header = bytearray()
    header.append((PROTOCOL_VERSION << 4) | DEFAULT_HEADER_SIZE)
    header.append((message_type << 4) | message_flags)
    header.append((JSON_SERIAL << 4) | GZIP_COMPRESS)
    header.append(0x00)  # reserved
    return header


def parse_response(res: bytes) -> dict:
    """Parse binary response from ASR server."""
    message_type = res[1] >> 4
    serialization = res[2] >> 4
    compression = res[2] & 0x0f
    header_size = res[0] & 0x0f
    payload = res[header_size * 4:]

    result = {}
    payload_msg = None

    if message_type == SERVER_FULL_RESPONSE:
        payload_size = int.from_bytes(payload[:4], "big", signed=True)
        payload_msg = payload[4:]
    elif message_type == SERVER_ACK:
        seq = int.from_bytes(payload[:4], "big", signed=True)
        result["seq"] = seq
        if len(payload) >= 8:
            payload_size = int.from_bytes(payload[4:8], "big", signed=False)
            payload_msg = payload[8:]
    elif message_type == SERVER_ERROR_RESPONSE:
        code = int.from_bytes(payload[:4], "big", signed=False)
        result["code"] = code
        payload_size = int.from_bytes(payload[4:8], "big", signed=False)
        payload_msg = payload[8:]

    if payload_msg is None:
        return result

    # Decompress if needed
    if compression == GZIP_COMPRESS:
        payload_msg = gzip.decompress(payload_msg)

    # Deserialize if JSON
    if serialization == JSON_SERIAL:
        payload_msg = json.loads(payload_msg.decode("utf-8"))

    result["payload_msg"] = payload_msg
    return result


def read_wav_info(data: bytes) -> tuple[int, int, int, int, int]:
    """Read WAV file information."""
    with BytesIO(data) as f:
        wave_fp = wave.open(f, "rb")
        nchannels, sampwidth, framerate, nframes = wave_fp.getparams()[:4]
        wave_bytes = wave_fp.readframes(nframes)
    return nchannels, sampwidth, framerate, nframes, len(wave_bytes)


def slice_data(data: bytes, chunk_size: int):
    """Slice audio data into chunks."""
    offset = 0
    data_len = len(data)
    while offset + chunk_size < data_len:
        yield data[offset:offset + chunk_size], False
        offset += chunk_size
    yield data[offset:data_len], True


async def transcribe_audio(
    audio_path: str,
    format: str = "wav",
    language: str = "zh-CN",
    workflow: str = "full",
    show_utterances: bool = False,
) -> dict:
    """
    Transcribe audio file to text.

    Args:
        audio_path: Path to audio file
        format: Audio format (wav, mp3, raw, ogg)
        language: Language code (zh-CN, en-US)
        workflow: Processing workflow preset
        show_utterances: Show detailed utterance info

    Returns:
        Recognition result dict
    """
    appid, token, cluster = check_config()

    # Check audio file exists
    if not os.path.exists(audio_path):
        print(f"Error: Audio file not found: {audio_path}")
        sys.exit(1)

    # Read audio data
    with open(audio_path, "rb") as f:
        audio_data = f.read()

    # Determine segment size
    if format == "mp3":
        segment_size = 10000  # Fixed size for MP3
    elif format == "wav":
        nchannels, sampwidth, framerate, _, _ = read_wav_info(audio_data)
        size_per_sec = nchannels * sampwidth * framerate
        segment_size = int(size_per_sec * 100 / 1000)  # 100ms segments
    else:
        segment_size = 10000  # Default

    # Get workflow string
    workflow_str = WORKFLOWS.get(workflow, workflow)

    # Generate unique request ID
    reqid = str(uuid.uuid4())

    # Build request
    request = {
        "app": {
            "appid": appid,
            "cluster": cluster,
            "token": token,
        },
        "user": {
            "uid": "doubao-asr-skill",
        },
        "request": {
            "reqid": reqid,
            "nbest": 1,
            "workflow": workflow_str,
            "show_utterances": show_utterances,
            "result_type": "full",
            "sequence": 1,
        },
        "audio": {
            "format": format,
            "rate": 16000,
            "language": language,
            "bits": 16,
            "channel": 1,
            "codec": "raw",
        },
    }

    # Prepare full client request
    payload_bytes = gzip.compress(json.dumps(request).encode())
    full_request = bytearray(generate_header(CLIENT_FULL_REQUEST, NO_SEQUENCE))
    full_request.extend(len(payload_bytes).to_bytes(4, "big"))
    full_request.extend(payload_bytes)

    # Set up headers
    headers = {"Authorization": f"Bearer; {token}"}

    try:
        async with websockets.connect(
            ASR_ENDPOINT,
            extra_headers=headers,
            max_size=100 * 1024 * 1024,
        ) as ws:
            # Send full client request
            await ws.send(full_request)
            res = await ws.recv()
            result = parse_response(res)

            # Check for errors
            if "payload_msg" in result:
                code = result["payload_msg"].get("code", 0)
                if code != 1000:
                    error_desc = ERROR_CODES.get(code, "Unknown error")
                    print(f"Error: {code} - {error_desc}")
                    print(f"Message: {result['payload_msg'].get('message', '')}")
                    return result

            # Send audio chunks
            for seq, (chunk, is_last) in enumerate(slice_data(audio_data, segment_size), 1):
                payload_bytes = gzip.compress(chunk)

                if is_last:
                    audio_request = bytearray(generate_header(CLIENT_AUDIO_ONLY_REQUEST, NEG_SEQUENCE))
                else:
                    audio_request = bytearray(generate_header(CLIENT_AUDIO_ONLY_REQUEST, NO_SEQUENCE))

                audio_request.extend(len(payload_bytes).to_bytes(4, "big"))
                audio_request.extend(payload_bytes)

                await ws.send(audio_request)
                res = await ws.recv()
                result = parse_response(res)

                # Check for errors
                if "payload_msg" in result:
                    code = result["payload_msg"].get("code", 0)
                    if code != 1000:
                        error_desc = ERROR_CODES.get(code, "Unknown error")
                        print(f"Error: {code} - {error_desc}")
                        return result

            return result

    except websockets.exceptions.ConnectionClosedError as e:
        print(f"Error: WebSocket connection closed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe audio to text using Doubao ASR API"
    )
    parser.add_argument(
        "--audio_path",
        required=True,
        help="Path to audio file",
    )
    parser.add_argument(
        "--format",
        default="wav",
        choices=["wav", "mp3", "raw", "ogg"],
        help="Audio format (default: wav)",
    )
    parser.add_argument(
        "--language",
        default="zh-CN",
        help="Language code (default: zh-CN)",
    )
    parser.add_argument(
        "--workflow",
        default="full",
        choices=list(WORKFLOWS.keys()),
        help="Processing workflow (default: full)",
    )
    parser.add_argument(
        "--show_utterances",
        action="store_true",
        help="Show detailed utterance information",
    )

    args = parser.parse_args()

    # Run transcription
    result = asyncio.run(
        transcribe_audio(
            audio_path=args.audio_path,
            format=args.format,
            language=args.language,
            workflow=args.workflow,
            show_utterances=args.show_utterances,
        )
    )

    # Output result
    if "payload_msg" in result:
        payload = result["payload_msg"]
        if payload.get("code") == 1000:
            # Success - extract text
            text_results = payload.get("result", [])
            if text_results:
                text = text_results[0].get("text", "")
                print(f"Transcription: {text}")

                if args.show_utterances:
                    utterances = text_results[0].get("utterances", [])
                    if utterances:
                        print("\nUtterances:")
                        for i, utt in enumerate(utterances, 1):
                            print(f"  {i}. [{utt.get('start_time', 0)}-{utt.get('end_time', 0)}ms] {utt.get('text', '')}")

                # Output full JSON for programmatic use
                print("\n--- Full Result (JSON) ---")
                print(json.dumps(payload, ensure_ascii=False, indent=2))
            else:
                print("No transcription result")
        else:
            print(f"Recognition failed: {payload.get('message', 'Unknown error')}")
    else:
        print("No response received")


if __name__ == "__main__":
    main()
