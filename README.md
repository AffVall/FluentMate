# English Teacher

Aplicativo desktop em Python para praticar inglês com ajuda de IA, com sessões de conversa, correções e explicações em português.

## O que faz

- Cria sessões separadas de prática
- Permite conversar em inglês com um tutor de IA
- Corrige textos e explica erros em português
- Mantém histórico de mensagens por sessão

## Requisitos

- Python 3.10+
- pip

## Instalação

### Opção 1: usando o script de instalação

```bash
bash install.sh
```

### Opção 2: instalação manual

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuração

Crie um arquivo `.env` na raiz do projeto com sua chave da Groq:

```env
GROQ_API_KEY=sua_chave_aqui
```

## Execução

```bash
source venv/bin/activate
python main.py
```

## Estrutura do projeto

```text
main.py
src/
  session_manager.py
  services/
    groq_service.py
    translate_service.py
```

## Licença

Este projeto está licenciado sob uma licença privada e proprietária. Todos os direitos são reservados ao autor do projeto.
