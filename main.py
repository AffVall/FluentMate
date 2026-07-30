import customtkinter as ctk
from tkinter import messagebox
import threading
from datetime import datetime
from typing import Optional, List, Dict, Any

from src.session_manager import SessionManager, Session
from src.services.groq_service import GroqService
from src.services.translate_service import TranslateService


# ============================================================
# CONFIGURAÇÕES DA INTERFACE
# ============================================================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# ============================================================
# CONSTANTES DE CORES
# ============================================================
COLOR_BACKGROUND_DARK: str = "#1e1e2e"
COLOR_BACKGROUND_MEDIUM: str = "#181825"
COLOR_BACKGROUND_LIGHT: str = "#313244"
COLOR_HOVER_EFFECT: str = "#45475a"
COLOR_TEXT_PRIMARY: str = "#cdd6f4"
COLOR_TEXT_SECONDARY: str = "#a6adc8"
COLOR_TEXT_MUTED: str = "#6c7086"
COLOR_ACCENT_BLUE: str = "#89b4fa"
COLOR_ACCENT_HOVER: str = "#74c7ec"
COLOR_ERROR_RED: str = "#f38ba8"


# ============================================================
# CONSTANTES DE DIMENSÕES
# ============================================================
SIDEBAR_WIDTH_PIXELS: int = 280
BUTTON_HEIGHT_PIXELS: int = 36
MESSAGE_BUBBLE_WRAP_LENGTH: int = 550
INPUT_TEXTBOX_HEIGHT: int = 50
TYPING_INDICATOR_HEIGHT: int = 32


# ============================================================
# COMPONENTE: BARRA LATERAL (SESSÕES)
# ============================================================
class SidebarPanel(ctk.CTkFrame):
    """Painel lateral com lista de sessões e tradutor."""
    
    def __init__(
        self,
        parent_widget,
        session_manager_instance: SessionManager,
        on_session_select_callback,
        on_new_session_callback
    ):
        super().__init__(
            parent_widget,
            width=SIDEBAR_WIDTH_PIXELS,
            fg_color=COLOR_BACKGROUND_MEDIUM,
            corner_radius=0
        )
        self.pack_propagate(False)
        
        self.session_manager = session_manager_instance
        self.on_session_select = on_session_select_callback
        self.on_new_session = on_new_session_callback
        
        self.session_button_widgets: Dict[str, ctk.CTkFrame] = {}
        
        self._create_panel_widgets()
        self.refresh_sessions_display()
    
    def _create_panel_widgets(self) -> None:
        """Cria todos os widgets do painel lateral."""
        header_container = ctk.CTkFrame(self, fg_color="transparent")
        header_container.pack(fill="x", padx=16, pady=(16, 8))
        
        application_title_label = ctk.CTkLabel(
            header_container,
            text="English Teacher",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY
        )
        application_title_label.pack(anchor="w")
        
        create_session_button = ctk.CTkButton(
            header_container,
            text="+ Nova Sessão",
            command=self.on_new_session,
            fg_color=COLOR_ACCENT_BLUE,
            hover_color=COLOR_ACCENT_HOVER,
            text_color=COLOR_BACKGROUND_DARK,
            font=ctk.CTkFont(weight="bold"),
            height=BUTTON_HEIGHT_PIXELS
        )
        create_session_button.pack(fill="x", pady=(12, 0))
        
        self.sessions_scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=COLOR_HOVER_EFFECT,
            scrollbar_button_hover_color="#585b70"
        )
        self.sessions_scroll_frame.pack(fill="both", expand=True, padx=8, pady=(8, 8))
    
    def refresh_sessions_display(self) -> None:
        """Atualiza a exibição da lista de sessões."""
        for existing_widget in self.sessions_scroll_frame.winfo_children():
            existing_widget.destroy()
        
        self.session_button_widgets.clear()
        
        if not self.session_manager.all_sessions:
            empty_state_label = ctk.CTkLabel(
                self.sessions_scroll_frame,
                text="Nenhuma sessão ainda",
                text_color=COLOR_TEXT_MUTED,
                font=ctk.CTkFont(size=12)
            )
            empty_state_label.pack(pady=20)
            return
        
        for single_session in self.session_manager.all_sessions:
            is_currently_active: bool = (
                single_session.session_id == self.session_manager.active_session_identifier
            )
            
            session_button_frame = ctk.CTkFrame(
                self.sessions_scroll_frame,
                fg_color=COLOR_BACKGROUND_LIGHT if is_currently_active else "transparent",
                corner_radius=8,
                border_width=2 if is_currently_active else 0,
                border_color=COLOR_ACCENT_BLUE
            )
            session_button_frame.pack(fill="x", pady=2)
            
            session_click_button = ctk.CTkButton(
                session_button_frame,
                text=single_session.session_name,
                anchor="w",
                fg_color="transparent",
                hover_color=COLOR_HOVER_EFFECT,
                text_color=COLOR_TEXT_PRIMARY,
                font=ctk.CTkFont(size=13),
                command=lambda sid=single_session.session_id: self.on_session_select(sid),
                height=40
            )
            session_click_button.pack(fill="x", padx=4, pady=4)
            
            creation_date_label = ctk.CTkLabel(
                session_button_frame,
                text=datetime.fromisoformat(single_session.created_at_timestamp).strftime("%d/%m"),
                text_color=COLOR_TEXT_MUTED,
                font=ctk.CTkFont(size=10)
            )
            creation_date_label.place(relx=1.0, rely=0.5, anchor="e", x=-12)
            
            self.session_button_widgets[single_session.session_id] = session_button_frame
    
    def select_session_by_id(self, target_session_id: str) -> None:
        """Seleciona uma sessão específica."""
        self.session_manager.set_session_as_active(target_session_id)
        self.refresh_sessions_display()
        self.on_session_select(target_session_id)


# ============================================================
# COMPONENTE: ÁREA DO CHAT
# ============================================================
class ChatAreaPanel(ctk.CTkFrame):
    """Painel principal do chat com mensagens e input."""
    
    def __init__(
        self,
        parent_widget,
        groq_service_instance: GroqService,
        session_manager_instance: SessionManager
    ):
        super().__init__(parent_widget, fg_color=COLOR_BACKGROUND_DARK, corner_radius=0)
        
        self.groq_service = groq_service_instance
        self.session_manager = session_manager_instance
        self.is_currently_loading: bool = False
        
        self._create_chat_widgets()
    
    def _create_chat_widgets(self) -> None:
        """Cria todos os widgets do chat."""
        self.chat_header_frame = ctk.CTkFrame(self, fg_color=COLOR_BACKGROUND_MEDIUM, corner_radius=0)
        self.chat_header_frame.pack(fill="x")
        
        self.session_title_label = ctk.CTkLabel(
            self.chat_header_frame,
            text="Selecione uma sessão",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY
        )
        self.session_title_label.pack(anchor="w", padx=24, pady=(16, 4))
        
        self.session_subtitle_label = ctk.CTkLabel(
            self.chat_header_frame,
            text="Converse em inglês e receba correções",
            font=ctk.CTkFont(size=12),
            text_color=COLOR_TEXT_MUTED
        )
        self.session_subtitle_label.pack(anchor="w", padx=24, pady=(0, 16))
        
        header_separator_line = ctk.CTkFrame(self, height=1, fg_color=COLOR_HOVER_EFFECT)
        header_separator_line.pack(fill="x")
        
        self.messages_display_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=COLOR_BACKGROUND_DARK,
            scrollbar_button_color=COLOR_HOVER_EFFECT,
            scrollbar_button_hover_color="#585b70"
        )
        self.messages_display_frame.pack(side="top", fill="both", expand=True, padx=16, pady=16)
        
        self._create_welcome_screen()
        
        self.input_container_frame = ctk.CTkFrame(self, fg_color=COLOR_BACKGROUND_MEDIUM, corner_radius=0)
        self.input_container_frame.pack(side="bottom", fill="x", padx=16, pady=(0, 16))
        
        self.message_input_textbox = ctk.CTkTextbox(
            self.input_container_frame,
            height=INPUT_TEXTBOX_HEIGHT,
            fg_color=COLOR_BACKGROUND_LIGHT,
            text_color=COLOR_TEXT_PRIMARY,
            font=ctk.CTkFont(size=16),
            border_width=1,
            border_color=COLOR_HOVER_EFFECT,
            corner_radius=12
        )
        self.message_input_textbox.pack(side="left", fill="x", expand=True, padx=(0, 12))
        self.message_input_textbox.bind("<Return>", self._on_enter_key_press)
        
        self.send_message_button = ctk.CTkButton(
            self.input_container_frame,
            text="➤",
            width=INPUT_TEXTBOX_HEIGHT,
            height=INPUT_TEXTBOX_HEIGHT,
            fg_color=COLOR_ACCENT_BLUE,
            hover_color=COLOR_ACCENT_HOVER,
            text_color=COLOR_BACKGROUND_DARK,
            font=ctk.CTkFont(size=18),
            command=self.send_user_message,
            corner_radius=12
        )
        self.send_message_button.pack(side="right")
        
        self.input_hint_label = ctk.CTkLabel(
            self.input_container_frame,
            text="Enter para enviar • Shift+Enter para nova linha",
            font=ctk.CTkFont(size=10),
            text_color=COLOR_TEXT_MUTED
        )
        self.input_hint_label.pack(pady=(8, 0))
    
    def _create_welcome_screen(self) -> None:
        """Cria a tela de boas-vindas."""
        self.welcome_container = ctk.CTkFrame(self.messages_display_frame, fg_color="transparent")
        self.welcome_container.pack(fill="both", expand=True, pady=100)
        
        welcome_emoji_label = ctk.CTkLabel(
            self.welcome_container,
            text="👋",
            font=ctk.CTkFont(size=48)
        )
        welcome_emoji_label.pack()
        
        welcome_title_label = ctk.CTkLabel(
            self.welcome_container,
            text="Olá! Como posso ajudar?",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY
        )
        welcome_title_label.pack(pady=(16, 8))
        
        welcome_description_label = ctk.CTkLabel(
            self.welcome_container,
            text="Escreva em português para receber correções,\nou em inglês para praticar!",
            font=ctk.CTkFont(size=13),
            text_color=COLOR_TEXT_MUTED,
            justify="center"
        )
        welcome_description_label.pack()
        
        examples_container = ctk.CTkFrame(self.welcome_container, fg_color="transparent")
        examples_container.pack(pady=24)
        
        portuguese_example_button = ctk.CTkButton(
            examples_container,
            text='🇧🇷 "Eu fui ao mercado ontem..."',
            command=lambda: self._set_input_text("Eu fui ao mercado ontem e comprei muitas frutas."),
            fg_color=COLOR_BACKGROUND_LIGHT,
            hover_color=COLOR_HOVER_EFFECT,
            text_color=COLOR_TEXT_PRIMARY,
            font=ctk.CTkFont(size=12),
            height=40
        )
        portuguese_example_button.pack(pady=4)
        
        english_example_button = ctk.CTkButton(
            examples_container,
            text='🇬🇧 "Hello! I want to practice..."',
            command=lambda: self._set_input_text("Hello! I want to practice my English."),
            fg_color=COLOR_BACKGROUND_LIGHT,
            hover_color=COLOR_HOVER_EFFECT,
            text_color=COLOR_TEXT_PRIMARY,
            font=ctk.CTkFont(size=12),
            height=40
        )
        english_example_button.pack(pady=4)
    
    def _set_input_text(self, text_to_insert: str) -> None:
        """Define o texto no campo de input."""
        self.message_input_textbox.delete("1.0", "end")
        self.message_input_textbox.insert("1.0", text_to_insert)
    
    def _on_enter_key_press(self, event) -> Optional[str]:
        """Trata o pressionamento da tecla Enter."""
        if not event.state & 0x1:
            self.send_user_message()
            return "break"
    
    def update_chat_header(self, new_session_name: str) -> None:
        """Atualiza o cabeçalho do chat com o nome da sessão."""
        self.session_title_label.configure(text=new_session_name)
    
    def clear_all_messages(self) -> None:
        """Remove todas as mensagens exibidas."""
        for widget in self.messages_display_frame.winfo_children():
            widget.destroy()
    
    def display_single_message(self, message_text: str, message_sender: str) -> None:
        """Exibe uma única mensagem na área de chat."""
        is_user_message: bool = (message_sender == "user")
        
        message_bubble_frame = ctk.CTkFrame(self.messages_display_frame, fg_color="transparent")
        message_bubble_frame.pack(fill="x", pady=8)
        
        if is_user_message:
            message_bubble_frame.pack(anchor="e")
            
            message_bubble = ctk.CTkFrame(
                message_bubble_frame,
                fg_color=COLOR_ACCENT_BLUE,
                corner_radius=16
            )
            message_bubble.pack(anchor="e", padx=(100, 0))
            
            sender_name_label = ctk.CTkLabel(
                message_bubble,
                text="Você",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=COLOR_BACKGROUND_DARK
            )
            sender_name_label.pack(anchor="e", padx=16, pady=(8, 0))
        else:
            message_bubble_frame.pack(anchor="w")
            
            avatar_container = ctk.CTkFrame(message_bubble_frame, fg_color="transparent", width=36)
            avatar_container.pack(side="left", padx=(0, 8))
            avatar_container.pack_propagate(False)
            
            avatar_emoji_label = ctk.CTkLabel(
                avatar_container,
                text="🎓",
                font=ctk.CTkFont(size=20)
            )
            avatar_emoji_label.pack(pady=4)
            
            message_bubble = ctk.CTkFrame(
                message_bubble_frame,
                fg_color=COLOR_BACKGROUND_LIGHT,
                corner_radius=16
            )
            message_bubble.pack(anchor="w", side="left")
            
            sender_name_label = ctk.CTkLabel(
                message_bubble,
                text="Professor",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=COLOR_TEXT_MUTED
            )
            sender_name_label.pack(anchor="w", padx=16, pady=(8, 0))
        
        message_content_label = ctk.CTkLabel(
            message_bubble,
            text=message_text,
            font=ctk.CTkFont(size=15),
            text_color=COLOR_BACKGROUND_DARK if is_user_message else COLOR_TEXT_PRIMARY,
            justify="left",
            wraplength=MESSAGE_BUBBLE_WRAP_LENGTH
        )
        message_content_label.pack(padx=16, pady=(4, 12))
    
    def show_typing_indicator(self) -> None:
        """Mostra o indicador de que a IA está digitando."""
        self.typing_indicator_frame = ctk.CTkFrame(self.messages_display_frame, fg_color="transparent")
        self.typing_indicator_frame.pack(fill="x", pady=8)
        
        typing_text_label = ctk.CTkLabel(
            self.typing_indicator_frame,
            text="Professor está digitando...",
            font=ctk.CTkFont(size=12),
            text_color=COLOR_TEXT_MUTED
        )
        typing_text_label.pack(anchor="w")
    
    def hide_typing_indicator(self) -> None:
        """Esconde o indicador de digitação."""
        if hasattr(self, 'typing_indicator_frame'):
            self.typing_indicator_frame.destroy()
    
    def send_user_message(self) -> None:
        """Envia a mensagem do usuário para a IA."""
        if self.is_currently_loading:
            return
        
        user_input_text: str = self.message_input_textbox.get("1.0", "end").strip()
        if not user_input_text:
            return
        
        current_active_session: Optional[Session] = self.session_manager.get_current_active_session()
        if not current_active_session:
            messagebox.showwarning("Aviso", "Selecione ou crie uma sessão primeiro!")
            return
        
        self.is_currently_loading = True
        self.message_input_textbox.delete("1.0", "end")
        
        self.display_single_message(user_input_text, "user")
        current_active_session.add_new_message(user_input_text, "user")
        
        if len(current_active_session.message_history) == 1:
            auto_generated_name: str = user_input_text[:50] + ("..." if len(user_input_text) > 50 else "")
            self.session_manager.update_session_name_by_id(current_active_session.session_id, auto_generated_name)
            self.update_chat_header(auto_generated_name)
        
        self.session_manager.save_all_sessions()
        
        self.show_typing_indicator()
        self.send_message_button.configure(state="disabled")
        
        ai_response_thread = threading.Thread(
            target=self._request_ai_response,
            args=(current_active_session,),
            daemon=True
        )
        ai_response_thread.start()
    
    def _request_ai_response(self, current_session: Session) -> None:
        """Solicita uma resposta da IA em background."""
        try:
            ai_response_text: str = self.groq_service.send_message_to_ai(current_session.message_history)
            
            current_session.add_new_message(ai_response_text, "assistant")
            self.session_manager.save_all_sessions()
            
            self.after(0, self._display_ai_response, ai_response_text)
        except Exception as error:
            self.after(0, self._display_error_message, str(error))
    
    def _display_ai_response(self, response_text: str) -> None:
        """Exibe a resposta da IA na interface."""
        self.hide_typing_indicator()
        self.display_single_message(response_text, "assistant")
        self.is_currently_loading = False
        self.send_message_button.configure(state="normal")
    
    def _display_error_message(self, error_text: str) -> None:
        """Exibe uma mensagem de erro na interface."""
        self.hide_typing_indicator()
        self.display_single_message(f"❌ Erro: {error_text}", "assistant")
        self.is_currently_loading = False
        self.send_message_button.configure(state="normal")


# ============================================================
# COMPONENTE: PAINEL DO TRADUTOR
# ============================================================
class TranslatorPanel(ctk.CTkFrame):
    """Painel do Google Tradutor integrado."""
    
    def __init__(self, parent_widget, translate_service_instance: TranslateService):
        super().__init__(parent_widget, fg_color=COLOR_BACKGROUND_MEDIUM, corner_radius=0, height=185)
        self.pack_propagate(False)
        
        self.translate_service = translate_service_instance
        self.current_translation_direction: str = "pt-en"
        
        self._create_translator_widgets()
    
    def _create_translator_widgets(self) -> None:
        """Cria todos os widgets do tradutor."""
        translator_header = ctk.CTkFrame(self, fg_color="transparent")
        translator_header.pack(fill="x", padx=12, pady=(8, 4))
        
        translator_title_label = ctk.CTkLabel(
            translator_header,
            text="🌐 Tradutor",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY
        )
        translator_title_label.pack(side="left")
        
        swap_languages_button = ctk.CTkButton(
            translator_header,
            text="⇄",
            width=28,
            height=28,
            fg_color="transparent",
            hover_color=COLOR_BACKGROUND_LIGHT,
            text_color=COLOR_TEXT_MUTED,
            font=ctk.CTkFont(size=12),
            command=self._swap_translation_direction
        )
        swap_languages_button.pack(side="right")
        
        direction_display_frame = ctk.CTkFrame(self, fg_color="transparent")
        direction_display_frame.pack(fill="x", padx=12, pady=(0, 4))
        
        self.direction_display_label = ctk.CTkLabel(
            direction_display_frame,
            text="PT → EN",
            font=ctk.CTkFont(size=10),
            text_color=COLOR_ACCENT_BLUE
        )
        self.direction_display_label.pack()
        
        self.translation_input_textbox = ctk.CTkTextbox(
            self,
            height=40,
            fg_color=COLOR_BACKGROUND_LIGHT,
            text_color=COLOR_TEXT_PRIMARY,
            font=ctk.CTkFont(size=11),
            border_width=1,
            border_color=COLOR_HOVER_EFFECT,
            corner_radius=6
        )
        self.translation_input_textbox.pack(fill="x", padx=12, pady=(0, 4))
        self.translation_input_textbox.bind("<Return>", self._on_enter_key_in_translator)
        
        translate_action_button = ctk.CTkButton(
            self,
            text="Traduzir",
            fg_color=COLOR_ACCENT_BLUE,
            hover_color=COLOR_ACCENT_HOVER,
            text_color=COLOR_BACKGROUND_DARK,
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.execute_translation,
            height=28
        )
        translate_action_button.pack(fill="x", padx=12, pady=(0, 4))
        
        self.translation_output_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.translation_output_frame.pack(fill="x", padx=12, pady=(0, 4))
        
        self.translation_output_textbox = ctk.CTkTextbox(
            self.translation_output_frame,
            height=50,
            fg_color=COLOR_BACKGROUND_LIGHT,
            text_color=COLOR_TEXT_PRIMARY,
            font=ctk.CTkFont(size=11),
            border_width=1,
            border_color=COLOR_HOVER_EFFECT,
            corner_radius=6,
            state="disabled"
        )
        self.translation_output_textbox.pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        copy_translation_button = ctk.CTkButton(
            self.translation_output_frame,
            text="📋",
            width=30,
            height=30,
            fg_color=COLOR_BACKGROUND_LIGHT,
            hover_color=COLOR_HOVER_EFFECT,
            text_color=COLOR_TEXT_PRIMARY,
            font=ctk.CTkFont(size=12),
            command=self._copy_translation_to_clipboard
        )
        copy_translation_button.pack(side="right")
    
    def _on_enter_key_in_translator(self, event) -> Optional[str]:
        """Trata o Enter no campo de tradução."""
        self.execute_translation()
        return "break"
    
    def _swap_translation_direction(self) -> None:
        """Inverte a direção da tradução."""
        if self.current_translation_direction == "pt-en":
            self.current_translation_direction = "en-pt"
            self.direction_display_label.configure(text="EN → PT")
        else:
            self.current_translation_direction = "pt-en"
            self.direction_display_label.configure(text="PT → EN")
    
    def execute_translation(self) -> None:
        """Executa a tradução do texto."""
        input_text: str = self.translation_input_textbox.get("1.0", "end").strip()
        if not input_text:
            return
        
        source_lang, target_lang = self.current_translation_direction.split("-")
        
        try:
            translation_result = self.translate_service.translate_text(
                input_text, source_lang, target_lang
            )
            
            self.translation_output_textbox.configure(state="normal")
            self.translation_output_textbox.delete("1.0", "end")
            self.translation_output_textbox.insert("1.0", translation_result["translated_text"])
            self.translation_output_textbox.configure(state="disabled")
        except Exception as error:
            messagebox.showerror("Erro de Tradução", str(error))
    
    def _copy_translation_to_clipboard(self) -> None:
        """Copia a tradução para a área de transferência."""
        translated_text: str = self.translation_output_textbox.get("1.0", "end").strip()
        if translated_text:
            self.clipboard_clear()
            self.clipboard_append(translated_text)


# ============================================================
# APLICAÇÃO PRINCIPAL
# ============================================================
class EnglishTeacherApp(ctk.CTk):
    """Janela principal da aplicação English Teacher."""
    
    def __init__(self):
        super().__init__()
        
        self.title("English Teacher")
        self.geometry("1200x700")
        self.minsize(900, 600)
        
        self.session_manager = SessionManager()
        
        try:
            self.groq_service = GroqService()
        except ValueError as config_error:
            messagebox.showerror("Erro de Configuração", str(config_error))
            self.groq_service = None
        
        self.translate_service = TranslateService()
        
        self._create_main_application_layout()
    
    def _create_main_application_layout(self) -> None:
        """Cria o layout principal da aplicação."""
        self.sidebar_container = ctk.CTkFrame(
            self,
            fg_color=COLOR_BACKGROUND_MEDIUM,
            width=SIDEBAR_WIDTH_PIXELS,
            corner_radius=0
        )
        self.sidebar_container.pack(side="left", fill="y")
        self.sidebar_container.pack_propagate(False)
        
        sidebar_header = ctk.CTkFrame(self.sidebar_container, fg_color="transparent")
        sidebar_header.pack(fill="x", padx=16, pady=(16, 8))
        
        application_title = ctk.CTkLabel(
            sidebar_header,
            text="English Teacher",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY
        )
        application_title.pack(anchor="w")
        
        new_session_button = ctk.CTkButton(
            sidebar_header,
            text="+ Nova Sessão",
            command=self._create_new_session,
            fg_color=COLOR_ACCENT_BLUE,
            hover_color=COLOR_ACCENT_HOVER,
            text_color=COLOR_BACKGROUND_DARK,
            font=ctk.CTkFont(weight="bold"),
            height=BUTTON_HEIGHT_PIXELS
        )
        new_session_button.pack(fill="x", pady=(12, 0))
        
        self.sessions_list_frame = ctk.CTkScrollableFrame(
            self.sidebar_container,
            fg_color="transparent",
            scrollbar_button_color=COLOR_HOVER_EFFECT,
            scrollbar_button_hover_color="#585b70",
            height=320
        )
        self.sessions_list_frame.pack(fill="x", padx=8, pady=(8, 8))
        
        separator_line = ctk.CTkFrame(self.sidebar_container, height=1, fg_color=COLOR_HOVER_EFFECT)
        separator_line.pack(fill="x", padx=12, pady=(4, 4))
        
        self.translator_panel = TranslatorPanel(self.sidebar_container, self.translate_service)
        self.translator_panel.pack(fill="x", padx=8, pady=(0, 8))
        
        self.main_content_frame = ctk.CTkFrame(self, fg_color=COLOR_BACKGROUND_DARK, corner_radius=0)
        self.main_content_frame.pack(side="left", fill="both", expand=True)
        
        self.chat_area = ChatAreaPanel(self.main_content_frame, self.groq_service, self.session_manager)
        self.chat_area.pack(fill="both", expand=True)
        
        self._refresh_sessions_display()
    
    def _create_new_session(self) -> None:
        """Cria uma nova sessão de conversação."""
        new_session: Session = self.session_manager.create_new_session()
        self._refresh_sessions_display()
        self.chat_area.update_chat_header(new_session.session_name)
        self.chat_area.clear_all_messages()
        
        if not self.groq_service:
            messagebox.showwarning(
                "API Não Configurada",
                "Configure sua GROQ_API_KEY no arquivo .env"
            )
    
    def _select_session(self, target_session_id: str) -> None:
        """Seleciona uma sessão existente."""
        self.session_manager.set_session_as_active(target_session_id)
        self._refresh_sessions_display()
        
        selected_session: Optional[Session] = self.session_manager.get_current_active_session()
        if selected_session:
            self.chat_area.update_chat_header(selected_session.session_name)
            self.chat_area.clear_all_messages()
            
            for single_message in selected_session.message_history:
                self.chat_area.display_single_message(
                    single_message["message_text"],
                    single_message["message_sender"]
                )
    
    def _refresh_sessions_display(self) -> None:
        """Atualiza a exibição da lista de sessões na sidebar."""
        for existing_widget in self.sessions_list_frame.winfo_children():
            existing_widget.destroy()
        
        if not self.session_manager.all_sessions:
            empty_sessions_label = ctk.CTkLabel(
                self.sessions_list_frame,
                text="Nenhuma sessão ainda",
                text_color=COLOR_TEXT_MUTED,
                font=ctk.CTkFont(size=12)
            )
            empty_sessions_label.pack(pady=20)
            return
        
        for single_session in self.session_manager.all_sessions:
            is_active_session: bool = (
                single_session.session_id == self.session_manager.active_session_identifier
            )
            
            session_item_frame = ctk.CTkFrame(
                self.sessions_list_frame,
                fg_color=COLOR_BACKGROUND_LIGHT if is_active_session else "transparent",
                corner_radius=8,
                border_width=2 if is_active_session else 0,
                border_color=COLOR_ACCENT_BLUE
            )
            session_item_frame.pack(fill="x", pady=2)
            
            session_button = ctk.CTkButton(
                session_item_frame,
                text=single_session.session_name,
                anchor="w",
                fg_color="transparent",
                hover_color=COLOR_HOVER_EFFECT,
                text_color=COLOR_TEXT_PRIMARY,
                font=ctk.CTkFont(size=13),
                command=lambda sid=single_session.session_id: self._select_session(sid),
                height=40
            )
            session_button.pack(fill="x", padx=4, pady=4, side="left", expand=True)
            
            session_date_label = ctk.CTkLabel(
                session_item_frame,
                text=datetime.fromisoformat(single_session.created_at_timestamp).strftime("%d/%m"),
                text_color=COLOR_TEXT_MUTED,
                font=ctk.CTkFont(size=10)
            )
            session_date_label.pack(side="right", padx=12)


# ============================================================
# PONTO DE ENTRADA DA APLICAÇÃO
# ============================================================
def main():
    """Inicia a aplicação English Teacher."""
    application = EnglishTeacherApp()
    application.mainloop()


if __name__ == "__main__":
    main()
