import os

TAMANHO_CLUSTER = 1024
TOTAL_CLUSTERS = 100
ARQUIVO_DISCO = "mini_fat_disco.bin"

FAT_FIM_DE_ARQUIVO = -1
FAT_LIVRE = 0
FAT_RESERVADO = 1


class DriverDisco:

    def __init__(self):
        self._disco = None
        self._inicializar_disco()

    def _inicializar_disco(self):
        try:
            tamanho_disco = TOTAL_CLUSTERS * TAMANHO_CLUSTER
            if not os.path.exists(ARQUIVO_DISCO):
                print(f"Criando novo disco virtual: {tamanho_disco} bytes")
                with open(ARQUIVO_DISCO, "wb") as f:
                    f.write(b"\x00" * tamanho_disco)

            self._disco = open(ARQUIVO_DISCO, "r+b")
            print(f"Disco virtual '{ARQUIVO_DISCO}' aberto com sucesso.")

        except IOError as e:
            print(f"ERRO FATAL: Não foi possível abrir/criar o arquivo de disco: {e}")
            self._disco = None

    def fechar(self):
        if self._disco:
            self._disco.close()
            print(f"Disco virtual '{ARQUIVO_DISCO}' fechado com sucesso.")
            self._disco = None

    def ler_cluster(self, indice_cluster):
        if self._disco is None:
            print("Erro: o disco não está acessível para leitura.")
            return None

        if 0 <= indice_cluster < TOTAL_CLUSTERS:
            deslocamento = indice_cluster * TAMANHO_CLUSTER
            self._disco.seek(deslocamento)
            return self._disco.read(TAMANHO_CLUSTER)
        return None

    def escrever_cluster(self, indice_cluster, dados):
        if self._disco is None:
            print("Erro: O disco não está acessível para escrita.")
            return False

        if 0 <= indice_cluster < TOTAL_CLUSTERS:
            if len(dados) > TAMANHO_CLUSTER:
                dados = dados[:TAMANHO_CLUSTER]
            elif len(dados) < TAMANHO_CLUSTER:
                dados += b"\x00" * (TAMANHO_CLUSTER - len(dados))

            deslocamento = indice_cluster * TAMANHO_CLUSTER
            self._disco.seek(deslocamento)
            self._disco.write(dados)
            return True
        return False
