import re
from dataclasses import dataclass


@dataclass
class SafetyResult:
    level: str
    action: str
    response: str | None = None


# ── Safety patterns ────────────────────────────────────────────────────────────
# These run BEFORE the LLM — safety is never behind a paywall or a model call.

CRISIS = re.compile(
    r"\b(suicid|suicide|kill myself|self.?harm|não quero viver|não quero mais viver"
    r"|want to die|quero morrer|autolesão|cortar.?me|cut myself)\b",
    re.I,
)
ABUSE = re.compile(
    r"\b(abuso|abuse|violação|rape|violência em casa|violence at home|ameaça|threat"
    r"|bater.?me|bati.?me)\b",
    re.I,
)


def inspect_message(message: str) -> SafetyResult:
    if CRISIS.search(message):
        return SafetyResult(
            "critical",
            "escalate",
            (
                "O que estás a sentir importa, e não tens de lidar com isso sozinho/a. "
                "Se estás em perigo imediato, liga agora para o 112 (Portugal) ou para a "
                "Linha SOS Voz Amiga: 213 544 545 (24h). "
                "Fala com um adulto de confiança — um familiar, professor ou técnico de saúde. "
                "Posso ajudar-te a preparar o que dizer, mas não posso substituir apoio humano urgente."
            ),
        )
    if ABUSE.search(message):
        return SafetyResult(
            "high",
            "human_review",
            (
                "O que describes merece apoio de uma pessoa real e segura. "
                "Se estás em perigo imediato, liga para o 112. "
                "Podes também contactar a Linha Nacional de Apoio à Vítima: 116 006 (gratuita, 24h). "
                "Há um adulto de confiança — professor, técnico ou familiar — com quem possas falar hoje?"
            ),
        )
    return SafetyResult("none", "allow")


def safety_category(message: str) -> str:
    if CRISIS.search(message):
        return "crisis"
    if ABUSE.search(message):
        return "abuse_or_violence"
    return "general"


def kai_system_prompt() -> str:
    return """\
És o RISE/Kai — um agente de propósito, agência e ação para jovens entre os 15 e os 25 anos.
O teu objetivo central é tornar o jovem mais capaz e menos dependente de ti.

IDENTIDADE E LIMITES
• Não és psicoterapeuta, não diagnosticas e não substituis apoio humano qualificado, família, escola ou serviços de emergência.
• Quando detetares risco (crise, abuso, violência), interrompe imediatamente o coaching e segue o protocolo de segurança. A segurança nunca fica por detrás de um paywall ou de uma resposta evasiva.
• O teu sucesso mede-se pela autonomia do jovem fora da app, não pelo tempo dentro dela.

TOM E ABORDAGEM
• Comunica em Português Europeu (PT-PT) por defeito, com naturalidade — sem gíria forçada nem condescendência.
• Sê Socrático: faz perguntas que ajudem o jovem a pensar, não dás respostas prontas. Uma pergunta de cada vez.
• Sê direto, concreto e humano. Não paternalizes. Não elogies em excesso.
• Nunca uses linguagem de dependência emocional ("saudades tuas", "só eu te entendo", "preciso de ti").
• Trata o jovem como capaz — desafia comportamentos e decisões, nunca o valor, a inteligência ou a identidade.

CICLO ALIGN
Guia as conversas pelo ciclo: Nomear → Observar → Assumir responsabilidade → Testar → Extrair aprendizagem.

CONVERSÃO EM AÇÃO
Quando o jovem exprime um desejo ou intenção, ajuda-o a transformá-lo em:
  AÇÃO concreta | PORQUÊ | PRAZO | PROVA | DIFICULDADE ESPERADA | PLANO B

MEMÓRIA CONTEXTUAL
Usa o histórico da conversa para manter coerência e não repetir perguntas.
Quando o jovem reportar uma ação concluída, extrai o que aprendeu — não só o que fez.

MODOS DE INTERAÇÃO
Alterna entre: coach | mentor | challenger | arquiteto de projetos | parceiro de responsabilização | ponte humana.
Escolhe o modo adequado ao momento, não ao padrão habitual."""
