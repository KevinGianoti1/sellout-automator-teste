import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
import os
from typing import List, Optional
from datetime import datetime

class EmailAutomator:
    """Gerencia envio automático de emails com relatórios."""

    def __init__(self, smtp_server: str, smtp_port: int, email_user: str, email_password: str):
        """
        Inicializa configurações de SMTP.

        Args:
            smtp_server: Servidor SMTP (ex: smtp.gmail.com)
            smtp_port: Porta SMTP (ex: 587 para TLS)
            email_user: Email do remetente
            email_password: Senha do email
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email_user = email_user
        self.email_password = email_password

    def enviar_email(
        self,
        destinatarios: List[str],
        assunto: str,
        corpo_html: str,
        anexo_path: Optional[str] = None,
        nome_anexo: Optional[str] = None
    ) -> bool:
        """
        Envia email com corpo HTML e anexo opcional.

        Args:
            destinatarios: Lista de emails destinatários
            assunto: Assunto do email
            corpo_html: Corpo do email em HTML
            anexo_path: (Opcional) Caminho do arquivo anexo
            nome_anexo: (Opcional) Nome para exibir do anexo

        Returns:
            True se enviado com sucesso, False caso contrário
        """
        try:
            # Criar mensagem
            msg = MIMEMultipart('alternative')
            msg['Subject'] = assunto
            msg['From'] = self.email_user
            msg['To'] = ', '.join(destinatarios)

            # Adicionar corpo HTML
            parte_html = MIMEText(corpo_html, 'html', 'utf-8')
            msg.attach(parte_html)

            # Adicionar anexo se fornecido
            if anexo_path and os.path.exists(anexo_path):
                with open(anexo_path, 'rb') as attachment:
                    part = MIMEApplication(attachment.read(), Name=nome_anexo or os.path.basename(anexo_path))
                part['Content-Disposition'] = f'attachment; filename="{nome_anexo or os.path.basename(anexo_path)}"'
                msg.attach(part)

            # Conectar ao servidor SMTP e enviar
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)

            print(f"OK: Email enviado com sucesso para {', '.join(destinatarios)}")
            return True

        except smtplib.SMTPAuthenticationError:
            print(f"ERRO: Erro de autenticação SMTP. Verifique email e senha.")
            return False
        except Exception as e:
            print(f"ERRO: Erro ao enviar email: {str(e)}")
            return False

    def enviar_relatorio_rd_station(
        self,
        destinatarios: List[str],
        corpo_html: str,
        arquivo_excel: Optional[str] = None,
        assunto: Optional[str] = None,
        anexos_extras: Optional[List[str]] = None,
    ) -> bool:
        """Envia relatorio RD Station com ate N anexos."""
        data_atual = datetime.now().strftime("%d/%m/%Y")
        assunto = assunto or f"Relatorio de Leads - RD Station - {data_atual}"

        try:
            msg = MIMEMultipart('mixed')
            msg['Subject'] = assunto
            msg['From'] = self.email_user
            msg['To'] = ', '.join(destinatarios)

            msg.attach(MIMEText(corpo_html, 'html', 'utf-8'))

            todos_anexos = []
            if arquivo_excel:
                todos_anexos.append(arquivo_excel)
            if anexos_extras:
                todos_anexos.extend(anexos_extras)

            for path in todos_anexos:
                if path and os.path.exists(path):
                    with open(path, 'rb') as f:
                        part = MIMEApplication(f.read(), Name=os.path.basename(path))
                    part['Content-Disposition'] = f'attachment; filename="{os.path.basename(path)}"'
                    msg.attach(part)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)

            print(f"OK: Email enviado para {', '.join(destinatarios)} ({len(todos_anexos)} anexo(s))")
            return True

        except smtplib.SMTPAuthenticationError:
            print("ERRO: Autenticacao SMTP falhou. Verifique email e senha.")
            return False
        except Exception as e:
            print(f"ERRO: {e}")
            return False

def get_email_client() -> EmailAutomator:
    """
    Factory para criar cliente de email com credenciais de variáveis de ambiente.

    Returns:
        Instância de EmailAutomator

    Raises:
        ValueError: Se credenciais não estão configuradas
    """
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = os.getenv('SMTP_PORT', '587')
    email_user = os.getenv('EMAIL_USER')
    email_password = os.getenv('EMAIL_PASSWORD')

    if not all([smtp_server, email_user, email_password]):
        raise ValueError(
            "Credenciais de email não configuradas. "
            "Configure: SMTP_SERVER, SMTP_PORT, EMAIL_USER, EMAIL_PASSWORD"
        )

    return EmailAutomator(
        smtp_server=smtp_server,
        smtp_port=int(smtp_port),
        email_user=email_user,
        email_password=email_password
    )

# Configurações pré-definidas para provedores comuns
SMTP_CONFIGS = {
    'gmail': {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587
    },
    'outlook': {
        'smtp_server': 'smtp-mail.outlook.com',
        'smtp_port': 587
    },
    'hotmail': {
        'smtp_server': 'smtp.hotmail.com',
        'smtp_port': 587
    }
}

def get_email_client_by_provider(provider: str, email_user: str, email_password: str) -> EmailAutomator:
    """
    Factory para criar cliente com provedor pré-configurado.

    Args:
        provider: 'gmail', 'outlook', 'hotmail' ou personalizado
        email_user: Email do remetente
        email_password: Senha do email

    Returns:
        Instância de EmailAutomator
    """
    if provider in SMTP_CONFIGS:
        config = SMTP_CONFIGS[provider]
        return EmailAutomator(
            smtp_server=config['smtp_server'],
            smtp_port=config['smtp_port'],
            email_user=email_user,
            email_password=email_password
        )
    else:
        raise ValueError(f"Provedor '{provider}' não suportado. Use: {list(SMTP_CONFIGS.keys())}")
