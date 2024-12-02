import os
import requests
from requests.exceptions import RequestException


def send_password_reset_email(email, reset_url):
    """
    Envia um e-mail de redefinição de senha para o destinatário especificado.

    :param email: Endereço de e-mail do destinatário.
    :param reset_url: URL para redefinição de senha.
    :raises RequestException: Em caso de erro no envio do e-mail.
    """
    try:
        api_key = os.environ.get('EMAIL_SERVICE_API_KEY')
        domain_name = os.environ.get('EMAIL_SERVICE_DOMAIN_NAME')
        sender = os.environ.get('EMAIL_SENDER')
        
        service_url = f"https://api.mailgun.net/v3/{domain_name}/messages"
        
        if not all([api_key, domain_name, sender]):
            raise ValueError("Erro nas configurações necessárias para envio do email.")
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    background-color: #f9f9f9;
                }}
                .header {{
                    text-align: center;
                    padding-bottom: 20px;
                    border-bottom: 1px solid #ddd;
                }}
                .content {{
                    padding: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    padding-top: 20px;
                    font-size: 0.9em;
                    color: #888;
                }}
                .cta-button {{
                    display: inline-block;
                    padding: 10px 20px;
                    color: #fff;
                    background-color: #007BFF;
                    text-decoration: none;
                    border-radius: 5px;
                    margin-top: 20px;
                }}
                .cta-button:hover {{
                    background-color: #0056b3;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Redefinição de Senha</h1>
                </div>
                <div class="content">
                    <p>Olá,</p>
                    <p>Você solicitou a redefinição da sua senha. Clique no botão abaixo para redefinir sua senha:</p>
                    <p style="text-align: center;">
                        <a href="{reset_url}" class="cta-button">Redefinir Senha</a>
                    </p>
                    <p>
                        Por motivos de segurança, este link será válido apenas por 24 horas. 
                        Caso não realize a redefinição nesse período, será necessário solicitar novamente.
                    </p>
                    <p>Se você não solicitou a redefinição de senha, ignore este e-mail.</p>
                </div>
                <div class="footer">
                    <p>Equipe de Suporte - SGM</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        plain_text_content = f"""
        Olá,

        Você solicitou a redefinição da sua senha. Clique no link abaixo para redefinir sua senha:

        {reset_url}
        
        Por motivos de segurança, este link será válido apenas por 24 horas. 
        Caso não realize a redefinição nesse período, será necessário solicitar novamente.

        Se você não solicitou a redefinição de senha, ignore este e-mail.

        Equipe de Suporte - SGM
        """
        
        response = requests.post(
            url=service_url,
            auth=('api', api_key),
            data={
                'from': f'SGM Suporte <{sender}>',
                'to': email,
                'subject': 'Redefinição de senha',
                'text': plain_text_content,
                'html': html_content,
            }
        )
        response.raise_for_status()
        
    except RequestException as re:
        raise RequestException(f"Erro ao enviar o email para o destinatário: {re}")

def send_password_reset_confirmation(email, name):
    """
    Método para enviar um email ao usuário confirmando que a senha foi alterada
    
    :param email: Email do usuário
    :param name: Nome do usuário
    """
    try:
        api_key = os.environ.get('EMAIL_SERVICE_API_KEY')
        domain_name = os.environ.get('EMAIL_SERVICE_DOMAIN_NAME')
        sender = os.environ.get('EMAIL_SENDER')
        
        service_url = f"https://api.mailgun.net/v3/{domain_name}/messages"
        
        if not all([api_key, domain_name, sender]):
            raise ValueError("Erro nas configurações necessárias para envio do email.")
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="pt-br">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #fff;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                }}
                .header {{
                    text-align: center;
                    padding-bottom: 20px;
                    border-bottom: 1px solid #ddd;
                }}
                .content {{
                    padding: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    padding-top: 20px;
                    font-size: 0.9em;
                    color: #888;
                }}
                .cta-button {{
                    display: inline-block;
                    padding: 10px 20px;
                    color: #fff;
                    background-color: #007BFF;
                    text-decoration: none;
                    border-radius: 5px;
                    margin-top: 20px;
                }}
                .cta-button:hover {{
                    background-color: #0056b3;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Senha Atualizada com Sucesso</h1>
                </div>
                <div class="content">
                    <p>Prezado(a) <strong>{name}</strong>,</p>
                    <p>Informamos que sua senha foi atualizada com sucesso.</p>
                    <p>Se você não solicitou essa alteração, por favor, entre em contato com a nossa equipe de suporte imediatamente.</p>
                    <p>Para mais informações ou caso precise de ajuda adicional, não hesite em nos contatar.</p>
                    
                    <p>Atenciosamente,</p>
                    <p>Equipe de Suporte - SGM</p>
                </div>
                <div class="footer">
                    <p>&copy; 2024 SGM - Todos os direitos reservados.</p>
                    <p>Se você tiver dúvidas ou precisar de mais informações, entre em contato com o suporte pelo e-mail: <a href="mailto:support@sgm.com">support@sgm.com</a>.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        plain_text_content = f"""
        Prezado(a) {name},

        Informamos que sua senha foi atualizada com sucesso.

        Se você não solicitou essa alteração, por favor, entre em contato com a nossa equipe de suporte imediatamente.

        Para mais informações ou caso precise de ajuda adicional, não hesite em nos contatar.

        Atenciosamente,
        Equipe de Suporte - SGM

        --------------------------------------
        Se você tiver dúvidas ou precisar de mais informações, entre em contato com o suporte pelo e-mail: support@sgm.com
        """
        
        response = requests.post(
            url=service_url,
            auth=('api', api_key),
            data={
                'from': f'SGM Suporte <{sender}>',
                'to': email,
                'subject': 'Senha atualizada com Sucesso',
                'text': plain_text_content,
                'html': html_content
            }
        )
        response.raise_for_status()
    
    except RequestException as re:
        raise RequestException(f"Erro ao enviar o email ao destinatário: {re}")
        
        
    
