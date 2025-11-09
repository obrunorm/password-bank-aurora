import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
import google.generativeai as genai
import threading
import os
import ctypes
from gui.password_manager_window import PasswordManagerWindow
from core.password_manager import salvar_senha
from core.database import inicializar_banco, verificar_banco
import secrets
import string
import sqlite3
from core.config import DB_PATH

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

root = tk.Tk()
root.title("Aurora")
largura = 200
altura = 250
largura_tela = root.winfo_screenwidth()
altura_tela = root.winfo_screenheight()

x = (largura_tela - largura) // 2 + 850
y = altura_tela - altura - 40

root.geometry(f"{largura}x{altura}+{x}+{y}")
root.overrideredirect(True)
root.wm_attributes("-transparentcolor", "white")
root.wm_attributes("-topmost", True)
root.configure(bg="white")
def start_move(event):
    root.x = event.x
    root.y = event.y

def do_move(event):
    x = root.winfo_pointerx() - root.x
    y = root.winfo_pointery() - root.y
    root.geometry(f"+{x}+{y}")

def stay_on_top_of_taskbar(hwnd=None):
    if hwnd is None:
        hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
    HWND_TOPMOST = -1
    SWP_NOMOVE = 0x0002
    SWP_NOSIZE = 0x0001
    SWP_SHOWWINDOW = 0x0040
    ctypes.windll.user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                                      SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW)

root.after(100, stay_on_top_of_taskbar)

root.bind("<Button-1>", start_move)
root.bind("<B1-Motion>", do_move)
img = Image.open("frieren.png").resize((200, 200))
photo = ImageTk.PhotoImage(img)

img2 = Image.open("frieren_work.png").resize((200, 200))
photo2 = ImageTk.PhotoImage(img2)

img3 = Image.open("frieren_duvida.png").resize((200, 200))
photo3 = ImageTk.PhotoImage(img3)

label = tk.Label(root, image=photo, bg="white", bd=0, highlightthickness=0)
label.pack()
fala = tk.Toplevel(root)
fala.overrideredirect(True)
fala.wm_attributes("-topmost", True)
fala.configure(bg="white")

fala1 = tk.Toplevel(root)
fala1.overrideredirect(True)
fala1.wm_attributes("-topmost", True)
fala1.configure(bg="white")

texto = tk.Label(fala, text="Oi, eu sou a Aurora!", font=("Arial", 10),
                 bg="white", padx=10, pady=5, relief="solid", bd=1)
texto.pack()

texto1 = tk.Label(fala1, text="Sua gerenciadora de senhas", font=("Arial", 10),
                  bg="white", padx=10, pady=5, relief="solid", bd=1)
texto1.pack()
menu_janela = tk.Toplevel(root)
menu_janela.overrideredirect(True)
menu_janela.wm_attributes("-topmost", True)
menu_janela.configure(bg="white")
menu_janela.withdraw()

tk.Label(menu_janela, text="Menu Aurora", font=("Arial", 11, "bold"),
         bg="white", pady=5).pack()

def create_password(root):
    alfabeto = string.ascii_letters + string.digits + string.punctuation
    senha = ''.join(secrets.choice(alfabeto) for _ in range(24))

    janela_senha = tk.Toplevel(root)
    janela_senha.title("Senha Gerada")
    janela_senha.overrideredirect(True)
    janela_senha.wm_attributes("-topmost", True)
    janela_senha.configure(bg="#f0f4f8")

    largura, altura = 420, 240
    x = (janela_senha.winfo_screenwidth() - largura) // 2
    y = (janela_senha.winfo_screenheight() - altura) // 2
    janela_senha.geometry(f"{largura}x{altura}+{x}+{y}")
    def start_move_window(event):
        janela_senha.x = event.x
        janela_senha.y = event.y

    def do_move_window(event):
        x = janela_senha.winfo_pointerx() - janela_senha.x
        y = janela_senha.winfo_pointery() - janela_senha.y
        janela_senha.geometry(f"+{x}+{y}")
    titulo_frame = tk.Frame(janela_senha, bg="#f0f4f8", cursor="hand2")
    titulo_frame.pack(pady=(15, 10), fill="x")
    titulo_frame.bind("<Button-1>", start_move_window)
    titulo_frame.bind("<B1-Motion>", do_move_window)
    
    titulo_label = tk.Label(
        titulo_frame,
        text="🔐 Senha Gerada",
        font=("Arial", 14, "bold"),
        bg="#f0f4f8",
        fg="#2c3e50",
        cursor="hand2"
    )
    titulo_label.pack()
    titulo_label.bind("<Button-1>", start_move_window)
    titulo_label.bind("<B1-Motion>", do_move_window)
    senha_frame = tk.Frame(janela_senha, bg="#ffffff", relief="solid", bd=2)
    senha_frame.pack(pady=10, padx=20, fill="x")
    label = tk.Label(
        senha_frame,
        text=senha,
        font=("Consolas", 13, "bold"),
        bg="#ffffff",
        fg="#1a1a1a",
        wraplength=360,
        padx=15,
        pady=12,
        justify="center"
    )
    label.pack()
    def copy_password():
        root.clipboard_clear()
        root.clipboard_append(senha)
        messagebox.showinfo(
            "✅ Copiado",
            "Senha copiada para a área de transferência!",
            parent=janela_senha
        )
    def has_passwords_in_database():
        try:
            if not verificar_banco():
                return False
            with sqlite3.connect(DB_PATH) as conn:
                c = conn.cursor()
                c.execute("SELECT COUNT(*) FROM senhas")
                count = c.fetchone()[0]
                return count > 0
        except:
            return False
    
    def save_to_database():
        janela_senha.lift()
        janela_senha.focus_force()
        
        inicializar_banco()
        if not has_passwords_in_database():
            messagebox.showwarning(
                "⚠️ Nenhuma Chave Mestra",
                "Não há nenhuma chave mestra cadastrada!\n\n"
                "Para salvar senhas, você precisa criar uma chave mestra primeiro.\n\n"
                "Acesse o 'Banco de senhas' no menu para criar sua chave mestra.",
                parent=janela_senha
            )
            return
        senha_mestra = simpledialog.askstring(
            "Senha-Mestra",
            "Digite sua senha-mestra:",
            show="*",
            parent=janela_senha
        )
        
        if not senha_mestra:
            return
        senha_mestra = senha_mestra.strip()
        nome_site = simpledialog.askstring(
            "Site/Serviço",
            "Para qual site/serviço é esta senha?\n(Ex: Gmail, Facebook, etc.)",
            parent=janela_senha
        )
        
        if not nome_site:
            messagebox.showwarning(
                "Aviso",
                "É necessário informar o site/serviço!",
                parent=janela_senha
            )
            return
        usuario = simpledialog.askstring(
            "Usuário",
            "Digite o nome de usuário/e-mail:\n(Deixe em branco se não quiser salvar)",
            show="",
            parent=janela_senha
        )
        if salvar_senha(nome_site.strip(), usuario.strip() if usuario else None, senha, senha_mestra):
            messagebox.showinfo(
                "✅ Sucesso",
                f"Senha salva com sucesso para '{nome_site}'!",
                parent=janela_senha
            )
        else:
            messagebox.showerror(
                "❌ Erro",
                "Erro ao salvar a senha. Verifique sua senha-mestra.",
                parent=janela_senha
            )
    
    def ask_to_save():
        janela_senha.lift()
        janela_senha.focus_force()
        
        resposta = messagebox.askyesno(
            "Salvar Senha",
            "Deseja salvar esta senha no banco de senhas?",
            parent=janela_senha
        )
        
        if resposta:
            save_to_database()
    
    janela_senha.after(300, ask_to_save)
    frame_botoes = tk.Frame(janela_senha, bg="#f0f4f8")
    frame_botoes.pack(pady=(5, 15))

    btn_copiar = tk.Button(
        frame_botoes,
        text="📋 Copiar",
        font=("Arial", 10, "bold"),
        bg="#3498db",
        fg="white",
        padx=15,
        pady=8,
        relief="flat",
        cursor="hand2",
        command=copy_password
    )
    btn_copiar.grid(row=0, column=0, padx=5)

    btn_salvar = tk.Button(
        frame_botoes,
        text="💾 Salvar no Banco",
        font=("Arial", 10, "bold"),
        bg="#27ae60",
        fg="white",
        padx=15,
        pady=8,
        relief="flat",
        cursor="hand2",
        command=save_to_database
    )
    btn_salvar.grid(row=0, column=1, padx=5)

    btn_fechar = tk.Button(
        frame_botoes,
        text="✕ Fechar",
        font=("Arial", 10, "bold"),
        bg="#e74c3c",
        fg="white",
        padx=15,
        pady=8,
        relief="flat",
        cursor="hand2",
        command=janela_senha.destroy
    )
    btn_fechar.grid(row=0, column=2, padx=5)

def open_password_manager():
    PasswordManagerWindow(root)

def open_conversation():
    label.config(image=photo3)
    menu_janela.withdraw()
    open_chat()

def exit_app():
    root.destroy()

opcoes = [
    ("Criar senha segura", lambda: create_password(root)),
    ("Conversar", open_conversation),
    ("Banco de senhas", open_password_manager),
    ("Encerrar", exit_app)
]

for nome, comando in opcoes:
    tk.Button(menu_janela, text=nome, width=20, command=comando).pack(pady=2)
def update_positions():
    x = root.winfo_x()
    y = root.winfo_y()
    fala.geometry(f"+{x - 110}+{y + 100}")
    fala1.geometry(f"+{x - 150}+{y + 130}")
    menu_janela.geometry(f"+{x - 220}+{y + 50}")
    root.after(100, update_positions)

def start_app():
    fala.withdraw()
    fala1.withdraw()
    janela_botao.withdraw()
    label.config(image=photo2)
    menu_janela.deiconify()

def open_chat():
    chat_win = tk.Toplevel(root)
    chat_win.title("Aurora - Conversa")
    chat_win.geometry("550x350+850+350")
    chat_win.configure(bg="#f9f9f9")
    chat_win.resizable(False, False)

    def return_to_start():
        chat_win.destroy()
        label.config(image=photo)
        fala.deiconify()
        fala1.deiconify()
        janela_botao.deiconify()
        menu_janela.withdraw()

    chat_win.protocol("WM_DELETE_WINDOW", return_to_start)

    resposta_frame = tk.Frame(chat_win, bg="#f9f9f9")
    resposta_frame.pack(fill="both", expand=True, padx=10, pady=(10, 5))

    resposta_label = tk.Label(
        resposta_frame,
        text="Olá! Alguma pergunta hoje?",
        bg="#d1f0ff",
        fg="#000000",
        wraplength=280,
        justify="left",
        anchor="w",
        padx=10,
        pady=8,
        font=("Arial", 10),
        relief="ridge",
        bd=2
    )
    resposta_label.pack(anchor="w", pady=(0, 10), fill="x")

    pergunta_frame = tk.Frame(chat_win, bg="#f9f9f9")
    pergunta_frame.pack(fill="x", pady=(0, 10), padx=10)

    entrada = tk.Entry(pergunta_frame, font=("Arial", 10))
    entrada.pack(side="left", fill="x", expand=True, padx=(0, 5))

    enviar_btn = tk.Button(
        pergunta_frame,
        text="Enviar",
        bg="#4CAF50",
        fg="white",
        font=("Arial", 9, "bold"),
        width=8
    )
    enviar_btn.pack(side="right")

    def send_message(event=None):
        user_msg = entrada.get().strip()
        if not user_msg:
            return
        entrada.delete(0, tk.END)

        resposta_label.config(text="⏳ Pensando...", bg="#eaeaea", fg="#333333")
        threading.Thread(target=lambda: respond_with_gemini(user_msg)).start()

    def respond_with_gemini(message):
        try:
            model = genai.GenerativeModel("gemini-2.0-flash")
            resposta = model.generate_content(
                f"Você é Aurora, uma assistente brava, mas gentil.Tente não responder com muitos caracteres\nUsuário: {message}"
            )
            texto = resposta.text.strip()
        except Exception as e:
            texto = f"[Erro ao conectar com o Gemini: {e}]"

        resposta_label.config(text=texto, bg="#d1f0ff", fg="#000000")

    enviar_btn.config(command=send_message)
    entrada.bind("<Return>", send_message)
    entrada.focus()
janela_botao = tk.Toplevel(root)
janela_botao.overrideredirect(True)
janela_botao.wm_attributes("-topmost", True)
janela_botao.configure(bg="#2c2c2c")

canvas_botao = tk.Canvas(janela_botao, bg="#2c2c2c", highlightthickness=0, borderwidth=0)
canvas_botao.pack(fill="both", expand=True)

def draw_rounded_button(color="#4CAF50"):
    canvas_botao.delete("all")
    largura = 80
    altura = 35
    raio = 10
    
    canvas_botao.config(width=largura, height=altura)
    
    canvas_botao.create_arc(0, 0, raio*2, raio*2, start=90, extent=90, fill=color, outline=color)
    canvas_botao.create_arc(largura-raio*2, 0, largura, raio*2, start=0, extent=90, fill=color, outline=color)
    canvas_botao.create_arc(0, altura-raio*2, raio*2, altura, start=180, extent=90, fill=color, outline=color)
    canvas_botao.create_arc(largura-raio*2, altura-raio*2, largura, altura, start=270, extent=90, fill=color, outline=color)
    
    canvas_botao.create_rectangle(raio, 0, largura-raio, altura, fill=color, outline=color)
    canvas_botao.create_rectangle(0, raio, largura, altura-raio, fill=color, outline=color)
    
    canvas_botao.create_text(largura//2, altura//2, text="Iniciar", 
                             fill="white", font=("Arial", 10, "bold"))

draw_rounded_button()

def on_button_click(event):
    start_app()

def on_button_enter(event):
    draw_rounded_button("#45a049")
    canvas_botao.config(cursor="hand2")

def on_button_leave(event):
    draw_rounded_button("#4CAF50")
    canvas_botao.config(cursor="")

canvas_botao.bind("<Button-1>", on_button_click)
canvas_botao.bind("<Enter>", on_button_enter)
canvas_botao.bind("<Leave>", on_button_leave)

def update_button_position():
    x = root.winfo_x()
    y = root.winfo_y()
    janela_botao.geometry(f"80x35+{x-20}+{y+10}")
    root.after(100, update_button_position)

update_button_position()

update_positions()
fala.deiconify()
fala1.deiconify()

root.mainloop()


