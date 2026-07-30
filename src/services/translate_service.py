import requests
from typing import Dict, Any

# ============================================================
# CONSTANTES
# ============================================================
API_URL = "https://translate.googleapis.com/translate_a/single"
TIMEOUT = 10


# ============================================================
# SERVIÇO DE TRADUÇÃO
# ============================================================
class TranslateService:
    """Serviço para tradução usando Google Translate API."""

    def translate_text(
        self,
        text: str,
        source: str = "auto",
        target: str = "pt",
    ) -> Dict[str, Any]:
        params = {
            "client": "gtx",
            "sl": source,
            "tl": target,
            "dt": "t",
            "q": text,
        }

        try:
            resp = requests.get(API_URL, params=params, timeout=TIMEOUT)
            resp.raise_for_status()
            data = resp.json()

            translated = "".join(part[0] for part in data[0])
            detected = data[2] if len(data) > 2 else source

            return {
                "translated_text": translated,
                "detected_source_language": detected,
                "target_language": target,
            }
        except requests.RequestException as e:
            raise Exception(f"Erro na requisição de tradução: {e}")
        except (IndexError, KeyError) as e:
            raise Exception(f"Erro ao processar resposta da tradução: {e}")
