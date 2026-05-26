import os
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from google import genai
from google.genai import types

app = Flask(__name__)
CORS(app)

MODELO_PADRAO = "gemini-2.0-flash-lite"

ESTILOS_POESIA = {
    "moderna": {"nome": "Poesia Moderna", "icone": "🌆"},
    "romantica": {"nome": "Poesia Romântica", "icone": "❤️"},
    "classica": {"nome": "Poesia Clássica", "icone": "🏛️"},
    "contemporanea": {"nome": "Poesia Contemporânea", "icone": "🎨"},
    "haikai": {"nome": "Haikai", "icone": "🍃"},
    "cordel": {"nome": "Cordel", "icone": "📖"},
    "infantil": {"nome": "Poesia Infantil", "icone": "🧸"},
    "epico": {"nome": "Poesia Épica", "icone": "⚔️"},
    "filosofica": {"nome": "Poesia Filosófica", "icone": "🧠"},
    "satirica": {"nome": "Poesia Satírica", "icone": "🎭"}
}

def gerar_poema(tema, estilo, versos):
    versos = max(4, min(30, versos))
    estilo_info = ESTILOS_POESIA.get(estilo, ESTILOS_POESIA["moderna"])
    
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    prompt = f"""Crie um poema sobre "{tema}" no estilo {estilo_info['nome']} com {versos} versos.

IMPORTANTE: 
- Não use pornografia, não incentive suicídio, não use drogas, não use pedofilia, não use zoofilia, não use racismo.
- Faça um poema bonito e inspirador.

Responda APENAS com este JSON:
{{
    "titulo": "título do poema",
    "conteudo": "verso 1\\nverso 2\\nverso 3\\n..."
}}"""
    
    config = types.GenerateContentConfig(response_mime_type="application/json")
    
    try:
        response = client.models.generate_content(
            model=MODELO_PADRAO,
            contents=prompt,
            config=config,
        )
        poema = json.loads(response.text)
        return {
            "status": "success",
            "titulo": poema.get("titulo", "Sem título"),
            "conteudo": poema.get("conteudo", "Poema não gerado"),
            "estilo": estilo_info["nome"],
            "icone": estilo_info["icone"],
            "tema": tema
        }
    except Exception as e:
        return {"status": "error", "mensagem": str(e)}

@app.route("/", methods=["GET"])
def root():
    return jsonify({"app": "Gerador de Poesias", "versao": "1.0"})

@app.route("/estilos", methods=["GET"])
def listar_estilos():
    estilos = [{"id": k, "nome": v["nome"], "icone": v["icone"]} for k, v in ESTILOS_POESIA.items()]
    return jsonify({"estilos": estilos})

@app.route("/gerar", methods=["POST"])
def gerar():
    data = request.get_json()
    tema = data.get("tema", "").strip()
    estilo = data.get("estilo", "moderna")
    versos = data.get("versos", 12)
    
    if not tema:
        return jsonify({"error": "Tema é obrigatório"}), 400
    if estilo not in ESTILOS_POESIA:
        return jsonify({"error": f"Estilo {estilo} não existe"}), 400
    
    return jsonify(gerar_poema(tema, estilo, versos))

handler = app