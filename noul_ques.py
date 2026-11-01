"""
Install:
    uv pip install typesafe-sdk==0.7.5 python-dotenv==1.2.4
"""

import os
from dotenv import load_dotenv
from typesafe_sdk import Noul, TypeSafeClient, NoulCriteria

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

# State: the pull request to check.
pull_request = {
    "title": "Speed up login by caching user sessions",
    "description": "Adds an in-memory session cache. Tests will come in a follow-up PR.",
    "diff_summary": (
        "auth/session.py: new SessionCache class\n"
        "config.py: SESSION_SECRET = 'sk_live_9f8a7b6c5d4e'\n"
        "api/login.py: login() now returns cached sessions"
    ),
}

# One condition per Noul, phrased so that a high value means "yes".
CHECKLIST = {
    "touches_auth": Noul(
        instructions="Does this change touch authentication or session handling?",
    ),
    "has_hardcoded_secret": Noul(
        instructions="Does the diff add a hardcoded secret, API key or password?",
        # Optional criteria: make the yes/no boundary explicit.
        criteria=NoulCriteria(
            true="A real-looking key, token or password appears as a literal value",
            false="Secrets are read from environment variables or a secret manager",
        ),
    ),
    "includes_tests": Noul(
        instructions="Does this pull request add or update tests?",
    ),
}

# Starting thresholds suggested by the docs. Tune them on your own data.
YES, NO = 0.7, 0.3


def verdict(p: float) -> str:
    """Map one Noul probability to yes / no / unsure."""
    if p >= YES:
        return "yes"
    if p <= NO:
        return "no"
    return "unsure"   # the middle band is NOT a no


with TypeSafeClient() as client:
    response = client.system_one(model=JEV_MODEL, state=pull_request, questions=CHECKLIST)

print("served by:", response.model)

# A Noul answer has a single field: .noul (probability of "yes").
# There is no .confidence and no .probabilities, unlike Choice and Score.
results = {}
for name, answer in response.answers.items():
    results[name] = verdict(answer.noul)
    print(f"{name:22} noul={answer.noul:.2f} -> {results[name]}")

print("====================")
print(results)
print("====================")

# The code decides what the combination means.
if results["has_hardcoded_secret"] == "yes":
    print("\n-> Block the merge: remove the secret and rotate it")
elif "unsure" in results.values():
    print("\n-> Ask a human reviewer: at least one check is unclear")
elif results["touches_auth"] == "yes" and results["includes_tests"] != "yes":
    print("\n-> Request changes: auth code changed without tests")
else:
    print("\n-> Checks passed: normal review")

print("====================")
print(response.answers)
print("====================")
