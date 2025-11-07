import tkinter as tk
from PIL import Image, ImageTk
import google.generativeai as genai
import threading
import os
import ctypes

# === Configura o cliente do Gemini ===
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# === Janela principal (transparente) ===
root = tk.Tk()
root.title("Aurora")
# Centraliza horizontalmente e encosta na barra de tarefas
largura = 200
altura = 250
largura_tela = root.winfo_screenwidth()
altura_tela = root.winfo_screenheight()

# Calcula posição
x = (largura_tela - largura) // 2 + 850
y = altura_tela - altura - 40  # "40" = altura média da barra de tarefas

root.geometry(f"{largura}x{altura}+{x}+{y}")
root.overrideredirect(True)  # Remove bordas e título
root.wm_attributes("-transparentcolor", "white")  # Cor branca vira transparente
root.wm_attributes("-topmost", True)
root.configure(bg="white")  # Fundo branco será invisível

# === Movimento com o mouse ===
def start_move(event):
    root.x = event.x
    root.y = event.y

def do_move(event):
    x = root.winfo_pointerx() - root.x
    y = root.winfo_pointery() - root.y
    root.geometry(f"+{x}+{y}")

# === Faz a janela ficar ACIMA da barra de tarefas ===
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

# === Imagens ===
img = Image.open("frieren.png").resize((200, 200))
photo = ImageTk.PhotoImage(img)

img2 = Image.open("frieren_work.png").resize((200, 200))
photo2 = ImageTk.PhotoImage(img2)

img3 = Image.open("frieren_duvida.png").resize((200, 200))
photo3 = ImageTk.PhotoImage(img3)

label = tk.Label(root, image=photo, bg="white", bd=0, highlightthickness=0)
label.pack()

# === Balões de fala iniciais ===
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

# === Menu ===
menu_janela = tk.Toplevel(root)
menu_janela.overrideredirect(True)
menu_janela.wm_attributes("-topmost", True)
menu_janela.configure(bg="white")
menu_janela.withdraw()

tk.Label(menu_janela, text="Menu Aurora", font=("Arial", 11, "bold"),
         bg="white", pady=5).pack()

def criar_senha():
    print("Criar senha segura (futuro recurso)")

def banco_senhas():
    print("Abrir banco de senhas (futuro recurso)")

def abrir_conversa():
    label.config(image=photo3)
    menu_janela.withdraw()
    abrir_chat()

def encerrar():
    root.destroy()  # Encerra completamente o programa    

opcoes = [
    ("Criar senha segura", criar_senha),
    ("Conversar", abrir_conversa),
    ("Banco de senhas", banco_senhas),
    ("Encerrar", encerrar)  
]

for nome, comando in opcoes:
    tk.Button(menu_janela, text=nome, width=20, command=comando).pack(pady=2)

# === Funções ===
def posicionar():
    x = root.winfo_x()
    y = root.winfo_y()
    fala.geometry(f"+{x - 110}+{y + 100}")
    fala1.geometry(f"+{x - 150}+{y + 130}")
    menu_janela.geometry(f"+{x - 220}+{y + 50}")
    root.after(100, posicionar)

def iniciar():
    fala.withdraw()
    fala1.withdraw()
    botao_iniciar.place_forget()
    label.config(image=photo2)
    menu_janela.deiconify()

# === Janela de chat (usando Gemini) ===
def abrir_chat():
    chat_win = tk.Toplevel(root)
    chat_win.title("Aurora - Conversa")
    chat_win.geometry("550x350+850+350")
    chat_win.configure(bg="#f9f9f9")
    chat_win.resizable(False, False)

    # 🆕 Quando o usuário fecha a janela, chama a função 'voltar_inicio'
    def voltar_inicio():
        chat_win.destroy()
        label.config(image=photo)         # Volta para imagem inicial
        fala.deiconify()                  # Mostra as falas iniciais
        fala1.deiconify()
        botao_iniciar.place(x=0.5, y=10)
        menu_janela.withdraw()            # Esconde o menu

    chat_win.protocol("WM_DELETE_WINDOW", voltar_inicio)  # 🆕 intercepta o fechamento

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

    def enviar(event=None):
        user_msg = entrada.get().strip()
        if not user_msg:
            return
        entrada.delete(0, tk.END)

        resposta_label.config(text="⏳ Pensando...", bg="#eaeaea", fg="#333333")
        threading.Thread(target=lambda: responder_gemini(user_msg)).start()

    def responder_gemini(mensagem):
        try:
            model = genai.GenerativeModel("gemini-2.0-flash")
            resposta = model.generate_content(
                f"Você é Aurora, uma assistente brava, mas gentil.Tente não responder com muitos caracteres\nUsuário: {mensagem}"
            )
            texto = resposta.text.strip()
        except Exception as e:
            texto = f"[Erro ao conectar com o Gemini: {e}]"

        resposta_label.config(text=texto, bg="#d1f0ff", fg="#000000")

    enviar_btn.config(command=enviar)
    entrada.bind("<Return>", enviar)
    entrada.focus()

# === Botão Iniciar (flutuante sobre a imagem) ===
botao_iniciar = tk.Button(root, text="Iniciar", command=iniciar,
                          bg="#4CAF50", fg="white",
                          font=("Arial", 10, "bold"))
botao_iniciar.place(x=0.5, y=10)

# === Inicia com falas ===
posicionar()
fala.deiconify()
fala1.deiconify()

root.mainloop()
