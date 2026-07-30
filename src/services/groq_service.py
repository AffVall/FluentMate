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
SYSTEM_INSTRUCTION_PROMPT: str = """Você é um professor de inglês experiente e amigável. Quando o usuário enviar um texto em português:

1. CORRIJA o texto em português, mostrando os erros encontrados
2. EXPLIQUE didaticamente cada correção
3. TRADUZA para inglês de forma natural
4. CONVERSE sobre o assunto, puxando assunto em inglês para praticar

Sempre responda no formato:
📝 Texto Corrigido: [correção]
📚 Explicação: [explicação didática]
🇬🇧 English: [tradução em inglês]
💬 Conversa: [comentário/conversa em inglês para praticar]

Se o usuário apenas estiver conversando em inglês, responda normalmente em inglês e ajude com dicas quando necessário."""


# ============================================================
# CONSTANTES DA API
# ============================================================
GROQ_API_ENDPOINT: str = "https://api.groq.com/openai/v1/chat/completions"
AI_MODEL_IDENTIFIER: str = "llama-3.1-8b-instant"
MAXIMUM_TOKEN_LIMIT: int = 1024
TEMPERATURE_SETTING: float = 0.7


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
