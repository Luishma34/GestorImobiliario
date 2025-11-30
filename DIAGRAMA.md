# Diagrama de Classes do Sistema

Este diagrama representa a estrutura do banco de dados e os relacionamentos entre as entidades do sistema **Gestor Imobiliário**.

```mermaid
classDiagram
    direction TB

    class Proprietario {
        +int id
        +str nome
        +str cpf
        +str email
        +str telefone
        +str endereco
    }

    class Imovel {
        +int id
        +str apelido_imovel
        +str descricao
        +str endereco
        +float valor_aluguel_base
        +str tipo_imovel
        +str status
        +int id_proprietario
    }

    class Inquilino {
        +int id
        +str nome
        +str cpf
        +str email
        +str telefone
        +str endereco_anterior
        +float renda_mensal
    }

    class Contrato {
        +int id
        +int id_inquilino
        +int id_imovel
        +date data_inicio
        +date data_fim
        +float valor_aluguel
        +int dia_vencimento
        +str status
        +str observacoes
    }

    %% Relacionamentos
    Proprietario "1" --> "0..*" Imovel : possui
    Inquilino "1" --> "0..*" Contrato : assina
    Imovel "1" --> "0..*" Contrato : tem_registro_em