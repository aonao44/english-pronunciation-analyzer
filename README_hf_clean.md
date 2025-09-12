# English Pronunciation Analysis API

Record English pronunciation and display actual pronunciation in katakana.
Designed for pronunciation learning and instruction, providing raw pronunciation results without auto-correction.

## Features

- **Speech Recognition**: English speech recognition using Whisper tiny model
- **Katakana Conversion**: Phonetic rule-based English to katakana conversion
- **Web UI**: User-friendly interface with Gradio
- **API**: REST API format for program integration

## Usage

### Web UI
1. Record with microphone button or upload audio file
2. Click "Start Analysis" button
3. Check English and katakana transcription results

### API Usage
```bash
curl -X POST \
  https://your-space.hf.space/api/predict \
  -F 'data=[null, audio_file]'
```

## Features

- **Pronunciation Learning Focused**: Faithful transcription of actual pronunciation
- **Free**: Runs on Hugging Face Spaces free tier
- **Fast**: Lightweight processing with Whisper tiny model
- **Accurate**: Phonetic rule-based katakana conversion

---

**英語発音解析API - 発音学習用**