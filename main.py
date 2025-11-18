import os
from sistema_arquivos import SistemaArquivos

def exibir_menu():
    print("\n" + "="*40)
    print("   SISTEMA DE FICHEIROS (Modo Interativo)")
    print("="*40)
    print("1. Listar ficheiros (dir/ls)")
    print("2. Escrever ficheiro (write)")
    print("3. Ler ficheiro (read)")
    print("4. Apagar ficheiro (del)")
    print("5. Renomear ficheiro (rename)")
    print("6. Alterar permissões R/O (attrib)")
    print("7. Desfragmentar disco (defrag)")
    print("8. Sair")
    print("-" * 40)

def main():
    # Inicializa o sistema de arquivos (carrega metadados se existirem)
    fs = SistemaArquivos()
    
    while True:
        exibir_menu()
        opcao = input("Escolha uma opção (1-8): ").strip()

        if opcao == "1":
            # Chama o método existente para listar
            fs.listar_arquivos()

        elif opcao == "2":
            print("\n--- Escrever Ficheiro ---")
            nome = input("Nome do ficheiro (ex: notas.txt): ").strip()
            if not nome:
                print("Erro: O nome não pode estar vazio.")
                continue
            
            conteudo = input("Conteúdo do ficheiro: ")
            
            # Opcional: definir se nasce como apenas leitura
            # Por padrão, deixamos editável (False)
            sucesso = fs.escrever_arquivo(nome, conteudo)
            if not sucesso:
                print("Falha ao escrever o ficheiro.")

        elif opcao == "3":
            print("\n--- Ler Ficheiro ---")
            nome = input("Nome do ficheiro a ler: ").strip()
            conteudo = fs.ler_arquivo(nome)
            
            if conteudo is not None:
                print(f"\n[INÍCIO DO FICHEIRO '{nome}']")
                print(conteudo)
                print(f"[FIM DO FICHEIRO '{nome}']")

        elif opcao == "4":
            print("\n--- Apagar Ficheiro ---")
            nome = input("Nome do ficheiro a apagar: ").strip()
            fs.apagar_arquivo(nome)

        elif opcao == "5":
            print("\n--- Renomear Ficheiro ---")
            antigo = input("Nome atual: ").strip()
            novo = input("Novo nome: ").strip()
            fs.renomear_arquivo(antigo, novo)

        elif opcao == "6":
            print("\n--- Alterar Permissões (Somente Leitura) ---")
            nome = input("Nome do ficheiro: ").strip()
            escolha = input("Tornar somente leitura? (s/n): ").strip().lower()
            
            if escolha == 's':
                fs.definir_atributo_somente_leitura(nome, True)
            elif escolha == 'n':
                fs.definir_atributo_somente_leitura(nome, False)
            else:
                print("Opção inválida. Nenhuma alteração feita.")

        elif opcao == "7":
            print("\n--- Desfragmentação ---")
            confirmacao = input("Isso reorganizará os clusters. Continuar? (s/n): ").lower()
            if confirmacao == 's':
                fs.desfragmentar_disco()
                fs.listar_arquivos()

        elif opcao == "8":
            print("\nA fechar o sistema...")
            fs.fechar()
            break
        
        else:
            print("\nOpção inválida! Por favor, escolha um número de 1 a 8.")

if __name__ == "__main__":
    # Verifica se o disco existe apenas para log visual, o SistemaArquivos trata o resto
    if os.path.exists("mini_fat_disco.bin"):
        print("Disco encontrado. A carregar sistema...")
    else:
        print("Disco não encontrado. Um novo será criado ao iniciar.")

    main()