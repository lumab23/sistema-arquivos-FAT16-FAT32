import copy
import json

from driver_disco import (
    FAT_FIM_DE_ARQUIVO,
    FAT_LIVRE,
    FAT_RESERVADO,
    TAMANHO_CLUSTER,
    TOTAL_CLUSTERS,
    DriverDisco,
)

CLUSTER_INICIAL_DADOS = 2
CLUSTERS_DADOS = TOTAL_CLUSTERS - CLUSTER_INICIAL_DADOS

DIR_TAMANHO_INDICE = 0
DIR_CLUSTER_INICIAL_INDEX = 1
DIR_SOMENTE_LEITURA_INDICE = 2


class SistemaArquivos:
    def __init__(self):
        self._driver = DriverDisco()
        self._fat = [FAT_RESERVADO, FAT_RESERVADO] + [FAT_LIVRE] * CLUSTERS_DADOS
        self._diretorio = {}

        self._carregar_metadados()

    def fechar(self):
        self._driver.fechar()

    def _carregar_metadados(self):
        try:
            fat_bytes = self._driver.ler_cluster(0)
            if fat_bytes is None:
                raise IOError("Falha ao ler o cluster 0.")

            fat_data = json.loads(fat_bytes.decode("utf-8").strip("\x00"))
            self._fat = fat_data["fat"]

            dir_bytes = self._driver.ler_cluster(1)
            if dir_bytes is None:
                raise IOError("Falha ao ler o cluster 1.")

            dir_dados = json.loads(dir_bytes.decode("utf-8").strip("\x00"))
            self._diretorio = dir_dados["diretorio"]
            print("\n**Metadados (FAT e Diretório) carregados com sucesso.**")

        except (
            AttributeError,
            json.JSONDecodeError,
            KeyError,
            IndexError,
            TypeError,
            IOError,
        ):
            print(
                "\n**Erro: Metadados não encontrados ou corrompidos. Inicializando novo sistema.**"
            )
            self._salvar_metadados()

    def _salvar_metadados(self):
        fat_data = {"fat": self._fat}
        fat_bytes = json.dumps(fat_data).encode("utf-8")
        self._driver.escrever_cluster(0, fat_bytes)

        dir_dados = {"diretorio": self._diretorio}
        dir_bytes = json.dumps(dir_dados).encode("utf-8")
        self._driver.escrever_cluster(1, dir_bytes)
        print("Metadados salvos.")

    def _encontrar_cluster_livre(self):
        try:
            return self._fat.index(FAT_LIVRE, CLUSTER_INICIAL_DADOS)
        except ValueError:
            return None

    def _liberar_cadeia(self, iniciar_cluster):
        atual = iniciar_cluster
        while atual != FAT_FIM_DE_ARQUIVO and atual is not None:
            proximo_cluster = self._fat[atual]
            self._fat[atual] = FAT_LIVRE
            atual = proximo_cluster

    def ler_arquivo(self, nome_arquivo):
        if nome_arquivo not in self._diretorio:
            print(f"Erro: Arquivo '{nome_arquivo}' não encontrado.")
            return None

        tamanho, atual_cluster, _ = self._diretorio[nome_arquivo]
        conteudo_bytes_completo = b""

        while atual_cluster != FAT_FIM_DE_ARQUIVO and atual_cluster is not None:
            chunk_bytes = self._driver.ler_cluster(atual_cluster)

            if chunk_bytes is None:
                print(
                    f"Aviso: Erro de leitura no cluster {atual_cluster}. Interrompendo leitura."
                )
                break

            conteudo_bytes_completo += chunk_bytes

            if atual_cluster < len(self._fat):
                atual_cluster = self._fat[atual_cluster]
            else:
                break

        return conteudo_bytes_completo[:tamanho].decode("utf-8")

    def definir_atributo_somente_leitura(self, nome_arquivo, status):
        if nome_arquivo not in self._diretorio:
            print(f"Erro: Arquivo '{nome_arquivo}' não encontrado.")
            return False

        self._diretorio[nome_arquivo][DIR_SOMENTE_LEITURA_INDICE] = status
        self._salvar_metadados()

        estado = "SOMENTE LEITURA" if status else "EDITÁVEL"
        print(f"Atributo '{estado}' definido para '{nome_arquivo}'.")
        return True

    def escrever_arquivo(self, nome_arquivo, conteudo, somente_leitura=False):
        conteudo_bytes = conteudo.encode("utf-8")
        conteudo_tamanho = len(conteudo_bytes)

        if (
            nome_arquivo in self._diretorio
            and self._diretorio[nome_arquivo][DIR_SOMENTE_LEITURA_INDICE] is True
        ):
            print(
                f"Erro: Arquivo '{nome_arquivo}' está como SOMENTE LEITURA e não pode ser sobrescrito."
            )
            return False

        if nome_arquivo in self._diretorio:
            print(f"Sobrescrevendo '{nome_arquivo}'. Liberando clusters antigos.")
            self._liberar_cadeia(
                self._diretorio[nome_arquivo][DIR_CLUSTER_INICIAL_INDEX]
            )

        num_clusters_necessario = (
            conteudo_tamanho + TAMANHO_CLUSTER - 1
        ) // TAMANHO_CLUSTER

        iniciar_cluster = None
        atual_cluster = None

        for i in range(num_clusters_necessario):
            cluster_livre = self._encontrar_cluster_livre()

            if cluster_livre is None:
                print("Erro: Disco cheio. Não é possível concluir a escrita.")
                if iniciar_cluster:
                    self._liberar_cadeia(iniciar_cluster)
                return False

            if iniciar_cluster is None:
                iniciar_cluster = cluster_livre
            if atual_cluster is not None:
                self._fat[atual_cluster] = cluster_livre

            atual_cluster = cluster_livre

            inicio = i * TAMANHO_CLUSTER
            fim = inicio + TAMANHO_CLUSTER
            chunk = conteudo_bytes[inicio:fim]

            self._driver.escrever_cluster(atual_cluster, chunk)

        if atual_cluster is not None:
            self._fat[atual_cluster] = FAT_FIM_DE_ARQUIVO

            self._diretorio[nome_arquivo] = [
                conteudo_tamanho,
                iniciar_cluster,
                somente_leitura,
            ]

            self._salvar_metadados()
            print(
                f"Arquivo '{nome_arquivo}' escrito com sucesso no cluster {iniciar_cluster}."
            )
            return True

        return False

    def apagar_arquivo(self, nome_arquivo):
        if nome_arquivo not in self._diretorio:
            print(f"Erro: Arquivo '{nome_arquivo}' não encontrado para apagar.")
            return False

        if self._diretorio[nome_arquivo][DIR_SOMENTE_LEITURA_INDICE] is True:
            print(
                f"Erro: Arquivo '{nome_arquivo}' está como SOMENTE LEITURA e não pode ser apagado."
            )
            return False

        cluster_inicial = self._diretorio[nome_arquivo][DIR_CLUSTER_INICIAL_INDEX]
        self._liberar_cadeia(cluster_inicial)

        del self._diretorio[nome_arquivo]
        self._salvar_metadados()
        print(f"Sucesso: Arquivo '{nome_arquivo}' apagado e clusters liberados.")
        return True

    def renomear_arquivo(self, nome_antigo, nome_novo):
        if nome_antigo not in self._diretorio:
            print(f"Erro: Arquivo '{nome_antigo}' não encontrado para renomear.")
            return False

        if self._diretorio[nome_antigo][DIR_SOMENTE_LEITURA_INDICE] is True:
            print(
                f"Erro: Arquivo '{nome_antigo}' está como SOMENTE LEITURA e não pode ser renomeado."
            )
            return False

        if nome_novo in self._diretorio:
            print(f"Erro: Já existe um arquivo chamado '{nome_novo}'.")
            return False

        self._diretorio[nome_novo] = self._diretorio.pop(nome_antigo)
        self._salvar_metadados()
        print(f"Sucesso: Arquivo '{nome_antigo}' renomeado para '{nome_novo}'.")
        return True

    def listar_arquivos(self):
        print("\n--- Diretório Raiz ---")
        if not self._diretorio:
            print("Diretório vazio.")
            return

        print(
            f"{'Nome do Arquivo':<20} | {'Tamanho (bytes)':<15} | {'Cluster Inicial':<15} | {'Atributo'}"
        )
        print("-" * 75)
        for nome, entry in self._diretorio.items():
            attr = "R/O" if entry[DIR_SOMENTE_LEITURA_INDICE] else "EDITÁVEL"
            print(
                f"{nome:<20} | {entry[DIR_TAMANHO_INDICE]:<15} | {entry[DIR_CLUSTER_INICIAL_INDEX]:<15} | {attr}"
            )
        print("-" * 75)

    def desfragmentar_disco(self):
        print("\n--- INICIANDO DESFRAGMENTAÇÃO (Processo Lento) ---")

        diretorio_para_iterar = copy.deepcopy(self._diretorio)
        novo_diretorio = {}

        self._fat = [FAT_RESERVADO, FAT_RESERVADO] + [FAT_LIVRE] * CLUSTERS_DADOS

        proximo_cluster = CLUSTER_INICIAL_DADOS

        for nome_arquivo, entry_antiga in diretorio_para_iterar.items():
            tamanho, cluster_inicial_antigo, somente_leitura = entry_antiga

            cadeia_antiga = []
            atual_cluster = cluster_inicial_antigo
            while atual_cluster != FAT_FIM_DE_ARQUIVO and atual_cluster is not None:
                cadeia_antiga.append(atual_cluster)
                atual_cluster = self._fat[atual_cluster]

            cluster_inicial_novo = proximo_cluster
            ultimo_novo_cluster = None

            for cluster_antigo in cadeia_antiga:
                dados_chunk = self._driver.ler_cluster(cluster_antigo)

                if dados_chunk is None:
                    print(
                        f"Aviso: Cluster {cluster_antigo} não pôde ser lido durante a desfragmentação. Dados perdidos."
                    )
                    break

                self._driver.escrever_cluster(proximo_cluster, dados_chunk)

                if ultimo_novo_cluster is not None:
                    self._fat[ultimo_novo_cluster] = proximo_cluster

                ultimo_novo_cluster = proximo_cluster
                proximo_cluster += 1

            if ultimo_novo_cluster is not None:
                self._fat[ultimo_novo_cluster] = FAT_FIM_DE_ARQUIVO

            novo_diretorio[nome_arquivo] = [
                tamanho,
                cluster_inicial_novo,
                somente_leitura,
            ]
            print(
                f"Arquivo '{nome_arquivo}' movido de {cluster_inicial_antigo} para {cluster_inicial_novo}."
            )

        self._diretorio = novo_diretorio
        self._salvar_metadados()

        print("--- DESFRAGMENTAÇÃO CONCLUÍDA. Clusters agora são sequenciais. ---")
