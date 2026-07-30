import customtkinter as ctk
from tkinter import messagebox
import threading
from datetime import datetime
from typing import Optional, Dict

from src.session_manager import SessionManager, Session
from src.services.groq_service import GroqService
from src.services.translate_service import TranslateService
from src.services.intents import classify, get_prompt

# ============================================================
# CONFIGURAÇÕES DA INTERFACE
# ============================================================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ============================================================
# CORES
# ============================================================
BG_DARK = "#1e1e2e"
BG_MEDIUM = "#181825"
BG_LIGHT = "#313244"
HOVER = "#45475a"
TEXT_PRIMARY = "#cdd6f4"
TEXT_SECONDARY = "#a6adc8"
TEXT_MUTED = "#6c7086"
ACCENT = "#89b4fa"
ACCENT_HOVER = "#74c7ec"
SCROLLBAR_HOVER = "#585b70"

# ============================================================
# DIMENSÕES
# ============================================================
SIDEBAR_WIDTH = 280
BTN_HEIGHT = 36
BUBBLE_WRAP = 550
INPUT_HEIGHT = 50


# ============================================================
# PAINEL LATERAL (SESSÕES + TRADUTOR)
# ============================================================
class Sidebar(ctk.CTkFrame):
    """Barra lateral com lista de sessões e tradutor integrado."""

    def __init__(
        self,
        parent,
        session_mgr: SessionManager,
        translate_svc: TranslateService,
        on_select,
        on_new,
    ):
        super().__init__(parent, width=SIDEBAR_WIDTH, fg_color=BG_MEDIUM, corner_radius=0)
        self.pack_propagate(False)

        self.session_mgr = session_mgr
        self.translate_svc = translate_svc
        self._on_select = on_select
        self._on_new = on_new
        self._session_frames: Dict[str, ctk.CTkFrame] = {}

        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(16, 8))

        ctk.CTkLabel(
            header,
            text="English Teacher",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=TEXT_PRIMARY,
        ).pack(anchor="w")

        ctk.CTkButton(
            header,
            text="+ Nova Sessão",
            command=self._on_new,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            text_color=BG_DARK,
            font=ctk.CTkFont(weight="bold"),
            height=BTN_HEIGHT,
        ).pack(fill="x", pady=(12, 0))

        self._sessions_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=HOVER,
            scrollbar_button_hover_color=SCROLLBAR_HOVER,
        )
        self._sessions_frame.pack(fill="both", expand=True, padx=8, pady=(8, 8))

        ctk.CTkFrame(self, height=1, fg_color=HOVER).pack(fill="x", padx=12, pady=(4, 4))

        self._build_translator()

    def _build_translator(self) -> None:
        container = ctk.CTkFrame(self, fg_color=BG_MEDIUM, corner_radius=0, height=185)
        container.pack(fill="x", padx=8, pady=(0, 8))
        container.pack_propagate(False)

        top_row = ctk.CTkFrame(container, fg_color="transparent")
        top_row.pack(fill="x", padx=12, pady=(8, 4))

        ctk.CTkLabel(
            top_row,
            text="🌐 Tradutor",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEXT_PRIMARY,
        ).pack(side="left")

        self._dir_label = ctk.CTkLabel(
            top_row,
            text="PT → EN",
            font=ctk.CTkFont(size=10),
            text_color=ACCENT,
        )
        self._dir_label.pack(side="right", padx=(0, 8))

        ctk.CTkButton(
            top_row,
            text="⇄",
            width=28,
            height=28,
            fg_color="transparent",
            hover_color=BG_LIGHT,
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=12),
            command=self._swap_direction,
        ).pack(side="right")

        self._translate_input = ctk.CTkTextbox(
            container,
            height=40,
            fg_color=BG_LIGHT,
            text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(size=11),
            border_width=1,
            border_color=HOVER,
            corner_radius=6,
        )
        self._translate_input.pack(fill="x", padx=12, pady=(0, 4))
        self._translate_input.bind("<Return>", lambda e: (self._do_translate(), "break"))

        ctk.CTkButton(
            container,
            text="Traduzir",
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            text_color=BG_DARK,
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self._do_translate,
            height=28,
        ).pack(fill="x", padx=12, pady=(0, 4))

        out_frame = ctk.CTkFrame(container, fg_color="transparent")
        out_frame.pack(fill="x", padx=12, pady=(0, 4))

        self._translate_output = ctk.CTkTextbox(
            out_frame,
            height=50,
            fg_color=BG_LIGHT,
            text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(size=11),
            border_width=1,
            border_color=HOVER,
            corner_radius=6,
            state="disabled",
        )
        self._translate_output.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            out_frame,
            text="📋",
            width=30,
            height=30,
            fg_color=BG_LIGHT,
            hover_color=HOVER,
            text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(size=12),
            command=self._copy_translation,
        ).pack(side="right")

        self._translate_dir = "pt-en"

    def refresh(self) -> None:
        for w in self._sessions_frame.winfo_children():
            w.destroy()
        self._session_frames.clear()

        if not self.session_mgr.sessions:
            ctk.CTkLabel(
                self._sessions_frame,
                text="Nenhuma sessão ainda",
                text_color=TEXT_MUTED,
                font=ctk.CTkFont(size=12),
            ).pack(pady=20)
            return

        for s in self.session_mgr.sessions:
            active = s.id == self.session_mgr.active_id
            frame = ctk.CTkFrame(
                self._sessions_frame,
                fg_color=BG_LIGHT if active else "transparent",
                corner_radius=8,
                border_width=2 if active else 0,
                border_color=ACCENT,
            )
            frame.pack(fill="x", pady=2)

            ctk.CTkButton(
                frame,
                text=s.name,
                anchor="w",
                fg_color="transparent",
                hover_color=HOVER,
                text_color=TEXT_PRIMARY,
                font=ctk.CTkFont(size=13),
                command=lambda sid=s.id: self._on_select(sid),
                height=40,
            ).pack(fill="x", padx=4, pady=4, side="left", expand=True)

            date_str = datetime.fromisoformat(s.created_at).strftime("%d/%m")
            ctk.CTkLabel(
                frame,
                text=date_str,
                text_color=TEXT_MUTED,
                font=ctk.CTkFont(size=10),
            ).pack(side="right", padx=12)

    def _swap_direction(self) -> None:
        if self._translate_dir == "pt-en":
            self._translate_dir = "en-pt"
            self._dir_label.configure(text="EN → PT")
        else:
            self._translate_dir = "pt-en"
            self._dir_label.configure(text="PT → EN")

    def _do_translate(self) -> None:
        text = self._translate_input.get("1.0", "end").strip()
        if not text:
            return
        src, tgt = self._translate_dir.split("-")
        try:
            result = self.translate_svc.translate_text(text, src, tgt)
            self._translate_output.configure(state="normal")
            self._translate_output.delete("1.0", "end")
            self._translate_output.insert("1.0", result["translated_text"])
            self._translate_output.configure(state="disabled")
        except Exception as e:
            messagebox.showerror("Erro de Tradução", str(e))

    def _copy_translation(self) -> None:
        text = self._translate_output.get("1.0", "end").strip()
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)


# ============================================================
# PAINEL DO CHAT
# ============================================================
class ChatPanel(ctk.CTkFrame):
    """Área principal do chat com mensagens e input."""

    def __init__(self, parent, groq: GroqService, session_mgr: SessionManager):
        super().__init__(parent, fg_color=BG_DARK, corner_radius=0)

        self.groq = groq
        self.session_mgr = session_mgr
        self._loading = False
        self._typing_frame: Optional[ctk.CTkFrame] = None

        self._build_ui()

    def _build_ui(self) -> None:
        header = ctk.CTkFrame(self, fg_color=BG_MEDIUM, corner_radius=0)
        header.pack(fill="x")

        self._title = ctk.CTkLabel(
            header,
            text="Selecione uma sessão",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=TEXT_PRIMARY,
        )
        self._title.pack(anchor="w", padx=24, pady=(16, 4))

        ctk.CTkLabel(
            header,
            text="Converse em inglês e receba correções",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED,
        ).pack(anchor="w", padx=24, pady=(0, 16))

        ctk.CTkFrame(self, height=1, fg_color=HOVER).pack(fill="x")

        self._messages = ctk.CTkScrollableFrame(
            self,
            fg_color=BG_DARK,
            scrollbar_button_color=HOVER,
            scrollbar_button_hover_color=SCROLLBAR_HOVER,
        )
        self._messages.pack(side="top", fill="both", expand=True, padx=16, pady=16)

        self._show_welcome()

        input_frame = ctk.CTkFrame(self, fg_color=BG_MEDIUM, corner_radius=0)
        input_frame.pack(side="bottom", fill="x", padx=16, pady=(0, 16))

        self._input = ctk.CTkTextbox(
            input_frame,
            height=INPUT_HEIGHT,
            fg_color=BG_LIGHT,
            text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(size=16),
            border_width=1,
            border_color=HOVER,
            corner_radius=12,
        )
        self._input.pack(side="left", fill="x", expand=True, padx=(0, 12))
        self._input.bind("<Return>", self._on_enter)

        self._send_btn = ctk.CTkButton(
            input_frame,
            text="➤",
            width=INPUT_HEIGHT,
            height=INPUT_HEIGHT,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            text_color=BG_DARK,
            font=ctk.CTkFont(size=18),
            command=self.send_message,
            corner_radius=12,
        )
        self._send_btn.pack(side="right")

        ctk.CTkLabel(
            input_frame,
            text="Enter para enviar • Shift+Enter para nova linha",
            font=ctk.CTkFont(size=10),
            text_color=TEXT_MUTED,
        ).pack(pady=(8, 0))

    def _show_welcome(self) -> None:
        container = ctk.CTkFrame(self._messages, fg_color="transparent")
        container.pack(fill="both", expand=True, pady=100)

        ctk.CTkLabel(container, text="👋", font=ctk.CTkFont(size=48)).pack()
        ctk.CTkLabel(
            container,
            text="Olá! Como posso ajudar?",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEXT_PRIMARY,
        ).pack(pady=(16, 8))
        ctk.CTkLabel(
            container,
            text="Escreva em português para receber correções,\nou em inglês para praticar!",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_MUTED,
            justify="center",
        ).pack()

        examples = ctk.CTkFrame(container, fg_color="transparent")
        examples.pack(pady=24)

        for text, fill in [
            ('"Eu fui ao mercado ontem..."', "Eu fui ao mercado ontem e comprei muitas frutas."),
            ('"Hello! I want to practice..."', "Hello! I want to practice my English."),
        ]:
            ctk.CTkButton(
                examples,
                text=text,
                command=lambda t=fill: self._set_input(t),
                fg_color=BG_LIGHT,
                hover_color=HOVER,
                text_color=TEXT_PRIMARY,
                font=ctk.CTkFont(size=12),
                height=40,
            ).pack(pady=4)

    def _set_input(self, text: str) -> None:
        self._input.delete("1.0", "end")
        self._input.insert("1.0", text)

    def _on_enter(self, event) -> Optional[str]:
        if not event.state & 0x1:
            self.send_message()
            return "break"

    def set_header(self, name: str) -> None:
        self._title.configure(text=name)

    def clear_messages(self) -> None:
        for w in self._messages.winfo_children():
            w.destroy()

    def show_message(self, text: str, sender: str) -> None:
        is_user = sender == "user"

        wrapper = ctk.CTkFrame(self._messages, fg_color="transparent")
        wrapper.pack(fill="x", pady=8)

        if is_user:
            wrapper.pack(anchor="e")
            bubble = ctk.CTkFrame(wrapper, fg_color=ACCENT, corner_radius=16)
            bubble.pack(anchor="e", padx=(100, 0))
            ctk.CTkLabel(
                bubble,
                text="Você",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=BG_DARK,
            ).pack(anchor="e", padx=16, pady=(8, 0))
        else:
            wrapper.pack(anchor="w")

            avatar = ctk.CTkFrame(wrapper, fg_color="transparent", width=36)
            avatar.pack(side="left", padx=(0, 8))
            avatar.pack_propagate(False)
            ctk.CTkLabel(avatar, text="🎓", font=ctk.CTkFont(size=20)).pack(pady=4)

            bubble = ctk.CTkFrame(wrapper, fg_color=BG_LIGHT, corner_radius=16)
            bubble.pack(anchor="w", side="left")
            ctk.CTkLabel(
                bubble,
                text="Professor",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=TEXT_MUTED,
            ).pack(anchor="w", padx=16, pady=(8, 0))

        ctk.CTkLabel(
            bubble,
            text=text,
            font=ctk.CTkFont(size=15),
            text_color=BG_DARK if is_user else TEXT_PRIMARY,
            justify="left",
            wraplength=BUBBLE_WRAP,
        ).pack(padx=16, pady=(4, 12))

    def show_typing(self) -> None:
        self._typing_frame = ctk.CTkFrame(self._messages, fg_color="transparent")
        self._typing_frame.pack(fill="x", pady=8)
        ctk.CTkLabel(
            self._typing_frame,
            text="Professor está digitando...",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED,
        ).pack(anchor="w")

    def hide_typing(self) -> None:
        if self._typing_frame is not None:
            self._typing_frame.destroy()
            self._typing_frame = None

    # --- envio de mensagem --------------------------------------------------

    def send_message(self) -> None:
        if self._loading:
            return

        text = self._input.get("1.0", "end").strip()
        if not text:
            return

        session = self.session_mgr.get_active()
        if not session:
            messagebox.showwarning("Aviso", "Selecione ou crie uma sessão primeiro!")
            return

        self._loading = True
        self._input.delete("1.0", "end")

        self.show_message(text, "user")
        session.add_message(text, "user")

        if len(session.messages) == 1:
            auto_name = text[:50] + ("..." if len(text) > 50 else "")
            self.session_mgr.update_name(session.id, auto_name)
            self.set_header(auto_name)

        self.session_mgr.save()

        self.show_typing()
        self._send_btn.configure(state="disabled")

        threading.Thread(
            target=self._request_ai, args=(session,), daemon=True
        ).start()

    def _request_ai(self, session: Session) -> None:
        try:
            last_user_msg = session.messages[-1]["text"]
            intent = classify(last_user_msg)
            system_prompt = get_prompt(intent)

            if intent == "clarification":
                prev = self._last_assistant_msg(session)
                api_messages = [
                    {"sender": "user", "text": f"O aluno não entendeu esta resposta:\n\n{prev}\n\nExplique em português."}
                ]
            else:
                api_messages = session.messages

            reply = self.groq.send_message(api_messages, system_prompt, session_id=session.id)

            session.add_message(reply, "assistant")
            self.session_mgr.save()

            self.after(0, self._on_ai_reply, reply)
        except Exception as e:
            self.after(0, self._on_ai_error, str(e))

    def _last_assistant_msg(self, session: Session) -> str:
        for msg in reversed(session.messages):
            if msg["sender"] == "assistant":
                return msg["text"]
        return ""

    def _on_ai_reply(self, reply: str) -> None:
        self.hide_typing()
        self.show_message(reply, "assistant")
        self._loading = False
        self._send_btn.configure(state="normal")

    def _on_ai_error(self, error: str) -> None:
        self.hide_typing()
        self.show_message(f"❌ Erro: {error}", "assistant")
        self._loading = False
        self._send_btn.configure(state="normal")


# ============================================================
# APLICAÇÃO PRINCIPAL
# ============================================================
class EnglishTeacherApp(ctk.CTk):
    """Janela principal da aplicação."""

    def __init__(self):
        super().__init__()
        self.title("English Teacher")
        self.geometry("1200x700")
        self.minsize(900, 600)

        self.session_mgr = SessionManager()

        try:
            self.groq = GroqService()
        except ValueError as e:
            messagebox.showerror("Erro de Configuração", str(e))
            self.groq = None

        self.translate_svc = TranslateService()
        self._build_layout()

    def _build_layout(self) -> None:
        self.sidebar = Sidebar(
            self,
            session_mgr=self.session_mgr,
            translate_svc=self.translate_svc,
            on_select=self._select_session,
            on_new=self._new_session,
        )
        self.sidebar.pack(side="left", fill="y")

        content = ctk.CTkFrame(self, fg_color=BG_DARK, corner_radius=0)
        content.pack(side="left", fill="both", expand=True)

        self.chat = ChatPanel(
            content,
            groq=self.groq,
            session_mgr=self.session_mgr,
        )
        self.chat.pack(fill="both", expand=True)

    def _new_session(self) -> None:
        session = self.session_mgr.create()
        self.sidebar.refresh()
        self.chat.set_header(session.name)
        self.chat.clear_messages()

        if not self.groq:
            messagebox.showwarning(
                "API Não Configurada",
                "Configure sua GROQ_API_KEY no arquivo .env",
            )

    def _select_session(self, session_id: str) -> None:
        self.session_mgr.set_active(session_id)
        self.sidebar.refresh()

        session = self.session_mgr.get_active()
        if session:
            self.chat.set_header(session.name)
            self.chat.clear_messages()
            for msg in session.messages:
                self.chat.show_message(msg["text"], msg["sender"])


# ============================================================
# PONTO DE ENTRADA
# ============================================================
def main():
    app = EnglishTeacherApp()
    app.mainloop()


if __name__ == "__main__":
    main()
