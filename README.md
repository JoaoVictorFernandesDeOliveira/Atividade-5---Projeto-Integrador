# Atividade-5---Projeto-Integrador
# Sistema de Ranking de Jogadores de Games

Este é um programa em Python que gerencia um ranking de jogadores. Ele lê dados de um arquivo CSV, salva o histórico em um banco de dados SQLite e exibe o ranking em uma interface gráfica (GUI).

## Pré-requisitos

O programa requer **Python 3.x** e as bibliotecas padrão. Nenhuma instalação extra é necessária.

## Como Executar

Siga estes passos para rodar o programa no seu computador:

1.  **Clone o Repositório:**
    Abra o terminal e execute o comando abaixo para baixar o projeto.
    ```bash
    git clone [https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git](https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git)
    ```

2.  **Acesse a Pasta do Projeto:**
    Vá para a pasta do projeto no terminal.
    ```bash
    cd SEU_REPOSITORIO
    ```

3.  **Verifique os Arquivos:**
    Certifique-se de que o arquivo de dados `jogadores.csv` está na mesma pasta que o `main.py`.

4.  **Execute o Programa:**
    Execute o script principal usando o comando:
    ```bash
    python main.py
    ```

## Uso do Programa

Uma janela com a interface gráfica será aberta. Siga as instruções abaixo:

1.  Clique no botão **"Importar Dados do CSV"** para carregar os jogadores para o banco de dados. Os dados do arquivo `jogadores.csv` serão importados.
2.  Após a importação, um novo histórico será criado. Selecione a data e hora no menu suspenso.
3.  Clique no botão **"Exibir Ranking"** para visualizar a lista de jogadores, com os 3 primeiros colocados em destaque.

O programa cria automaticamente os arquivos `erros.log` (com as linhas inválidas do CSV) e `ranking.db` (o banco de dados) na mesma pasta.
