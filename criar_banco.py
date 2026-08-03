import sqlite3

# Conecta ao banco de dados (cria o arquivo 'cupcakes.db' se não existir)
conn = sqlite3.connect('cupcakes.db')
cursor = conn.cursor()

# Executa o script SQL garantindo ponto e vírgula (;) no final de cada instrução
cursor.executescript('''
    -- 1. Remove a tabela antiga caso ela já exista
    DROP TABLE IF EXISTS cupcakes;

    -- 2. Criação da tabela de cupcakes
    CREATE TABLE cupcakes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        descricao TEXT,
        preco REAL NOT NULL,
        imagem TEXT,
        estoque INTEGER DEFAULT 0,
        destaque INTEGER DEFAULT 0,
        ingredientes TEXT,
        informacao_nutricional TEXT,
        alergicos TEXT
    );

    -- 3. Inserção de dados iniciais
    INSERT INTO cupcakes (
        nome, 
        descricao, 
        preco, 
        imagem, 
        estoque, 
        destaque, 
        ingredientes, 
        informacao_nutricional, 
        alergicos
    ) VALUES 
    (
        'Cupcake de Limão', 
        'Massa cítrica com merengue tostado', 
        8.00, 
        'https://via.placeholder.com/150/ccffcc/000000?text=Limao', 
        20, 
        0, 
        'Farinha, açúcar, suco de limão, claras em neve.', 
        'Porção 100g: 300kcal.', 
        'Contém glúten.'
    ),
    (
        'Cupcake de Chocolate', 
        'Massa de cacau com cobertura de ganache', 
        9.50, 
        'https://via.placeholder.com/150/4d2600/ffffff?text=Chocolate', 
        15, 
        1, 
        'Farinha, cacau 70%, açúcar, leite, manteiga.', 
        'Porção 100g: 380kcal.', 
        'Contém glúten e lactose.'
    ),
    (
        'Cupcake Red Velvet', 
        'Tradicional red velvet com cream cheese', 
        10.00, 
        'https://via.placeholder.com/150/800000/ffffff?text=Red+Velvet', 
        10, 
        1, 
        'Farinha, cacau, corante vermelho, cream cheese.', 
        'Porção 100g: 350kcal.', 
        'Contém glúten, lactose e ovos.'
    );
''')

# Salva as alterações e encerra a conexão
conn.commit()
conn.close()

print("Banco de dados 'cupcakes.db' criado e populado com sucesso!")