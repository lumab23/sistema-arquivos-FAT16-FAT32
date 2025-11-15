import json
from disk_driver import DiskDriver, TAMANHO_CLUSTER, TOTAL_CLUSTERS, FAT_FIM_DE_ARQUIVO, FAT_LIVRE, FAT_RESERVADO
import copy

FAT_INICIAR_CLUSTER = 2
DADOS_CLUSTERS = TOTAL_CLUSTERS - FAT_INICIAR_CLUSTER

# Estrutura do Diretório: {nome: [tamanho, cluster_inicial, is_readonly]}
DIR_TAMANHO_INDICE = 0
DIR_INICIAR_INDICE_CLUSTER = 1
DIR_READONLY_INDICE = 2

class MiniFileSystem:
    """
    Gerencia a lógica do sistema de arquivos (FAT e Diretório) com persistência.
    """
    
    def __init__(self):
        self._driver = DiskDriver()
        self._fat = [FAT_RESERVADO, FAT_RESERVADO] + [FAT_LIVRE] * DADOS_CLUSTERS
        self._directory = {}
        
        self._carregar_metadados()

    def _carregar_metadados(self):
        """Carrega FAT e Diretório dos clusters reservados (persistência)."""
        try:
            fat_bytes = self._driver.ler_cluster(0)
            fat_data = json.loads(fat_bytes.decode('utf-8').strip('\x00'))
            self._fat = fat_data['fat']
            
            dir_bytes = self._driver.ler_cluster(1)
            dir_dados = json.loads(dir_bytes.decode('utf-8').strip('\x00'))
            self._directory = dir_dados['directory']
            print("Metadados (FAT e Diretório) carregados com sucesso.")
            
        except (AttributeError, json.JSONDecodeError, KeyError, IndexError):
            print("Erro: Metadados não encontrados ou corrompidos. Inicializando novo sistema")
            self._salvar_metadados()

    def _salvar_metadados(self):
        """Salva FAT e Diretório nos clusters reservados (persistência)."""
        fat_data = {'fat': self._fat}
        fat_bytes = json.dumps(fat_data).encode('utf-8')
        self._driver.escrever_cluster(0, fat_bytes)
        
        dir_dados = {'directory': self._directory}
        dir_bytes = json.dumps(dir_dados).encode('utf-8')
        self._driver.escrever_cluster(1, dir_bytes)
        
    def _encontrar_cluster_livre(self):
        try:
            return self._fat.index(FAT_LIVRE, FAT_INICIAR_CLUSTER)
        except ValueError:
            return None
            
    def _liberar_cadeia(self, iniciar_cluster):
        atual = iniciar_cluster
        while atual != FAT_FIM_DE_ARQUIVO and atual is not None:
            proximo_cluster = self._fat[atual]
            self._fat[atual] = FAT_LIVRE
            atual = proximo_cluster

    def set_readonly_attribute(self, nome_arquivo, is_readonly):
        """Define o atributo 'somente leitura' de um arquivo."""
        if nome_arquivo not in self._directory:
            print(f"Erro: Arquivo '{nome_arquivo}' não encontrado.")
            return False
        
        self._directory[nome_arquivo][DIR_READONLY_INDICE] = is_readonly
        self._salvar_metadados()

        estado = "SOMENTE LEITURA" if is_readonly else "EDITÁVEL"
        print(f"Atributo '{estado}' definido para '{nome_arquivo}'.")
        return True
    

    def escrever_arquivo(self, nome_arquivo, conteudo, is_readonly=False):
        """Escreve ou sobrescreve arquivo (Pessoa 3)."""
        
        conteudo_bytes = conteudo.encode('utf-8')
        conteudo_tamanho = len(conteudo_bytes)

        # Checa atributo somente leitura
        if nome_arquivo in self._directory and self._directory[nome_arquivo][DIR_READONLY_INDICE] is True:
            print(f"Erro: Arquivo '{nome_arquivo}' está como SOMENTE LEITURA e não pode ser sobrescrito.")
            return False
        
        # Se existe → libera cadeia antiga
        if nome_arquivo in self._directory:
            print(f"Sobrescrevendo '{nome_arquivo}'. Liberando clusters antigos.")
            self._liberar_cadeia(self._directory[nome_arquivo][DIR_INICIAR_INDICE_CLUSTER])
        
        # Calcula clusters necessários
        num_clusters_necessario = (conteudo_tamanho + TAMANHO_CLUSTER - 1) // TAMANHO_CLUSTER
        
        iniciar_cluster = None
        atual_cluster = None

        # Alocação cluster por cluster
        for i in range(num_clusters_necessario):

            cluster_livre = self._encontrar_cluster_livre()

            if cluster_livre is None:
                print("Erro: Disco cheio. Não é possível concluir a escrita.")
                if iniciar_cluster:
                    self._liberar_cadeia(iniciar_cluster)
                return False

            # ligar encadeamento FAT
            if iniciar_cluster is None:
                iniciar_cluster = cluster_livre
            if atual_cluster is not None:
                self._fat[atual_cluster] = cluster_livre

            atual_cluster = cluster_livre

            # gravar o bloco no disco
            inicio = i * TAMANHO_CLUSTER
            fim = inicio + TAMANHO_CLUSTER
            chunk = conteudo_bytes[inicio:fim]

            self._driver.escrever_cluster(atual_cluster, chunk)

        # Finaliza cadeia FAT
        if atual_cluster is not None:
            self._fat[atual_cluster] = FAT_FIM_DE_ARQUIVO

            # Atualiza diretório
            self._directory[nome_arquivo] = [
                conteudo_tamanho,
                iniciar_cluster,
                is_readonly
            ]

            self._salvar_metadados()

            print(f"Arquivo '{nome_arquivo}' escrito com sucesso no cluster {iniciar_cluster}.")
            return True

        return False
