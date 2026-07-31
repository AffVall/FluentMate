# FluentMate

Aplicativo desktop em Python para praticar inglês com um tutor de IA. Conversas em inglês, correções em tempo real e explicações em português.

## ✨ Funcionalidades

- 🗂️ **Sessões separadas de prática** — organize suas conversas por tópico
- 💬 **Tutor de IA** — converse em inglês com um professor virtual (Llama 3.1 via Groq)
- ✏️ **Correções em tempo real** — erros corrigidos com explicações em português
- 📖 **Modo explicação** — peça "não entendi" e a IA traduz e explica o inglês usado
- 🌐 **Tradutor integrado** — traduza qualquer texto (PT ↔ EN) direto na sidebar
- 💾 **Histórico persistente** — todas as conversas são salvas automaticamente

## 🛠️ Requisitos

- Python 3.10+
- pip

## 🚀 Instalação

### Opção 1: script de instalação

```bash
bash install.sh
```

### Opção 2: manual

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 🔑 Configuração

Crie um arquivo `.env` na raiz do projeto com sua chave da Groq:

```env
GROQ_API_KEY=sua_chave_aqui
```

Obtenha uma chave gratuita em [console.groq.com](https://console.groq.com).

## ▶️ Execução

```bash
source venv/bin/activate
python main.py
```

## 📁 Estrutura do projeto

```text
main.py
src/
  session_manager.py
  services/
    groq_service.py
    translate_service.py
    intents.py
tests/
  test_groq_service_prompt.py
```

## 🧪 Testes

```bash
python3 -m unittest discover tests/ -v
```

## 📄 Licença

Este projeto está licenciado sob uma licença privada e proprietária. Todos os direitos são reservados ao autor do projeto.
