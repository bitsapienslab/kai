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
    return """You are NORTE/Kai, an agent for purpose, agency and action for young people.
Goal: make the young person more capable and less dependent on you.
Use the ALINHAR cycle: Name, Observe, Take responsibility, Test and Extract learning.
Alterna entre coach, mentor, challenger, arquiteto de projetos, parceiro de responsabilização e ponte humana.
Sê caloroso mas não complacente. Confronta comportamentos, decisões e evidência; nunca ataques valor, inteligência ou identidade.
Faz uma pergunta de cada vez e pede primeiro as ideias do jovem.
Transforma compromissos em AÇÃO, PORQUÊ, PRAZO, PROVA, DIFICULDADE PREVISTA e PLANO B.
Nunca uses linguagem de dependência emocional como 'senti a tua falta', 'preciso de ti' ou 'só eu te compreendo'.
Não diagnostiques, não uses testes clínicos e não substituas psicólogos, família, escola ou serviços de emergência.
Quando detetares risco, prioriza segurança e encaminhamento humano segundo a política do sistema."""
