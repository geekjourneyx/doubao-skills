# Doubao TTS Voice Types

Reference for available voice types in Doubao TTS API.

## Cluster Selection

| Voice Prefix | Cluster | Description |
|--------------|---------|-------------|
| Standard voices | `volcano_tts` | Default cluster for most voices |
| `S_` prefix | `volcano_icl` | ICL voice cloning voices |

The script automatically selects the correct cluster based on voice_type.

## Common Voice Types

### Female Voices

| Voice ID | Description | Features |
|----------|-------------|----------|
| `zh_female_cancan_mars_bigtts` | Cancan - Sweet female | Default voice |
| `zh_female_shuangkuaisisi_moon_bigtts` | Shuangkuai - Lively female | Multi-emotion support |
| `zh_female_tianmeixiaoyuan_moon_bigtts` | Tianmei - Sweet student | Young voice |

### Male Voices

| Voice ID | Description | Features |
|----------|-------------|----------|
| `zh_male_rap_mars_bigtts` | Rap style male | Rhythmic |
| `zh_male_M392_conversation_wvae_bigtts` | Conversational male | Natural tone |

### Multi-Emotion Voices

These voices support the `--emotion` parameter:

| Voice ID | Supported Emotions |
|----------|-------------------|
| `zh_female_shuangkuaisisi_moon_bigtts` | happy, sad, angry, surprise |

**Usage with emotion:**

```bash
python scripts/tts.py \
  --text "I am very happy!" \
  --voice_type zh_female_shuangkuaisisi_moon_bigtts \
  --emotion happy
```

## Audio Settings

### Encoding Formats

| Format | Description | Streaming Support |
|--------|-------------|-------------------|
| `mp3` | MPEG Audio Layer 3 | Yes |
| `wav` | Waveform Audio | No (non-streaming only) |
| `pcm` | Raw PCM audio | Yes |
| `ogg_opus` | Ogg with Opus codec | Yes |

### Sample Rate

Default: 24000 Hz. Can be set to 8000 or 16000 if needed.

### Speed Ratio

Range: 0.1 - 2.0 (default: 1.0)

- `0.5` = Half speed (slower)
- `1.0` = Normal speed
- `2.0` = Double speed (faster)

### Loudness Ratio

Range: 0.5 - 2.0 (default: 1.0)

- `0.5` = Half volume
- `1.0` = Normal volume
- `2.0` = Double volume

## Language Support

Most voices support Chinese-English mixed text. For specific language modes:

| explicit_language | Description |
|-------------------|-------------|
| (not set) | Chinese-English mixed |
| `zh-cn` | Chinese primary, supports Chinese-English |
| `en` | English only |
| `ja` | Japanese only |
| `crosslingual` | Multi-language (zh/en/ja/es/id/pt-br) |

## Getting More Voices

For the complete and up-to-date voice list, visit:
- [Volcano Engine Console](https://console.volcengine.com/speech/service/8)
- [Voice List Documentation](https://www.volcengine.com/docs/6561/97465)

## Notes

1. Some voices require purchase before use
2. Free voices (BV001_streaming, BV002_streaming) need to be "purchased" at 0 cost in console
3. Trial quota has limits; upgrade to paid plan for production use
