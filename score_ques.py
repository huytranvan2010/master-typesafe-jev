"""
Install:
    uv pip install typesafe-sdk==0.7.5 python-dotenv==1.2.4
"""

import os
from dotenv import load_dotenv
from typesafe_sdk import Score, TypeSafeClient

load_dotenv()


# Use the OpenRouter key if there is no TypeSafe key.
# The SDK reads TYPESAFE_API_KEY and TYPESAFE_BASE_URL from the environment.
if not os.getenv("TYPESAFE_API_KEY") and os.getenv("OPENROUTER_API_KEY"):
    os.environ["TYPESAFE_API_KEY"] = os.environ["OPENROUTER_API_KEY"]
    os.environ["TYPESAFE_BASE_URL"] = os.environ["OPENROUTER_BASE_URL"]


# Model name from .env. "jev-latest" works on both TypeSafe and OpenRouter
# (OpenRouter maps it to ~typesafe/jev-latest). "or" also covers JEV_MODEL= left empty.
JEV_MODEL = os.getenv("JEV_MODEL") or "jev-latest"
print("model:", JEV_MODEL)


# State: an object with descriptive field names.
report = {
    "title": "Checkout fails for some users after v2.3.1",
    "body": (
        "Since this morning about a third of users get a 500 error when they "
        "click Pay. Logs show 'connection pool exhausted'. We are losing orders. "
        "Please fix this NOW, this is the second time this month!!"
    ),
    "has_repro_steps": False,
    "has_logs": True,
}

# One Score per dimension. Levels go from low (index 0) to high,
# and each level describes a concrete situation, not a vague degree.
QUESTIONS = {
    "severity": Score(
        instructions="How severe is the reported issue?",
        criteria=[
            "Cosmetic; no impact to functionality",
            "Broken or degraded feature, but a workaround exists",
            "Blocking issue; no workaround exists",
            "Revenue or data is being lost right now",  # rare extreme gets its own level
        ],
    ),
    "frustration": Score(
        instructions="How frustrated does the reporter appear?",
        criteria=[
            "Calm, just stating facts",
            "Frustrated but civil",
            "Very angry, strong language or repeated complaints",
        ],
    ),
    "report_quality": Score(
        instructions="How actionable is this report for an engineer?",
        criteria=[
            "Vague; no details to start from",
            "Some details, such as error messages or logs, but no steps to reproduce",
            "Clear steps to reproduce, plus logs or error messages",
        ],
    ),
}

# Weights reflect what matters to your team. Example values; tune them.
WEIGHTS = {"severity": 0.6, "frustration": 0.25, "report_quality": 0.15}

with TypeSafeClient() as client:
    response = client.system_one(model=JEV_MODEL, state=report, questions=QUESTIONS)

print("served by:", response.model)
answers = response.answers

# 1. Read each Score: score, probabilities, legend, confidence.
for name in QUESTIONS:
    a = answers[name]
    top = max(a.legend)                    # top level number = len(criteria) - 1
    nearest = round(a.score)               # round when code needs one level
    print(f"\n{name}: score {a.score:.2f} / {top}  (confidence {a.confidence:.2f})")
    print(f"  nearest level {nearest}: {a.legend[nearest]}")
    print(f"  probabilities: {a.probabilities}")
    if a.confidence < 0.5:                 # example threshold
        print("  -> low confidence: levels may overlap or the report lacks detail")


# 2. Composite score: normalize each Score to 0..1, then apply weights.
def normalized(answer) -> float:
    return answer.score / max(answer.legend)


priority = sum(w * normalized(answers[name]) for name, w in WEIGHTS.items())
print(f"\npriority: {priority:.2f} (0 = lowest, 1 = highest)")

# 3. Act on thresholds in code. Example cut-offs; tune them on your own data.
if priority >= 0.7:
    print("-> Page the on-call engineer")
elif priority >= 0.4:
    print("-> Put it in the current sprint")
else:
    print("-> Add it to the backlog")

# A rare, high-stakes extreme gets its own check instead of relying on the average.
if answers["severity"].probabilities.get(3, 0) > 0.5:
    print("-> Revenue impact likely: notify the incident channel")