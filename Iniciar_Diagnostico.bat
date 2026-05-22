@echo off
cd /d %~dp0

if not exist venv (
    echo Criando venv...
    python -m venv venv
) else (
    echo venv já existe
)

echo Ativando venv...
call venv\Scripts\activate

echo Instalando dependencias...
pip install -r requirements.txt

echo Criando tabelas do banco...
python manage.py migrate

echo Iniciando o navegador...
timeout /t 2 /nobreak
start http://127.0.0.1:8000/painel/

echo Iniciando o programa...
python manage.py runserver
