# 🧠 AI Quiz Arena – DSC401-6 (Units I & II)

Streamlit quiz game with 74 questions, timer, scoring, hints, 50-50 lifeline, difficulty levels,
leaderboard and a **Gemini-powered AI Tutor + Study Planner**.

## Files
| File | Purpose |
|---|---|
| `app.py` | Streamlit app (UI, scoring, timer, leaderboard, Gemini calls) |
| `questions.py` | Question bank with correct answers, hints, explanations |
| `requirements.txt` | streamlit, google-genai, pandas |
| `render.yaml` | Render Blueprint (optional) |

## Run locally
```bash
pip install -r requirements.txt
export GEMINI_API_KEY=your-key      # Windows PowerShell: $env:GEMINI_API_KEY="your-key"
streamlit run app.py
```

## Deploy on Render
1. Push this folder to a GitHub repo (files at the repo root).
2. Render dashboard → **New → Web Service** → connect the repo (or **New → Blueprint** to use `render.yaml`).
3. Settings (if not using the Blueprint):
   - Runtime: **Python 3**
   - Build command: `pip install -r requirements.txt`
   - Start command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`
4. Environment variables: `GEMINI_API_KEY` (free key from https://aistudio.google.com/apikey), `PYTHON_VERSION=3.11.9`, optional `GEMINI_MODEL`.
5. Deploy and open the `onrender.com` URL.

Notes: the free plan sleeps after inactivity (first load can take ~1 min) and its disk is wiped on
redeploy, so the SQLite leaderboard resets. Attach a Render Disk and set `LEADERBOARD_DB=/data/leaderboard.db`
if you need it to persist. Open the app once before your class demo to wake it up.

## Report outline (submit with screenshots)
1. **Tool used:** Python + Streamlit, deployed on Render; Google Gemini API for AI features.
2. **Question bank:** 74 questions covering all prescribed topics; formats: MCQ, True/False, Assertion-Reason,
   Fill in the Blanks, Match the Following, Scenario-based, Problem-Solving; 12 real-world, 10 search/state-space.
   Download the CSV from the **Question Bank** page of the app.
3. **Game design:** random sampling and shuffled options, Easy/Medium/Hard/Mixed/Progressive levels, per-question
   countdown, score = base points (10/15/20) + speed bonus (≤5) − hint (3) / 50-50 (5) penalties, streak counter,
   progress bar, instant feedback with explanation, final score, topic-wise chart, leaderboard.
4. **AI integration:** 🤖 AI Tutor explains each answer (and the likely misconception); 🤖 Study Planner builds a
   revision plan from the questions you missed.
5. **Screenshots:** home, a question with timer, feedback + AI tutor, results, leaderboard, question bank.
