@echo off
:: ============================================================
:: RELATÓRIO COMERCIAL DIÁRIO — Script de Execução Agendada
:: ============================================================
::
:: COMO CONFIGURAR NO AGENDADOR DE TAREFAS DO WINDOWS
:: ---------------------------------------------------
:: 1. Abrir o Agendador de Tarefas:
::       Pressione Win+R → digite: taskschd.msc → Enter
::
:: 2. Criar nova tarefa básica:
::       Painel direito → "Criar Tarefa Básica..."
::       Nome: Relatorio Comercial Diario
::       Descrição: Gera e envia o relatório comercial diário
::
:: 3. Configurar o TRIGGER (quando executar):
::       Selecione: Diariamente
::       Hora de início: 18:00:00
::       Repetir a cada: 1 dia
::
:: 4. Configurar a ACTION (o que executar):
::       Ação: Iniciar um programa
::       Programa/script: C:\caminho\completo\para\agendar_relatorio.bat
::         (use o botão "Procurar" para navegar até este arquivo)
::
:: 5. Configurações de segurança (ABA "Geral"):
::       ✅ Marque: "Executar com privilégios máximos"
::       ✅ Marque: "Executar mesmo que o usuário não esteja conectado"
::       → Isso abre uma janela pedindo sua senha do Windows
::       Configurar para: Windows 10 / Windows 11
::
:: 6. Configurações extras (ABA "Configurações"):
::       ✅ Permitir que a tarefa seja executada por demanda
::       ✅ Executar a tarefa o mais rápido possível se o início agendado for perdido
::
:: 7. Teste imediato:
::       Após criar, clique com botão direito na tarefa → "Executar"
::       Verifique o arquivo de log: logs\relatorio_diario.log
::
:: ============================================================
:: CONFIGURAÇÃO DO SCRIPT — EDITE AS LINHAS ABAIXO
:: ============================================================

:: Caminho completo do diretório do projeto
set PROJECT_DIR=C:\Users\Maxiforce 01\OneDrive - MAXIFORCE\SALES OPS\RELATORIOS CLAUDE COWORK\.claude\worktrees\thirsty-robinson-d7b290

:: Caminho para o executável Python
:: Opção A — Python do sistema (verifique com: where python)
set PYTHON_EXE=python

:: Opção B — Python de um ambiente virtual (venv)
:: set PYTHON_EXE=%PROJECT_DIR%\venv\Scripts\python.exe

:: Nome do script principal
set SCRIPT_NAME=relatorio_diario.py

:: Diretório de logs (será criado automaticamente)
set LOG_DIR=%PROJECT_DIR%\logs

:: Diretório de output (HTML gerado)
set OUTPUT_DIR=%PROJECT_DIR%\output

:: ============================================================
:: EXECUÇÃO — não edite abaixo desta linha
:: ============================================================

:: Muda para o diretório do projeto
cd /d "%PROJECT_DIR%"
if errorlevel 1 (
    echo [ERRO] Nao foi possivel acessar o diretorio: %PROJECT_DIR%
    exit /b 1
)

:: Cria os diretórios se não existirem
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

:: Monta o nome do arquivo de log com timestamp
for /f "tokens=1-3 delims=/ " %%a in ("%date%") do (
    set DIA=%%a
    set MES=%%b
    set ANO=%%c
)
for /f "tokens=1-2 delims=:." %%a in ("%time%") do (
    set HORA=%%a
    set MIN=%%b
)
:: Remove espaço do horário (ex: " 8" → "08")
set HORA=%HORA: =0%

set LOG_FILE=%LOG_DIR%\relatorio_%ANO%%MES%%DIA%_%HORA%%MIN%.log
set LATEST_LOG=%LOG_DIR%\relatorio_diario.log

echo ============================================================ >> "%LOG_FILE%"
echo Inicio: %date% %time% >> "%LOG_FILE%"
echo Diretorio: %PROJECT_DIR% >> "%LOG_FILE%"
echo Python: %PYTHON_EXE% >> "%LOG_FILE%"
echo ============================================================ >> "%LOG_FILE%"

:: Executa o script Python com output para pasta output/ e redireciona stdout+stderr para o log
"%PYTHON_EXE%" "%SCRIPT_NAME%" --output "%OUTPUT_DIR%\relatorio_diario.html" >> "%LOG_FILE%" 2>&1

:: Verifica o código de retorno
if errorlevel 1 (
    echo [ERRO] O script terminou com erro. Codigo: %errorlevel% >> "%LOG_FILE%"
    echo [ERRO] Verifique o log em: %LOG_FILE%
    :: Copia o log de hoje como "ultimo log" para facilitar diagnóstico
    copy /y "%LOG_FILE%" "%LATEST_LOG%" >nul
    exit /b 1
) else (
    echo [OK] Script executado com sucesso em %date% %time% >> "%LOG_FILE%"
    copy /y "%LOG_FILE%" "%LATEST_LOG%" >nul
    exit /b 0
)
