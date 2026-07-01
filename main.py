import tkinter as tk
import subprocess
import os
import sys

# =========================
# CONFIGURAÇÃO DA JANELA
# =========================
root = tk.Tk()
root.title("Survivor Game - Menu")
root.attributes("-fullscreen", True)
root.configure(bg="black")

W = root.winfo_screenwidth()
H = root.winfo_screenheight()

canvas = tk.Canvas(root, width=W, height=H, bg="black", highlightthickness=0)
canvas.pack()

# =========================
# FUNÇÕES DOS BOTÕES
# =========================

def iniciar_jogo():
    root.destroy()

    subprocess.Popen([
        sys.executable,
        os.path.join(os.path.dirname(__file__), "jogo.py")
    ])

def sair_jogo():
    root.destroy()

# =========================
# INTERFACE DO MENU
# =========================

canvas.create_text(
    W // 2,
    H // 3,
    text="💀 SURVIVOR ROGUELIKE 💀",
    fill="white",
    font=("Arial", 50, "bold")
)

canvas.create_text(
    W // 2,
    H // 3 + 60,
    text="Sobreviva o máximo de tempo que puder",
    fill="#888",
    font=("Arial", 16, "italic")
)

btn_jogar = tk.Button(
    root,
    text="JOGAR",
    command=iniciar_jogo,
    fg="black",
    bg="white",
    activebackground="#ddd",
    font=("Arial", 20, "bold"),
    width=15,
    bd=0,
    cursor="hand2"
)
btn_jogar.place(x=W // 2 - 130, y=H // 2 + 20)

btn_sair = tk.Button(
    root,
    text="SAIR",
    command=sair_jogo,
    fg="white",
    bg="#222",
    activebackground="#444",
    font=("Arial", 16, "bold"),
    width=15,
    bd=0,
    cursor="hand2"
)
btn_sair.place(x=W // 2 - 100, y=H // 2 + 110)

canvas.create_text(
    W // 2,
    H - 50,
    text="Dica: O jogo roda em Tela Cheia.",
    fill="#444",
    font=("Arial", 12)
)

root.mainloop()