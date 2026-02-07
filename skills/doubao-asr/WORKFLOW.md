# Doubao ASR Workflow Configuration

Reference for ASR workflow configuration options.

## Workflow Presets

The ASR script provides these preset workflows:

| Preset | Description | Workflow String |
|--------|-------------|-----------------|
| `default` | Basic recognition only | `audio_in,resample,partition,vad,fe,decode` |
| `itn` | With ITN (number normalization) | `...decode,itn` |
| `punctuate` | With punctuation | `...decode,nlu_punctuate` |
| `smooth` | With smoothing (disfluency removal) | `...decode,nlu_ddc` |
| `full` | All post-processing enabled | `...decode,itn,nlu_ddc,nlu_punctuate` |

## Workflow Components

| Component | Description |
|-----------|-------------|
| `audio_in` | Audio input processing |
| `resample` | Resample to target rate |
| `partition` | Audio partitioning |
| `vad` | Voice Activity Detection |
| `fe` | Feature extraction |
| `decode` | Speech decoding |
| `itn` | Inverse Text Normalization |
| `nlu_punctuate` | Punctuation prediction |
| `nlu_ddc` | Disfluency Detection and Correction |

## ITN (Inverse Text Normalization)

Converts spoken-form numbers and expressions to written form:

| Spoken | Written |
|--------|---------|
| "two thousand twenty five" | "2025" |
| "one hundred dollars" | "$100" |
| "march fifteenth" | "March 15" |

**Enable with:**

```bash
python scripts/asr.py --audio_path file.wav --workflow itn
```

## Punctuation

Automatically adds punctuation based on speech patterns:

- Periods at sentence ends
- Commas at natural pauses
- Question marks for questions

**Enable with:**

```bash
python scripts/asr.py --audio_path file.wav --workflow punctuate
```

## Smoothing (DDC)

Removes disfluencies like:

- Repeated words ("I I think")
- Filler words ("um", "uh")
- False starts

**Enable with:**

```bash
python scripts/asr.py --audio_path file.wav --workflow smooth
```

## Custom Workflow

You can also pass a custom workflow string directly:

```bash
python scripts/asr.py \
  --audio_path file.wav \
  --workflow "audio_in,resample,partition,vad,fe,decode,itn"
```

## Recommended Settings

| Use Case | Recommended Workflow |
|----------|---------------------|
| Transcription for reading | `full` |
| Subtitles | `punctuate` |
| Voice commands | `default` |
| Meeting notes | `full` |
| Search indexing | `itn` |

## Language Support

| Language | Code | Notes |
|----------|------|-------|
| Chinese (Mandarin) | `zh-CN` | Default, best supported |
| English | `en-US` | Good support |
| Japanese | `ja-JP` | Limited |

## Audio Quality Tips

1. **Sample Rate**: Use 16000 Hz for best results
2. **Channels**: Mono (1 channel) preferred
3. **Bit Depth**: 16 bits standard
4. **Format**: WAV recommended, MP3 supported
5. **Duration**: Keep under 60 seconds for one-shot ASR
6. **Noise**: Minimize background noise for better accuracy
