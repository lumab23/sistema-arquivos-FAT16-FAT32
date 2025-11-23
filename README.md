# Sistema de Arquivos (Simulador FAT)

Este projeto implementa um simulador de sistema de arquivos simples em Python, utilizando um arquivo binário como disco virtual. Ele demonstra conceitos fundamentais de sistemas operacionais, como Tabela de Alocação de Arquivos (FAT), clusters e diretórios.

## Funcionalidades

O sistema oferece uma interface de linha de comando (CLI) para realizar as seguintes operações:

1.  **Listar ficheiros (dir/ls)**: Exibe os arquivos armazenados, seus tamanhos, cluster inicial e atributos.
2.  **Escrever ficheiro (write)**: Cria um novo arquivo ou sobrescreve um existente com o conteúdo fornecido.
3.  **Ler ficheiro (read)**: Exibe o conteúdo de um arquivo armazenado.
4.  **Apagar ficheiro (del)**: Remove um arquivo do sistema e libera os clusters ocupados.
5.  **Renomear ficheiro (rename)**: Altera o nome de um arquivo existente.
6.  **Alterar permissões R/O (attrib)**: Define um arquivo como "Somente Leitura" ou "Editável".

## Estrutura do Projeto

*   **`main.py`**: Ponto de entrada da aplicação. Gerencia a interação com o usuário (menu e inputs).
*   **`sistema_arquivos.py`**: Contém a lógica do sistema de arquivos (`SistemaArquivos`). Gerencia a FAT, o diretório raiz e as operações de alto nível (ler, escrever, apagar).
*   **`driver_disco.py`**: Simula o driver de disco físico (`DriverDisco`). Responsável por ler e escrever blocos (clusters) brutos no arquivo `mini_fat_disco.bin`.
*   **`mini_fat_disco.bin`**: Arquivo binário que atua como o disco virtual persistente. (Criado automaticamente na primeira execução).

## Como Executar

Certifique-se de ter o Python 3 instalado.

1.  Abra o terminal na pasta do projeto.
2.  Execute o comando:

```bash
python3 main.py
```

3.  Siga as instruções no menu interativo.

## Detalhes Técnicos

*   **Tamanho do Cluster**: 1024 bytes (1 KB).
*   **Total de Clusters**: 100.
*   **Capacidade Total**: ~100 KB.
*   **Persistência**: Os metadados (FAT e Diretório) são armazenados nos primeiros clusters do disco (Cluster 0 e 1), garantindo que os dados persistam entre execuções.
