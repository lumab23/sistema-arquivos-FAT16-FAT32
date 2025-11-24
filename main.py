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
    print("8. Sair")
    print("-" * 40)

def main():
    fs = SistemaArquivos()

    while True:
        exibir_menu()
        opcao = input("Escolha uma opção (1-8): ").strip()

        if opcao == "1":
            fs.listar_arquivos()

        elif opcao == "2":
            print("\n--- Escrever Arquivo ---")
            nome = input("Nome do arquivo (ex: notas.txt): ").strip()
            if not nome:
                print("Erro: O nome não pode estar vazio.")
                continue

            conteudo = input("Conteúdo do arquivo: ")

            sucesso = fs.escrever_arquivo(nome, conteudo)
            if not sucesso:
                print("Falha ao escrever o arquivo.")

        elif opcao == "3":
            print("\n--- Ler Arquivo ---")
            nome = input("Nome do arquivo a ler: ").strip()
            conteudo = fs.ler_arquivo(nome)

            if conteudo is not None:
                print(f"\n[INÍCIO DO ARQUIVO '{nome}']")
                print(conteudo)
                print(f"[FIM DO ARQUIVO '{nome}']")

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
            print("\n--- Alterar Permissões (Somente Leitura) ---")
            nome = input("Nome do arquivo: ").strip()
            escolha = input("Tornar somente leitura? (s/n): ").strip().lower()

            if escolha == 's':
                fs.definir_atributo_somente_leitura(nome, True)
            elif escolha == 'n':
                fs.definir_atributo_somente_leitura(nome, False)
            else:
                print("Opção inválida. Nenhuma alteração feita.")

        elif opcao == "7":
            print("\n--- Criar Diretório (mkdir) ---")
            nome = input("Nome do diretório: ").strip()
            if not nome:
                print("Erro: O nome do diretório não pode ser vazio.")
            else:
                fs.mkdir(nome)

        elif opcao == "8":
            print("\nFechando o sistema...")
            fs.fechar()
            break

        else:
            print("\nOpção inválida! Por favor, escolha um número de 1 a 8.")

if __name__ == "__main__":
    if os.path.exists("mini_fat_disco.bin"):
        print("Disco encontrado. Carregando sistema...")
    else:
        print("Disco não encontrado. Um novo será criado ao iniciar.")

    main()
