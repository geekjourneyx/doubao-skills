---
name: doubao-asr
description: Transcribes audio to text using Doubao (ByteDance) ASR API. Supports streaming recognition, WAV/MP3 formats, ITN, punctuation, and Chinese/English speech. Use when converting speech to text, transcribing audio files, or ASR tasks. 豆包语音识别，语音转文字，音频转录。
metadata: {"openclaw": {"emoji": "🎧", "homepage": "https://www.volcengine.com/docs/6561/80816", "requires": {"bins": ["python3"], "env": ["DOUBAO_APPID", "DOUBAO_TOKEN", "DOUBAO_CLUSTER"]}, "primaryEnv": "DOUBAO_TOKEN"}}
---

# Doubao ASR (Automatic Speech Recognition)

Transcribes audio files to text using ByteDance Volcano Engine ASR WebSocket API.

## Prerequisites

Set environment variables:

```bash
export DOUBAO_APPID="your-appid"
export DOUBAO_TOKEN="your-access-token"
export DOUBAO_CLUSTER="your-cluster"
```

Install dependencies:

```bash
pip install websockets
```

## Quick Start

```bash
python {baseDir}/scripts/asr.py --audio_path recording.wav
```

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `--audio_path` | Yes | - | Path to audio file |
| `--format` | No | `wav` | Audio format: wav, mp3, raw, ogg |
| `--language` | No | `zh-CN` | Language code |
| `--workflow` | No | `full` | Processing workflow |
| `--show_utterances` | No | `false` | Show detailed utterance info |

## Usage Examples

**Basic transcription:**

```bash
python {baseDir}/scripts/asr.py --audio_path speech.wav
```

**MP3 file:**

```bash
python {baseDir}/scripts/asr.py --audio_path speech.mp3 --format mp3
```

**With all post-processing (ITN, punctuation, smoothing):**

```bash
python {baseDir}/scripts/asr.py \
  --audio_path speech.wav \
  --workflow full
```

**Show detailed utterance information:**

```bash
python {baseDir}/scripts/asr.py \
  --audio_path speech.wav \
  --show_utterances
```

## Workflow Options

| Workflow | Description |
|----------|-------------|
| `default` | Basic recognition only |
| `itn` | Enable ITN (Inverse Text Normalization) |
| `punctuate` | Enable punctuation |
| `smooth` | Enable smoothing |
| `full` | Enable all: ITN + punctuation + smoothing |

For detailed workflow configuration, see [WORKFLOW.md]({baseDir}/WORKFLOW.md).

## Output Format

```json
{
  "text": "Transcribed text here",
  "utterances": [
    {
      "text": "Sentence text",
      "start_time": 0,
      "end_time": 2500
    }
  ]
}
```

## Error Handling

| Code | Description | Solution |
|------|-------------|----------|
| 1000 | Success | - |
| 1001 | Invalid parameters | Check request format |
| 1002 | Authentication failed | Verify token |
| 1003 | Rate limit exceeded | Reduce request frequency |
| 1010 | Audio too long | Use shorter audio clips |
| 1012 | Invalid audio format | Check audio file format |
| 1013 | Silent audio | No speech detected in audio |
| 1020 | Recognition timeout | Retry the request |

## Audio Requirements

| Property | Requirement |
|----------|-------------|
| Sample Rate | 16000 Hz (default), 8000 Hz supported |
| Channels | Mono (1 channel) |
| Bit Depth | 16 bits |
| Format | WAV, MP3, OGG, RAW PCM |
| Duration | Recommended < 60 seconds |

## API Reference

- Endpoint: `wss://openspeech.bytedance.com/api/v2/asr`
- Protocol: WebSocket with binary frames
- Authentication: `Authorization: Bearer; {token}`
