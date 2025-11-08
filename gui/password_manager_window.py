"""
Interface gráfica para o gerenciador de senhas
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from core.password_manager import salvar_senha, ler_senhas, deletar_senha
from core.database import inicializar_banco


class PasswordManagerWindow:
    def __init__(self, parent):
        self.parent = parent
        self.senha_mestra = None
        self.window = None
        self.senhas_tree = None
        self.id_map = {}  # Mapeia item_id do Treeview para id_senha do banco
        
        # Inicializa o banco se necessário
        inicializar_banco()
        
        # Abre a janela de autenticação
        self.autenticar()
    
    def autenticar(self):
        """
        Solicita a senha-mestra ao usuário.
        Na primeira vez, cria a senha-mestra com confirmação.
        """
        from core.database import verificar_banco
        from core.config import DB_PATH
        import os
        
        # Verifica se é a primeira vez (banco não existe ou está vazio)
        primeira_vez = not verificar_banco() or not self._tem_senhas()
        
        if primeira_vez:
            # Primeira vez: criar senha-mestra com confirmação
            self._criar_senha_mestra()
        else:
            # Já existe senha-mestra: apenas autenticar
            self._entrar_com_senha_mestra()
    
    def _tem_senhas(self):
        """Verifica se já existem senhas no banco"""
        import sqlite3
        from core.config import DB_PATH
        
        try:
            with sqlite3.connect(DB_PATH) as conn:
                c = conn.cursor()
                c.execute("SELECT COUNT(*) FROM senhas")
                count = c.fetchone()[0]
                return count > 0
        except:
            return False
    
    def _criar_senha_mestra(self):
        """
        Cria a senha-mestra pela primeira vez com confirmação.
        """
        while True:
            senha1 = simpledialog.askstring(
                "Criar Senha-Mestra",
                "Digite sua nova senha-mestra:\n(Crie uma senha mestra forte e longa (ex: “frase de senha” com 5+ palavras))",
                show="*"
            )
            
            if not senha1:
                return  # Usuário cancelou
            
            if len(senha1) < 4:
                messagebox.showwarning(
                    "Senha muito curta",
                    "A senha-mestra deve ter pelo menos 4 caracteres!"
                )
                continue
            
            senha2 = simpledialog.askstring(
                "Confirmar Senha-Mestra",
                "Digite novamente para confirmar:",
                show="*"
            )
            
            if not senha2:
                return  # Usuário cancelou
            
            if senha1 != senha2:
                messagebox.showerror(
                    "Senhas não coincidem",
                    "As senhas digitadas não são iguais. Tente novamente."
                )
                continue
            
            # Senhas coincidem - define a senha-mestra
            self.senha_mestra = senha1
            messagebox.showinfo(
                "Senha-Mestra Criada",
                "Sua senha-mestra foi criada com sucesso!\n\n"
                "IMPORTANTE: Lembre-se desta senha. Sem ela, você não conseguirá acessar suas senhas salvas."
            )
            self.abrir_janela_principal()
            break
    
    def _entrar_com_senha_mestra(self):
        """
        Autentica com a senha-mestra existente.
        """
        self.senha_mestra = simpledialog.askstring(
            "Autenticação",
            "Digite sua senha-mestra:",
            show="*"
        )
        
        if not self.senha_mestra:
            return  # Usuário cancelou
        
        # Verifica se a senha-mestra está correta tentando ler as senhas
        senhas = ler_senhas(self.senha_mestra)
        
        # Se houver senhas e alguma retornar erro, a senha está incorreta
        if senhas:
            senhas_incorretas = any("⚠️" in str(senha[3]) for senha in senhas)
            if senhas_incorretas:
                messagebox.showerror(
                    "Erro",
                    "Senha-mestra incorreta! Não foi possível descriptografar as senhas."
                )
                return
        
        # Se chegou aqui, a senha está correta
        self.abrir_janela_principal()
    
    def abrir_janela_principal(self):
        """
        Abre a janela principal do gerenciador de senhas.
        """
        self.window = tk.Toplevel(self.parent)
        self.window.title("Aurora - Banco de Senhas")
        self.window.geometry("700x500+800+300")
        self.window.configure(bg="#f9f9f9")
        self.window.resizable(True, True)
        
        # Frame principal
        main_frame = tk.Frame(self.window, bg="#f9f9f9")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título
        titulo = tk.Label(
            main_frame,
            text="🔐 Banco de Senhas",
            font=("Arial", 16, "bold"),
            bg="#f9f9f9",
            fg="#333333"
        )
        titulo.pack(pady=(0, 15))
        
        # Frame para botões
        botoes_frame = tk.Frame(main_frame, bg="#f9f9f9")
        botoes_frame.pack(fill="x", pady=(0, 10))
        
        # Botão adicionar senha
        btn_adicionar = tk.Button(
            botoes_frame,
            text="➕ Adicionar Senha",
            command=self.adicionar_senha,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5
        )
        btn_adicionar.pack(side="left", padx=(0, 5))
        
        # Botão atualizar
        btn_atualizar = tk.Button(
            botoes_frame,
            text="🔄 Atualizar",
            command=self.atualizar_lista,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5
        )
        btn_atualizar.pack(side="left", padx=(0, 5))
        
        # Botão deletar
        btn_deletar = tk.Button(
            botoes_frame,
            text="🗑️ Deletar",
            command=self.deletar_senha_selecionada,
            bg="#f44336",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5
        )
        btn_deletar.pack(side="left")
        
        # Frame para a árvore (tabela)
        tree_frame = tk.Frame(main_frame, bg="#f9f9f9")
        tree_frame.pack(fill="both", expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Treeview (tabela)
        self.senhas_tree = ttk.Treeview(
            tree_frame,
            columns=("Nome", "Usuário", "Senha"),
            show="headings",
            yscrollcommand=scrollbar.set,
            selectmode="browse"
        )
        
        scrollbar.config(command=self.senhas_tree.yview)
        
        # Configurar colunas
        self.senhas_tree.heading("Nome", text="Nome/Site")
        self.senhas_tree.heading("Usuário", text="Usuário")
        self.senhas_tree.heading("Senha", text="Senha")
        
        self.senhas_tree.column("Nome", width=200)
        self.senhas_tree.column("Usuário", width=200)
        self.senhas_tree.column("Senha", width=250)
        
        self.senhas_tree.pack(fill="both", expand=True)
        
        # Bind duplo clique para copiar senha
        self.senhas_tree.bind("<Double-1>", self.copiar_senha)
        
        # Carregar senhas
        self.atualizar_lista()
        
        # Protocolo de fechamento
        self.window.protocol("WM_DELETE_WINDOW", self.fechar_janela)
    
    def atualizar_lista(self):
        """
        Atualiza a lista de senhas na interface.
        """
        # Limpa a árvore e o mapeamento
        for item in self.senhas_tree.get_children():
            self.senhas_tree.delete(item)
        self.id_map.clear()
        
        # Carrega senhas do banco
        senhas = ler_senhas(self.senha_mestra)
        
        # Adiciona à árvore e mapeia os IDs
        for id_senha, nome, usuario, senha in senhas:
            usuario_display = usuario if usuario else "(sem usuário)"
            # Mostra apenas os primeiros caracteres da senha por segurança
            senha_display = senha[:3] + "***" if len(senha) > 3 and "⚠️" not in senha else senha
            item_id = self.senhas_tree.insert("", "end", values=(nome, usuario_display, senha_display))
            # Armazena o mapeamento item_id -> id_senha
            self.id_map[item_id] = id_senha
    
    def adicionar_senha(self):
        """
        Abre uma janela para adicionar uma nova senha.
        """
        dialog = tk.Toplevel(self.window)
        dialog.title("Adicionar Senha")
        dialog.geometry("400x200+900+400")
        dialog.configure(bg="#f9f9f9")
        dialog.resizable(False, False)
        dialog.transient(self.window)
        dialog.grab_set()
        
        # Campos
        tk.Label(dialog, text="Nome/Site:", bg="#f9f9f9", font=("Arial", 10)).grid(
            row=0, column=0, padx=10, pady=10, sticky="w"
        )
        entry_nome = tk.Entry(dialog, width=30, font=("Arial", 10))
        entry_nome.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="Usuário:", bg="#f9f9f9", font=("Arial", 10)).grid(
            row=1, column=0, padx=10, pady=10, sticky="w"
        )
        entry_usuario = tk.Entry(dialog, width=30, font=("Arial", 10))
        entry_usuario.grid(row=1, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="Senha:", bg="#f9f9f9", font=("Arial", 10)).grid(
            row=2, column=0, padx=10, pady=10, sticky="w"
        )
        entry_senha = tk.Entry(dialog, width=30, font=("Arial", 10), show="*")
        entry_senha.grid(row=2, column=1, padx=10, pady=10)
        
        def salvar():
            nome = entry_nome.get().strip()
            usuario = entry_usuario.get().strip() or None
            senha = entry_senha.get().strip()
            
            if not nome or not senha:
                messagebox.showwarning("Aviso", "Nome e senha são obrigatórios!")
                return
            
            if salvar_senha(nome, usuario, senha, self.senha_mestra):
                messagebox.showinfo("Sucesso", "Senha salva com sucesso!")
                dialog.destroy()
                self.atualizar_lista()
            else:
                messagebox.showerror("Erro", "Erro ao salvar a senha!")
        
        # Botões
        btn_frame = tk.Frame(dialog, bg="#f9f9f9")
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        tk.Button(
            btn_frame,
            text="Salvar",
            command=salvar,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5
        ).pack(side="left", padx=5)
        
        tk.Button(
            btn_frame,
            text="Cancelar",
            command=dialog.destroy,
            bg="#757575",
            fg="white",
            font=("Arial", 10),
            padx=20,
            pady=5
        ).pack(side="left", padx=5)
        
        entry_nome.focus()
    
    def deletar_senha_selecionada(self):
        """
        Deleta a senha selecionada na lista.
        """
        selecionado = self.senhas_tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione uma senha para deletar!")
            return
        
        item_id = selecionado[0]
        item = self.senhas_tree.item(item_id)
        nome = item['values'][0]
        
        # Obtém o ID do banco através do mapeamento
        senha_id = self.id_map.get(item_id)
        
        if not senha_id:
            messagebox.showerror("Erro", "Não foi possível identificar a senha!")
            return
        
        if messagebox.askyesno("Confirmar", f"Deseja realmente deletar a senha de '{nome}'?"):
            if deletar_senha(senha_id):
                messagebox.showinfo("Sucesso", "Senha deletada com sucesso!")
                self.atualizar_lista()
            else:
                messagebox.showerror("Erro", "Erro ao deletar a senha!")
    
    def copiar_senha(self, event):
        """
        Copia a senha selecionada para a área de transferência.
        """
        selecionado = self.senhas_tree.selection()
        if not selecionado:
            return
        
        item = self.senhas_tree.item(selecionado[0])
        nome = item['values'][0]
        
        # Buscar a senha completa
        senhas = ler_senhas(self.senha_mestra)
        for _, nome_item, _, senha_item in senhas:
            if nome_item == nome:
                self.window.clipboard_clear()
                self.window.clipboard_append(senha_item)
                messagebox.showinfo("Copiado", f"Senha de '{nome}' copiada para a área de transferência!")
                break
    
    def fechar_janela(self):
        """
        Fecha a janela e limpa a senha-mestra da memória.
        """
        if self.senha_mestra:
            del self.senha_mestra
        self.window.destroy()

