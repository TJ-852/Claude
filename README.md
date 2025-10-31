# AMP Video Automation Toolkit

A production-ready Python toolkit for batch-generating personalized AI avatar videos with text-to-speech across multiple languages, plus intelligent video translation with style adaptation.

## What It Does

AMP Video Automation Toolkit provides two powerful workflows:

### 1. Batch Video Generation
Creates personalized AI avatar videos from CSV data:

1. **Script Generation** - Renders personalized scripts from Jinja2 templates with variable substitution
2. **Text-to-Speech** - Converts scripts to audio using ElevenLabs or OpenAI TTS
3. **Avatar Video** - Generates lip-synced avatar videos via HeyGen
4. **Export & Tracking** - Saves outputs locally or to S3 with detailed JSON manifests

### 2. Video Translation & Localization
Translates existing videos to new languages with AI avatars:

1. **Audio Extraction** - Extracts audio from source video using ffmpeg
2. **Transcription** - Transcribes audio using OpenAI Whisper with automatic language detection
3. **Style-Aware Translation** - Translates with GPT-4 applying your chosen communication style (casual, business, explainer, etc.)
4. **TTS Generation** - Creates natural-sounding audio in target language
5. **Avatar Video** - Generates new lip-synced video with translated content

Perfect for customer onboarding videos, multilingual training content, personalized marketing campaigns, video localization, and scalable video production workflows.

## Quick Start

```bash
# 1. Clone and setup
git clone <repo-url>
cd amp-video-automation
make venv
make install

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 3. Validate your input CSV
make render  # Dry run to preview scripts

# 4. Run batch video generation
make run     # Process data/input/samples.csv
```

## Features

- **Video Translation** - translate existing videos to any language with style-aware AI avatars
- **Automatic Transcription** - Whisper-powered transcription with language detection
- **Style-Aware Translation** - 6 translation styles (casual, conversational, business, explainer, formal, technical)
- **Async batch processing** - configurable concurrency and rate limiting
- **Provider abstraction** - swap TTS or avatar vendors without changing code
- **Resume failed jobs** - intelligent retry logic with exponential backoff
- **Templating engine** - Jinja2 templates for script personalization
- **Manifest tracking** - detailed JSON logs per batch with status and URLs
- **S3 export** - optional cloud storage with signed URLs
- **Rich CLI** - beautiful terminal output with progress tracking
- **Fully tested** - comprehensive test suite with fixtures

## Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Required | Description |
|----------|----------|-------------|
| `HEYGEN_API_KEY` | Yes | HeyGen API key from https://app.heygen.com/settings/api |
| `ELEVENLABS_API_KEY` | Yes | ElevenLabs API key from https://elevenlabs.io/api |
| `OPENAI_API_KEY` | Yes | OpenAI API key for Whisper transcription and GPT-4 translation |
| `DEFAULT_VOICE` | No | Default voice ID (default: Rachel) |
| `DEFAULT_AVATAR` | No | Default avatar ID (default: SantaFe_v2) |
| `GPT_MODEL` | No | GPT model for translation: gpt-4o, gpt-4-turbo, gpt-4 (default: gpt-4o) |
| `OUTPUT_BUCKET` | No | S3 bucket path like s3://bucket-name |
| `LOG_LEVEL` | No | Logging level: DEBUG, INFO, WARNING, ERROR |

**System Requirements for Video Translation:**
- **ffmpeg** - Required for video/audio processing. Install with:
  - Ubuntu/Debian: `sudo apt-get install ffmpeg`
  - macOS: `brew install ffmpeg`
  - Windows: Download from https://ffmpeg.org/

## CSV Input Schema

Place your input CSV in `data/input/`. Required columns:

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| `id` | string | Yes | Unique job identifier |
| `name` | string | Yes | Person's name for personalization |
| `language` | string | Yes | Language code (e.g., English, Chinese, Hindi) |
| `voice` | string | No | Voice ID (falls back to DEFAULT_VOICE) |
| `avatar` | string | No | Avatar ID (falls back to DEFAULT_AVATAR) |
| `script` | string | No | Literal script text (overrides template) |
| `variables` | JSON | No | Variables for template rendering |

### Example CSV

```csv
id,name,language,voice,avatar,script,variables
001,Tariq,English,Rachel,SantaFe_v2,,"{\"product\":\"OnboardIQ\"}"
002,Mei,Chinese,Mei_CN,SantaFe_v2,,"{\"product\":\"OnboardIQ\",\"role\":\"Engineer\"}"
003,Arun,Hindi,Arun_IN,SantaFe_v2,"Hello {{name}}, welcome!","{\"role\":\"Manager\"}"
```

## Script Templating with Jinja2

If the `script` column is empty, the tool renders `data/templates/script.j2`:

```jinja2
Hello {{name}},

Welcome to {{product}}! We're excited to have you join as {{role}}.

Let's get started with your personalized onboarding journey.
```

Variables from the CSV `variables` column are passed to the template:

```json
{"product": "OnboardIQ", "role": "Engineer"}
```

You can create multiple templates and reference them in your pipeline logic.

## CLI Usage

### 1. Render (Dry Run)

Preview rendered scripts without calling APIs:

```bash
python -m amp_video.cli render data/input/samples.csv --out output/preview
```

This validates your CSV and templates, writing rendered scripts to `output/preview/`.

### 2. Run (Full Pipeline)

Execute TTS → Avatar → Export:

```bash
python -m amp_video.cli run data/input/samples.csv \
  --concurrency 3 \
  --tag "sunlife-pilot-batch-1"
```

**Options:**
- `--concurrency N` - Max parallel jobs (default: 3)
- `--tag NAME` - Label for this batch in manifest

Output is written to timestamped directories like `output/2025-10-31T14-30-45Z/`.

### 3. Resume Failed Jobs

If jobs fail due to rate limits or transient errors:

```bash
python -m amp_video.cli resume output/2025-10-31T14-30-45Z/manifest.json
```

This re-processes only jobs with `"status": "error"`.

### 4. Export to S3

Upload manifest and videos to S3:

```bash
python -m amp_video.cli export output/2025-10-31T14-30-45Z/manifest.json --dest s3
```

Requires `OUTPUT_BUCKET` configured in `.env`.

### 5. Translate Video (NEW!)

Translate an existing video to a new language with style-aware AI avatar:

```bash
# Basic translation
python -m amp_video.cli translate input.mp4 Thai

# With custom style
python -m amp_video.cli translate video.mp4 Spanish --style business

# With specific avatar and voice
python -m amp_video.cli translate video.mp4 Thai \
  --style conversational \
  --avatar SantaFe_v2 \
  --voice Rachel

# With custom output directory
python -m amp_video.cli translate input.mp4 "Mandarin Chinese" \
  --style explainer \
  --output output/chinese_version
```

**Options:**
- `--style` / `-s` - Translation style: `casual`, `conversational` (default), `business`, `explainer`, `formal`, `technical`
- `--avatar` / `-a` - Avatar ID (uses default if not specified)
- `--voice` - Voice ID for target language (uses default if not specified)
- `--output` / `-o` - Custom output directory
- `--no-detect` - Skip automatic source language detection
- `--verbose` / `-v` - Enable detailed logging

**Available Translation Styles:**

| Style | Best For | Characteristics |
|-------|----------|----------------|
| `casual` | Social media, informal content | Relaxed, friendly, colloquial |
| `conversational` | General videos, tutorials | Natural, engaging, personal |
| `business` | Corporate, professional content | Authoritative, clear, professional |
| `explainer` | Educational, how-to videos | Clear, patient, accessible |
| `formal` | Official communications | Sophisticated, respectful, dignified |
| `technical` | Technical documentation, demos | Precise, accurate, terminology-focused |

**Output:**
The translate command creates a timestamped directory containing:
- Original transcription (`.txt`)
- Translated script (`.txt`)
- Generated TTS audio (`.mp3`)
- Final translated video (`.mp4`)
- Translation manifest (`.json`) with all metadata

## Output Structure

Each batch creates a timestamped directory:

```
output/2025-10-31T14-30-45Z/
├── manifest.json          # Job status, URLs, errors
├── 001_tts.mp3           # TTS audio files
├── 001_video.mp4         # Final avatar videos
├── 002_tts.mp3
├── 002_video.mp4
└── pipeline.log          # Detailed execution log
```

### Manifest Format

```json
{
  "tag": "sunlife-pilot-batch-1",
  "timestamp": "2025-10-31T14:30:45Z",
  "results": [
    {
      "id": "001",
      "status": "ok",
      "tts_path": "output/2025-10-31T14-30-45Z/001_tts.mp3",
      "video_path": "output/2025-10-31T14-30-45Z/001_video.mp4",
      "meta": {
        "video_url": "https://heygen.com/v/abc123",
        "duration_sec": 42.5,
        "cost_usd": 0.15
      }
    },
    {
      "id": "002",
      "status": "error",
      "error": "Rate limit exceeded, retry after 60s"
    }
  ]
}
```

## Vendor Notes

### HeyGen
- **Rate limits:** 10 concurrent video generations, 100/hour
- **Video length:** Max 5 minutes per video
- **Polling:** Videos take 30-180 seconds to generate
- **Docs:** https://docs.heygen.com/reference/api-reference

### ElevenLabs
- **Rate limits:** Varies by plan (Free: 10k chars/month, Pro: 100k/month)
- **Voices:** 120+ multilingual voices available
- **Latency:** ~2-5 seconds for 30-second audio
- **Docs:** https://elevenlabs.io/docs

### OpenAI TTS (Alternative)
- **Voices:** alloy, echo, fable, onyx, nova, shimmer
- **Quality:** HD quality available (tts-1-hd model)
- **Cost:** $0.015/1K chars (standard), $0.030/1K chars (HD)

## Troubleshooting

### Rate Limit Errors

The toolkit automatically retries with exponential backoff. If you hit persistent rate limits:

1. Reduce `--concurrency` value
2. Use the `resume` command after waiting
3. Contact provider to increase limits

### Authentication Errors

```
Error: Invalid API key
```

Check your `.env` file and verify keys are active in provider dashboards.

### Template Rendering Errors

```
Error: 'product' is undefined
```

Ensure all variables referenced in templates exist in the CSV `variables` column.

### Memory Issues

For large batches (100+ videos), process in smaller chunks:

```bash
# Split CSV and run in batches
python -m amp_video.cli run data/input/batch_1.csv --tag "batch-1"
python -m amp_video.cli run data/input/batch_2.csv --tag "batch-2"
```

## Development

### Run Tests

```bash
make test              # Quick test run
make test-coverage     # With HTML coverage report
```

### Linting and Formatting

```bash
make lint              # Check code style
make format            # Auto-format code
```

### Add a New Provider

1. Create `src/amp_video/providers/new_provider.py`
2. Implement async methods: `synth()` or `create_video()`
3. Add configuration to `config.py`
4. Update `pipeline.py` to use new provider
5. Add tests in `tests/test_providers.py`

## Roadmap

### MVP ✓
- [x] CSV ingest and validation
- [x] Jinja2 templating
- [x] ElevenLabs TTS integration
- [x] HeyGen video generation
- [x] JSON manifest output
- [x] Basic CLI with render/run commands
- [x] **Video Translation Pipeline** 🆕
- [x] **Whisper Transcription** 🆕
- [x] **GPT-4 Style-Aware Translation** 🆕
- [x] **6 Translation Styles** 🆕
- [x] **ffmpeg Audio Extraction** 🆕

### In Progress
- [ ] S3 uploader with signed URLs
- [ ] Resumable batch processing for translations
- [ ] Language code mapping table
- [ ] Concurrency controls per provider
- [ ] Error taxonomy and classification
- [ ] Streamlit web UI for monitoring

### Backlog (High Value)
- [ ] Batch video translation (multiple videos at once)
- [ ] Subtitle generation and synchronization
- [ ] Voice cloning for consistency across languages
- [ ] Google Sheets / Airtable connectors
- [ ] Webhook notifications (Slack, Teams)
- [ ] Consent hash tracking for compliance
- [ ] SSML support for advanced TTS
- [ ] Pronunciation dictionaries
- [ ] Cost estimator per batch
- [ ] Analytics dashboard

## Architecture

```
┌─────────────────┐
│   CLI (Typer)   │
└────────┬────────┘
         │
         v
┌─────────────────┐     ┌──────────────┐
│     Pipeline    │────▶│   Storage    │
│   (Orchestrator)│     │ (Local / S3) │
└────────┬────────┘     └──────────────┘
         │
         ├──────────────┬─────────────┐
         v              v             v
    ┌────────┐    ┌─────────┐   ┌──────────┐
    │  TTS   │    │ Avatar  │   │ Template │
    │Provider│    │Provider │   │  Engine  │
    └────────┘    └─────────┘   └──────────┘
```

## License

MIT License - see LICENSE file for details.

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure `make lint` and `make test` pass
5. Submit a pull request

---

**Built with** Python 3.11+ • Typer • Pydantic • HeyGen • ElevenLabs
