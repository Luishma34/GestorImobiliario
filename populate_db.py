import random
from faker import Faker
from app.database.delta_db import DeltaDatabase

fake = Faker('pt_BR')

TIPOS_IMOVEL = ['Casa', 'Apartamento', 'Kitnet', 'Sobrado', 'Cobertura', 'Studio']

STATUS_IMOVEL = ['Disponivel', 'Alugado', 'Em Manutenção']

APELIDOS_PREFIX = [
    'Casa', 'Apto', 'Sobrado', 'Kitnet', 'Residência', 'Cobertura',
    'Studio', 'Flat', 'Loft', 'Chalé'
]

APELIDOS_SUFFIX = [
    'do Centro', 'da Praia', 'do Jardim', 'da Colina', 'do Bosque',
    'da Lagoa', 'do Parque', 'Vista Mar', 'Vista Verde', 'Bela Vista',
    'dos Anjos', 'das Flores', 'do Sol', 'da Lua', 'das Estrelas',
    'Aconchegante', 'Moderno', 'Espaçoso', 'Completo', 'Luxo',
    'Premium', 'Comfort', 'Family', 'VIP', 'Gold'
]

CARACTERISTICAS = [
    'com sacada', 'com varanda', 'com quintal', 'com garagem',
    'com churrasqueira', 'com piscina', 'com área de lazer',
    'com portaria 24h', 'com elevador', 'com armários embutidos',
    'com ar-condicionado', 'mobiliado', 'semi-mobiliado',
    'recém reformado', 'iluminado', 'ventilado', 'amplo',
    'com vista panorâmica', 'próximo ao metrô', 'em condomínio fechado'
]

COMODOS = [
    '1 quarto', '2 quartos', '3 quartos', '4 quartos',
    '1 suíte', '2 suítes', '3 suítes',
    '1 banheiro', '2 banheiros', '3 banheiros',
    'sala', 'cozinha', 'área de serviço', 'despensa',
    'escritório', 'closet'
]


def gerar_apelido():
    prefix = random.choice(APELIDOS_PREFIX)
    suffix = random.choice(APELIDOS_SUFFIX)
    
    if random.random() > 0.7:
        numero = random.randint(1, 999)
        return f"{prefix} {suffix} {numero}"
    
    return f"{prefix} {suffix}"


def gerar_descricao(tipo_imovel):
    descricoes = []
    
    num_quartos = random.choice(['1', '2', '3', '4'])
    num_banheiros = random.choice(['1', '2', '3'])
    
    descricoes.append(f"{tipo_imovel} com {num_quartos} quarto(s) e {num_banheiros} banheiro(s)")
    
    num_caracteristicas = random.randint(2, 5)
    caracteristicas_selecionadas = random.sample(CARACTERISTICAS, num_caracteristicas)
    descricoes.append(', '.join(caracteristicas_selecionadas))
    
    if random.random() > 0.5:
        num_comodos = random.randint(1, 3)
        comodos_selecionados = random.sample(COMODOS, num_comodos)
        descricoes.append(f"Possui {', '.join(comodos_selecionados)}")
    
    localizacao_info = [
        "Ótima localização",
        "Localização privilegiada",
        "Região tranquila e segura",
        "Bairro nobre",
        "Próximo a comércios e serviços",
        "Fácil acesso a transporte público",
        "Área residencial",
        "Região comercial"
    ]
    descricoes.append(random.choice(localizacao_info))
    
    return '. '.join(descricoes) + '.'


def gerar_endereco():
    tipo_logradouro = random.choice(['Rua', 'Avenida', 'Travessa', 'Alameda', 'Praça'])
    numero = random.randint(1, 9999)
    
    nome_rua = fake.street_name()
    bairro = fake.bairro()
    cidade = fake.city()
    estado = fake.estado_sigla()
    cep = fake.postcode()
    
    complementos = ['', 'Apto 101', 'Apto 202', 'Casa 1', 'Casa 2', 'Bloco A', 'Bloco B', 'Torre 1', 'Torre 2']
    complemento = random.choice(complementos)
    
    if complemento:
        endereco = f"{tipo_logradouro} {nome_rua}, {numero} - {complemento}, {bairro}, {cidade} - {estado}, CEP: {cep}"
    else:
        endereco = f"{tipo_logradouro} {nome_rua}, {numero}, {bairro}, {cidade} - {estado}, CEP: {cep}"
    
    return endereco


def gerar_valor_aluguel(tipo_imovel):
    faixas_preco = {
        'Kitnet': (500, 1200),
        'Studio': (800, 1800),
        'Apartamento': (1000, 5000),
        'Casa': (1200, 6000),
        'Sobrado': (1800, 8000),
        'Cobertura': (3000, 15000)
    }
    
    min_preco, max_preco = faixas_preco.get(tipo_imovel, (800, 3000))
    
    valor = random.uniform(min_preco, max_preco)
    valor_arredondado = round(valor / 50) * 50
    
    return float(valor_arredondado)


def gerar_id_proprietario():
    return random.randint(1, 100)


def gerar_status():
    rand = random.random()
    if rand < 0.60:
        return 'Disponivel'
    elif rand < 0.95:
        return 'Alugado'
    else:
        return 'Em Manutenção'


def gerar_imovel():
    """Gera um imóvel completo com dados fictícios realistas."""
    tipo_imovel = random.choice(TIPOS_IMOVEL)
    
    imovel = {
        'apelido_imovel': gerar_apelido(),
        'descricao': gerar_descricao(tipo_imovel),
        'endereco': gerar_endereco(),
        'valor_aluguel_base': gerar_valor_aluguel(tipo_imovel),
        'tipo_imovel': tipo_imovel,
        'status': gerar_status(),
        'id_proprietario': gerar_id_proprietario()
    }
    
    return imovel


def popular_banco(quantidade=1000, tamanho_lote=100):
    print(f"Iniciando população do banco de dados com {quantidade} imóveis...")
    
    db = DeltaDatabase(table_name="imoveis")
    
    registros_existentes = db.count()
    print(f"Registros existentes no banco: {registros_existentes}\n")
    
    total_inseridos = 0
    lotes_processados = 0
    
    print(f"Processando em lotes de {tamanho_lote} registros...\n")
    
    while total_inseridos < quantidade:
        registros_neste_lote = min(tamanho_lote, quantidade - total_inseridos)
        
        lote = []
        for _ in range(registros_neste_lote):
            imovel = gerar_imovel()
            lote.append(imovel)
        
        try:
            ids = db.insert_batch(lote)
            total_inseridos += len(ids)
            lotes_processados += 1
            print(f"Lote {lotes_processados}: {len(ids)} imóveis inseridos. Total: {total_inseridos}/{quantidade}")
        except Exception as e:
            print(f"Erro ao inserir lote {lotes_processados + 1}: {e}")
            break

    print(f"\n✅ População do banco de dados concluída! Banco está com {db.count()} registros no total.")


if __name__ == "__main__":
    popular_banco(1000, tamanho_lote=100)
