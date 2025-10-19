# Gestor Imobiliário

API REST simples para gerenciamento de imóveis usando FastAPI e Delta Lake.

## 🚀 Setup Rápido

### 1. Criar ambiente virtual
```bash
python -m venv venv
```

### 2. Ativar ambiente virtual
```bash
# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

### 4. Rodar a aplicação
```bash
uvicorn app.main:app --reload
```

### 5. Acessar documentação
- http://localhost:8000/docs
- caso estiver usando wsl: http://127.0.0.1:8000/docs

### 6. Popular o Banco
```bash
#pode ser python3 ao invés de python
python populate_db.py
```

