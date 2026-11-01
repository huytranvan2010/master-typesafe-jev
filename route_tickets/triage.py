

import os, yaml
from dotenv import load_dotenv
from typesafe_sdk import Choice, TypeSafeClient

load_dotenv("/Users/aicoding/Desktop/typesafe_course/.env")


# Use the OpenRouter key if there is no TypeSafe key.
# The SDK reads TYPESAFE_API_KEY and TYPESAFE_BASE_URL from the environment.
if not os.getenv("TYPESAFE_API_KEY") and os.getenv("OPENROUTER_API_KEY"):
    os.environ["TYPESAFE_API_KEY"] = os.environ["OPENROUTER_API_KEY"]
    os.environ["TYPESAFE_BASE_URL"] = os.environ["OPENROUTER_BASE_URL"]


# Model name from .env. "jev-latest" works on both TypeSafe and OpenRouter
# (OpenRouter maps it to ~typesafe/jev-latest). "or" also covers JEV_MODEL= left empty.
JEV_MODEL = os.getenv("JEV_MODEL") or "jev-latest"
print("model:", JEV_MODEL)

#NOTE: load yaml file
rules = yaml.safe_load(open("/Users/aicoding/Desktop/typesafe_course/route_tickets/rules.yaml"))
deparments = rules["departments"]
min_probality = rules["min_probability"]

print(f"Deparments: {deparments}")
print(f"Min prob: {min_probality}")

#NOTE: define the client
client = TypeSafeClient()

#NOTE: define a function that will process customer's ticket
def triage(ticket: str):
    # ask Typesafe Jev
    response = client.system_one(
        model=JEV_MODEL,
        state={"ticket": ticket},
        questions={
            "deparment": Choice(
                instructions="Which deparment should handle this ticket?",
                criteria=deparments
            )
        }
    )

    print("================")
    print(response)
    print("================")

    answer = response.answers["deparment"]
    probability = answer.probabilities[answer.choice]   # highest probalibity

    #NOTE: route to the correspond deparment
    route = answer.choice   # deparment name or other
    if answer.choice == "other" or probability < min_probality:
        route = "Human_review"

    print(f"Deparment: {answer.choice}  probability = {probability}")
    print(f"Route to {route}")  # the final answer


if __name__ == "__main__":
    ticket = "What is the weather today?"

    triage(ticket=ticket)