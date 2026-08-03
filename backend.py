from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3

# A variável OBRIGATORIAMENTE precisa se chamar 'app'
app = FastAPI()

# Permite requisições do frontend Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def buscar_cupcakes():
    conn = sqlite3.connect('cupcakes.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, descricao, preco, imagem, estoque, destaque, ingredientes, informacao_nutricional, alergicos FROM cupcakes")
    colunas = [column[0] for column in cursor.description]
    resultados = [dict(zip(colunas, row)) for row in cursor.fetchall()]
    conn.close()
    return resultados

@app.get("/")
def home():
    return {"mensagem": "API da Loja de Cupcakes rodando!"}

@app.get("/cupcakes")
def listar_cupcakes():
    return buscar_cupcakes()