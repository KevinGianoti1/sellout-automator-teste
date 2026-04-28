# Relatório Comercial Diário

Script Python que busca dados da view `relatorio_comercial_diario` no Supabase,
gera um relatório HTML estilizado e envia por e-mail e WhatsApp.

## Requisitos

- Python 3.9+
- Dependências: `pip install requests python-dotenv`

## Configuração

1. Copie `.env.example` para `.env` e preencha todas as variáveis:

```bash
cp .env.example .env
```

### Variáveis obrigatórias

| Variável | Descrição |
|---|---|
| `SUPABASE_URL` | URL do projeto Supabase |
| `SUPABASE_KEY` | Chave `anon` ou `service_role` |

### Variáveis para e-mail

| Variável | Descrição |
|---|---|
| `EMAIL_USER` | Conta Gmail remetente |
| `EMAIL_PASSWORD` | [Senha de App do Gmail](https://myaccount.google.com/apppasswords) |
| `EMAIL_TO` | Destinatários separados por vírgula |

> **Atenção:** Use **Senha de App**, não a senha normal da conta Google. Ative a verificação em 2 etapas antes de gerar.

### Variáveis para WhatsApp (Evolution API)

| Variável | Descrição |
|---|---|
| `EVOLUTION_API_URL` | URL base da Evolution API |
| `EVOLUTION_API_KEY` | Chave de API (se configurada) |
| `EVOLUTION_INSTANCE` | Nome da instância |
| `WHATSAPP_NUMBERS` | Números no formato `5511999999999`, separados por vírgula |

## Uso

```bash
# Relatório do dia mais recente no banco
python relatorio_diario.py

# Relatório de uma data específica
python relatorio_diario.py --date 2024-04-15

# Gera apenas o HTML (sem enviar e-mail/WhatsApp)
python relatorio_diario.py --html-only

# Define nome do arquivo HTML gerado
python relatorio_diario.py --output meu_relatorio.html
```

## Automação (cron)

Para rodar todo dia às 18h:

```cron
0 18 * * 1-5 cd /caminho/do/projeto && /usr/bin/python3 relatorio_diario.py >> /var/log/relatorio.log 2>&1
```

## Estrutura do Projeto

```
relatorio_diario.py     # Script principal
.env                    # Variáveis de ambiente (não commitar)
.env.example            # Template de variáveis
requirements.txt        # Dependências Python
README_relatorio_diario.md
```

## Saída

- `relatorio_diario.html` — relatório HTML gerado localmente
- E-mail HTML enviado aos destinatários configurados
- Mensagem de texto WhatsApp enviada aos números configurados
