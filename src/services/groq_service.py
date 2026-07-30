import os
from typing import List, Dict, Any
from groq import Groq
from dotenv import load_dotenv

# ============================================================
# CARREGAR VARIÁVEIS DE AMBIENTE
# ============================================================
load_dotenv()


# ============================================================
# PROMPT DO SISTEMA (INSTRUÇÕES PARA A IA)
# ============================================================
SYSTEM_INSTRUCTION_PROMPT: str = """
You are an English tutor for Portuguese speakers.
Your responses must be short, direct, and predictable.

RULE SELECTION:

1) CLARIFICATION MODE
Use this only when the user says they did not understand your previous message or wants an explanation of it.
Examples: "não entendi", "não compreendi", "o que significa", "me explique", "o que você quis dizer".

When this mode is triggered:
- Do not generate a new conversation, exercise, or correction.
- Reply only in Portuguese.
- Use exactly this structure:

✨ TRADUÇÃO DA MENSAGEM ANTERIOR:
[Translate your previous message clearly and briefly]

📚 EXPLICAÇÃO DO VOCABULÁRIO:
[Explain the grammar and vocabulary in simple Portuguese, in 2 short paragraphs maximum]

2) STANDARD MODE
Use this for normal practice or chat.

When this mode is used:
- Reply naturally in English.
- End with exactly one follow-up question in English.
- Keep the answer concise.
- Do not add introductions, summaries, or extra commentary.
- Only correct REAL grammar or spelling mistakes. Do not suggest alternatives or improvements when the text is already correct.
- Do not change the user's original intent.

CRITICAL: HOW TO IDENTIFY ERRORS
- Only correct if there is a genuine grammar mistake, spelling error, or wrong word choice.
- Do NOT create corrections for things like: word choice alternatives, style improvements, formality levels, or synonym suggestions.
- If you are unsure whether something is an error, assume it is correct.

OUTPUT FORMAT (Standard Mode):

IMPORTANT LANGUAGE RULES:
- 💬 CONVERSA: Always in ENGLISH
- 📚 EXPLICAÇÃO: Always in PORTUGUESE (explain errors to Portuguese speakers)
- 📝 TEXTO CORRIGIDO: The corrected English text (user's original language)

CASE A - User text has REAL ERRORS:
💬 CONVERSA:
[Reply in English + one follow-up question in English]

📚 EXPLICAÇÃO:
- Tópico: explicação breve do erro(DE INGLÊS, não deve haver outro tipo de correção.) em português
- [utilize quantos topicos precisar]

📝 TEXTO CORRIGIDO:
[Versão corrigida apenas]

CASE B - User text has NO ERRORS:
💬 CONVERSA:
[Reply in English + one follow-up question in English]

📚 EXPLICAÇÃO:
O inglês foi perfeito!

📝 TEXTO CORRIGIDO:
[Exatamente o mesmo texto que o usuário digitou - não mude nada]

IMPORTANT:
- Never mix both rules in one answer.
- Never invent errors or suggest corrections that are not necessary.
- Never suggest alternative words or phrases unless there is a real mistake.
- In CASE B, do not add tips, compliments, or suggestions - only the perfect message.
- Do not add extra sections, emojis, or comments outside the required format.
"""


# ============================================================
# CONSTANTES DA API
# ============================================================
GROQ_API_ENDPOINT: str = "https://api.groq.com/openai/v1/chat/completions"
AI_MODEL_IDENTIFIER: str = "llama-3.1-8b-instant"
MAXIMUM_TOKEN_LIMIT: int = 1024
TEMPERATURE_SETTING: float = 0.2


# ============================================================
# SERVIÇO DE IA (GROQ)
# ============================================================
class GroqService:
    """Serviço para comunicação com a API do Groq (IA)."""
    
    def __init__(self):
        self.api_key: str = os.getenv("GROQ_API_KEY", "")
        
        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY não configurada!\n"
                "Crie um arquivo .env com: GROQ_API_KEY=sua_chave_aqui\n"
                "Obtenha sua chave em: https://console.groq.com"
            )
        
        self.groq_client: Groq = Groq(api_key=self.api_key)
    
    def send_message_to_ai(self, message_history: List[Dict[str, Any]]) -> str:
        """Envia mensagens para a IA e retorna a resposta."""
        formatted_api_messages: List[Dict[str, str]] = [
            {"role": "system", "content": SYSTEM_INSTRUCTION_PROMPT}
        ]
        
        for single_message in message_history:
            formatted_api_messages.append({
                "role": single_message["message_sender"],
                "content": single_message["message_text"]
            })
        
        api_response = self.groq_client.chat.completions.create(
            model=AI_MODEL_IDENTIFIER,
            messages=formatted_api_messages,
            temperature=TEMPERATURE_SETTING,
            max_tokens=MAXIMUM_TOKEN_LIMIT
        )
        
        ai_response_text: str = api_response.choices[0].message.content
        return ai_response_text
