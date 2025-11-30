import random
from sqlmodel import Session, select
from faker import Faker
from app.database import engine, create_db_and_tables
from app.models import Proprietario, Imovel, Inquilino, Contrato
from datetime import date, timedelta

fake = Faker('pt_BR')

def create_fake_data():
    print("Criando tabelas...")
    create_db_and_tables()

    with Session(engine) as session:
        # 1. Verificar se já existem dados para não duplicar excessivamente
        existing_props = session.exec(select(Proprietario)).first()
        if existing_props:
            print("O banco de dados já parece estar povoado. Pulando população.")
            return

        print("Gerando dados realistas...")

        # 2. Criar 10 Proprietários
        proprietarios = []
        for _ in range(10):
            p = Proprietario(
                nome=fake.name(),
                cpf=fake.cpf(),
                email=fake.email(),
                telefone=fake.phone_number(),
                endereco=fake.address()
            )
            session.add(p)
            proprietarios.append(p)
        
        session.commit()
        # Recarregar para pegar os IDs
        for p in proprietarios:
            session.refresh(p)
        
        print(f"{len(proprietarios)} Proprietários criados.")

        # 3. Criar 50 Imóveis
        tipos = ["Casa", "Apartamento", "Studio", "Cobertura", "Sobrado"]
        imoveis = []
        for _ in range(50):
            prop = random.choice(proprietarios)
            tipo = random.choice(tipos)
            
            imovel = Imovel(
                apelido_imovel=f"{tipo} {fake.city()}",
                descricao=fake.sentence(nb_words=10),
                endereco=fake.address(),
                valor_aluguel_base=round(random.uniform(800, 5000), 2),
                tipo_imovel=tipo,
                status=random.choice(["Disponivel", "Alugado", "Manutencao"]),
                id_proprietario=prop.id
            )
            session.add(imovel)
            imoveis.append(imovel)
        
        session.commit()
        for i in imoveis:
            session.refresh(i)
        
        print(f"{len(imoveis)} Imóveis criados.")

        # 4. Criar alguns Inquilinos e Contratos (Para os relatórios funcionarem)
        inquilinos = []
        for _ in range(15):
            inq = Inquilino(
                nome=fake.name(),
                cpf=fake.cpf(),
                email=fake.email(),
                telefone=fake.phone_number(),
                renda_mensal=round(random.uniform(3000, 10000), 2)
            )
            session.add(inq)
            inquilinos.append(inq)
        session.commit()

        # Criar Contratos para imóveis "Alugado"
        imoveis_alugados = [i for i in imoveis if i.status == "Alugado"]
        for imovel in imoveis_alugados:
            inq = random.choice(inquilinos)
            data_inicio = fake.date_between(start_date='-1y', end_date='today')
            data_fim = data_inicio + timedelta(days=365) # Contrato de 1 ano
            
            contrato = Contrato(
                id_inquilino=inq.id,
                id_imovel=imovel.id,
                data_inicio=data_inicio,
                data_fim=data_fim,
                valor_aluguel=imovel.valor_aluguel_base,
                dia_vencimento=random.randint(1, 28),
                status="Ativo"
            )
            session.add(contrato)
        
        session.commit()
        print("Inquilinos e Contratos gerados para teste de relatórios.")
        print("--- Processo Finalizado com Sucesso ---")

if __name__ == "__main__":
    create_fake_data()