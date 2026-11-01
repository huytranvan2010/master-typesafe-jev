"""
Install:
    uv pip install typesafe-sdk==0.7.5 python-dotenv==1.2.4
"""

import os
from dotenv import load_dotenv
from typesafe_sdk import Choice, TypeSafeClient

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

# State: an object with descriptive field names (recommended by the docs).
issue = {
    "title": "Login page hangs after upgrading to v3.2",
    "body": "Since v3.2 the login button spins forever. The API returns 200 but the page never redirects. Console shows 'Cannot read properties of undefined (reading token)'.",
    "labels": [],
}

with TypeSafeClient() as client:
    response = client.system_one(
        model=JEV_MODEL,
        state=issue,
        questions={
            # Choice 1: full option list, plus an "other" fallback.
            "component": Choice(
                instructions="Which part of the codebase most likely needs a fix?",
                criteria={
                    "frontend": "UI, browser code, client-side state.",
                    "backend": "API handlers and business logic.",
                    "database": "Queries, migrations, data storage.",
                    "infra": "Build, deploy, servers, CI/CD.",
                    "other": None,  # null description: the name is clear enough
                },
            ),
            # Choice 2: structured criteria to separate confusable options.
            # The key names (what, not_for, examples) are free-form.
            "issue_type": Choice(
                instructions="What kind of issue is this?",
                criteria={
                    "bug": {
                        "what": "Existing behavior is broken or wrong.",
                        "not_for": "Requests for behavior that never existed.",
                        "examples": ["Button does nothing", "Crash on save"],
                    },
                    "feature": {
                        "what": "A request for new behavior.",
                        "not_for": "Something that used to work and stopped.",
                        "examples": ["Add dark mode", "Support SSO"],
                    },
                    "question": "The author is asking how something works.",
                },
            ),
        },
    )

component = response.answers["component"]
issue_type = response.answers["issue_type"]

# Every Choice answer has: choice, probabilities, confidence.
print("component  :", component.choice, f"(confidence {component.confidence:.2f})")
print("probabilities:", component.probabilities)
print("issue_type :", issue_type.choice, f"(confidence {issue_type.confidence:.2f})")

# Branch on the numbers, not only on the top choice.
# Thresholds follow the docs' triage example; tune them on your own data.
if component.confidence < 0.3:
    print("-> Unclear component: send to manual triage")
else:
    print(f"-> Assign to the {component.choice} team")
    for team, p in component.probabilities.items():
        if team != component.choice and p > 0.25:
            print(f"-> Also notify the {team} team (p={p:.2f})")

if issue_type.choice == "bug":
    print("-> Add label: bug")