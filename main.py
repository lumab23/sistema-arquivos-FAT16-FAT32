import os

from sistema_arquivos import SistemaArquivos

def criar_disco_e_preencher_fragmentado(fs):
    print("\n--- INICIANDO CRIAÇÃO DE ARQUIVOS FRAGMENTADOS ---")

    fs.escrever_arquivo("arq_grande_A.txt", "A" * 3500)

    fs.escrever_arquivo("arq_pequeno_1.tmp", "B" * 100)

    fs.escrever_arquivo("arq_medio_C.doc", "C" * 2500)

    fs.apagar_arquivo("arq_pequeno_1.tmp")

    fs.escrever_arquivo("arq_frag.pdf", "D" * 3000)

    print("\nEstado do Disco após Fragmentação:")
    fs.listar_arquivos()


if __name__ == "__main__":
    ARQUIVO_DISCO_CORRIGIDO = "mini_fat_disco.bin"
    if os.path.exists(ARQUIVO_DISCO_CORRIGIDO):
        os.remove(ARQUIVO_DISCO_CORRIGIDO)
        print(f"Disco antigo '{ARQUIVO_DISCO_CORRIGIDO}' removido.")

    fs = SistemaArquivos()
    print("=" * 50)

    criar_disco_e_preencher_fragmentado(fs)
    print("Clusters de 'arq_frag.pdf' estão espalhados.")

    fs.desfragmentar_disco()
    fs.listar_arquivos()

    print("\n--- Teste de Atributo Somente Leitura ---")

    fs.definir_atributo_somente_leitura("arq_grande_A.txt", True)
    fs.listar_arquivos()

    print("\nTentando sobrescrever arquivo R/O...")
    fs.escrever_arquivo("arq_grande_A.txt", "TENTATIVA DE SOBRESCRITA")

    print("\nTentando apagar arquivo R/O...")
    fs.apagar_arquivo("arq_grande_A.txt")

    print("\nRemovendo R/O e apagando...")
    fs.definir_atributo_somente_leitura("arq_grande_A.txt", False)
    fs.apagar_arquivo("arq_grande_A.txt")

    fs.listar_arquivos()

    print("\n--- Teste de Leitura ---")
    fs.escrever_arquivo("teste_leitura.txt", "Testando a funcionalidade de leitura.")
    conteudo = fs.ler_arquivo("teste_leitura.txt")
    print(f"Conteúdo lido: {conteudo}")

    print("\n--- Teste de Renomear ---")
    fs.renomear_arquivo("teste_leitura.txt", "doc_final.txt")
    fs.listar_arquivos()

    fs.fechar()

    print("\n" + "=" * 50)
    print("**Implementação Completa e Aprimorada (FAT-like)**")
    print("O sistema está pronto para apresentação.")
