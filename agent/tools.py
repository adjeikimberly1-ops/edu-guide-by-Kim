from langchain.tools import tool # type: ignore
from langchain_groq import ChatGroq # type: ignore
from langchain.prompts import PromptTemplate # type: ignore
from langchain_community.tools.tavily_search import TavilySearchResults # type: ignore
from dotenv import load_dotenv # type: ignore
import json
import os

from agent.database import (
    log_topic, log_quiz_score, log_roadmap, get_progress_summary
)

load_dotenv()

# ---------------------------------------------------------------------------
# Shared LLM instance used inside tools
# ---------------------------------------------------------------------------
def get_llm():
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.5,
        api_key=os.getenv("GROQ_API_KEY"),
    )


# ---------------------------------------------------------------------------
# TOOL 1 — Explain any concept in plain, simple language
# ---------------------------------------------------------------------------
@tool
def explain_concept_tool(concept: str) -> str:
    """
    Explains any educational concept in clear, simple, beginner-friendly language.
    Use this when the user wants to understand a topic or term.
    Input: a concept or topic name (e.g. 'photosynthesis', 'machine learning', 'compound interest')
    """
    llm = get_llm()

    prompt = PromptTemplate(
        input_variables=["concept"],
        template="""
You are a friendly and patient tutor explaining to a complete beginner.

Explain the concept of "{concept}" in a way that:
- Uses very simple, everyday language
- Gives 1-2 relatable real-world analogies
- Covers: what it is, why it matters, and one practical example
- Is concise but thorough (around 150-200 words)

Your explanation:
""",
    )

    chain = prompt | llm
    response = chain.invoke({"concept": concept})

    # 📊 Log to database
    log_topic(concept)

    return response.content


# ---------------------------------------------------------------------------
# TOOL 2 — Build a personalized learning roadmap
# ---------------------------------------------------------------------------
@tool
def roadmap_builder_tool(learning_goal: str) -> str:
    """
    Builds a structured, step-by-step learning roadmap for any learning goal.
    Use this when the user mentions a skill they want to learn or a goal they want to achieve.
    Input: the user's learning goal (e.g. 'learn Python for data science', 'understand personal finance')
    """
    llm = get_llm()

    prompt = PromptTemplate(
        input_variables=["goal"],
        template="""
You are an expert education coach building a personalized learning plan.

Create a clear, actionable learning roadmap for someone who wants to: "{goal}"

Structure the roadmap as follows:
1. Estimated total time to achieve this goal
2. 4-6 progressive learning stages (from beginner to confident)
   - For each stage: Stage name, key topics to cover, and estimated duration
3. One motivational tip to keep the learner on track

Keep it practical, encouraging, and realistic for a self-learner with limited time.
""",
    )

    chain = prompt | llm
    response = chain.invoke({"goal": learning_goal})

    # 📊 Log to database
    log_roadmap(learning_goal)

    return response.content


# ---------------------------------------------------------------------------
# TOOL 3 — Find free learning resources from the web
# ---------------------------------------------------------------------------
@tool
def resource_finder_tool(topic: str) -> str:
    """
    Searches the web for free, high-quality learning resources on any topic.
    Use this when the user asks for resources, courses, articles, videos, or
    where to learn something.
    Input: the topic or skill to find resources for (e.g. 'free Python tutorials',
    'learn SQL for beginners', 'machine learning courses')
    """
    search = TavilySearchResults(
        max_results=5,
        api_key=os.getenv("TAVILY_API_KEY"),
        search_depth="advanced",
        include_answer=True,
    )

    query = f"free learning resources for {topic} beginners"
    raw_results = search.invoke(query)

    llm = get_llm()

    results_text = "\n".join([
        f"- Title: {r.get('title', 'N/A')}\n  URL: {r.get('url', 'N/A')}\n  Summary: {r.get('content', 'N/A')[:200]}"
        for r in raw_results
    ])

    prompt = PromptTemplate(
        input_variables=["topic", "results"],
        template="""
You are a helpful education coach. Based on these web search results,
recommend the best free learning resources for someone wanting to learn "{topic}".

Search Results:
{results}

Format your response as:
1. A brief intro line
2. List the top 3-5 resources with:
   - Resource name
   - Why it's great for beginners
   - The link
3. A closing tip on how to get started

Be encouraging and practical.
""",
    )

    chain = prompt | llm
    response = chain.invoke({"topic": topic, "results": results_text})

    # 📊 Log to database
    log_topic(topic)

    return response.content


# ---------------------------------------------------------------------------
# TOOL 4 — Assess user knowledge level on a topic
# ---------------------------------------------------------------------------
@tool
def assess_knowledge_tool(topic: str) -> str:
    """
    Assesses the user's current knowledge level on a topic by asking
    3 quick diagnostic questions. Use this when the user wants to be assessed
    or tested on what they already know.
    Input: the topic to assess (e.g. 'Python', 'algebra', 'nutrition')
    """
    llm = get_llm()

    prompt = PromptTemplate(
        input_variables=["topic"],
        template="""
You are an adaptive education coach doing a quick knowledge assessment.

Generate exactly 3 diagnostic questions for the topic: "{topic}"

Rules:
- Question 1: Very basic (complete beginner level)
- Question 2: Intermediate (some exposure)
- Question 3: Advanced (confident practitioner)
- Mix question types: use a combination of True/False, Multiple Choice, and Short Answer
- For MCQ, provide 4 options labeled A, B, C, D
- For True/False, clearly label it as [True/False]
- For Short Answer, clearly label it as [Short Answer]

After the questions, add this note:
"💡 Answer these questions and I'll assess your level and generate a personalised quiz!"

Format cleanly with question numbers and clear labels.
""",
    )

    chain = prompt | llm
    response = chain.invoke({"topic": topic})

    # 📊 Log to database
    log_topic(topic)

    return response.content


# ---------------------------------------------------------------------------
# TOOL 5 — Generate adaptive quiz questions on any topic
# ---------------------------------------------------------------------------
@tool
def quiz_generator_tool(quiz_request: str) -> str:
    """
    Generates an adaptive quiz with mixed question types (MCQ, True/False, Short Answer)
    on any topic. Adapts difficulty based on any level context provided.
    Use this when the user asks to be quizzed, wants practice questions,
    or wants to test their knowledge on a topic.
    Input: topic and optional level, e.g. 'Python basics for beginner' or
    'machine learning intermediate' or just 'photosynthesis'
    """
    llm = get_llm()

    prompt = PromptTemplate(
        input_variables=["quiz_request"],
        template="""
You are an expert educator creating an adaptive quiz.

Create a 5-question quiz based on this request: "{quiz_request}"

Instructions:
- Infer the difficulty level from the request (default to beginner if unclear)
- Mix question types across the 5 questions:
    * At least 2 Multiple Choice Questions (MCQ) with options A, B, C, D
    * At least 1 True/False question — label with [True/False]
    * At least 1 Short Answer question — label with [Short Answer]
- Scale difficulty adaptively: beginner = simple recall, intermediate = applied,
  advanced = analytical
- After ALL questions, provide an "Answer Key" section with:
    * The correct answer for each question
    * A one-sentence explanation of why it's correct

Format the quiz cleanly with:
- A title line: "📝 Quiz: [Topic] — [Level] Level"
- Numbered questions
- Clear type labels
- Separated Answer Key at the bottom
""",
    )

    chain = prompt | llm
    response = chain.invoke({"quiz_request": quiz_request})

    # 📊 Log quiz topic to database (score logged separately when user reports it)
    topic = quiz_request.split()[0] if quiz_request else "general"
    log_topic(topic)

    return response.content


# ---------------------------------------------------------------------------
# TOOL 6 — Save quiz score (Phase 4)
# ---------------------------------------------------------------------------
@tool
def save_quiz_score_tool(score_data: str) -> str:
    """
    Saves the user's quiz score to the progress database.
    Use this when the user tells you their quiz score or how many they got right.
    Input: a string like 'topic=Python, score=4, total=5' or
    'I got 3 out of 5 on the SQL quiz'
    """
    llm = get_llm()

    # Use LLM to extract structured score data from natural language
    prompt = PromptTemplate(
        input_variables=["score_data"],
        template="""
Extract quiz score information from this text: "{score_data}"

Respond ONLY with a JSON object in this exact format (no extra text):
{{"topic": "topic name", "score": number, "total": number, "level": "beginner/intermediate/advanced/adaptive"}}

If level is not mentioned, use "adaptive".
If total is not mentioned, assume 5.
""",
    )

    chain = prompt | llm
    raw = chain.invoke({"score_data": score_data})

    try:
        clean = raw.content.strip().replace("```json", "").replace("```", "")
        data = json.loads(clean)
        log_quiz_score(
            topic=data.get("topic", "general"),
            score=int(data.get("score", 0)),
            total=int(data.get("total", 5)),
            level=data.get("level", "adaptive"),
        )
        pct = round((data["score"] / data["total"]) * 100)
        emoji = "🏆" if pct >= 80 else "👍" if pct >= 60 else "📚"
        return (
            f"{emoji} Score saved! You got **{data['score']}/{data['total']} ({pct}%)** "
            f"on **{data['topic']}**.\n\n"
            f"{'Excellent work! Keep it up! 🌟' if pct >= 80 else 'Good effort! Review the answer key and try again soon.' if pct >= 60 else 'Keep studying — every attempt makes you better! 💪'}"
        )
    except Exception:
        return "I couldn't parse the score. Try saying something like: 'I got 4 out of 5 on the Python quiz'"


# ---------------------------------------------------------------------------
# TOOL 7 — View progress summary (Phase 4)
# ---------------------------------------------------------------------------
@tool
def progress_tracker_tool(query: str) -> str:
    """
    Retrieves and summarises the user's full learning progress including
    topics studied, quiz scores, roadmaps generated, and learning streak.
    Use this when the user asks about their progress, history, scores,
    streak, or learning summary.
    Input: any progress-related query e.g. 'show my progress', 'how am I doing?',
    'what have I studied?', 'my learning streak'
    """
    summary = get_progress_summary()

    topics_list = ", ".join([t["topic"] for t in summary["topics"]]) or "None yet"
    roadmaps_list = ", ".join([r["goal"] for r in summary["roadmaps"]]) or "None yet"

    quiz_lines = ""
    if summary["quizzes"]:
        for q in summary["quizzes"]:
            pct = round((q["score"] / q["total"]) * 100) if q["total"] else 0
            quiz_lines += f"  • {q['topic'].title()}: {q['score']}/{q['total']} ({pct}%) — {q['level']}\n"
    else:
        quiz_lines = "  No quiz scores saved yet.\n"

    streak = summary["streak_days"]
    streak_msg = f"🔥 {streak} day streak!" if streak > 1 else "📅 Start your streak by learning something today!"

    return f"""
📊 **Your Learning Progress**

🔥 **Streak:** {streak_msg}

📚 **Topics Studied ({summary['total_topics']}):**
{topics_list}

🗺️ **Roadmaps Generated ({summary['total_roadmaps']}):**
{roadmaps_list}

📝 **Quiz Scores ({summary['total_quizzes']}):**
{quiz_lines}
💡 Keep going — consistency is the key to mastery!
"""


# ---------------------------------------------------------------------------
# Export all tools as a list for the agent
# ---------------------------------------------------------------------------
all_tools = [
    explain_concept_tool,
    roadmap_builder_tool,
    resource_finder_tool,
    assess_knowledge_tool,
    quiz_generator_tool,
    save_quiz_score_tool,
    progress_tracker_tool,
]