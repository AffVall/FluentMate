import os
from typing import List, Dict, Any
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# CONSTANTES
# ============================================================
MODEL = "llama-3.1-8b-instant"
MAX_TOKENS = 1024
TEMPERATURE = 0.2
MAX_HISTORY = 20


# ============================================================
# SERVIÇO DE IA
# ============================================================
class GroqService:
    """Serviço para comunicação com a API do Groq."""

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY não configurada!\n"
                "Crie um arquivo .env com: GROQ_API_KEY=sua_chave_aqui\n"
                "Obtenha sua chave em: https://console.groq.com"
            )
        self._client = Groq(api_key=api_key)

    def send_message(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: str,
        session_id: str | None = None,
    ) -> str:
        """Envia mensagens para a IA com o system prompt fornecido."""
        api_msgs = [{"role": "system", "content": system_prompt}]

        if session_id:
            api_msgs.append({
                "role": "system",
                "content": (
                    f"Session-ID: {session_id}. "
                    "Only use the messages provided in this request; "
                    "do not assume any other conversation context."
                ),
            })

        valid_roles = {"user", "assistant"}
        filtered = [m for m in messages if m.get("sender") in valid_roles]
        for m in filtered[-MAX_HISTORY:]:
            api_msgs.append({"role": m["sender"], "content": m["text"]})

        resp = self._client.chat.completions.create(
            model=MODEL,
            messages=api_msgs,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )
        return resp.choices[0].message.content
