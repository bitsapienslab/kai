import re
from dataclasses import dataclass


@dataclass
class SafetyResult:
    level: str
    action: str
    response: str | None = None


CRISIS = re.compile(r"\b(suicid|suicide|kill myself|self.?harm|do not want to live|don't want to live)\b", re.I)
ABUSE = re.compile(r"\b(abuse|rape|violence at home|threat)\b", re.I)


def inspect_message(message: str) -> SafetyResult:
    if CRISIS.search(message):
        return SafetyResult("critical", "escalate", "I am sorry you are going through this. You do not have to handle it alone. If you are in immediate danger, call your local emergency number now. Contact a trusted adult and tell them exactly what is happening. I can help you prepare that message, but I cannot replace urgent human help.")
    if ABUSE.search(message):
        return SafetyResult("high", "human_review", "What you describe deserves support from a safe real person. If you are in immediate danger, call your local emergency number. Can you contact a trusted adult, teacher or support professional now?")
    return SafetyResult("none", "allow")

def safety_category(message: str) -> str:
    if CRISIS.search(message): return "crisis"
    if ABUSE.search(message): return "abuse_or_violence"
    return "general"


def kai_system_prompt() -> str:
    return """You are RISE/Kai, an agent for purpose, agency and action for young people.
Goal: make the young person more capable and less dependent on you.
Use the ALIGN cycle: Name, Observe, Take responsibility, Test and Extract learning.
Alternate between coach, mentor, challenger, project architect, accountability partner and human bridge.
Be warm but not indulgent. Challenge behaviors, decisions and evidence; never attack worth, intelligence or identity.
Ask one question at a time and ask for the young person's ideas first.
Turn commitments into ACTION, WHY, DEADLINE, PROOF, EXPECTED DIFFICULTY and PLAN B.
Never use emotional dependency language such as 'I missed you', 'I need you' or 'only I understand you'.
Do not diagnose, do not use clinical tests and do not replace psychologists, family, school or emergency services.
When you detect risk, prioritize safety and human escalation according to system policy."""
