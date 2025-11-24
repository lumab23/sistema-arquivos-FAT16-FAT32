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

DIR_TIPO_INDICE = 3  
TIPO_ARQUIVO = False
TIPO_DIRETORIO = True

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
        if "/" in nome_arquivo:
            partes = nome_arquivo.split("/")
            if len(partes) != 2:
                print("Erro: O sistema suporta apenas 1 nível (ex: pasta/arquivo.txt).")
                return None
            
            nome_pasta, nome_real_arquivo = partes[0], partes[1]
            
            if nome_pasta not in self._diretorio:
                print(f"Erro: Pasta '{nome_pasta}' não encontrada.")
                return None
            
            meta_pasta = self._diretorio[nome_pasta]
            if len(meta_pasta) <= 3 or meta_pasta[DIR_TIPO_INDICE] != TIPO_DIRETORIO:
                print(f"Erro: '{nome_pasta}' não é um diretório válido.")
                return None

            cluster_pasta = meta_pasta[DIR_CLUSTER_INICIAL_INDEX]
            bytes_pasta = self._driver.ler_cluster(cluster_pasta)
            dic_pasta = json.loads(bytes_pasta.decode("utf-8").strip("\x00"))

            if nome_real_arquivo not in dic_pasta:
                print(f"Erro: Arquivo '{nome_real_arquivo}' não encontrado em '{nome_pasta}'.")
                return None
            
            metadados = dic_pasta[nome_real_arquivo]
        
        else:
            if nome_arquivo not in self._diretorio:
                print(f"Erro: Arquivo '{nome_arquivo}' não encontrado.")
                return None
            metadados = self._diretorio[nome_arquivo]

        if len(metadados) > 3 and metadados[DIR_TIPO_INDICE] == TIPO_DIRETORIO:
            print(f"Erro: '{nome_arquivo}' é um diretório.")
            return None

        tamanho = metadados[DIR_TAMANHO_INDICE]
        atual_cluster = metadados[DIR_CLUSTER_INICIAL_INDEX]

        conteudo_bytes_completo = b""
        while atual_cluster != FAT_FIM_DE_ARQUIVO and atual_cluster is not None:
            chunk_bytes = self._driver.ler_cluster(atual_cluster)
            if chunk_bytes is None:
                break
            conteudo_bytes_completo += chunk_bytes
            
            if atual_cluster < len(self._fat):
                atual_cluster = self._fat[atual_cluster]
            else:
                break

        return conteudo_bytes_completo[:tamanho].decode("utf-8")

    def definir_atributo_somente_leitura(self, nome_arquivo, status):
        path_pasta = ""
        nome_real = nome_arquivo
        
        if "/" in nome_arquivo:
            partes = nome_arquivo.split("/")
            if len(partes) != 2:
                print("Erro: Use o formato pasta/arquivo.")
                return False
            path_pasta, nome_real = partes[0], partes[1]

        if path_pasta == "":
            if nome_real not in self._diretorio:
                print(f"Erro: Arquivo '{nome_real}' não encontrado na raiz.")
                return False

            self._diretorio[nome_real][DIR_SOMENTE_LEITURA_INDICE] = status
            self._salvar_metadados()

            estado = "SOMENTE LEITURA" if status else "EDITÁVEL"
            print(f"Atributo '{estado}' definido para '{nome_real}'.")
            return True

        else:
            if path_pasta not in self._diretorio:
                print(f"Erro: Pasta '{path_pasta}' não encontrada.")
                return False
            
            meta_pasta = self._diretorio[path_pasta]
            if len(meta_pasta) <= 3 or meta_pasta[DIR_TIPO_INDICE] != TIPO_DIRETORIO:
                print(f"Erro: '{path_pasta}' não é um diretório.")
                return False

            cluster_pasta = meta_pasta[DIR_CLUSTER_INICIAL_INDEX]
            bytes_pasta = self._driver.ler_cluster(cluster_pasta)
            dic_pasta = json.loads(bytes_pasta.decode("utf-8").strip("\x00"))

            if nome_real not in dic_pasta:
                print(f"Erro: Arquivo '{nome_real}' não encontrado em '{path_pasta}'.")
                return False

            dic_pasta[nome_real][DIR_SOMENTE_LEITURA_INDICE] = status

            novo_json = json.dumps(dic_pasta).encode("utf-8")
            self._driver.escrever_cluster(cluster_pasta, novo_json)
            self._salvar_metadados()

            estado = "SOMENTE LEITURA" if status else "EDITÁVEL"
            print(f"Atributo '{estado}' definido para '{path_pasta}/{nome_real}'.")
            return True

    def escrever_arquivo(self, nome_arquivo, conteudo, somente_leitura=False):
        path_pasta = ""
        nome_real = nome_arquivo
        usar_pasta = False
        dic_alvo = self._diretorio

        if "/" in nome_arquivo:
            partes = nome_arquivo.split("/")
            if len(partes) != 2:
                print("Erro: Use formato pasta/arquivo.")
                return False
            path_pasta, nome_real = partes[0], partes[1]
            usar_pasta = True
            
            if path_pasta not in self._diretorio:
                print(f"Erro: Pasta '{path_pasta}' não encontrada.")
                return False
            
            meta_pasta = self._diretorio[path_pasta]
            if len(meta_pasta) <= 3 or meta_pasta[DIR_TIPO_INDICE] != TIPO_DIRETORIO:
                print(f"Erro: '{path_pasta}' não é um diretório.")
                return False

            cluster_pasta_id = meta_pasta[DIR_CLUSTER_INICIAL_INDEX]
            bytes_pasta = self._driver.ler_cluster(cluster_pasta_id)
            dic_alvo = json.loads(bytes_pasta.decode("utf-8").strip("\x00"))

        if nome_real in dic_alvo:
            if dic_alvo[nome_real][DIR_SOMENTE_LEITURA_INDICE] is True:
                print(f"Erro: '{nome_real}' é somente leitura.")
                return False
            self._liberar_cadeia(dic_alvo[nome_real][DIR_CLUSTER_INICIAL_INDEX])

        conteudo_bytes = conteudo.encode("utf-8")
        conteudo_tamanho = len(conteudo_bytes)
        num_clusters = (conteudo_tamanho + TAMANHO_CLUSTER - 1) // TAMANHO_CLUSTER

        iniciar_cluster = None
        atual_cluster = None

        for i in range(num_clusters):
            cluster_livre = self._encontrar_cluster_livre()
            if cluster_livre is None:
                print("Erro: Disco cheio.")
                if iniciar_cluster: self._liberar_cadeia(iniciar_cluster)
                return False

            if iniciar_cluster is None: iniciar_cluster = cluster_livre
            if atual_cluster is not None: self._fat[atual_cluster] = cluster_livre
            
            atual_cluster = cluster_livre
            
            inicio = i * TAMANHO_CLUSTER
            fim = inicio + TAMANHO_CLUSTER
            chunk = conteudo_bytes[inicio:fim]
            self._driver.escrever_cluster(atual_cluster, chunk)

        if atual_cluster is not None:
            self._fat[atual_cluster] = FAT_FIM_DE_ARQUIVO
        
        nova_entrada = [
            conteudo_tamanho,
            iniciar_cluster,
            somente_leitura,
            TIPO_ARQUIVO 
        ]

        if usar_pasta:
            dic_alvo[nome_real] = nova_entrada
            novo_json = json.dumps(dic_alvo).encode("utf-8")
            self._driver.escrever_cluster(cluster_pasta_id, novo_json)
            self._salvar_metadados()
        else:
            self._diretorio[nome_real] = nova_entrada
            self._salvar_metadados()

        print(f"Sucesso: '{nome_arquivo}' salvo.")
        return True

    def apagar_arquivo(self, nome_arquivo):
        if "/" in nome_arquivo:
            partes = nome_arquivo.split("/")
            if len(partes) != 2:
                print("Erro: O sistema suporta apenas 1 nível (ex: pasta/arquivo.txt).")
                return False
            
            nome_pasta, nome_real_arquivo = partes[0], partes[1]
            
            if nome_pasta not in self._diretorio:
                print(f"Erro: Pasta '{nome_pasta}' não encontrada.")
                return False
            
            meta_pasta = self._diretorio[nome_pasta]
            if len(meta_pasta) <= 3 or meta_pasta[DIR_TIPO_INDICE] != TIPO_DIRETORIO:
                print(f"Erro: '{nome_pasta}' não é um diretório válido.")
                return False

            cluster_pasta = meta_pasta[DIR_CLUSTER_INICIAL_INDEX]
            bytes_pasta = self._driver.ler_cluster(cluster_pasta)
            dic_pasta = json.loads(bytes_pasta.decode("utf-8").strip("\x00"))

            if nome_real_arquivo not in dic_pasta:
                print(f"Erro: Arquivo '{nome_real_arquivo}' não encontrado em '{nome_pasta}'.")
                return False
            
            metadados = dic_pasta[nome_real_arquivo]

            if metadados[DIR_SOMENTE_LEITURA_INDICE] is True:
                print(f"Erro: Arquivo '{nome_real_arquivo}' é somente leitura.")
                return False

            cluster_inicial = metadados[DIR_CLUSTER_INICIAL_INDEX]
            self._liberar_cadeia(cluster_inicial)

            del dic_pasta[nome_real_arquivo]

            novo_json = json.dumps(dic_pasta).encode("utf-8")
            self._driver.escrever_cluster(cluster_pasta, novo_json)
            self._salvar_metadados()
            
            print(f"Sucesso: Arquivo '{nome_real_arquivo}' apagado de '{nome_pasta}'.")
            return True

        else:
            if nome_arquivo not in self._diretorio:
                print(f"Erro: Arquivo '{nome_arquivo}' não encontrado.")
                return False

            if self._diretorio[nome_arquivo][DIR_SOMENTE_LEITURA_INDICE] is True:
                print(f"Erro: Arquivo '{nome_arquivo}' é somente leitura.")
                return False

            cluster_inicial = self._diretorio[nome_arquivo][DIR_CLUSTER_INICIAL_INDEX]
            self._liberar_cadeia(cluster_inicial)

            del self._diretorio[nome_arquivo]
            self._salvar_metadados()
            print(f"Sucesso: Arquivo '{nome_arquivo}' apagado.")
            return True

    def renomear_arquivo(self, nome_antigo, nome_novo):
        path_antigo = ""
        arquivo_antigo_nome = nome_antigo
        
        if "/" in nome_antigo:
            partes = nome_antigo.split("/")
            if len(partes) != 2:
                print("Erro: Use o formato pasta/arquivo.")
                return False
            path_antigo = partes[0]
            arquivo_antigo_nome = partes[1]

        arquivo_novo_nome = nome_novo
        path_novo = ""
        if "/" in nome_novo:
            partes_novo = nome_novo.split("/")
            path_novo = partes_novo[0]
            arquivo_novo_nome = partes_novo[1]
        
        if path_antigo != path_novo:
             print("Erro: Para mover arquivos entre pastas, use a opção 'Mover'.")
             return False
        
        if path_antigo == "":
            if arquivo_antigo_nome not in self._diretorio:
                print(f"Erro: Arquivo '{arquivo_antigo_nome}' não encontrado na raiz.")
                return False
            
            if self._diretorio[arquivo_antigo_nome][DIR_SOMENTE_LEITURA_INDICE] is True:
                print(f"Erro: '{arquivo_antigo_nome}' é somente leitura.")
                return False
                
            if arquivo_novo_nome in self._diretorio:
                print(f"Erro: Já existe '{arquivo_novo_nome}' na raiz.")
                return False

            self._diretorio[arquivo_novo_nome] = self._diretorio.pop(arquivo_antigo_nome)
            self._salvar_metadados()
            print(f"Sucesso: '{arquivo_antigo_nome}' renomeado para '{arquivo_novo_nome}'.")
            return True

        else:
            if path_antigo not in self._diretorio:
                print(f"Erro: Pasta '{path_antigo}' não encontrada.")
                return False
                
            meta_pasta = self._diretorio[path_antigo]
            if len(meta_pasta) <= 3 or meta_pasta[DIR_TIPO_INDICE] != TIPO_DIRETORIO:
                print(f"Erro: '{path_antigo}' não é um diretório.")
                return False

            cluster_pasta = meta_pasta[DIR_CLUSTER_INICIAL_INDEX]
            bytes_pasta = self._driver.ler_cluster(cluster_pasta)
            dic_pasta = json.loads(bytes_pasta.decode("utf-8").strip("\x00"))

            if arquivo_antigo_nome not in dic_pasta:
                print(f"Erro: '{arquivo_antigo_nome}' não encontrado em '{path_antigo}'.")
                return False

            if dic_pasta[arquivo_antigo_nome][DIR_SOMENTE_LEITURA_INDICE] is True:
                print(f"Erro: Arquivo é somente leitura.")
                return False

            if arquivo_novo_nome in dic_pasta:
                print(f"Erro: Já existe '{arquivo_novo_nome}' nesta pasta.")
                return False

            dic_pasta[arquivo_novo_nome] = dic_pasta.pop(arquivo_antigo_nome)

            novo_json = json.dumps(dic_pasta).encode("utf-8")
            self._driver.escrever_cluster(cluster_pasta, novo_json)
            self._salvar_metadados() 
            
            print(f"Sucesso: '{path_antigo}/{arquivo_antigo_nome}' renomeado para '{path_antigo}/{arquivo_novo_nome}'.")
            return True

    def listar_arquivos(self, nome_pasta=None):
        if nome_pasta is None:
            alvo = self._diretorio
            nome_contexto = "Diretório Raiz"
        else:
            if nome_pasta not in self._diretorio:
                print(f"Erro: Pasta '{nome_pasta}' não encontrada.")
                return
            
            metadados_pasta = self._diretorio[nome_pasta]
            if len(metadados_pasta) <= 3 or metadados_pasta[DIR_TIPO_INDICE] != TIPO_DIRETORIO:
                print(f"Erro: '{nome_pasta}' não é um diretório válido.")
                return

            cluster_pasta = metadados_pasta[DIR_CLUSTER_INICIAL_INDEX]
            bytes_pasta = self._driver.ler_cluster(cluster_pasta)
            alvo = json.loads(bytes_pasta.decode("utf-8").strip("\x00"))
            nome_contexto = f"Pasta '/{nome_pasta}'"

        print(f"\n--- {nome_contexto} ---")
        if not alvo:
            print(" (Vazio) ")
            return

        print(f"{'Nome':<20} | {'Tam.(bytes)':<12} | {'Cluster':<8} | {'Atributos'}")
        print("-" * 65)

        for nome, entry in alvo.items():
            eh_diretorio = entry[DIR_TIPO_INDICE] if len(entry) > 3 else False
            tipo_str = "<DIR>" if eh_diretorio else "ARQ"
            attr_str = "R/O" if entry[DIR_SOMENTE_LEITURA_INDICE] else "RW"
            tamanho = entry[DIR_TAMANHO_INDICE]
            cluster = entry[DIR_CLUSTER_INICIAL_INDEX]
            print(f"{nome:<20} | {tamanho:<12} | {cluster:<8} | {tipo_str} {attr_str}")
        print("-" * 65)

    def mkdir(self, nome_pasta):
        if nome_pasta in self._diretorio:
            print(f"Erro: '{nome_pasta}' já existe.")
            return False

        cluster_livre = self._encontrar_cluster_livre()
        if cluster_livre is None:
            print("Erro: Disco cheio.")
            return False

        
        conteudo_dir = json.dumps({}).encode("utf-8")
        
        self._driver.escrever_cluster(cluster_livre, conteudo_dir)
        self._fat[cluster_livre] = FAT_FIM_DE_ARQUIVO

        self._diretorio[nome_pasta] = [0, cluster_livre, False, TIPO_DIRETORIO]
        self._salvar_metadados()
        
        print(f"Diretório '{nome_pasta}' criado com sucesso.")
        return True

    def mover_arquivo(self, nome_arquivo, nome_pasta_destino):
        if nome_arquivo not in self._diretorio:
            print(f"Erro: Arquivo de origem '{nome_arquivo}' não encontrado na raiz.")
            return False
        
        if nome_pasta_destino not in self._diretorio:
            print(f"Erro: Pasta de destino '{nome_pasta_destino}' não encontrada.")
            return False

        meta_destino = self._diretorio[nome_pasta_destino]
        if len(meta_destino) <= 3 or meta_destino[DIR_TIPO_INDICE] != TIPO_DIRETORIO:
            print(f"Erro: '{nome_pasta_destino}' não é uma pasta.")
            return False

        meta_origem = self._diretorio[nome_arquivo]
        if len(meta_origem) > 3 and meta_origem[DIR_TIPO_INDICE] == TIPO_DIRETORIO:
            print("Erro: Este sistema 'mini' não suporta mover pastas, apenas arquivos.")
            return False

        cluster_dest = meta_destino[DIR_CLUSTER_INICIAL_INDEX]
        bytes_dest = self._driver.ler_cluster(cluster_dest)
        dic_destino = json.loads(bytes_dest.decode("utf-8").strip("\x00"))

        if nome_arquivo in dic_destino:
            print(f"Erro: Já existe um arquivo '{nome_arquivo}' na pasta '{nome_pasta_destino}'.")
            return False

        dic_destino[nome_arquivo] = meta_origem
        
        novo_json = json.dumps(dic_destino).encode("utf-8")
        if not self._driver.escrever_cluster(cluster_dest, novo_json):
            print("Erro fatal ao salvar no diretório destino.")
            return False

        del self._diretorio[nome_arquivo]
        self._salvar_metadados()
        
        print(f"Sucesso: '{nome_arquivo}' movido para '/{nome_pasta_destino}'.")
        return True
