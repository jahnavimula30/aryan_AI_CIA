"""AI Quiz Arena - DSC401-6 Artificial Intelligence (Units I & II)

Interactive Streamlit quiz with timer, scoring, hints, 50-50 lifeline, difficulty levels,
leaderboard, progress bar and a Gemini-powered AI Tutor / Study Planner.
"""
import copy
import os
import random
import sqlite3
import time
from contextlib import closing
from datetime import datetime

import pandas as pd
import streamlit as st

from questions import FIXED_ORDER_FORMATS, QUESTIONS, TOPICS, answer_text, normalize

st.set_page_config(page_title="AI Quiz Arena", page_icon="🧠", layout="centered")

# ───────────────────────── config ─────────────────────────
DB_PATH = os.getenv("LEADERBOARD_DB", "leaderboard.db")
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.7-flash")
BASE_POINTS = {"Easy": 10, "Medium": 15, "Hard": 20}
RANK = {"Easy": 0, "Medium": 1, "Hard": 2}
SPEED_BONUS = 5      # max extra points for answering quickly
HINT_PENALTY = 3
FIFTY_PENALTY = 5
PLACEHOLDER = "— select —"


# ───────────────────────── leaderboard (SQLite) ─────────────────────────
def _db():
    con = sqlite3.connect(DB_PATH)
    con.execute(
        "CREATE TABLE IF NOT EXISTS scores (name TEXT, score INTEGER, correct INTEGER, "
        "total INTEGER, level TEXT, taken_at TEXT)"
    )
    return con


def save_score(name, score, correct, total, level):
    with closing(_db()) as con:
        con.execute("INSERT INTO scores VALUES (?,?,?,?,?,?)",
                    (name, score, correct, total, level, datetime.now().strftime("%Y-%m-%d %H:%M")))
        con.commit()


def leaderboard_df(limit=10):
    with closing(_db()) as con:
        df = pd.read_sql_query(
            'SELECT name AS Player, score AS Score, correct || "/" || total AS Correct, '
            'level AS Level, taken_at AS "When" FROM scores '
            "ORDER BY score DESC, taken_at ASC LIMIT ?", con, params=(limit,))
    df.insert(0, "Rank", range(1, len(df) + 1))
    return df


# ───────────────────────── Gemini (AI tutor) ─────────────────────────
def get_api_key():
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not key:
        try:
            key = st.secrets.get("GEMINI_API_KEY")
        except Exception:
            key = None
    return key or st.session_state.get("user_key") or None


@st.cache_data(show_spinner=False, ttl=3600)
def _ask_gemini(prompt: str, system: str, api_key: str, max_tokens: int) -> str:
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=api_key)
    resp = client.models.generate_content(
        model=MODEL, contents=prompt,
        # extra headroom: some Gemini models spend output tokens on internal "thinking"
        config=types.GenerateContentConfig(system_instruction=system, max_output_tokens=max_tokens * 3))
    return resp.text or "⚠️ The AI returned an empty answer - please try again."


def ask_ai(prompt, system, max_tokens=400):
    key = get_api_key()
    if not key:
        return "⚠️ AI features are off: add a free Gemini API key (sidebar or GEMINI_API_KEY env variable)."
    try:
        return _ask_gemini(prompt, system, key, max_tokens)
    except Exception as e:  # network / auth / quota problems
        return f"⚠️ The AI request failed: {e}"


TUTOR_SYSTEM = (
    "You are a friendly AI tutor helping B.Sc. Data Science students learn Artificial Intelligence "
    "(Units I-II: agents, environments, search, heuristics, CSP, means-end analysis). "
    "Answer in at most 120 words, in simple language, with one short real-world analogy. "
    "No headings. If the student was wrong, name the likely misconception."
)


def tutor_prompt(q, user_ans_text):
    opts = ""
    if q["kind"] == "choice":
        opts = "Options: " + " | ".join(q["options"]) + "\n"
    code = f"\n{q['code']}\n" if q.get("code") else ""
    return (f"Topic: {q['topic']} ({q['fmt']})\nQuestion: {q['q']}{code}\n{opts}"
            f"Correct answer: {answer_text(q)}\nStudent's answer: {user_ans_text}\n"
            "Explain why the correct answer is right.")


# ───────────────────────── quiz logic ─────────────────────────
def build_quiz(level, n, topics):
    pool = [q for q in QUESTIONS
            if q["topic"] in topics and (level in ("Mixed", "Progressive") or q["diff"] == level)]
    random.shuffle(pool)
    quiz = []
    for q in pool[:n]:
        q = copy.deepcopy(q)
        if q["kind"] == "choice" and q["fmt"] not in FIXED_ORDER_FORMATS:
            correct = q["options"][q["answer"]]
            random.shuffle(q["options"])
            q["answer"] = q["options"].index(correct)
        if q["kind"] == "match":
            q["right_opts"] = [r for _, r in q["pairs"]]
            random.shuffle(q["right_opts"])
        quiz.append(q)
    if level == "Progressive":
        quiz.sort(key=lambda q: RANK[q["diff"]])
    return quiz


def new_question_state():
    st.session_state.cur = {"start": time.time(), "penalty": 0, "hint": False, "hidden": [], "tutor": None}
    st.session_state.phase = "ask"


def start_quiz(name, level, n, topics, secs):
    quiz = build_quiz(level, n, topics)
    if not quiz:
        return False
    st.session_state.update(stage="quiz", quiz=quiz, i=0, score=0, streak=0, best_streak=0, log=[],
                            limit=secs, hints_left=5, fifty_left=2, saved=False, player=name.strip(),
                            level=level, plan=None)
    new_question_state()
    return True


def is_correct(q, ans):
    if ans is None:
        return False
    if q["kind"] == "choice":
        return ans == q["answer"]
    if q["kind"] == "text":
        return normalize(ans) in q["answer"]
    return all(ans.get(l) == r for l, r in q["pairs"])


def user_answer_text(q, ans):
    if ans is None:
        return "(no answer)"
    if q["kind"] == "choice":
        return q["options"][ans]
    if q["kind"] == "match":
        return "; ".join(f"{l} → {r}" for l, r in ans.items())
    return str(ans)


def finalize(ans=None, timed_out=False):
    s = st.session_state
    if s.phase != "ask":          # already answered / timed out
        return
    q, cur = s.quiz[s.i], s.cur
    elapsed = time.time() - cur["start"]
    ok = (not timed_out) and is_correct(q, ans)
    pts = 0
    if ok:
        bonus = round(SPEED_BONUS * max(0.0, 1 - elapsed / s.limit))
        pts = max(1, BASE_POINTS[q["diff"]] + bonus - cur["penalty"])
    s.score += pts
    s.streak = s.streak + 1 if ok else 0
    s.best_streak = max(s.best_streak, s.streak)
    s.log.append(dict(n=s.i + 1, topic=q["topic"], fmt=q["fmt"], diff=q["diff"], question=q["q"],
                      your_answer=user_answer_text(q, ans), correct_answer=answer_text(q),
                      correct=ok, points=pts, seconds=round(min(elapsed, s.limit), 1)))
    s.result = dict(correct=ok, pts=pts, timed_out=timed_out, ans=ans)
    s.phase = "feedback"


# ───────────────────────── callbacks ─────────────────────────
def use_hint():
    s = st.session_state
    if s.hints_left > 0 and not s.cur["hint"]:
        s.hints_left -= 1
        s.cur["hint"] = True
        s.cur["penalty"] += HINT_PENALTY


def use_fifty(i):
    s = st.session_state
    q = s.quiz[i]
    if s.fifty_left > 0 and not s.cur["hidden"] and q["kind"] == "choice" and len(q["options"]) >= 4:
        wrong = [k for k in range(len(q["options"])) if k != q["answer"]]
        s.cur["hidden"] = random.sample(wrong, 2)
        s.fifty_left -= 1
        s.cur["penalty"] += FIFTY_PENALTY
        s.pop(f"a_{i}", None)


# ───────────────────────── screens ─────────────────────────
def home_screen():
    st.title("🧠 AI Quiz Arena")
    st.caption("DSC401-6 · Artificial Intelligence · Units I & II")
    st.markdown("Test yourself on agents, environments, search, heuristics, CSP and more. "
                "Earn speed bonuses, use hints/50-50 lifelines and ask the **Gemini AI Tutor** when you're stuck.")
    name = st.text_input("Your name", key="name", placeholder="e.g. Aryan")
    c1, c2 = st.columns(2)
    level = c1.selectbox("Difficulty", ["Mixed", "Progressive", "Easy", "Medium", "Hard"],
                         help="Progressive = questions sorted from Easy to Hard.")
    secs = c2.slider("Seconds per question", 20, 120, 45, step=5)
    topics = st.multiselect("Topics", TOPICS, default=TOPICS)
    avail = sum(1 for q in QUESTIONS if q["topic"] in topics and (level in ("Mixed", "Progressive") or q["diff"] == level))
    if avail == 0:
        st.warning("No questions match these filters.")
    else:
        n = st.slider("Number of questions", 1, avail, min(10, avail)) if avail > 1 else 1
        st.caption(f"{avail} questions available with these filters.")
        if st.button("🚀 Start Quiz", type="primary", disabled=not name.strip()):
            if start_quiz(name, level, n, topics, secs):
                st.rerun()
        if not name.strip():
            st.caption("Enter your name to begin.")
    st.divider()
    st.subheader("🏆 Top players")
    lb = leaderboard_df(5)
    st.dataframe(lb, hide_index=True) if len(lb) else st.caption("No scores yet - be the first!")


@st.fragment(run_every=1)
def timer_box(limit):
    s = st.session_state
    if s.get("phase") != "ask":
        return
    left = limit - (time.time() - s.cur["start"])
    if left <= 0:
        finalize(timed_out=True)
        st.rerun()
    st.progress(max(0.0, left / limit), text=f"⏱️ {int(left)}s left")


def read_answer(q, i):
    key = f"a_{i}"
    if q["kind"] == "choice":
        return st.session_state.get(key)
    if q["kind"] == "text":
        v = (st.session_state.get(key) or "").strip()
        return v or None
    ans = {l: st.session_state.get(f"{key}_{j}") for j, (l, _) in enumerate(q["pairs"])}
    return None if any(v in (None, PLACEHOLDER) for v in ans.values()) else ans


def ask_ui(q, i):
    s = st.session_state
    key = f"a_{i}"
    if q["kind"] == "choice":
        visible = [k for k in range(len(q["options"])) if k not in s.cur["hidden"]]
        st.radio("Select one:", visible, format_func=lambda k: q["options"][k], index=None, key=key)
    elif q["kind"] == "text":
        st.text_input("Your answer:", key=key, placeholder="Type your answer…")
    else:
        for j, (left, _) in enumerate(q["pairs"]):
            st.selectbox(left, [PLACEHOLDER] + q["right_opts"], key=f"{key}_{j}")

    if s.cur["hint"]:
        st.info(f"💡 **Hint:** {q['hint']}")
    b1, b2, b3 = st.columns(3)
    b1.button(f"💡 Hint (−{HINT_PENALTY})", on_click=use_hint, key=f"hint_{i}",
              disabled=s.hints_left == 0 or s.cur["hint"])
    can_fifty = q["kind"] == "choice" and len(q["options"]) >= 4 and s.fifty_left > 0 and not s.cur["hidden"]
    b2.button(f"✂️ 50-50 (−{FIFTY_PENALTY})", on_click=use_fifty, args=(i,), key=f"fifty_{i}", disabled=not can_fifty)
    if b3.button("✅ Submit", type="primary", key=f"sub_{i}"):
        ans = read_answer(q, i)
        if ans is None:
            st.warning("Please answer the question first.")
        else:
            finalize(ans)
            st.rerun()


def feedback_ui(q, i):
    s = st.session_state
    r = s.result
    if r["timed_out"]:
        st.warning("⌛ Time's up! No points for this question.")
    elif r["correct"]:
        st.success(f"✅ Correct! +{r['pts']} points")
    else:
        st.error("❌ Not quite.")
    if q["kind"] == "match":
        rows = []
        for l, right in q["pairs"]:
            mine = (r["ans"] or {}).get(l, "—")
            rows.append({"Item": l, "Your match": mine, "Correct match": right, "": "✓" if mine == right else "✗"})
        st.dataframe(pd.DataFrame(rows), hide_index=True)
    else:
        st.markdown(f"**Correct answer:** {answer_text(q)}")
    st.info(f"💬 {q['expl']}")

    c1, c2 = st.columns(2)
    if c1.button("🤖 Ask AI Tutor", key=f"tutor_{i}"):
        with st.spinner("Gemini is thinking…"):
            s.cur["tutor"] = ask_ai(tutor_prompt(q, user_answer_text(q, r["ans"])), TUTOR_SYSTEM)
    last = i == len(s.quiz) - 1
    if c2.button("🏁 Finish" if last else "Next ➡️", type="primary", key=f"next_{i}"):
        if last:
            s.stage = "result"
        else:
            s.i += 1
            new_question_state()
        st.rerun()
    if s.cur.get("tutor"):
        with st.chat_message("assistant"):
            st.markdown(s.cur["tutor"])


def quiz_screen():
    s = st.session_state
    q, i = s.quiz[s.i], s.i
    st.progress(i / len(s.quiz), text=f"Question {i + 1} of {len(s.quiz)}")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Score", s.score)
    m2.metric("🔥 Streak", s.streak)
    m3.metric("💡 Hints", s.hints_left)
    m4.metric("✂️ 50-50", s.fifty_left)
    tags = " · 🌍 Real-world" if "real_world" in q["tags"] else ""
    tags += " · 🔎 Search" if "search" in q["tags"] else ""
    st.caption(f"📂 {q['topic']} · 🧩 {q['fmt']} · 🎚️ {q['diff']}{tags}")
    if s.phase == "ask":
        timer_box(s.limit)
    st.markdown(f"**Q{i + 1}.** {q['q']}")
    if q.get("code"):
        st.code(q["code"], language="text")
    ask_ui(q, i) if s.phase == "ask" else feedback_ui(q, i)


def result_screen():
    s = st.session_state
    df = pd.DataFrame(s.log)
    total, correct = len(df), int(df["correct"].sum())
    acc = round(100 * correct / total)
    if not s.saved:
        save_score(s.player, s.score, correct, total, s.level)
        s.saved = True
        if acc >= 70:
            st.balloons()
    st.title("🎉 Quiz complete!")
    st.subheader(f"{s.player}, you scored {s.score} points")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Accuracy", f"{acc}%")
    c2.metric("Correct", f"{correct}/{total}")
    c3.metric("Best streak", s.best_streak)
    c4.metric("Avg time", f"{df['seconds'].mean():.0f}s")
    st.write("🏅 **Outstanding!**" if acc >= 85 else "👍 **Good work!**" if acc >= 60 else "📚 **Keep practising - you'll get there!**")

    st.markdown("#### Topic-wise accuracy (%)")
    by_topic = df.groupby("topic")["correct"].mean().mul(100).round(0)
    st.bar_chart(by_topic)

    st.markdown("#### 🤖 AI Study Plan")
    if st.button("Generate my personalised study plan"):
        weak = df[~df["correct"]]
        if weak.empty:
            s.plan = "You answered everything correctly - try the Hard level or all topics for a bigger challenge!"
        else:
            summary = "\n".join(f"- [{r.topic}] {r.question[:120]!r} (you: {r.your_answer[:60]}; correct: {r.correct_answer[:60]})"
                                for r in weak.itertuples())
            prompt = (f"A student scored {acc}% on an AI quiz. Questions they got wrong:\n{summary}\n\n"
                      "Create a short study plan: 4-5 bullet points naming the topics to revise and one concrete "
                      "exercise for each. Maximum 150 words.")
            with st.spinner("Gemini is preparing your plan…"):
                s.plan = ask_ai(prompt, TUTOR_SYSTEM, max_tokens=500)
    if s.get("plan"):
        with st.chat_message("assistant"):
            st.markdown(s.plan)

    with st.expander("📋 Review all questions"):
        for r in s.log:
            st.markdown(f"**{'✅' if r['correct'] else '❌'} Q{r['n']} ({r['topic']}, {r['diff']})** — +{r['points']} pts")
            st.markdown(r["question"])
            st.caption(f"Your answer: {r['your_answer']}  |  Correct: {r['correct_answer']}")
            st.divider()

    st.subheader("🏆 Leaderboard")
    st.dataframe(leaderboard_df(10), hide_index=True)
    if st.button("🔁 Play again", type="primary"):
        s.stage = "home"
        st.rerun()


def leaderboard_page():
    st.title("🏆 Leaderboard")
    lb = leaderboard_df(25)
    st.dataframe(lb, hide_index=True) if len(lb) else st.info("No scores yet.")


def bank_page():
    st.title("📚 Question Bank")
    rows = []
    for q in QUESTIONS:
        rows.append({
            "ID": q["id"], "Topic": q["topic"], "Format": q["fmt"], "Difficulty": q["diff"],
            "Question": q["q"].replace("\n\n", " ") + (f"\n{q['code']}" if q.get("code") else ""),
            "Options / Pairs": " | ".join(q["options"]) if q["kind"] == "choice"
            else " | ".join(f"{l} -> {r}" for l, r in q["pairs"]) if q["kind"] == "match" else "(type the answer)",
            "Correct Answer": answer_text(q), "Explanation": q["expl"],
            "Real-world": "real_world" in q["tags"], "Search/State-space": "search" in q["tags"],
        })
    df = pd.DataFrame(rows)
    c1, c2, c3 = st.columns(3)
    c1.metric("Total questions", len(df))
    c2.metric("Real-world", int(df["Real-world"].sum()))
    c3.metric("Search / state-space", int(df["Search/State-space"].sum()))
    st.write("**By format:**", ", ".join(f"{k}: {v}" for k, v in df["Format"].value_counts().items()))
    fmts = st.multiselect("Filter by format", sorted(df["Format"].unique()))
    view = df[df["Format"].isin(fmts)] if fmts else df
    st.dataframe(view, hide_index=True)
    st.download_button("⬇️ Download question bank (CSV)", df.to_csv(index=False).encode("utf-8-sig"),
                       "question_bank.csv", "text/csv")


# ───────────────────────── router ─────────────────────────
st.session_state.setdefault("stage", "home")
page = st.sidebar.radio("Menu", ["🎮 Play", "🏆 Leaderboard", "📚 Question Bank"])
st.sidebar.divider()
if not (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")):
    st.sidebar.text_input("Gemini API key (for AI Tutor)", type="password", key="user_key",
                          help="Optional. Needed only for the 🤖 AI Tutor and Study Plan.")
st.sidebar.caption(f"AI model: `{MODEL}`")

if page == "🎮 Play":
    {"home": home_screen, "quiz": quiz_screen, "result": result_screen}[st.session_state.stage]()
elif page == "🏆 Leaderboard":
    leaderboard_page()
else:
    bank_page()
