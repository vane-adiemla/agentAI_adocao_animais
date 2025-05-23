# -*- coding: utf-8 -*-
"""Cópia de Cópia de agent_pet

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1bk6N-QpCZX_5bJcDDu5udSzHyNanDqCQ
"""

# Commented out IPython magic to ensure Python compatibility.
# %pip -q install google-genai

# Configura a API Key do Google Gemini

import os
from google.colab import userdata
import os
from google.colab import userdata

os.environ["GOOGLE_API_KEY"] = userdata.get('GOOGLE_API_KEY')
from getpass import getpass
import os
os.environ['EMAIL_REMETENTE'] = input("Digite seu e-mail do Gmail: ")
os.environ['SENHA_EMAIL_APP'] = getpass("Digite sua senha de app do Gmail: ")

# Instalar Framework de agentes do Google ################################################
!pip install -q google-adk

from google import genai
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search  # Importante para permitir buscas
from google.genai import types
from IPython.display import display, Markdown
import textwrap
import warnings
import smtplib
from email.message import EmailMessage
warnings.filterwarnings("ignore")

client = genai.Client()
MODEL_ID = "gemini-2.0-flash"

def call_agent(agent: Agent, message_text: str) -> str:
    session_service = InMemorySessionService()
    session = session_service.create_session(app_name=agent.name, user_id="user1", session_id="session1")
    runner = Runner(agent=agent, app_name=agent.name, session_service=session_service)
    content = types.Content(role="user", parts=[types.Part(text=message_text)])

    final_response = ""
    for event in runner.run(user_id="user1", session_id="session1", new_message=content):
        if event.is_final_response():
            for part in event.content.parts:
                if part.text is not None:
                    final_response += part.text
                    final_response += "\n"
    return final_response


def to_markdown(text):
    text = text.replace('•', '  *')
    return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))


# --- Agente Coordenador de Adoção Animal --- #
#############################################

coordenador_adocao_agent = Agent(
    name="coordenador_adocao_animais",
    model=MODEL_ID,
    instruction="""
    Você é um Agente de IA Coordenador de Adoção Animal. Seu papel é:

    - Realizar triagem inicial conversando com o interessado, coletando informações como: tipo de animal desejado, experiências prévias, ambiente onde vive, expectativas e compromisso com adoção responsável.
    - Responder dúvidas frequentes sobre adoção, vacinação, castração, requisitos e processo.
    - Ao final da triagem, apresentar o link do formulário de adoção: [https://docs.google.com/forms/d/e/1FAIpQLSe7hDZPL59al_Gd1369i6p6Yx736SHhexiCl-NtMB9oYQHyTw/viewform?usp=header]
    - Se solicitado, auxiliar no preenchimento do formulário.
    - Ser sempre acolhedor, claro e incentivar a adoção responsável de animais (não de crianças).
    - Use a ferramenta google_search para buscar informações adicionais, se necessário.
    """,
    description="Agente especializado em coordenar o processo de adoção de animais.",
    tools=[google_search]
)

planilha_animais_disponiveis = "https://docs.google.com/spreadsheets/d/1U3EBw1YZR0Qt_iqeWZD0rb2kpbogJENbyIe72XXRXws/edit?usp=sharing"
formulario_adocao = "https://docs.google.com/forms/d/e/1FAIpQLSe7hDZPL59al_Gd1369i6p6Yx736SHhexiCl-NtMB9oYQHyTw/viewform?usp=header"

def conversar_com_gemini(mensagem, contexto=[]):
    response = model.generate_content(mensagem, history=contexto)
    return response.text

def enviar_email(destinatario, assunto, corpo):
    """
    Envia um e-mail de texto simples para o destinatário informado.
    Requer uma conta Gmail com senha de app.
    As credenciais devem estar em variáveis de ambiente:
    - EMAIL_REMETENTE
    - SENHA_EMAIL_APP
    """
    email_remetente = os.environ.get('EMAIL_REMETENTE')
    senha = os.environ.get('SENHA_EMAIL_APP')
    if not email_remetente or not senha:
        print("Erro: defina EMAIL_REMETENTE e SENHA_EMAIL_APP como variáveis de ambiente.")
        return

    msg = EmailMessage()
    msg['Subject'] = assunto
    msg['From'] = email_remetente
    msg['To'] = destinatario
    msg.set_content(corpo)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(email_remetente, senha)
            smtp.send_message(msg)
        print(f"E-mail enviado para {destinatario}!")
    except Exception as e:
        print("Erro ao enviar e-mail:", e)

def triagem_fluxo():
    print("Olá! Que bom que você se interessa pela adoção responsável de animais. Vou te fazer algumas perguntas para te conhecer melhor e indicar os melhores pets para você! 🐾")

    tipo_animal = input("Você tem interesse em adotar um cachorro, um gato, ou está aberto a ambos? ").strip().lower()
    experiencia = input("Você já teve animais antes? Se sim, quais? ").strip()
    residencia = input("Você mora em casa, apartamento ou outro tipo de moradia? ").strip()
    seguranca = input("Sua casa/apto possui telas nas janelas/ quintal? (sim/não) ").strip()
    seguranca2 = input("Sua casa/apto permite acesso à rua? (sim/não) ").strip()
    pessoas = input("Todos na sua casa concordam com a adoção? (sim/não) ").strip().lower()
    preferencias = input("Tem preferência de porte, idade ou temperamento do animal? ").strip()
    tempo = input("Quanto tempo por dia a casa fica vazia? ").strip()
    compromisso = input("Você se compromete a vacinar, castrar e cuidar do animal com responsabilidade? (sim/não) ").strip().lower()

    if pessoas != "sim":
        print("\n❗️ Para adotar um animal, é fundamental que todos na casa estejam de acordo. Converse com sua família/moradores e, quando todos concordarem, ficaremos felizes em te ajudar!")
        print("Se precisar de informações para convencer alguém ou tirar dúvidas sobre adoção responsável, posso ajudar. 😊")
        return

    if seguranca != "sim":
        print("\n ❗️ Para adotar um animal, é fundamental que ele esteja protegido do acesso à rua com telas e proteção nas janelas, sacadas, portas e quintais. Deixe sua casa protegida e entre novamente em contato!")
        print("Se precisar de dicas de empresas que instalam telas de proteção, ou dicas de como fazer, posso ajudar. 😊")
        return
    if seguranca2 != "não":
        print("\n ❗️ Para adotar um animal, é fundamental que ele esteja protegido do acesso à rua, sem nenhuma rota de fuga! Certifique-se de examinar e eliminar todas as possíveis rotas de fuga existentes para que seu próximo melhor amigo esteja seguro!")
        return
    if compromisso != "sim":
        print("\A adoção responsável inclui o compromisso com vacinação, castração e bem-estar do animal. Quando estiver pronto para assumir esses cuidados, ficaremos felizes em te ajudar na adoção!")
        return
    print("\nÓtimo! Aqui está nossa lista de animais disponíveis:")
    print(planilha_animais_disponiveis)
    print("Se gostar de algum, você pode preencher o formulário de adoção a seguir. Se tiver dúvidas, estou aqui para ajudar!")

    print("\n👉 Formulário de adoção:", formulario_adocao)
    print("Se quiser, posso te explicar como preencher cada campo.")
    print("Se precisar de mais alguma coisa, digite sua dúvida ou 'sair' para encerrar.")

    email = input("\nInforme seu e-mail para receber os próximos passos e links importantes: ").strip()
    if email and "@" in email:
        corpo = (
            f"Olá!\n\n"
            f"Parabéns! Você foi aprovado(a) na triagem para adoção responsável.\n"
            f"Veja aqui os próximos passos e links úteis:\n"
            f"- Lista de animais disponíveis: {planilha_animais_disponiveis}\n"
            f"- Formulário de adoção: {formulario_adocao}\n\n"
            f"Se tiver dúvidas, responda este e-mail ou fale conosco!\n"
            f"Abraço 🐶🐱"
        )
        enviar_email(
            destinatario=email,
            assunto="Parabéns! Você foi aprovado para adoção responsável 🐾",
            corpo=corpo
        )
        print("Você receberá um e-mail com os próximos passos!")
    else:
        print("E-mail não informado ou inválido. Se quiser receber por e-mail depois, é só pedir!")
    continuar = input("Deseja realizar outra ação ou encerrar? (digite 'sair' para encerrar ou pressione Enter para voltar ao menu): ").strip().lower()
    if continuar == "sair":
        print("Muito obrigado por buscar a adoção responsável. Se precisar, estarei aqui! 💚🐾")
    exit()
contexto = []

while True:
    user_input = input("❓ Como posso ajudar? (Digite 'sair' para encerrar): ").strip().lower()
    if user_input in ["sair", "encerrar", "tchau"]:
        print("Muito obrigado por buscar a adoção responsável. Se precisar, estarei aqui! 💚🐾")
        break

    elif "quero adotar" in user_input or "adotar" in user_input:
        triagem_fluxo()
        continue

    elif "animais disponíveis" in user_input or "ver animais" in user_input:
        print(f"\n📋 Veja os animais disponíveis aqui: {planilha_animais_disponiveis}")

    elif any(x in user_input for x in ["castração", "castrado", "vacina", "vacinação", "responsável"]):
        if "castra" in user_input:
            print("\n📌 Todos os nossos animais são castrados antes da adoção. Se precisar, explico mais!")
        elif "vacin" in user_input:
            print("\n💉 Todos são entregues com vacinação em dia, conforme a idade.")
        elif "responsável" in user_input:
            print("\n🐾 Adoção responsável é garantir laço, cuidado, amor e compromisso com o bem-estar do animal.")
        else:
            print("\nPosso te ajudar com informações sobre vacinação, castração e adoção responsável.")

    elif "formulário" in user_input or "formulario" in user_input:
        print("\n📝 Você pode preencher o formulário aqui:")
        print("👉", formulario_adocao)
        print("Se tiver dúvidas sobre o que preencher, é só perguntar!")

    else:
        resposta = conversar_com_gemini(user_input, contexto)
        contexto.append({"role": "user", "parts": [user_input]})
        contexto.append({"role": "model", "parts": [resposta]})
        print(resposta)

    print("--------------------------------------------------------------")