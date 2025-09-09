import csv
import sqlite3
import tkinter as tk
from tkinter import scrolledtext, messagebox
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

# --- Funções da Interface Gráfica ---

def importar_dados():
    """Função para ser chamada pelo botão de importar."""
    nome_csv = 'jogadores.csv'
    nome_log = 'erros.log'
    
    jogadores_importados = importar_csv_para_db(nome_csv, nome_log)
    
    if jogadores_importados > 0:
        messagebox.showinfo("Sucesso", f"Importação concluída!\n{jogadores_importados} jogadores importados com sucesso.\nLinhas inválidas registradas em '{nome_log}'.")
        atualizar_menu_historico()
        
    else:
        pass # Mensagem de erro já é tratada dentro da função

def exibir_ranking_na_interface(data_importacao=None):
    """Função para ser chamada pelo botão de exibir ranking."""
    if not data_importacao:
        messagebox.showwarning("Aviso", "Selecione um histórico para exibir.")
        return

    ranking = buscar_ranking_do_db(data_importacao)
    
    area_ranking.configure(state='normal')
    area_ranking.delete(1.0, tk.END)

    if not ranking:
        area_ranking.insert(tk.END, "Nenhum jogador encontrado para este histórico.")
        area_ranking.configure(state='disabled')
        return
        
    area_ranking.insert(tk.END, f"--- Ranking de Jogadores (Histórico: {data_importacao}) ---\n\n")
    
    for i, jogador in enumerate(ranking):
        nome, nivel, pontuacao = jogador
        
        if i == 0:
            destaque = "🏆 1º LUGAR 🏆"
        elif i == 1:
            destaque = "🥈 2º LUGAR 🥈"
        elif i == 2:
            destaque = "🥉 3º LUGAR 🥉"
        else:
            destaque = f"{i + 1}º Lugar"
        
        linha = f"{destaque:<15} | Nome: {nome:<10} | Nível: {nivel:<5} | Pontuação: {pontuacao:,.2f}\n"
        area_ranking.insert(tk.END, linha)
        
    area_ranking.configure(state='disabled')

def atualizar_menu_historico():
    """Atualiza o menu de seleção com as datas de histórico disponíveis."""
    historicos = buscar_historicos_disponiveis()
    menu_historico['menu'].delete(0, 'end')
    
    if not historicos:
        var_historico.set("Nenhum histórico disponível")
        return
        
    for h in historicos:
        menu_historico['menu'].add_command(label=h, command=tk._setit(var_historico, h))
        
    # Seta o histórico mais recente como o padrão
    if historicos:
        var_historico.set(historicos[0])
    else:
        var_historico.set("Nenhum histórico disponível")


# --- Configuração da Janela Principal (GUI) ---

janela = tk.Tk()
janela.title("Sistema de Ranking de Jogadores")
janela.geometry("700x500")
janela.configure(bg="#f0f0f0")

# --- Layout da Interface ---

frame_botoes = tk.Frame(janela, bg="#f0f0f0", pady=10)
frame_botoes.pack(side="top", fill="x")

btn_importar = tk.Button(
    frame_botoes, 
    text="Importar Dados do CSV", 
    command=importar_dados, 
    bg="#4CAF50", 
    fg="white", 
    font=("Helvetica", 12, "bold")
)
btn_importar.pack(side="left", padx=10, pady=5)

# Menu de seleção de histórico
var_historico = tk.StringVar(janela)
var_historico.set("Nenhum histórico disponível") # Texto inicial

menu_historico = tk.OptionMenu(frame_botoes, var_historico, "")
menu_historico.pack(side="left", padx=10, pady=5)
menu_historico.config(font=('Helvetica', 12))
menu_historico['menu'].config(font=('Helvetica', 12))

btn_exibir = tk.Button(
    frame_botoes, 
    text="Exibir Ranking", 
    command=lambda: exibir_ranking_na_interface(var_historico.get()), 
    bg="#2196F3", 
    fg="white", 
    font=("Helvetica", 12, "bold")
)
btn_exibir.pack(side="left", padx=10, pady=5)

area_ranking = scrolledtext.ScrolledText(janela, wrap=tk.WORD, width=60, height=20, font=("Courier", 11))
area_ranking.pack(padx=10, pady=10, expand=True, fill="both")
area_ranking.configure(state='disabled')

# --- Inicia a aplicação ---
janela.mainloop()