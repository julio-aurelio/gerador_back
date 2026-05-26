# app_poetry.py - GERADOR DE POESIAS SIMPLES
# Versão: 1.0 - SEM COMPLICAÇÕES

import os
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("ERRO: GEMINI_API_KEY não encontrada")
    exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)
app = Flask(__name__)
CORS(app)

MODELO_PADRAO = "gemini-3.1-flash-lite"

# ============================================
# ESTILOS DE POESIA
# ============================================

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

# ============================================
# FUNÇÃO PRINCIPAL
# ============================================

def gerar_poema(tema, estilo, versos):
    # Ajusta versos
    versos = max(4, min(30, versos))
    
    estilo_info = ESTILOS_POESIA.get(estilo, ESTILOS_POESIA["moderna"])
    
    prompt = f"""
    Crie um poema sobre "{tema}" no estilo {estilo_info['nome']} com {versos} versos.
    
    IMPORTANTE: 
    - Não use pornografia, não incentive suicídio, não use drogas, não use pedofilia, não use zoofilia, não use racismo.
    - Faça um poema bonito e inspirador.
    
    Responda APENAS com este JSON:
    {{
        "titulo": "título do poema",
        "conteudo": "verso 1\\nverso 2\\nverso 3\\n..."
    }}
    """
    
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
    )
    
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
        print(f"Erro: {e}")
        return {
            "status": "error",
            "mensagem": str(e)
        }

# ============================================
# ROTAS
# ============================================

@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "app": "Gerador de Poesias",
        "versao": "1.0"
    })

@app.route("/estilos", methods=["GET"])
def listar_estilos():
    estilos = []
    for key, value in ESTILOS_POESIA.items():
        estilos.append({
            "id": key,
            "nome": value["nome"],
            "icone": value["icone"]
        })
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
    
    resultado = gerar_poema(tema, estilo, versos)
    return jsonify(resultado)

if __name__ == "__main__":
    app.run(debug=True)