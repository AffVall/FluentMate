#!/bin/bash

echo "=== English Teacher - Instalação ==="
echo ""

echo "Criando ambiente virtual..."
python3 -m venv venv

echo "Ativando ambiente virtual..."
source venv/bin/activate

echo "Instalando dependências..."
pip install -r requirements.txt

echo ""
echo "=== Instalação concluída! ==="
echo ""
echo "Para executar:"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
