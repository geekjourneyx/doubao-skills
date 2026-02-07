# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-07

### Added

#### Skills
- **doubao-tts**: Text-to-Speech skill using ByteDance Volcano Engine TTS V3 API
  - 100+ voice types support
  - Emotion control for supported voices
  - Speed ratio adjustment (0.1 - 2.0)
  - Multiple output formats: MP3, WAV, PCM, OGG_OPUS
  - Streaming HTTP response handling

- **doubao-asr**: Automatic Speech Recognition skill using ByteDance Volcano Engine ASR API
  - WebSocket streaming recognition
  - Multiple audio formats: WAV, MP3, RAW, OGG
  - ITN (Inverse Text Normalization) support
  - Punctuation and smoothing options
  - Multi-language support (zh-CN, en-US, etc.)

#### Installation Methods
- One-click install script (`scripts/install-openclaw.sh`)
- `npx skills add` support
- Claude Code plugin support (`.claude-plugin/`)
- Manual installation guide

#### Documentation
- Comprehensive README.md (Chinese)
- SKILL.md files (English with Chinese keywords for intent recognition)
- VOICES.md - Complete voice type reference
- WORKFLOW.md - ASR workflow configuration guide
- Architecture documentation (`docs/architecture.md`)
- Skills specification documentation (`docs/skills-specification.md`)

#### Developer Experience
- Friendly error messages with solution hints
- Bilingual install script (Chinese/English)
- Environment variable validation
- Dependency checking (requests, websockets)

### Technical Details

- TTS Endpoint: `https://openspeech.bytedance.com/api/v3/tts/unidirectional`
- ASR Endpoint: `wss://openspeech.bytedance.com/api/v2/asr`
- Required Environment Variables:
  - `DOUBAO_APPID` - Application ID
  - `DOUBAO_TOKEN` - Access Token
  - `DOUBAO_CLUSTER` - Cluster ID (ASR only)

---

[1.0.0]: https://github.com/geekjourneyx/doubao-skills/releases/tag/v1.0.0
