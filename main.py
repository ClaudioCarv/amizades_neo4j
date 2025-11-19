from neo4j import GraphDatabase
import json
import uuid

with open("token.json") as f:
    tokens = json.load(f)

URI = "neo4j+s://623a5b8f.databases.neo4j.io"
AUTH = (tokens['user'], tokens['password'])

driver = GraphDatabase.driver(URI, auth=AUTH)



def gerar_id_curto():
    return str(uuid.uuid4())[:8]


def pessoa_existe(id):
    with driver.session() as session:
        result = session.run(
            "MATCH (p:Pessoa {id: $id}) RETURN p",
            id=id
        )
        return result.single() is not None



def criar_pessoa(nome, idade, telefone):
    id_pessoa = gerar_id_curto()

    with driver.session() as session:
        session.run("""
            MERGE (p:Pessoa {id: $id})
            SET p.nome = $nome,
                p.idade = $idade,
                p.telefone = $telefone
        """, id=id_pessoa, nome=nome, idade=idade, telefone=telefone)

    print(f"Pessoa '{nome}' criada com sucesso (ID: {id_pessoa})")


def listar_pessoas():
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Pessoa)
            RETURN p.id AS id, p.nome AS nome, p.idade AS idade, p.telefone AS telefone
        """)

        pessoas = list(result)

    if pessoas:
        print("\nLista de pessoas:")
        for p in pessoas:
            print(f"- {p['nome']} (idade {p['idade']}, tel: {p['telefone']}) [ID: {p['id']}]")
    else:
        print("Nenhuma pessoa cadastrada.")


def atualizar_nome(id, novo_nome):
    if not pessoa_existe(id):
        print("ID não encontrado")
        return

    with driver.session() as session:
        session.run("""
            MATCH (p:Pessoa {id: $id})
            SET p.nome = $novo_nome
        """, id=id, novo_nome=novo_nome)

    print("Nome atualizado com sucesso.")


def atualizar_idade(id, nova_idade):
    if not pessoa_existe(id):
        print("ID não encontrado")
        return

    with driver.session() as session:
        session.run("""
            MATCH (p:Pessoa {id: $id})
            SET p.idade = $idade
        """, id=id, idade=nova_idade)

    print("Idade atualizada com sucesso.")


def deletar_pessoa_por_id(id):
    if not pessoa_existe(id):
        print("ID não encontrado")
        return

    with driver.session() as session:
        session.run("""
            MATCH (p:Pessoa {id: $id})
            DETACH DELETE p
        """, id=id)

    print("Pessoa deletada com sucesso.")



def criar_amizade(id1, id2):

    if not pessoa_existe(id1) or not pessoa_existe(id2):
        print("um dos IDs não existe")
        return

    with driver.session() as session:
        session.run("""
            MATCH (a:Pessoa {id: $id1})
            MATCH (b:Pessoa {id: $id2})
            MERGE (a)-[:AMIGO_DE]->(b)
            MERGE (b)-[:AMIGO_DE]->(a)
        """, id1=id1, id2=id2)

    print("Amizade criada!")


def remover_amizade(id1, id2):
    with driver.session() as session:
        session.run("""
            MATCH (a:Pessoa {id: $id1})-[r1:AMIGO_DE]->(b:Pessoa {id: $id2})
            DELETE r1
        """, id1=id1, id2=id2)

        session.run("""
            MATCH (b:Pessoa {id: $id2})-[r2:AMIGO_DE]->(a:Pessoa {id: $id1})
            DELETE r2
        """, id1=id1, id2=id2)

    print("Amizade completamente removida.")



def listar_amizades():
    with driver.session() as session:
        result = session.run("""
            MATCH (a:Pessoa)-[:AMIGO_DE]->(b:Pessoa)
            RETURN a.nome AS pessoa1, b.nome AS pessoa2
        """)

        amizades = list(result)

    if amizades:
        print("\nLista de amizades:")
        for a in amizades:
            print(f"- {a['pessoa1']} → {a['pessoa2']}")
    else:
        print("Nenhuma amizade encontrada")


def amigos_de(id):
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Pessoa {id: $id})-[:AMIGO_DE]->(amigo)
            RETURN amigo.nome AS nome, amigo.id AS id
        """, id=id)

        amigos = list(result)

    if amigos:
        print("\namigos:")
        for a in amigos:
            print(f"- {a['nome']} [ID: {a['id']}]")
    else:
        print("Essa pessoa não tem amigos cadastrados.")



def wipe():
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
    print("banco formatado")


def menu():
    while True:
        print("\n=== NEO4J CRUD ===")
        print("1. Criar pessoa")
        print("2. Listar pessoas")
        print("3. Atualizar dados")
        print("4. Deletar pessoa")
        print("5. Criar amizade")
        print("6. Listar amizades")
        print("7. Ver amigos de uma pessoa")
        print("8. Remover amizade")
        print("9. Wipe geral (deletar tudo)")
        print("10. Sair")

        op = input("Escolha: ")

        if op == "1":
            criar_pessoa(
                input("Nome: "),
                int(input("Idade: ")),
                input("Telefone: ")
            )

        elif op == "2":
            listar_pessoas()

        elif op == "3":
            print("1. Nome\n2. Idade")
            esc = input("Opção: ")
            idloc = input("ID: ")

            if esc == "1":
                atualizar_nome(idloc, input("Novo nome: "))
            else:
                atualizar_idade(idloc, int(input("Nova idade: ")))

        elif op == "4":
            deletar_pessoa_por_id(input("ID: "))

        elif op == "5":
            criar_amizade(input("ID1: "), input("ID2: "))

        elif op == "6":
            listar_amizades()

        elif op == "7":
            amigos_de(input("ID: "))

        elif op == "8":
            remover_amizade(input("ID1: "), input("ID2: "))

        elif op == "9":
            wipe()

        elif op == "10":
            break

        else:
            print("Opção inválida.")


if __name__ == "__main__":
    print("Testando conexão")
    try:
        with driver.session() as session:
            msg = session.run("RETURN 'Conectado' AS msg").single()["msg"]
            print(msg)
    except Exception as e:
        print("Erro ao conectar:", e)
    else:
        menu()
