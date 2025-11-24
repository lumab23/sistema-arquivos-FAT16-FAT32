import os
from sistema_arquivos import SistemaArquivos

def exibir_menu():
    print("\n" + "="*40)
    print("   SISTEMA DE ARQUIVOS (Modo Interativo)")
    print("="*40)
    print("1. Listar arquivos (dir/ls)")
    print("2. Escrever arquivo (write)")
    print("3. Ler arquivo (read)")
    print("4. Apagar arquivo (del)")
    print("5. Renomear arquivo (rename)")
    print("6. Alterar permissões R/O (attrib)")
    print("7. Criar Diretório (mkdir)")
    print("8. Mover arquivo para pasta (move)") 
    print("9. Sair")
    print("-" * 40)

def main():
    fs = SistemaArquivos()

    while True:
        exibir_menu()
        opcao = input("Escolha uma opção (1-9): ").strip()

        if opcao == "1":
            subpasta = input("Pressione ENTER para raiz ou digite o nome da pasta: ").strip()
            if subpasta:
                fs.listar_arquivos(subpasta)
            else:
                fs.listar_arquivos()

        elif opcao == "2":
            print("\n--- Escrever Arquivo (na Raiz) ---")
            nome = input("Nome do arquivo (ex: notas.txt): ").strip()
            if not nome:
                print("Erro: O nome não pode estar vazio.")
                continue
            conteudo = input("Conteúdo do arquivo: ")
            fs.escrever_arquivo(nome, conteudo)

        elif opcao == "3":
            print("\n--- Ler Arquivo ---")
            nome = input("Nome do arquivo a ler: ").strip()
            conteudo = fs.ler_arquivo(nome)
            if conteudo is not None:
                print(f"\n[CONTEÚDO DE '{nome}']: \n{conteudo}")

        elif opcao == "4":
            print("\n--- Apagar Arquivo ---")
            nome = input("Nome do arquivo a apagar: ").strip()
            fs.apagar_arquivo(nome)

        elif opcao == "5":
            print("\n--- Renomear Arquivo ---")
            antigo = input("Nome atual: ").strip()
            novo = input("Novo nome: ").strip()
            fs.renomear_arquivo(antigo, novo)

        elif opcao == "6":
            print("\n--- Alterar Permissões ---")
            nome = input("Nome do arquivo: ").strip()
            escolha = input("Tornar somente leitura? (s/n): ").strip().lower()
            if escolha == 's':
                fs.definir_atributo_somente_leitura(nome, True)
            elif escolha == 'n':
                fs.definir_atributo_somente_leitura(nome, False)

        elif opcao == "7":
            print("\n--- Criar Diretório ---")
            nome = input("Nome do diretório: ").strip()
            if nome: fs.mkdir(nome)

        elif opcao == "8":
            print("\n--- Mover Arquivo ---")
            arquivo = input("Nome do arquivo (na raiz): ").strip()
            pasta = input("Nome da pasta destino: ").strip()
            if arquivo and pasta:
                fs.mover_arquivo(arquivo, pasta)

        elif opcao == "9":
            print("\nFechando sistema...")
            fs.fechar()
            break
        else:
            print("Opção inválida!")

if __name__ == "__main__":
    if os.path.exists("mini_fat_disco.bin"):
        print("Disco encontrado. Carregando...")
    else:
        print("Novo disco criado.")
    main()
