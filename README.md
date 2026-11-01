<div align="center">

# 🧠 Master TypeSafe Jev AI

### Fast and Low-Cost AI Decision Models

Companion code for the Udemy course **"Master TypeSafe Jev AI: Fast and Low-Cost AI Decision Models"**

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![TypeSafe SDK](https://img.shields.io/badge/typesafe--sdk-0.7.5-6C47FF)
![Model](https://img.shields.io/badge/model-jev--latest-00C2A8)
![Course](https://img.shields.io/badge/Udemy-Course-A435F0?logo=udemy&logoColor=white)

</div>

---

## 📖 About

Instead of asking an LLM to write free-form text and then parsing it, **TypeSafe Jev** answers your questions with **typed, numeric results**: a choice with probabilities, a score, or a yes/no probability. You get fast, cheap and *branchable* decisions you can plug straight into `if` statements.

This repo contains:

- 3 small scripts, one for each **TypeSafe AI primitive**
- 1 **milestone project** that puts them to work

## 🧩 The 3 Primitives

| Script | Primitive | What it returns | Example use |
|---|---|---|---|
| [choice_ques.py](choice_ques.py) | **`Choice`** | The best option + probability for every option + confidence | Route a GitHub issue to the right team |
| [score_ques.py](score_ques.py) | **`Score`** | A level on a low → high scale + probabilities + confidence | Rate severity and frustration of a bug report |
| [noul_ques.py](noul_ques.py) | **`Noul`** | One probability that the answer is "yes" | Run a yes/no checklist on a pull request |

## 🚀 Milestone Project: Ticket Router

📁 [route_tickets/](route_tickets/)

A customer-support ticket router. It reads departments from [rules.yaml](route_tickets/rules.yaml), asks Jev which department should handle a ticket, and sends the ticket to a human whenever the model is not confident enough (`min_probability`).

| File | Purpose |
|---|---|
| [triage.py](route_tickets/triage.py) | The router |
| [rules.yaml](route_tickets/rules.yaml) | Departments, their descriptions, and the confidence threshold |

## ⚙️ Setup

### 1. Get the code

```bash
git clone <your-repo-url>
cd typesafe_course
```

### 2. Create a virtual environment and install dependencies

Python **3.12** is recommended. This guide uses [uv](https://github.com/astral-sh/uv):

```bash
uv python install 3.12
uv python pin 3.12
uv venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
uv pip install typesafe-sdk==0.7.5 python-dotenv==1.2.4 pyyaml==6.0.3
```

### 3. Create your `.env` file 🔑

Rename `.env.example` to `.env`:

```bash
# macOS / Linux
cp .env.example .env

# Windows (PowerShell)
Copy-Item .env.example .env
```

Then open `.env` and fill in **one** of the two options:

| Option | When to use | Variables |
|---|---|---|
| **A. TypeSafe directly** | You bought credits at [console.typesafe.ai](https://console.typesafe.ai) | `TYPESAFE_API_KEY` |
| **B. OpenRouter** | You bought credits at [openrouter.ai](https://openrouter.ai/settings/keys) | `OPENROUTER_API_KEY`, `OPENROUTER_BASE_URL` |

> ⚠️ **Never commit your `.env` file.** It contains your secret keys.

`JEV_MODEL` is optional. If you leave it empty, the scripts fall back to `jev-latest`.

## ▶️ Run the Examples

```bash
uv run python choice_ques.py     # Choice: route an issue to a team
uv run python score_ques.py      # Score:  rate severity & frustration
uv run python noul_ques.py       # Noul:   yes/no PR checklist
```

Then try the milestone project:

```bash
un run python route_tickets/triage.py
```

## 📂 Project Structure

```
typesafe_course/
├── choice_ques.py        # Primitive 1: Choice
├── score_ques.py         # Primitive 2: Score
├── noul_ques.py          # Primitive 3: Noul
├── route_tickets/        # 🚀 Milestone project
│   ├── triage.py
│   └── rules.yaml
├── .env.example          # Copy to .env and add your key
└── .python-version
```

## 💡 Tips

- Branch on the **numbers** (`confidence`, `probabilities`, `noul`), not only on the top answer.
- The thresholds in the examples are starting points. **Tune them on your own data.**
- The middle band of a `Noul` answer is *unsure*, not "no".

## 🙋 Questions?

Ask in the Q&A section of the course on Udemy.

<div align="center">

⭐ If this repo helps you, give it a star!

</div>
