from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sqlite3

app = FastAPI(title="API Loja de Cupcakes", version="1.0")

def inicializar_banco():
    """Cria as tabelas do banco de dados SQLite e popula cupcakes iniciais se necessário"""
    conn = sqlite3.connect("banco.db")
    cursor = conn.cursor()
    
    # Tabela de Clientes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            cpf TEXT PRIMARY KEY,
            nome TEXT,
            telefone TEXT,
            cep TEXT,
            logradouro TEXT,
            numero TEXT,
            complemento TEXT,
            bairro TEXT,
            cidade TEXT,
            uf TEXT
        )
    """)
    
    # Tabela de Pedidos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            numero TEXT PRIMARY KEY,
            cliente_cpf TEXT,
            total REAL,
            status TEXT,
            endereco TEXT,
            metodo_pagamento TEXT,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_cpf) REFERENCES clientes(cpf)
        )
    """)
    
    # Tabela de Itens do Pedido
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS itens_pedido (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_numero TEXT,
            item_id INTEGER,
            nome TEXT,
            preco REAL,
            FOREIGN KEY (pedido_numero) REFERENCES pedidos(numero)
        )
    """)
    
    # Tabela de Cupcakes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cupcakes (
            id INTEGER PRIMARY KEY,
            nome TEXT,
            descricao TEXT,
            preco REAL,
            ingredientes TEXT,
            informacao_nutricional TEXT,
            alergicos TEXT,
            imagem TEXT
        )
    """)
    
    # Inserir cupcakes padrão se a tabela estiver vazia
    cursor.execute("SELECT COUNT(*) FROM cupcakes")
    if cursor.fetchone()[0] == 0:
        cupcakes_iniciais = [
            (1, "Cupcake de Chocolate", "Massa fofinha de chocolate com cobertura de ganache rica.", 8.50, "Farinha, cacau em pó, açúcar, ovos, manteiga, chocolate meio amargo", "250 kcal | Carboidratos: 30g", "Contém glúten, lactose e derivados de ovos", "https://via.placeholder.com/150/5C4033/FFFFFF?text=Chocolate"),
            (2, "Cupcake de Baunilha", "Massa clássica de baunilha com cobertura de buttercream artesanal.", 7.50, "Farinha, extrato de baunilha natural, açúcar, ovos, manteiga", "220 kcal | Carboidratos: 28g", "Contém glúten, lactose e ovos", "https://via.placeholder.com/150/F5DEB3/000000?text=Baunilha"),
            (3, "Cupcake de Morango", "Massa leve de baunilha com recheio cremoso e cobertura de morango.", 9.00, "Farinha, morango natural, açúcar, ovos, manteiga, leite condensado", "210 kcal | Carboidratos: 27g", "Contém glúten e lactose", "https://via.placeholder.com/150/FF69B4/FFFFFF?text=Morango")
        ]
        cursor.executemany("INSERT OR IGNORE INTO cupcakes VALUES (?, ?, ?, ?, ?, ?, ?, ?)", cupcakes_iniciais)
        
    conn.commit()
    conn.close()

# Inicializa o banco ao iniciar o servidor
inicializar_banco()

# --- MODELOS PYDANTIC ---
class ClienteDTO(BaseModel):
    cpf: str
    nome: str
    telefone: str
    cep: str
    logradouro: str
    numero: str
    complemento: Optional[str] = ""
    bairro: str
    cidade: str
    uf: str

class ItemPedidoDTO(BaseModel):
    id: int
    nome: str
    preco: float

class PedidoDTO(BaseModel):
    numero: str
    cliente_cpf: str
    total: float
    status: str
    endereco: str
    metodo_pagamento: str
    itens: List[ItemPedidoDTO]

class StatusDTO(BaseModel):
    status: str

# --- ROTAS DA API ---
@app.get("/cupcakes")
def listar_cupcakes():
    conn = sqlite3.connect("banco.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cupcakes")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/clientes/{cpf}")
def buscar_cliente(cpf: str):
    conn = sqlite3.connect("banco.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes WHERE cpf = ?", (cpf,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return dict(row)

@app.post("/clientes")
def criar_cliente(cliente: ClienteDTO):
    try:
        conn = sqlite3.connect("banco.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO clientes (cpf, nome, telefone, cep, logradouro, numero, complemento, bairro, cidade, uf)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (cliente.cpf, cliente.nome, cliente.telefone, cliente.cep, cliente.logradouro, cliente.numero, cliente.complemento, cliente.bairro, cliente.cidade, cliente.uf))
        conn.commit()
        conn.close()
        return {"mensagem": "Cliente salvo com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/pedidos")
def criar_pedido(pedido: PedidoDTO):
    try:
        conn = sqlite3.connect("banco.db")
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO pedidos (numero, cliente_cpf, total, status, endereco, metodo_pagamento)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (pedido.numero, pedido.cliente_cpf, pedido.total, pedido.status, pedido.endereco, pedido.metodo_pagamento))
        
        for item in pedido.itens:
            cursor.execute("""
                INSERT INTO itens_pedido (pedido_numero, item_id, nome, preco)
                VALUES (?, ?, ?, ?)
            """, (pedido.numero, item.id, item.nome, item.preco))
            
        conn.commit()
        conn.close()
        return {"mensagem": "Pedido criado com sucesso", "numero": pedido.numero}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/pedidos/{numero}/status")
def atualizar_status_pedido(numero: str, payload: StatusDTO):
    try:
        conn = sqlite3.connect("banco.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE pedidos SET status = ? WHERE numero = ?", (payload.status, numero))
        conn.commit()
        conn.close()
        return {"mensagem": "Status atualizado com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/pedidos/cliente/{cpf}")
def listar_pedidos_cliente(cpf: str):
    conn = sqlite3.connect("banco.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pedidos WHERE cliente_cpf = ? ORDER BY data_criacao DESC", (cpf,))
    pedidos = cursor.fetchall()
    
    resultado = []
    for p in pedidos:
        p_dict = dict(p)
        cursor.execute("SELECT item_id as id, nome, preco FROM itens_pedido WHERE pedido_numero = ?", (p_dict["numero"],))
        itens = [dict(row) for row in cursor.fetchall()]
        p_dict["itens"] = itens
        resultado.append(p_dict)
        
    conn.close()
    return resultado
