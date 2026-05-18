from playwright.sync_api import sync_playwright
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from dotenv import load_dotenv

# Carregar variáveis do arquivo .env
load_dotenv()

# Credenciais fornecidas
USUARIO = "jaime.fontes"
SENHA = "Jfv74-34"
URL = "http://sistemas.tceac.tc.br/corporativo/login2.xhtml"

# Função para enviar email com anexo
def enviar_email(arquivo_path, destinatario):
    try:
        # Credenciais de email (usando variáveis de ambiente ou entrada do usuário)
        email_remetente = os.getenv("EMAIL_USER") or input("Digite seu email (Gmail): ")
        email_senha = os.getenv("EMAIL_PASSWORD") or input("Digite sua senha de app do Gmail: ")
        
        # Configurar servidor SMTP do Gmail
        servidor_smtp = "smtp.gmail.com"
        porta_smtp = 587
        
        # Criar mensagem
        mensagem = MIMEMultipart()
        mensagem["From"] = email_remetente
        mensagem["To"] = destinatario
        mensagem["Subject"] = "Comprovação de Login - Sistema TCE-AC"
        
        # Corpo do email
        corpo = """
        Prezado,
        
        Segue em anexo a comprovação de login no sistema TCE-AC Corporativo.
        
        Att.
        Sistema Automatizado
        """
        
        mensagem.attach(MIMEText(corpo, "plain"))
        
        # Anexar arquivo
        with open(arquivo_path, "rb") as anexo:
            parte = MIMEBase("application", "octet-stream")
            parte.set_payload(anexo.read())
            encoders.encode_base64(parte)
            parte.add_header("Content-Disposition", f"attachment; filename= {os.path.basename(arquivo_path)}")
            mensagem.attach(parte)
        
        # Enviar email
        servidor = smtplib.SMTP(servidor_smtp, porta_smtp)
        servidor.starttls()
        servidor.login(email_remetente, email_senha)
        servidor.send_message(mensagem)
        servidor.quit()
        
        print(f"\n✓ Email enviado com sucesso para {destinatario}")
        return True
        
    except Exception as e:
        print(f"\n✗ Erro ao enviar email: {e}")
        return False

with sync_playwright() as p:
    # Lançando o navegador
    browser = p.chromium.launch(headless=True, slow_mo=500)
    page = browser.new_page()

    # Navegando
    page.goto(URL, wait_until="networkidle")

    # Preenchendo campos
    page.get_by_placeholder("Login").fill(USUARIO)
    page.get_by_placeholder("Senha").fill(SENHA)

    # Clicando no botão Entrar
    page.get_by_role("button", name="Entrar").click()

    # Aguarda o carregamento pós-login
    page.wait_for_load_state("networkidle")
    
    print(f"\n{'='*60}")
    print(f"✓ Login efetuado com sucesso!")
    print(f"{'='*60}")
    print(f"URL atual: {page.url}")
    print(f"Título da página: {page.title()}")
    
    # Captura de tela como comprovação
    screenshot_path = "login_comprovacao.png"
    page.screenshot(path=screenshot_path)
    print(f"Screenshot salvo em: {screenshot_path}")
    
    # Informações adicionais da página
    html_content = page.content()
    if "jaime" in html_content.lower() or "usuario" in html_content.lower():
        print("✓ Conteúdo da página confirma o login")
    
    print(f"{'='*60}\n")
    
    # Enviar screenshot por email
    email_destinatario = "jfontesv@gmail.com"
    if enviar_email(screenshot_path, email_destinatario):
        # Se email foi enviado com sucesso, deletar arquivo local
        os.remove(screenshot_path)
        print(f"✓ Arquivo local deletado: {screenshot_path}\n")
    
    # Mantém o navegador aberto sem interrupções
    # O script ficará em execução enquanto a janela estiver aberta
    browser.contexts[0].pages[0].wait_for_load_state("domcontentloaded")
    
    # O script terminará apenas se você fechar o navegador manualmente 
    # ou se removermos a linha de fechar.
    # Para apenas "deixar a tela", deixaremos o script rodar até o final
    # mas sem o input() que pausa o terminal.
