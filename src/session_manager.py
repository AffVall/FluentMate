import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

# ============================================================
# CAMINHOS DE ARQUIVOS
# ============================================================
APP_DATA_DIRECTORY: str = os.path.join(os.path.expanduser("~"), ".english_teacher")
SESSIONS_FILE_PATH: str = os.path.join(APP_DATA_DIRECTORY, "sessions.json")


# ============================================================
# MODELO DE SESSÃO
# ============================================================
class Session:
    """Representa uma sessão de conversação com a IA."""
    
    def __init__(
        self,
        session_id: str,
        session_name: str = "Nova conversa",
        message_history: Optional[List[Dict[str, Any]]] = None
    ):
        self.session_id: str = session_id
        self.session_name: str = session_name
        self.message_history: List[Dict[str, Any]] = message_history or []
        self.created_at_timestamp: str = datetime.now().isoformat()
    
    def to_dictionary(self) -> Dict[str, Any]:
        """Converte a sessão para um dicionário serializável."""
        return {
            "session_id": self.session_id,
            "session_name": self.session_name,
            "message_history": self.message_history,
            "created_at_timestamp": self.created_at_timestamp
        }
    
    @classmethod
    def from_dictionary(cls, data: Dict[str, Any]) -> "Session":
        """Cria uma sessão a partir de um dicionário."""
        session = cls(
            session_id=data["session_id"],
            session_name=data["session_name"],
            message_history=data["message_history"]
        )
        session.created_at_timestamp = data.get("created_at_timestamp", datetime.now().isoformat())
        return session
    
    def add_new_message(self, message_text: str, message_sender: str) -> Dict[str, Any]:
        """Adiciona uma nova mensagem ao histórico."""
        new_message: Dict[str, Any] = {
            "message_id": str(datetime.now().timestamp()),
            "message_text": message_text,
            "message_sender": message_sender,
            "message_timestamp": datetime.now().isoformat()
        }
        self.message_history.append(new_message)
        return new_message


# ============================================================
# GERENCIADOR DE SESSÕES
# ============================================================
class SessionManager:
    """Gerencia todas as sessões de conversação."""
    
    def __init__(self):
        self.all_sessions: List[Session] = []
        self.active_session_identifier: Optional[str] = None
        
        self._ensure_data_directory_exists()
        self.load_all_sessions()
    
    def _ensure_data_directory_exists(self) -> None:
        """Garante que o diretório de dados existe."""
        os.makedirs(APP_DATA_DIRECTORY, exist_ok=True)
    
    def load_all_sessions(self) -> None:
        """Carrega todas as sessões salvas do arquivo."""
        if not os.path.exists(SESSIONS_FILE_PATH):
            return
        
        try:
            with open(SESSIONS_FILE_PATH, "r", encoding="utf-8") as file:
                file_data: Dict[str, Any] = json.load(file)
                
                self.all_sessions = [
                    Session.from_dictionary(session_data)
                    for session_data in file_data.get("all_sessions", [])
                ]
                self.active_session_identifier = file_data.get("active_session_identifier")
        except (json.JSONDecodeError, KeyError):
            self.all_sessions = []
            self.active_session_identifier = None
    
    def save_all_sessions(self) -> None:
        """Salva todas as sessões no arquivo."""
        file_data: Dict[str, Any] = {
            "all_sessions": [session.to_dictionary() for session in self.all_sessions],
            "active_session_identifier": self.active_session_identifier
        }
        
        with open(SESSIONS_FILE_PATH, "w", encoding="utf-8") as file:
            json.dump(file_data, file, ensure_ascii=False, indent=2)
    
    def create_new_session(self) -> Session:
        """Cria uma nova sessão e a torna ativa."""
        current_timestamp: str = str(datetime.now().timestamp())
        new_session = Session(session_id=current_timestamp)
        
        self.all_sessions.insert(0, new_session)
        self.active_session_identifier = new_session.session_id
        self.save_all_sessions()
        
        return new_session
    
    def get_current_active_session(self) -> Optional[Session]:
        """Retorna a sessão atualmente ativa."""
        if not self.active_session_identifier:
            return None
        
        for session in self.all_sessions:
            if session.session_id == self.active_session_identifier:
                return session
        
        return None
    
    def set_session_as_active(self, target_session_id: str) -> None:
        """Define uma sessão específica como ativa."""
        self.active_session_identifier = target_session_id
        self.save_all_sessions()
    
    def delete_session_by_id(self, target_session_id: str) -> None:
        """Remove uma sessão pelo seu ID."""
        self.all_sessions = [
            session for session in self.all_sessions
            if session.session_id != target_session_id
        ]
        
        if self.active_session_identifier == target_session_id:
            if self.all_sessions:
                self.active_session_identifier = self.all_sessions[0].session_id
            else:
                self.active_session_identifier = None
        
        self.save_all_sessions()
    
    def update_session_name_by_id(self, target_session_id: str, new_session_name: str) -> None:
        """Atualiza o nome de uma sessão específica."""
        for session in self.all_sessions:
            if session.session_id == target_session_id:
                session.session_name = new_session_name
                self.save_all_sessions()
                break
