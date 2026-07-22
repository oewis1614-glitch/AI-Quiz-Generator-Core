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




<div align="center">
  <sub>Built with ❤️ as part of the Dentor dental education platform</sub>
</div>
