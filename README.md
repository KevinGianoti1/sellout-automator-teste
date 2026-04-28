# 📊 Relatório Comercial Diário

Automação completa de **relatório comercial diário em HTML** com envio via **e-mail** e **WhatsApp**, integrado com **Supabase**.

---

## 🚀 Quick Start

### 1. Configurar credenciais
```bash
# Copie o template
cp .env.example .env

# Edite o .env com suas credenciais (Supabase, Gmail, WhatsApp)
```

> ⚠️ **Gmail**: Use **Senha de App**, não a senha normal. Gere em https://myaccount.google.com/apppasswords

### 2. Instalar dependências
```bash
pip install requests python-dotenv
```

### 3. Testar (modo teste)
```bash
# Busca dados de hoje, gera HTML e envia para TEST_EMAIL
python relatorio_diario.py
```

Esperado:
```
✅ HTML salvo em output/relatorio_teste.html
✅ E-mail enviado para seu_email_de_teste@gmail.com
```

### 4. Produção (modo normal)
```bash
# Gera HTML e envia para EMAIL_TO via e-mail + WhatsApp
python relatorio_diario.py --html-only
```

---

## 📁 Estrutura do Projeto

```
.
├── relatorio_diario.py            # Script principal
├── agendar_relatorio.bat           # Automação Windows (tarefa agendada)
├── .env                            # Variáveis de ambiente (NÃO commitar)
├── .env.example                    # Template de .env
├── .gitignore                      # Ignore para git
├── requirements.txt                # Dependências Python
├── output/                         # 📁 Relatórios HTML gerados
│   ├── relatorio_diario.html
│   └── relatorio_teste.html
├── logs/                           # 📁 Logs de execução
│   └── relatorio_*.log
└── README.md                       # Este arquivo
```

---

## 🔧 Opções de Uso

### Modo Teste
```bash
python relatorio_diario.py
```
- ✅ Busca dados **de hoje** em Brasília (UTC-3)
- ✅ Gera `output/relatorio_teste.html`
- ✅ Envia para `TEST_EMAIL` do `.env`

### Modo Produção (HTML-only)
```bash
python relatorio_diario.py --html-only
```
- Gera `output/relatorio_diario.html`
- Envia para `EMAIL_TO`
- Envia WhatsApp se configurado

### Data Específica
```bash
python relatorio_diario.py --date 2024-04-15
```

### Output customizado
```bash
python relatorio_diario.py --output meus_relatorios/relatorio.html
```

---

## 📧 E-mail

### Estrutura
- **Assunto dinâmico**: `📊 Relatório Comercial Diário - DATA | Projeção: R$ VALOR`
- **Corpo**: HTML responsivo + tabela resumida de KPIs
- **Anexo**: HTML completo para download

### Compatibilidade
- ✅ Gmail
- ✅ Outlook
- ✅ Apple Mail
- ✅ Clientes mobile

---

## 💬 WhatsApp (Evolution API)

Envia mensagem de texto formatada para número(s) configurados em `WHATSAPP_NUMBERS`.

```
📊 *Relatório Comercial - 28/04/2024*
Mês: ABRIL

👥 Total de vendedores: *5*
✅ Atingiram a meta: *3* (60,00%)
💰 Projeção total: *R$ 125.000,00*
🎯 Meta mensal total: *R$ 100.000,00*
📈 % Global atingido: *125,00%*

*PYRAMID*
  ✅ João Silva — 95,00% da meta mensal
  ✅ Maria Santos — 110,00% da meta mensal
...
```

---

## ⏰ Automação Windows (Agendador de Tarefas)

1. Edite o arquivo `agendar_relatorio.bat` — defina o caminho correto em `PROJECT_DIR`
2. Abra o Agendador de Tarefas: `Win+R` → `taskschd.msc`
3. Crie uma nova tarefa básica:
   - **Nome**: Relatório Comercial Diário
   - **Trigger**: Diariamente às 18:00
   - **Action**: Executar `agendar_relatorio.bat`
   - **Segurança**: ✅ Executar com privilégios máximos
   - **Segurança**: ✅ Executar mesmo se usuário não estiver logado

4. Verifique os logs em `logs/relatorio_diario.log`

---

## 📊 HTML Gerado

### Design
- ✨ Gradiente no cabeçalho
- 📱 Responsivo (mobile-first)
- 🎨 Barras de progresso coloridas
- 🏷️ Badges de status (META BATIDA, QUASE, ABAIXO)
- 🌙 Dark mode automático
- ♿ Acessível com tooltips

### Cards Executivos
- Total de vendedores
- % que atingiu a meta
- Projeção total
- Meta mensal total
- % Global com barra

### Tabela de Vendedores
| Coluna | Descrição |
|---|---|
| Equipe | Nome da equipe (agrupado visualmente) |
| Vendedor | Nome + ⭐ se atingiu meta |
| Projeção | Pedidos com alta probabilidade |
| Proc. Fat. | Pedidos em faturamento |
| Rem. Futura | Pedidos para entrega futura |
| Orc. Aberto | Orçamentos não fechados |
| Total Comp. | Soma de tudo acima |
| Meta Diária | Meta proporcional ao dia |
| Meta Mensal | Meta do mês inteiro |
| % Meta Mensal | **Barra + % colorida** |
| Status | Badge (ATINGIU/QUASE/ABAIXO) |
| Falta Mensal | Quanto falta para atingir |

---

## 🔑 Variáveis de Ambiente (`.env`)

```bash
# Supabase
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-chave-aqui

# Gmail SMTP
EMAIL_USER=seu_email@gmail.com
EMAIL_PASSWORD=senha_de_app_aqui
EMAIL_TO=destinatario1@empresa.com,destinatario2@empresa.com
TEST_EMAIL=seu_email_de_teste@gmail.com

# WhatsApp (Evolution API)
EVOLUTION_API_URL=https://sua-evolution-api.com
EVOLUTION_API_KEY=sua-chave-aqui
EVOLUTION_INSTANCE=nome-instancia
WHATSAPP_NUMBERS=5511999999999,5521988888888
```

---

## 🐛 Solução de Problemas

### "Nenhum dado encontrado"
- Verifique se a view `relatorio_comercial_diario` existe no Supabase
- Verifique se há dados para a data de hoje em Brasília

### "Erro ao enviar e-mail"
- Verifique `EMAIL_USER`, `EMAIL_PASSWORD` (senha de app, não a normal)
- Se usar 2FA, gere uma senha de app em https://myaccount.google.com/apppasswords
- Verifique internet

### "Erro de fuso horário"
- O script usa Brasília (UTC-3) por padrão
- Para outra zona, edite `fetch_relatorio()`: mude `timedelta(hours=-3)` para seu fuso

---

## 📝 Logs

Logs são salvos em `logs/relatorio_YYYYMMDD_HHMM.log`

Acesso rápido: `logs/relatorio_diario.log` (sempre o último)

```
2024-04-28 18:30:45 [INFO] === Relatório Comercial Diário ===
2024-04-28 18:30:45 [INFO] Data atual em Brasília (UTC-3): 2024-04-28
2024-04-28 18:30:46 [INFO] Registros carregados: 8
2024-04-28 18:30:46 [INFO] Resumo: 8 vendedores, 6 atingiram meta (75.0%), projeção total R$ 150.000,00
2024-04-28 18:30:46 [INFO] HTML salvo em: output/relatorio_diario.html
2024-04-28 18:30:47 [INFO] E-mail enviado para: ['analista.vendas@mfferramentas.com.br']
2024-04-28 18:30:47 [INFO] === Concluído ===
```

---

## 📄 Licença

Desenvolvido com ❤️ para MAXIFORCE

---

## 📞 Suporte

Dúvidas? Verifique os logs (`logs/relatorio_diario.log`) ou ajuste as variáveis de ambiente.
