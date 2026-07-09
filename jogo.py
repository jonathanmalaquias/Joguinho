import tkinter as tk
import random
import math
import subprocess
import sys
import os

def voltar_menu():
    root.destroy()

    subprocess.Popen([
        sys.executable,
        os.path.join(os.path.dirname(__file__), "main.py")
    ])
# =========================
# WINDOW
# =========================

root = tk.Tk()
root.title("Survivor Final Fixed")
root.attributes("-fullscreen", True)
root.configure(bg="black")

W = root.winfo_screenwidth()
H = root.winfo_screenheight()

canvas = tk.Canvas(root, width=W, height=H, bg="black", highlightthickness=0)
canvas.pack()


# =========================
# PLAYER
# =========================

player ={
    "x": W//2,
    "y": H//2,
    "speed": 6,
    "hp": 100,
    "hp_max": 100,
    "xp": 0,
    "level": 1,

    # --- ARMA INICIAL ---
    "main_damage": 15,
    "main_cd": 500,        # Recarga inicial (ms)
    
    # --- TIRO LATERAL ---
    "side_unlocked": False,
    "side_damage": 30,
    "side_cd": 1000,        # Recarga inicial (ms)
    
    # --- TIRO DIAGONAL ---
    "diag_unlocked": False,
    "diag_damage": 30,
    "diag_cd": 1000,        # Recarga inicial (ms)

    # --- OUTROS UPGRADES ---
    "red": False,
    "red_cd": 1000,        # Recarga da Sniper individualizada
    "trap_master": False,
    "vampirism": 0.0,
    
    # --- NOVOS STATUS ---
    "bullet_radius_bonus": 0,
    "crit_chance": 0.0,
    "freeze_unlocked": False,
    "xp_bonus": 0.0,
    "thorns_damage": 0.0,
    # ===== FOGUETE =====
    "rocket_unlocked": False,
    "rocket_damage": 200,
    "rocket_radius": 150,
    "rocket_cd": 5000,

    # ===== TEMPESTADE =====
    "storm_unlocked": False,
    "storm_damage": 70,
    "storm_cd": 4000,
    "storm_hits": 4,

    # ===== TORRETAS =====
    "orb_unlocked": False,
    "orb_damage": 20,
    "orb_cd": 1200,
    "orb_count": 1,

}

enemies = []
bullets = []
traps = []
keys = {}
snowballs = []
rockets = []
explosions = []

orbs = []

effects = []
paused = True
game_started = False
countdown = 5

current_options = []
boss_spawned_this_milestone = False


# =========================
# ENEMIES
# =========================

enemy_types = [
    # ("ícone", vida, velocidade, tamanho, DANO_POR_FRAME)
    ("💀", 40, 4, 30, 2),  
    ("👻", 10, 7, 30, 1),  
    ("🧟", 100, 2, 30, 5), 
    ("🕷️", 50, 4, 30, 2),  
    ("🐺", 70, 5, 30, 2),  
]

enemy_types_LV39 = [
    # ("ícone", vida, velocidade, tamanho, DANO_POR_FRAME)
    ("🧜🏼‍♀️", 300, 4, 30, 5),  
    ("⛄", 250, 4, 30, 5),  
    ("🐸", 100, 2, 30, 5), 
    ("🦖", 700, 3, 50, 10),  
]

bosses = [
    # ("ícone", vida, velocidade, tamanho, DANO_POR_FRAME)
    ("🐉", 1000, 10, 100, 25), 
    ("👹", 1000, 2, 100, 50), 
]


# =========================
# INPUT & CONTROLS
# =========================

def down(e): 
    key = e.keysym.lower()
    keys[key] = True
    
    if paused and current_options:
        if key == "1" and len(current_options) >= 1: select_upgrade_by_index(0)
        elif key == "2" and len(current_options) >= 2: select_upgrade_by_index(1)
        elif key == "3" and len(current_options) >= 3: select_upgrade_by_index(2)

def up(e): 
    keys[e.keysym.lower()] = False

root.bind("<KeyPress>", down)
root.bind("<KeyRelease>", up)


# =========================
# CONTAGEM INICIAL
# =========================

def start_countdown():
    global countdown, paused

    canvas.delete("all")

    if countdown > 0:
        canvas.create_text(
            W//2,
            H//2,
            text=str(countdown),
            fill="white",
            font=("Arial", 100, "bold")
        )

        countdown -= 1
        root.after(1000, start_countdown)

    else:
        canvas.create_text(
            W//2,
            H//2,
            text="SOBREVIVA !",
            fill="lime",
            font=("Arial", 80, "bold")
        )
        root.after(700, begin_game)


def begin_game():
    global paused
    canvas.delete("all")
    paused = False


# =========================
# SPAWN ENEMIES
# =========================

def spawn_enemy():
    global boss_spawned_this_milestone
    if paused:
        root.after(500, spawn_enemy)
        return

    if player["level"] % 6 == 0:
        if not boss_spawned_this_milestone:
            e = random.choice(bosses)
            boss_spawned_this_milestone = True
            
            enemies.append({
                "x": random.randint(0, W),
                "y": random.randint(0, H),
                "hp": e[1] + player["level"] * 10,
                "base_speed": e[2],
                "speed": e[2],
                "icon": e[0],
                "size": e[3],
                "damage": e[4],
                "is_boss": True
            })
    else:
        boss_spawned_this_milestone = False
        
        if player["level"] >= 30:
            e = random.choice(enemy_types + enemy_types_LV39)
        else:
            e = random.choice(enemy_types)
        enemies.append({
            "x": random.randint(0, W),
            "y": random.randint(0, H),
            "hp": e[1] + player["level"] * 10,
            "base_speed": e[2],
            "speed": e[2],
            "icon": e[0],
            "size": e[3],
            "damage": e[4],
            "is_boss": False
        })

    root.after(650, spawn_enemy)

spawn_enemy()


# =========================
# INDEPENDENT SHOOT SYSTEMS
# =========================

# 1. ARMA INICIAL (Foca no mais próximo)
def shoot_main():
    if not paused and enemies:
        target = min(enemies, key=lambda e: (e["x"]-player["x"])**2 + (e["y"]-player["y"])**2)
        dx, dy = target["x"] - player["x"], target["y"] - player["y"]
        dist = math.sqrt(dx*dx + dy*dy) + 0.1
        ux, uy = dx / dist, dy / dist

        bullets.append({
            "x": player["x"], "y": player["y"], "vx": ux * 12, "vy": uy * 12,
            "life": 160, "r": 5, "type": "main", "dmg": player["main_damage"]
        })

    root.after(int(player["main_cd"]), shoot_main)

# 2. TIRO LATERAL (Perpendicular ao inimigo mais próximo)
def shoot_side():
    if not paused and player["side_unlocked"] and enemies:
        target = min(enemies, key=lambda e: (e["x"]-player["x"])**2 + (e["y"]-player["y"])**2)
        dx, dy = target["x"] - player["x"], target["y"] - player["y"]
        dist = math.sqrt(dx*dx + dy*dy) + 0.1
        ux, uy = dx / dist, dy / dist

        for vx, vy in [(-uy * 12, ux * 12), (uy * 12, -ux * 12)]:
            bullets.append({
                "x": player["x"], "y": player["y"], "vx": vx, "vy": vy,
                "life": 140, "r": 5, "type": "side", "dmg": player["side_damage"]
            })

    root.after(int(player["side_cd"]), shoot_side)

# 3. TIRO DIAGONAL (Fixo nas 4 diagonais)
def shoot_diag():
    if not paused and player["diag_unlocked"] and enemies:
        diag_speed = 12 * math.cos(math.radians(45))
        dirs = [(diag_speed, diag_speed), (-diag_speed, diag_speed), 
                (diag_speed, -diag_speed), (-diag_speed, -diag_speed)]
        
        for vx, vy in dirs:
            bullets.append({
                "x": player["x"], "y": player["y"], "vx": vx, "vy": vy,
                "life": 140, "r": 5, "type": "diag", "dmg": player["diag_damage"]
            })

    root.after(int(player["diag_cd"]), shoot_diag)

# 4. TIRO VERMELHO (Sniper focando o mais forte)
def shoot_red():
    if not paused and player["red"] and enemies:
        strongest = max(enemies, key=lambda e: e["hp"])
        sdx, sdy = strongest["x"] - player["x"], strongest["y"] - player["y"]
        sdist = math.sqrt(sdx*sdx + sdy*sdy) + 0.1

        bullets.append({
            "x": player["x"], "y": player["y"],
            "vx": (sdx/sdist) * 14, "vy": (sdy/sdist) * 14,
            "life": 200, "r": 6, "type": "red", "dmg": player["main_damage"] * 3
        })

    root.after(int(player["red_cd"]), shoot_red)
def shoot_rocket():

    if not paused and player["rocket_unlocked"] and enemies:

        alvo = max(enemies, key=lambda e: e["hp"])

        dx = alvo["x"] - player["x"]
        dy = alvo["y"] - player["y"]

        dist = math.sqrt(dx*dx + dy*dy) + 0.1

        rockets.append({

            "x": player["x"],
            "y": player["y"],

            "vx": dx/dist * 7,
            "vy": dy/dist * 7,

            "life": 350

        })

    root.after(player["rocket_cd"], shoot_rocket)
# Iniciar loops de tiro independentes
shoot_main()
shoot_side()
shoot_diag()
shoot_red()
shoot_rocket()

# =========================
# TRAPS
# =========================

def spawn_trap(x, y):
    traps.append({"x": x, "y": y, "life": 220})


# =========================
# LEVEL UP & UPGRADES
# =========================

def level_up():
    global paused, current_options
    paused = True

    options = [
        # --- Upgrades Arma Inicial ---
        ("⚔️ Inicial: Dano +6", lambda: upgrade_main_dmg()),
        ("⏱️ Inicial: Cadência +15%", lambda: upgrade_main_cd()),
        
        # --- Upgrades Tiro Lateral ---
        ("↔️ Tiro Lateral (Libera/Cadência +15%)", lambda: upgrade_side()),
        ("💥 Lateral: Dano +4", lambda: upgrade_side_dmg()),
        
        # --- Upgrades Tiro Diagonal ---
        ("✖ Tiro Diagonal (Libera/Cadência +15%)", lambda: upgrade_diag()),
        ("⚡ Diagonal: Dano +4", lambda: upgrade_diag_dmg()),
        
        # --- Upgrades de Combate Avançados ---
        ("🔮 Projéteis Gigantes (+2 Raio)", lambda: upgrade_bullet_size()),
        ("🎯 Acerto Crítico (+10% Chance de 2x Dano)", lambda: upgrade_crit()),
        ("❄️ Tiro Congelante (Deixa alvos lentos)", lambda: upgrade_freeze()),
        ("🚀 Lança-Foguetes", lambda: upgrade_rocket()),
        # --- Upgrades Utilitários e Defensivos ---
        ("🧲 Ímã de XP (+0.2 XP passivo extra)", lambda: upgrade_xp_magnet()),
        ("🛡️ Escudo de Espinhos (Contra-ataca ao tocar)", lambda: upgrade_thorns()),
        
        # --- Gerais/Outros ---
        ("🔴 Sniper", lambda: set_red()),
        ("🪤 Armadilhas", lambda: set_trap()),
        ("❤️ Vida +40", lambda: hp_up()),
        ("⚡ Velocidade +1", lambda: speed_up()),
        ("🦇 Vampirismo +10%", lambda: vamp_up()),
    ]

    # Filtra para não exibir upgrades de dano de armas bloqueadas
    filtered_options = []
    for opt in options:
        if "Lateral: Dano" in opt[0] and not player["side_unlocked"]:
            continue
        if "Diagonal: Dano" in opt[0] and not player["diag_unlocked"]:
            continue
        filtered_options.append(opt)

    current_options = random.sample(filtered_options, 3)
    show_upgrade(current_options)

# Funções de ativação dos Upgrades
def upgrade_main_dmg(): player["main_damage"] += 6
def upgrade_main_cd(): player["main_cd"] *= 0.85
def upgrade_side():
    player["side_unlocked"] = True
    player["side_cd"] *= 0.85
def upgrade_side_dmg(): player["side_damage"] += 4
def upgrade_diag():
    player["diag_unlocked"] = True
    player["diag_cd"] *= 0.85
def upgrade_diag_dmg(): player["diag_damage"] += 4
def upgrade_bullet_size(): player["bullet_radius_bonus"] += 2
def upgrade_crit(): player["crit_chance"] += 0.10
def upgrade_freeze(): player["freeze_unlocked"] = True
def upgrade_xp_magnet(): player["xp_bonus"] += 0.2
def upgrade_thorns(): player["thorns_damage"] += 5.0
def set_red(): player["red"] = True
def set_trap(): player["trap_master"] = True
def hp_up():
    player["hp_max"] += 40
    player["hp"] += 40
def speed_up(): player["speed"] += 1
def vamp_up(): player["vampirism"] += 0.10
def upgrade_rocket():

    if not player["rocket_unlocked"]:

        player["rocket_unlocked"] = True

    else:

        player["rocket_damage"] += 50
        player["rocket_radius"] += 20
        player["rocket_cd"] = int(player["rocket_cd"] * 0.85)
def select_upgrade_by_index(index):
    global paused, current_options
    _, func = current_options[index]
    func()
    paused = False
    current_options = []
    clear_buttons()


# =========================
# UI
# =========================

def show_upgrade(options):
    canvas.delete("all")

    canvas.create_text(W//2, 120, text="🔥 LEVEL UP 🔥", fill="white", font=("Arial", 40, "bold"))
    canvas.create_text(W//2, 180, text="Escolha usando o MOUSE ou as teclas [1], [2] ou [3]", fill="#aaa", font=("Arial", 14, "italic"))

    for i, (txt, func) in enumerate(options):
        display_txt = f"[{i+1}] {txt}"
        btn = tk.Button(root, text=display_txt, command=lambda idx=i: select_upgrade_by_index(idx),
                        fg="white", bg="#222", font=("Arial", 14), width=40)
        btn.place(x=W//2-220, y=250+i*70)

def clear_buttons():
    for w in root.winfo_children():
        if isinstance(w, tk.Button): w.destroy()


# =========================
# UPDATE LOOP
# =========================

def update():
    global paused

    if not paused:
        # Movimentação
        if keys.get("w"): player["y"] -= player["speed"]
        if keys.get("s"): player["y"] += player["speed"]
        if keys.get("a"): player["x"] -= player["speed"]
        if keys.get("d"): player["x"] += player["speed"]

        # Regen passiva
        player["hp"] = min(player["hp_max"], player["hp"] + 0.02)

        # IA dos Inimigos
        for e in enemies:
            dx, dy = player["x"] - e["x"], player["y"] - e["y"]
            dist = math.sqrt(dx*dx + dy*dy) + 0.1

            if e["hp"] > 120: e["speed"] = e["base_speed"] * 0.6
            elif e["hp"] > 60: e["speed"] = e["base_speed"]
            else: e["speed"] = e["base_speed"] * 1.4

            e["x"] += dx/dist * e["speed"]
            e["y"] += dy/dist * e["speed"]

            # Dano recebido pelo player + Ativação dos Espinhos
            if dist < 20: 
                player["hp"] -= e["damage"]
                if player["thorns_damage"] > 0:
                    e["hp"] -= player["thorns_damage"] * 0.1

        # Atualizar Projéteis
        for b in bullets:
            b["x"] += b["vx"]
            b["y"] += b["vy"]
            b["life"] -= 1
        bullets[:] = [b for b in bullets if b["life"] > 0]

                # Atualiza Foguetes
        # ==========================
        # ATUALIZA FOGUETES
        # ==========================

        for r in rockets[:]:

            r["x"] += r["vx"]
            r["y"] += r["vy"]

            r["life"] -= 1

            if (
                r["x"] < 0 or
                r["x"] > W or
                r["y"] < 0 or
                r["y"] > H
            ):

                explosions.append({

                    "x": r["x"],
                    "y": r["y"],
                    "life": 18,
                    "radius": player["rocket_radius"]

                })

                rockets.remove(r)

            elif r["life"] <= 0:

                explosions.append({

                    "x": r["x"],
                    "y": r["y"],
                    "life": 18,
                    "radius": player["rocket_radius"]

                })

                rockets.remove(r)


        # Atualizar Armadilhas
        for t in traps:
            t["life"] -= 1
            for e in enemies:
                if (e["x"]-t["x"])**2 + (e["y"]-t["y"])**2 < 500:
                    e["hp"] -= 4
                    if player["vampirism"] > 0:
                        player["hp"] = min(player["hp_max"], player["hp"] + 4 * player["vampirism"])
        traps[:] = [t for t in traps if t["life"] > 0]

        # Colisão de Projéteis com Inimigos (Cálculo de Crítico e Gelo)
        for b in bullets:
            for e in enemies:
                if (e["x"]-b["x"])**2 + (e["y"]-b["y"])**2 < 400:
                    dmg = b["dmg"]
                    
                    # Sistema de Crítico
                    if random.random() < player["crit_chance"]:
                        dmg *= 2    
                    
                    e["hp"] -= dmg
                    b["life"] = 0
                    
                    # Sistema de Congelamento
                    if player["freeze_unlocked"]:
                        e["speed"] = e["base_speed"] * 0.4
                    
                    if player["vampirism"] > 0:
                        player["hp"] = min(player["hp_max"], player["hp"] + dmg * player["vampirism"])

        # ==========================
        # COLISÃO DOS FOGUETES
        # ==========================

        for r in rockets[:]:

            for e in enemies:

                if (e["x"]-r["x"])**2 + (e["y"]-r["y"])**2 < 500:

                    explosions.append({

                        "x": r["x"],
                        "y": r["y"],
                        "life": 18,
                        "radius": player["rocket_radius"]

                    })

                    for alvo in enemies:

                        dist = math.sqrt(
                            (alvo["x"]-r["x"])**2 +
                            (alvo["y"]-r["y"])**2
                        )

                        if dist <= player["rocket_radius"]:

                            alvo["hp"] -= player["rocket_damage"]

                    if r in rockets:
                        rockets.remove(r)

                    break
        for ex in explosions:
            ex["life"] -= 1

        explosions[:] = [e for e in explosions if e["life"] > 0]

        # Morte dos Inimigos
        dead = [e for e in enemies if e["hp"] <= 0]
        for d in dead:
            if d in enemies:
                enemies.remove(d)
                if player["trap_master"]: spawn_trap(d["x"], d["y"])

        # Sistema de Experiência com bônus de Ímã
        player["xp"] += 0.4 + player["xp_bonus"]
        if player["xp"] >= player["level"] * 25:
            player["xp"] = 0
            player["level"] += 1
            level_up()

    # Fim de Jogo
    if player["hp"] <= 0:
        paused = True

        canvas.delete("all")
        clear_buttons()

        canvas.create_text(
            W//2,
            H//2-120,
            text="💀 VOCÊ MORREU 💀",
            fill="white",
            font=("Arial", 42, "bold")
        )

        canvas.create_text(
            W//2,
            H//2-50,
            text=f"Você chegou ao nível {player['level']}",
            fill="#aaa",
            font=("Arial", 18)
        )

        btn_menu = tk.Button(
            root,
            text="Voltar ao Menu Principal",
            command=voltar_menu,
            font=("Arial", 18, "bold"),
            bg="white",
            fg="black",
            width=25,
            cursor="hand2"
        )

        btn_menu.place(
            x=W//2-170,
            y=H//2+20
        )

        return
    
    draw()
    root.after(16, update)


# =========================
# DRAW
# =========================

def draw():
    if paused: return
    canvas.delete("all")

    # Jogador
    canvas.create_oval(player["x"]-12, player["y"]-12, player["x"]+12, player["y"]+12, fill="white")

    # Inimigos
    for e in enemies:
        canvas.create_text(e["x"], e["y"], text=e["icon"], fill="white", font=("Arial", e["size"]))

    # Projéteis (com bônus de tamanho)
    for b in bullets:
        color = "red" if b["type"] == "red" else "white"
        bonus_r = player["bullet_radius_bonus"] if b["type"] != "red" else 0
        r = b.get("r", 5) + bonus_r
        canvas.create_oval(b["x"]-r, b["y"]-r, b["x"]+r, b["y"]+r, fill=color, outline=color)

    for r in rockets:

        canvas.create_oval(
            r["x"]-9,
            r["y"]-9,
            r["x"]+9,
            r["y"]+9,
            fill="#ff7f00",
            outline="red",
            width=2
        )

        canvas.create_oval(
            r["x"]-4,
            r["y"]-4,
            r["x"]+4,
            r["y"]+4,
            fill="yellow",
            outline=""
        )

    for ex in explosions:

        r = ex["radius"] * (1 - ex["life"] / 18)

        canvas.create_oval(

            ex["x"]-r,
            ex["y"]-r,

            ex["x"]+r,
            ex["y"]+r,

            outline="orange",
            width=4
        )
    # Armadilhas
    for t in traps:
        canvas.create_rectangle(t["x"]-6, t["y"]-6, t["x"]+6, t["y"]+6, outline="cyan")

    # Interface de Texto
    canvas.create_text(
        20, 20, anchor="nw", fill="white", font=("Arial", 14),
        text=f"HP {int(player['hp'])}/{player['hp_max']} | LVL {player['level']} | Vamp: {int(player['vampirism']*100)}%"
    )


# =========================
# START
# =========================

start_countdown()
update()
root.mainloop()
