import requests
from typing import Dict, Any


# ============================================================
# CONSTANTES DA API DE TRADUÇÃO
# ============================================================
GOOGLE_TRANSLATE_API_URL: str = "https://translate.googleapis.com/translate_a/single"
REQUEST_TIMEOUT_SECONDS: int = 10
MAXIMUM_TEXT_LENGTH_FOR_DETECTION: int = 500


# ============================================================
# CÓDIGOS DE IDIOMAS SUPORTADOS
# ============================================================
LANGUAGE_PORTUGUESE: str = "pt"
LANGUAGE_ENGLISH: str = "en"
LANGUAGE_AUTO_DETECT: str = "auto"


# ============================================================
# SERVIÇO DE TRADUÇÃO (GOOGLE TRANSLATE)
# ============================================================
class TranslateService:
    """Serviço para tradução de texto usando Google Translate API."""
    
    def translate_text(
        self,
        input_text: str,
        source_language: str = LANGUAGE_AUTO_DETECT,
        target_language: str = LANGUAGE_PORTUGUESE
    ) -> Dict[str, Any]:
        """
        Traduz o texto do idioma de origem para o idioma de destino.
        
        Args:
            input_text: Texto a ser traduzido
            source_language: Código do idioma de origem (padrão: auto)
            target_language: Código do idioma de destino (padrão: pt)
        
        Returns:
            Dicionário com o texto traduzido e informações do idioma
        """
        try:
            request_parameters: Dict[str, str] = {
                "client": "gtx",
                "sl": source_language,
                "tl": target_language,
                "dt": "t",
                "q": input_text
            }
            
            http_response = requests.get(
                GOOGLE_TRANSLATE_API_URL,
                params=request_parameters,
                timeout=REQUEST_TIMEOUT_SECONDS
            )
            http_response.raise_for_status()
            
            response_data = http_response.json()
            
            translated_text_parts = [item[0] for item in response_data[0]]
            complete_translated_text: str = "".join(translated_text_parts)
            
            detected_source_language: str = (
                response_data[2] if len(response_data) > 2 else source_language
            )
            
            return {
                "translated_text": complete_translated_text,
                "detected_source_language": detected_source_language,
                "target_language": target_language
            }
        
        except requests.RequestException as request_error:
            raise Exception(f"Erro na requisição de tradução: {str(request_error)}")
        except (IndexError, KeyError) as parse_error:
            raise Exception(f"Erro ao processar resposta da tradução: {str(parse_error)}")
    
    def detect_text_language(self, input_text: str) -> str:
        """
        Detecta o idioma do texto fornecido.
        
        Args:
            input_text: Texto para detectar o idioma
        
        Returns:
            Código do idioma detectado
        """
        try:
            text_sample: str = input_text[:MAXIMUM_TEXT_LENGTH_FOR_DETECTION]
            detection_result = self.translate_text(text_sample, LANGUAGE_AUTO_DETECT, LANGUAGE_PORTUGUESE)
            return detection_result["detected_source_language"]
        except Exception:
            return "unknown"
