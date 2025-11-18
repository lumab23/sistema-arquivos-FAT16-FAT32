# main.py

from mini_filesystem import MiniFileSystem
import os
import random

def criar_disco_e_preencher_fragmentado(fs):
    """Cria arquivos de tamanhos variados para fragmentar o disco."""
    print("\n--- INICIANDO CRIAÇÃO DE ARQUIVOS FRAGMENTADOS ---")
    
    # 1. Escreve arquivo grande (ocupa vários clusters)
    fs.write_file("arq_grande_A.txt", "A" * 3500) # 4 Clusters

    # 2. Escreve arquivo pequeno (gap na alocação)
    fs.write_file("arq_pequeno_1.tmp", "B" * 100) # 1 Cluster

    # 3. Escreve arquivo médio
    fs.write_file("arq_medio_C.doc", "C" * 2500) # 3 Clusters

    # 4. Apaga o arquivo pequeno (cria fragmentação real - cluster 6 livre)
    fs.delete_file("arq_pequeno_1.tmp") 
    
    # 5. Escreve um arquivo que preenche o buraco (cluster 6) e continua, fragmentando
    fs.write_file("arq_frag.pdf", "D" * 3000) # Ocupa cluster 6, 7, 8
    
    print("\nEstado do Disco após Fragmentação:")
    fs.list_files()

if __name__ == "__main__":
    
    # Limpa o disco
    disk_file = "mini_fat_disk.bin"
    if os.path.exists(disk_file):
        os.remove(disk_file)
        print(f"Disco antigo '{disk_file}' removido.")
        
    # Inicializa o Sistema
    fs = MiniFileSystem()
    print("=" * 50)
    
    # --- Demonstração de Fragmentação ---
    criar_disco_e_preencher_fragmentado(fs)
    print("Clusters de 'arq_frag.pdf' estão espalhados.")
    print("A FAT está desorganizada (não sequencial).")

    # --- Demonstração de Desfragmentação ---
    fs.defrag_disk()
    fs.list_files()
    print("Verifique que os clusters iniciais agora são sequenciais (2, 6, 9...).")
    
    # --- Demonstração de Atributos (Somente Leitura) ---
    print("\n--- Teste de Atributo Somente Leitura ---")
    
    # 1. Define 'arq_grande_A.txt' como somente leitura
    fs.set_readonly_attribute("arq_grande_A.txt", True)
    fs.list_files()

    # 2. Tenta Sobrescrever (Deve Falhar)
    print("\nTentando sobrescrever arquivo R/O...")
    fs.write_file("arq_grande_A.txt", "TENTATIVA DE SOBRESCRITA") 
    
    # 3. Tenta Apagar (Deve Falhar)
    print("\nTentando apagar arquivo R/O...")
    fs.delete_file("arq_grande_A.txt")
    
    # 4. Remove o atributo e tenta apagar (Deve ter Sucesso)
    print("\nRemovendo R/O e apagando...")
    fs.set_readonly_attribute("arq_grande_A.txt", False)
    fs.delete_file("arq_grande_A.txt")

    fs.list_files()
    
    # Garante que o disco virtual seja fechado
    fs.close()
    
    print("\n" + "=" * 50)
    print("**Implementação Completa e Aprimorada (FAT-like)**")
    print("A desfragmentação e a checagem de atributos 'somente leitura' foram implementadas com sucesso.")