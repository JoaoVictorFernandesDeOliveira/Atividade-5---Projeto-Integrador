import csv
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from datetime import datetime

# --- Classe para representar um jogador ---
class Jogador:
    def __init__(self, nome, nivel, pontuacao, data_importacao):
        self.nome = nome
        self.nivel = nivel
        self.pontuacao = pontuacao
        self.data_importacao = data_importacao

    def __repr__(self):
        return f"Jogador(Nome: {self.nome}, Nível: {self.nivel}, Pontuação: {self.pontuacao}, Data: {self.data_importacao})"

# --- Funções do sistema ---

def criar_tabela(cursor):
    """Cria a tabela de ranking no banco de dados com um campo para a data de importação."""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ranking (
            nome TEXT,
            nivel INTEGER,
            pontuacao REAL,
            data_importacao TEXT
        )
    ''')
    print("Tabela 'ranking' criada ou já existente.")

def importar_csv_para_db(nome_arquivo_csv, nome_arquivo_log):
    """Lê o CSV, valida os dados e importa para o banco de dados SQLite."""
    jogadores_validos = []
    data_hora_importacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with open(nome_arquivo_log, 'w', encoding='utf-8') as log_file:
            with open(nome_arquivo_csv, 'r', encoding='utf-8') as csv_file:
                leitor_csv = csv.reader(csv_file)
                next(leitor_csv)  # Pula o cabeçalho

                for i, linha in enumerate(leitor_csv):
                    try:
                        if len(linha) != 3:
                            raise ValueError("Número de colunas inválido.")
                        
                        nome, nivel_str, pontuacao_str = linha
                        
                        nivel = int(nivel_str.strip())
                        pontuacao = float(pontuacao_str.strip())
                        
                        if not nome.strip():
                            raise ValueError("Nome do jogador não pode ser vazio.")
                            
                        jogador = Jogador(nome.strip(), nivel, pontuacao, data_hora_importacao)
                        jogadores_validos.append(jogador)
                    
                    except (ValueError, IndexError) as e:
                        log_file.write(f"Linha {i+2}: '{','.join(linha)}' -> Erro: {e}\n")
    
    except FileNotFoundError:
        messagebox.showerror("Erro", f"O arquivo '{nome_arquivo_csv}' não foi encontrado.")
        return 0
    
    conn = sqlite3.connect('ranking.db')
    cursor = conn.cursor()
    
    criar_tabela(cursor)
    
    # Prepara os dados para inserção com a data da importação
    dados_para_inserir = [(j.nome, j.nivel, j.pontuacao, j.data_importacao) for j in jogadores_validos]
    cursor.executemany("INSERT INTO ranking (nome, nivel, pontuacao, data_importacao) VALUES (?, ?, ?, ?)", dados_para_inserir)
    
    conn.commit()
    conn.close()
    
    return len(jogadores_validos)

def buscar_historicos_disponiveis():
    """Busca as datas de importação únicas no banco de dados."""
    conn = sqlite3.connect('ranking.db')
    cursor = conn.cursor()
    
    # Primeiro, garanta que a tabela existe
    criar_tabela(cursor)

    cursor.execute("SELECT DISTINCT data_importacao FROM ranking ORDER BY data_importacao DESC")
    historicos = [item[0] for item in cursor.fetchall()]
    conn.close()
    return historicos

def buscar_ranking_do_db(data_importacao):
    """Busca o ranking para uma data de importação específica."""
    conn = sqlite3.connect('ranking.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT nome, nivel, pontuacao FROM ranking WHERE data_importacao = ? ORDER BY pontuacao DESC", (data_importacao,))
    ranking = cursor.fetchall()
    
    conn.close()
    return ranking

def excluir_historico_do_db(data_importacao):
    """Exclui um histórico de importação específico do banco de dados."""
    if not data_importacao or data_importacao == "Nenhum histórico disponível":
        messagebox.showwarning("Aviso", "Selecione um histórico válido para excluir.")
        return

    confirmar = messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir o histórico de importação de {data_importacao}?\nEsta ação não pode ser desfeita.")
    if confirmar:
        conn = sqlite3.connect('ranking.db')
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM ranking WHERE data_importacao = ?", (data_importacao,))
        conn.commit()
        conn.close()
        
        messagebox.showinfo("Sucesso", "Histórico excluído com sucesso!")
        atualizar_menu_historico() # Atualiza a lista de históricos após a exclusão
        # Limpa a exibição se o histórico excluído era o que estava sendo mostrado
        if var_historico.get() == data_importacao:
            exibir_ranking_na_interface() # Chama sem parâmetros para limpar a tabela
    

# --- Funções da Interface Gráfica ---

def selecionar_arquivo_csv():
    """Abre uma janela para o usuário selecionar o arquivo CSV."""
    nome_arquivo_csv = filedialog.askopenfilename(
        title="Selecione o arquivo CSV",
        filetypes=(("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*"))
    )
    if nome_arquivo_csv:
        nome_log = 'erros.log' # O arquivo de log pode continuar fixo ou ser dinâmico também
        jogadores_importados = importar_csv_para_db(nome_arquivo_csv, nome_log)
        
        if jogadores_importados > 0:
            messagebox.showinfo("Sucesso", f"Importação concluída!\n{jogadores_importados} jogadores importados com sucesso.\nLinhas inválidas registradas em '{nome_log}'.")
            atualizar_menu_historico()
        else:
            # A mensagem de erro já é tratada dentro de importar_csv_para_db
            pass
    else:
        messagebox.showwarning("Aviso", "Nenhum arquivo foi selecionado.")


def exibir_ranking_na_interface(data_importacao=None):
    """Função para ser chamada pelo botão de exibir ranking."""
    # Limpa a tabela antes de inserir novos dados
    for i in tree_ranking.get_children():
        tree_ranking.delete(i)

    if not data_importacao or data_importacao == "Nenhum histórico disponível":
        messagebox.showwarning("Aviso", "Selecione um histórico para exibir.")
        return

    ranking = buscar_ranking_do_db(data_importacao)
    
    if not ranking:
        messagebox.showinfo("Informação", "Nenhum jogador encontrado para este histórico.")
        return
        
    for i, jogador in enumerate(ranking):
        nome, nivel, pontuacao = jogador
        
        # Inserir dados na Treeview
        tree_ranking.insert("", "end", values=(i + 1, nome, nivel, f"{pontuacao:,.2f}"))


def atualizar_menu_historico():
    """Atualiza o menu de seleção com as datas de histórico disponíveis."""
    historicos = buscar_historicos_disponiveis()
    
    # Limpa as opções existentes e adiciona as novas
    menu_historico['values'] = historicos
    
    if historicos:
        var_historico.set(historicos[0]) # Seta o histórico mais recente como o padrão
    else:
        var_historico.set("Nenhum histórico disponível")
        # Limpa a tabela se não houver histórico para exibir
        for i in tree_ranking.get_children():
            tree_ranking.delete(i)


# --- Configuração da Janela Principal (GUI) ---

janela = tk.Tk()
janela.title("Sistema de Ranking de Jogadores")
janela.geometry("800x600") # Ajuste a geometria conforme necessário
janela.configure(bg="#e0e0e0") # Cor de fundo mais suave

# Estilo para os widgets ttk
style = ttk.Style()
style.theme_use("clam") # Um tema mais moderno

# Configurações gerais de estilo
style.configure("TFrame", background="#e0e0e0")
style.configure("TLabel", background="#e0e0e0", font=("Helvetica", 12))

# Estilo para os botões
style.configure("TButton", 
                font=("Helvetica", 11, "bold"), 
                foreground="white", 
                background="#4a7a8c", # Azul escuro para botões
                padding=8,
                borderwidth=0) # Remove borda padrão do TButton
style.map("TButton", 
        background=[("active", "#5c92a9")]) # Cor mais clara ao passar o mouse

# Estilo para a combobox (menu de histórico)
style.map("TCombobox", 
          fieldbackground=["readonly", "#ffffff"], 
          selectbackground=["readonly", "#ffffff"],
          selectforeground=["readonly", "#000000"])
style.configure("TCombobox", 
                font=("Helvetica", 11),
                padding=5,
                arrowcolor="#4a7a8c")

# Estilo para o cabeçalho da Treeview
style.configure("Treeview.Heading", 
                font=("Helvetica", 11, "bold"), 
                background="#4a7a8c", # Cor do cabeçalho da tabela
                foreground="white",
                padding=5)

# Estilo para a Treeview (tabela)
style.configure("Treeview", 
                background="#ffffff", # Fundo das linhas
                foreground="#000000", # Cor do texto das linhas
                fieldbackground="#ffffff", # Fundo dos campos
                rowheight=25,
                borderwidth=0) # Remove borda padrão da Treeview
style.map("Treeview", 
        background=[("selected", "#cce0e5")]) # Cor de seleção da linha


# --- Layout da Interface ---

frame_botoes = ttk.Frame(janela, padding=(10, 10))
frame_botoes.pack(side="top", fill="x")

btn_importar = ttk.Button(
    frame_botoes, 
    text="Importar Dados do CSV", 
    command=selecionar_arquivo_csv, # Chama a função para abrir a janela de seleção
    style="TButton"
)
btn_importar.pack(side="left", padx=10, pady=5)

# Combobox para seleção de histórico
var_historico = tk.StringVar()
menu_historico = ttk.Combobox(
    frame_botoes, 
    textvariable=var_historico, 
    state="readonly", # Impede digitação manual
    width=25 # Ajuste a largura conforme necessário
)
menu_historico.pack(side="left", padx=10, pady=5)
menu_historico.bind("<<ComboboxSelected>>", lambda event: exibir_ranking_na_interface(var_historico.get()))


btn_exibir = ttk.Button(
    frame_botoes, 
    text="Exibir Ranking", 
    command=lambda: exibir_ranking_na_interface(var_historico.get()), 
    style="TButton"
)
btn_exibir.pack(side="left", padx=10, pady=5)

btn_excluir = ttk.Button(
    frame_botoes,
    text="Excluir Histórico Selecionado",
    command=lambda: excluir_historico_do_db(var_historico.get()),
    style="TButton",
    cursor="hand2" # Muda o cursor para indicar que é clicável
)
btn_excluir.pack(side="left", padx=10, pady=5)

# Frame para conter a Treeview e suas barras de rolagem
frame_tabela = ttk.Frame(janela, padding=(10, 10))
frame_tabela.pack(expand=True, fill="both", padx=10, pady=10)

# Barras de rolagem para a Treeview
scrollbar_y = ttk.Scrollbar(frame_tabela, orient="vertical")
scrollbar_x = ttk.Scrollbar(frame_tabela, orient="horizontal")

# Treeview (tabela)
tree_ranking = ttk.Treeview(
    frame_tabela,
    columns=("Posicao", "Nome", "Nivel", "Pontuacao"),
    show="headings", # Oculta a coluna padrão vazia
    yscrollcommand=scrollbar_y.set,
    xscrollcommand=scrollbar_x.set,
    style="Treeview"
)

# Configuração das barras de rolagem
scrollbar_y.config(command=tree_ranking.yview)
scrollbar_x.config(command=tree_ranking.xview)

# Configuração das colunas
tree_ranking.heading("Posicao", text="Posição")
tree_ranking.heading("Nome", text="Nome do Jogador")
tree_ranking.heading("Nivel", text="Nível")
tree_ranking.heading("Pontuacao", text="Pontuação")

# Largura das colunas
tree_ranking.column("Posicao", width=80, anchor="center") # Centraliza o texto
tree_ranking.column("Nome", width=200, anchor="w")       # Alinha à esquerda
tree_ranking.column("Nivel", width=100, anchor="center") # Centraliza o texto
tree_ranking.column("Pontuacao", width=150, anchor="e")  # Alinha à direita

# Posicionamento dos elementos dentro do frame_tabela
scrollbar_y.pack(side="right", fill="y")
scrollbar_x.pack(side="bottom", fill="x")
tree_ranking.pack(expand=True, fill="both")

# --- Inicia a aplicação ---
atualizar_menu_historico() # Carrega os históricos disponíveis ao iniciar
janela.mainloop()