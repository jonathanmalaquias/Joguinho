import tkinter as tk
import json
from PIL import Image, ImageTk

# tamanho dos retratos (mude aqui e tudo se ajusta)
IMG_SIZE = 300  

def carregar_cutscene(nome):
    with open("cutscenes.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return data[nome]

def iniciar_dialogo(root, falas, on_finish=None):
    W, H = root.winfo_screenwidth(), root.winfo_screenheight()

    # Caixa de texto
    caixa_altura = 150
    caixa = tk.Frame(root, bg="black", highlightbackground="white", highlightthickness=2)
    caixa.place(x=100, y=H-caixa_altura, width=W-200, height=caixa_altura)

    texto = tk.Label(caixa, text="", fg="white", bg="black",
                     font=("Arial", 18), anchor="nw", justify="left")
    texto.pack(padx=20, pady=20, fill="both")

    # Labels para retratos
    esquerda = tk.Label(root, bg="black")
    direita = tk.Label(root, bg="black")

    # posiciona acima da caixa de texto
    esquerda.place(x=100, y=H-caixa_altura-IMG_SIZE-20)
    direita.place(x=W-IMG_SIZE-100, y=H-caixa_altura-IMG_SIZE-20)

    imagens_cache = {}

    def mostrar_fala(i=0):
        if i >= len(falas):
            caixa.destroy()
            esquerda.destroy()
            direita.destroy()
            if on_finish: on_finish()
            return

        fala = falas[i]
        texto.config(text=fala["texto"])

        if fala["imagem"] not in imagens_cache:
            img = Image.open(fala["imagem"])
            img = img.resize((IMG_SIZE, IMG_SIZE))
            imagens_cache[fala["imagem"]] = ImageTk.PhotoImage(img)

        img = imagens_cache[fala["imagem"]]

        if fala["lado"] == "esquerda":
            esquerda.config(image=img)
            direita.config(image="")
        else:
            direita.config(image=img)
            esquerda.config(image="")

        root.bind("<space>", lambda e: mostrar_fala(i+1))

    mostrar_fala()
