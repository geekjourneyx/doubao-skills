---
name: doubao-tts
description: Synthesizes speech from text using Doubao (ByteDance) TTS V3 API. Supports 100+ voice types, emotions, speed control, and audio formats (mp3/wav/pcm/ogg_opus). Use when converting text to audio, generating voice content, reading text aloud, or TTS tasks. 豆包语音合成，文字转语音，朗读文本。
metadata: {"openclaw": {"emoji": "🎙️", "homepage": "https://www.volcengine.com/docs/6561/1257584", "requires": {"bins": ["python3"], "env": ["DOUBAO_APPID", "DOUBAO_TOKEN"]}, "primaryEnv": "DOUBAO_TOKEN"}}
---

# Doubao TTS (Text-to-Speech)

Converts text to speech using ByteDance Volcano Engine TTS V3 HTTP streaming API.

## Prerequisites

Set environment variables:

```bash
export DOUBAO_APPID="your-appid"
export DOUBAO_TOKEN="your-access-token"
```

Install dependencies:

```bash
pip install requests
```

## Quick Start

```bash
python {baseDir}/scripts/tts.py --text "Hello, this is a test." --output output.mp3
```

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `--text` | Yes | - | Text to synthesize (max 1024 bytes, recommended <300 chars) |
| `--voice_type` | No | `zh_female_cancan_mars_bigtts` | Voice ID |
| `--encoding` | No | `mp3` | Output format: mp3, wav, pcm, ogg_opus |
| `--output` | No | `output.<encoding>` | Output file path |
| `--speed_ratio` | No | `1.0` | Speed ratio (0.1 - 2.0) |
| `--emotion` | No | - | Emotion for multi-emotion voices |

## Usage Examples

**Basic synthesis:**

```bash
python {baseDir}/scripts/tts.py --text "Welcome to Doubao TTS service."
```

**Custom voice and format:**

```bash
python {baseDir}/scripts/tts.py \
  --text "This is synthesized with a different voice." \
  --voice_type zh_male_rap_mars_bigtts \
  --encoding wav \
  --output custom_voice.wav
```

**Adjust speed:**

```bash
python {baseDir}/scripts/tts.py \
  --text "This is slower speech." \
  --speed_ratio 0.8 \
  --output slow.mp3
```

**With emotion (for supported voices):**

```bash
python {baseDir}/scripts/tts.py \
  --text "I am very happy today!" \
  --voice_type zh_female_shuangkuaisisi_moon_bigtts \
  --emotion happy \
  --output happy.mp3
```

## Voice Types

For a complete list of available voices, see [VOICES.md]({baseDir}/VOICES.md).

Common voice types:
- `zh_female_cancan_mars_bigtts` - Female, Cancan (default)
- `zh_male_rap_mars_bigtts` - Male, Rap style
- `zh_female_shuangkuaisisi_moon_bigtts` - Female, supports emotions

## Error Handling

| Code | Description | Solution |
|------|-------------|----------|
| 3000 | Success | - |
| 3001 | Invalid request | Check parameters |
| 3003 | Concurrent limit exceeded | Retry later |
| 3010 | Text too long | Split into smaller chunks (<300 chars) |
| 3011 | Invalid text | Check text content |
| 3050 | Voice not found | Verify voice_type parameter |

## API Reference

- Endpoint: `https://openspeech.bytedance.com/api/v3/tts/unidirectional`
- Method: HTTP POST with streaming response
- Authentication: `Authorization: Bearer; {token}`
