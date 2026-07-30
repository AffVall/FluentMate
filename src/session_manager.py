import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

# ============================================================
# CAMINHOS DE ARQUIVOS
# ============================================================
APP_DATA_DIR = os.path.join(os.path.expanduser("~"), ".english_teacher")
SESSIONS_FILE = os.path.join(APP_DATA_DIR, "sessions.json")


# ============================================================
# MODELO DE SESSÃO
# ============================================================
class Session:
    """Representa uma sessão de conversação com a IA."""

    def __init__(
        self,
        id: str,
        name: str = "Nova conversa",
        messages: Optional[List[Dict[str, Any]]] = None,
    ):
        self.id = id
        self.name = name
        self.messages: List[Dict[str, Any]] = messages or []
        self.created_at: str = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "messages": self.messages,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Session":
        s = cls(
            id=data["id"],
            name=data["name"],
            messages=data["messages"],
        )
        s.created_at = data.get("created_at", datetime.now().isoformat())
        return s

    def add_message(self, text: str, sender: str) -> Dict[str, Any]:
        msg = {
            "text": text,
            "sender": sender,
            "timestamp": datetime.now().isoformat(),
        }
        self.messages.append(msg)
        return msg


# ============================================================
# GERENCIADOR DE SESSÕES
# ============================================================
class SessionManager:
    """Gerencia todas as sessões de conversação."""

    def __init__(self):
        self.sessions: List[Session] = []
        self.active_id: Optional[str] = None

        os.makedirs(APP_DATA_DIR, exist_ok=True)
        self._load()

    def _load(self) -> None:
        if not os.path.exists(SESSIONS_FILE):
            return
        try:
            with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.sessions = [Session.from_dict(s) for s in data.get("sessions", [])]
                self.active_id = data.get("active_id")
        except (json.JSONDecodeError, KeyError):
            self.sessions = []
            self.active_id = None

    def save(self) -> None:
        data = {
            "sessions": [s.to_dict() for s in self.sessions],
            "active_id": self.active_id,
        }
        with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

    def create(self) -> Session:
        s = Session(id=str(datetime.now().timestamp()))
        self.sessions.insert(0, s)
        self.active_id = s.id
        self.save()
        return s

    def get_active(self) -> Optional[Session]:
        if not self.active_id:
            return None
        for s in self.sessions:
            if s.id == self.active_id:
                return s
        return None

    def set_active(self, session_id: str) -> None:
        self.active_id = session_id
        self.save()

    def delete(self, session_id: str) -> None:
        self.sessions = [s for s in self.sessions if s.id != session_id]
        if self.active_id == session_id:
            self.active_id = self.sessions[0].id if self.sessions else None
        self.save()

    def update_name(self, session_id: str, new_name: str) -> None:
        for s in self.sessions:
            if s.id == session_id:
                s.name = new_name
                self.save()
                break
