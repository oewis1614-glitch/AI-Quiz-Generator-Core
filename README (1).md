# 🦷 Dentor — AI Quiz Generator Module

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Mistral](https://img.shields.io/badge/Mistral--7B-Instruct_v0.2-FF6B35?style=for-the-badge&logo=huggingface&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-2.x-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)
![Colab](https://img.shields.io/badge/Google_Colab-Ready-F9AB00?style=for-the-badge&logo=googlecolab&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Graduation Project**

*An AI-powered exam generator that reads your lecture files and creates a full quiz — automatically.*

---

[📖 Overview](#-overview) · [🚀 Quick Start](#-quick-start) · [🧠 How It Works](#-how-it-works) · [📁 Structure](#-project-structure) · [⚙️ Configuration](#️-configuration) · [🛠 Troubleshooting](#-troubleshooting)

</div>

---

## 📖 Overview

The **AI Quiz Generator** is a standalone module within the [Dentor](https://github.com/) dental education platform. It allows instructors and students to:

- **Upload** any lecture file (PDF, DOCX, TXT)
- **Generate** a complete exam with multiple question types, difficulty levels, and page ranges — all powered by a **local** open-source LLM (no API key needed)
- **Answer** the generated quiz through an interactive interface
- **Get corrected instantly** with verdicts, correct answers, and explanations
- **Receive a detailed accuracy report** broken down by question type

### Supported Question Types

| Type | Description |
|---|---|
| `multiple-choice` | 4-option MCQ drawn from lecture content |
| `true-false` | Statement to evaluate as True or False |
| `short-answer` | Open-ended question with written response |
| `case-study` | Scenario-based multi-step question |
| `image-based` | Question anchored to a figure from the lecture |

### Difficulty Levels

| Level | Target | Context Size | Temperature |
|---|---|---|---|
| `beginner` | Year 1 students, recall questions | 1× | 0.60 |
| `intermediate` | Year 3, mechanisms & clinical application | 1.3× | 0.75 |
| `advanced` | Final year, case-based critical thinking | 1.8× | 0.90 |

---

## 🚀 Quick Start

### Option A — Google Colab (Recommended)

1. Open the notebook in Colab:

   [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YOUR_USERNAME/ai-quiz-generator/blob/main/notebooks/quiz_generator.ipynb)

2. Set the runtime to **GPU** (Runtime → Change runtime type → T4 GPU)

3. Run all cells in order — the notebook is fully self-contained

### Option B — Local Setup

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/ai-quiz-generator.git
cd ai-quiz-generator

# Install dependencies
pip install -r requirements.txt

# Launch the notebook
jupyter notebook notebooks/quiz_generator.ipynb
```

> ⚠️ **GPU strongly recommended.** The model (Mistral-7B) runs on CPU as a fallback but is significantly slower. A GPU with ≥ 8 GB VRAM is ideal.

---

## 🧠 How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                        PIPELINE OVERVIEW                        │
├──────────────┬──────────────┬──────────────┬────────────────────┤
│  1. UPLOAD   │ 2. CONFIGURE │  3. GENERATE │    4. CORRECT      │
│              │              │              │                    │
│  PDF / DOCX  │  Difficulty  │  Mistral-7B  │  Mistral-7B        │
│  TXT / MD    │  # Questions │  builds each │  reads lecture +   │
│              │  Page range  │  question    │  student answer →  │
│  ↓ Extract   │  Types       │  from a      │  VERDICT +         │
│  Text +      │  Per-type    │  lecture     │  Explanation       │
│  Images      │  count       │  chunk       │                    │
└──────────────┴──────────────┴──────────────┴────────────────────┘
                                      ↓
                          ┌───────────────────────┐
                          │   ACCURACY REPORT      │
                          │  Overall %  + Grade    │
                          │  Breakdown by type     │
                          └───────────────────────┘
```

### Key Components

**`src/extractor.py`** — Reads PDF/DOCX/TXT files, extracts full text and filters meaningful images from PDF pages using pixel variance and color-count thresholds (avoids blank pages, covers, title slides).

**`src/generator.py`** — Builds Mistral-formatted `[INST]...[/INST]` prompts per question type and difficulty, runs inference, then retries (up to 4×) if output fails validation.

**`src/cleaner.py`** — Strips leftover prompt artifacts, LaTeX math, base64 image blobs, and leaked answer lines from the model output using regex pipelines.

**`src/corrector.py`** — Re-uses the same Mistral model as an examiner: feeds lecture context + question + student answer, parses `VERDICT: CORRECT/INCORRECT` with typo-tolerant regex.

**`src/ui.py`** — Full `ipywidgets` control panel and answer sheet UI (sliders, dropdowns, toggle buttons, live output).

---

## 📁 Project Structure

```
ai-quiz-generator/
│
├── 📓 notebooks/
│   └── quiz_generator.ipynb      ← Main runnable notebook (Colab-ready)
│
├── 🐍 src/
│   ├── __init__.py
│   ├── extractor.py              ← PDF/DOCX/TXT text & image extraction
│   ├── generator.py              ← Question generation (Mistral prompts + inference)
│   ├── cleaner.py                ← Post-processing & output cleaning
│   ├── corrector.py              ← Automatic answer correction
│   └── ui.py                     ← ipywidgets Control Panel + Answer Sheet
│
├── 📚 docs/
│   ├── architecture.md           ← System design deep-dive
│   └── prompt_guide.md           ← Prompt engineering decisions
│
├── 🖼️  assets/
│   └── demo/                     ← Screenshots / demo GIFs
│
├── 🔧 scripts/
│   └── save_model_to_drive.py    ← Optional: cache model weights to Google Drive
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## ⚙️ Configuration

All settings are controlled through the **interactive Control Panel** (Cell 4 in the notebook). No code changes needed.

| Setting | Default | Description |
|---|---|---|
| Difficulty | `intermediate` | `beginner` / `intermediate` / `advanced` |
| Total Questions | `10` | 1–50 |
| Lecture Range | `1–10` | Page range to draw content from |
| Question Types | `multiple-choice` | Multi-select; set per-type count |
| Context / Question | `1800 chars` | Text fed to model per question (600–4000) |

### Model Parameters (in `generator.py`)

```python
# Controlled per difficulty level:
temperature        = 0.60 / 0.75 / 0.90
top_k              = 50
top_p              = 0.92
repetition_penalty = 1.3
max_new_tokens     = 250          # generation
max_new_tokens     = 300          # correction
```

---

## 🛠 Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| Model loads very slowly | No GPU / running on CPU | Switch Colab runtime to GPU (T4) |
| `CUDA out of memory` | VRAM too small | Reduce `max_new_tokens` or use Colab Pro |
| Questions repeat same content | Context chunk too large | Lower "Context / Q" slider to 1000–1200 |
| Generated question has LaTeX symbols | Model ignored format instruction | Already handled by `cleaner.py`; if persists, lower temperature |
| Correction always returns INCORRECT | Model misread options | Check that question options were parsed correctly (short-answer edge case) |
| `SETTINGS_CONFIRMED` error | Skipped Control Panel cell | Run Cell 4 and click ✅ Confirm Settings before Cell 7 |
| Cell 14 / 15 show no output | Not run yet | Run those cells manually to test correction & Drive caching |

---

## 📦 Requirements

```
torch>=2.0
transformers>=4.40
accelerate>=0.29
bitsandbytes>=0.43
PyMuPDF>=1.24
python-docx>=1.1
Pillow>=10.0
numpy>=1.26
ipywidgets>=8.1
```

Install all at once:
```bash
pip install -r requirements.txt
```

---

## 🔗 Related

- **Dentor Web App** → [github.com/YOUR_ORG/dentor-web](https://github.com/)
- **Dentor Backend API** → [github.com/YOUR_ORG/dentor-api](https://github.com/)
- **Mistral-7B-Instruct-v0.2** → [huggingface.co/mistralai/Mistral-7B-Instruct-v0.2](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2)

---

## 👥 Team

> Dentor Graduation Project — Faculty of Dentistry

| Name | Role |
|---|---|
| — | AI / ML Module |
| — | Frontend (Web App) |
| — | Backend / API |
| — | System Design |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
  <sub>Built with ❤️ as part of the Dentor dental education platform</sub>
</div>
