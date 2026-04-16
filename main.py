import os
import time
import schedule
import requests
from instagrapi import Client
from openai import OpenAI

USERNAME = os.getenv("INSTAGRAM_USERNAME")
PASSWORD = os.getenv("INSTAGRAM_PASSWORD")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
NICHO = os.getenv("NICHO", "Agencia de Inteligencia Artificial")
IMAGES_PER_CAROUSEL = int(os.getenv("IMAGES_PER_CAROUSEL", 4))

cl = Client()
ai = OpenAI(api_key=OPENAI_KEY)

def login():
    try:
        cl.load_settings("session.json")
        cl.login(USERNAME, PASSWORD)
    except:
        cl.login(USERNAME, PASSWORD)
        cl.dump_settings("session.json")
    print("✅ Instagram conectado")

def generar_tema():
    prompt = f"Dame un tema atractivo y educativo para una {NICHO}"
    res = ai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=60
    )
    return res.choices[0].message.content.strip()

def generar_caption(tema):
    prompt = f"""
    Escribe un caption profesional para Instagram sobre: {tema}
    para una Agencia de Inteligencia Artificial.
    Incluye:
    - Gancho fuerte
    - CTA
    - Hashtags estratégicos
    """
    res = ai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )
    return res.choices[0].message.content

def generar_imagen(prompt, nombre):
    res = ai.images.generate(
        model="dall-e-3",
        prompt=prompt + ", estilo branding tech premium minimalista",
        size="1024x1024"
    )
    url = res.data[0].url
    img = requests.get(url).content
    with open(nombre, "wb") as f:
        f.write(img)

def publicar():
    print("🚀 Generando carrusel...")
    tema = generar_tema()
    caption = generar_caption(tema)

    imagenes = []
    for i in range(IMAGES_PER_CAROUSEL):
        nombre = f"slide_{i}.png"
        generar_imagen(f"{tema} - Slide {i+1}", nombre)
        imagenes.append(nombre)

    cl.album_upload(imagenes, caption)
    print("✅ Carrusel publicado")

def job():
    try:
        publicar()
    except Exception as e:
        print("❌ Error:", e)

login()

schedule.every().day.at("15:00").do(job)

print("🤖 Bot corriendo 24/7...")

while True:
    schedule.run_pending()
    time.sleep(60)
