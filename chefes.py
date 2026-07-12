import math
import random

def spawn_esqueleto_gigante(player, enemies, W, H):
    hp_cabeca = 2000 + (player["level"] * 50)
    
    cabeca = {
        "x": W // 2, "y": -100,
        "hp": hp_cabeca, "hp_max": hp_cabeca,
        "base_speed": 3,
        "icon": "💀", "size": 90, "damage": 5,
        "is_boss": True,
        "boss_type": "skeletron_head",
        "state": "IDLE", # ESTADOS: IDLE, CHARGE, ATTACK_SEQUENCE, ARM_ATTACK, FURY, DEATH_SEQUENCE, DYING
        "state_timer": 0,
        "bracos_vivos": 4,
        "angle": 0
    }
    enemies.append(cabeca)
    
    # Ossos orbitando
    for i in range(4):
        lado = -1 if i < 2 else 1
        distancia_base = 120 if (i % 2 == 0) else 200
        hp_braco = 600 + (player["level"] * 20)
        
        braco = {
            "x": cabeca["x"] + (lado * distancia_base), "y": cabeca["y"] + 50,
            "hp": hp_braco,
            "base_speed": 4, "speed": 4,
            "icon": "🦴", "size": 100, "damage": 5,
            "is_boss": True,
            "boss_type": "skeletron_hand",
            "lado": lado,
            "index": i,
            "cabeca_vinculada": cabeca
        }
        enemies.append(braco)

    # Braços completos (superior, antebraço e mão)
    for lado in [-1, 1]:
        base_x = cabeca["x"] + lado * 150
        base_y = cabeca["y"] + 50
        braco_superior = {
            "x": base_x, "y": base_y,
            "hp": 800,
            "damage": 5,
            "base_speed": 3, "speed": 3,   # <--- adiciona aqui
            "is_boss": True,
            "boss_type": "skeletron_arm_upper",
            "lado": lado,
            "cabeca_vinculada": cabeca
        }
        antebraco = {
            "x": base_x + lado * 60, "y": base_y + 60,
            "hp": 600,
            "damage": 5,
            "base_speed": 3, "speed": 3,   # <--- adiciona aqui
            "is_boss": True,
            "boss_type": "skeletron_arm_lower",
            "parent": braco_superior
        }
        mao = {
            "x": base_x + lado * 100, "y": base_y + 100,
            "hp": 400,
            "damage": 8,
            "base_speed": 3, "speed": 3,   # <--- adiciona aqui
            "is_boss": True,
            "boss_type": "skeletron_hand_full",
            "parent": antebraco
        }

        enemies.extend([braco_superior, antebraco, mao])


def atualizar_esqueleto(e, player, W, H):
    if e["boss_type"] == "skeletron_head":
        e["state_timer"] += 1

        # Morte dramática
        if e.get("hp", 1) <= 0 and e["state"] not in ["DYING", "DEATH_SEQUENCE"]:
            e["state"] = "DEATH_SEQUENCE"
            e["state_timer"] = 0

        if e["state"] == "DEATH_SEQUENCE":
            e["state_timer"] += 1
            e["angle"] = e.get("angle", 0) + 0.4
            e["x"] += random.randint(-3, 3)
            e["y"] += random.randint(-3, 3)
            if e["state_timer"] > 120:
                e["state"] = "DYING"
                e["state_timer"] = 0
            return

        if e["state"] == "DYING":
            e["state_timer"] += 1
            if e["state_timer"] > 60:
                e["remove_me"] = True
                e["boss_finalizado"] = True
            return

        # Fúria
        if e["bracos_vivos"] <= 0 and e["state"] not in ["DYING", "DEATH_SEQUENCE"]:
            e["state"] = "FURY"
            e["angle"] = e.get("angle", 0) + 0.3
            dx, dy = player["x"] - e["x"], player["y"] - e["y"]
            dist = math.sqrt(dx**2 + dy**2) + 0.1
            e["x"] += (dx/dist) * 8
            e["y"] += (dy/dist) * 8
            return

        # Escolha de ataque
        if e["state"] == "IDLE" and e["state_timer"] > 300:
            e["state"] = random.choice(["CHARGE", "ATTACK_SEQUENCE", "ARM_ATTACK"])
            e["state_timer"] = 0

        # Movimento base
        if e["state"] == "IDLE":
            target_x = W // 2 + math.sin(e["state_timer"] * 0.05) * 100
            target_y = 150
            e["x"] += (target_x - e["x"]) * 0.05
            e["y"] += (target_y - e["y"]) * 0.05

        elif e["state"] == "CHARGE":
            if e["state_timer"] < 60:
                dx, dy = player["x"] - e["x"], player["y"] - e["y"]
                e["x"] += dx * 0.15
                e["y"] += dy * 0.15
            else:
                e["state"] = "IDLE"
                e["state_timer"] = 0

        elif e["state"] == "ATTACK_SEQUENCE":
            if e["state_timer"] > 400:
                e["state"] = "IDLE"
                e["state_timer"] = 0

        elif e["state"] == "ARM_ATTACK":
            if e["state_timer"] > 200:
                e["state"] = "IDLE"
                e["state_timer"] = 0

    elif e["boss_type"] == "skeletron_hand":
        if e.get("hp", 1) <= 0:
            e["remove_me"] = True
            return
        cabeca = e["cabeca_vinculada"]

        if cabeca["state"] == "ATTACK_SEQUENCE":
            tempo_ataque = e["index"] * 80
            if tempo_ataque - 40 < cabeca["state_timer"] < tempo_ataque:
                ang = cabeca["state_timer"] * 0.3
                e["x"] = cabeca["x"] + math.cos(ang + e["index"]) * 60
                e["y"] = cabeca["y"] + math.sin(ang + e["index"]) * 60
                e["girando"] = True
            elif cabeca["state_timer"] == tempo_ataque:
                e["target_x"], e["target_y"] = player["x"], player["y"]
                e["atacando"] = True
                e["girando"] = False
            if e.get("atacando"):
                dx, dy = e["target_x"] - e["x"], e["target_y"] - e["y"]
                e["x"] += dx * 0.18
                e["y"] += dy * 0.18
                if abs(dx) < 15 and abs(dy) < 15:
                    e["atacando"] = False
                    e["retornando"] = True
            elif e.get("retornando"):
                dx, dy = cabeca["x"] - e["x"], cabeca["y"] - e["y"]
                e["x"] += dx * 0.1
                e["y"] += dy * 0.1
                if abs(dx) < 20 and abs(dy) < 20:
                    e["retornando"] = False
            elif not e.get("atacando"):
                e["x"] = cabeca["x"] + math.cos(cabeca["state_timer"] * 0.1 + e["index"]) * 100
                e["y"] = cabeca["y"] + math.sin(cabeca["state_timer"] * 0.1 + e["index"]) * 100
        else:
            e["x"] = cabeca["x"] + math.cos(cabeca["state_timer"] * 0.1 + e["index"]) * 100
            e["y"] = cabeca["y"] + math.sin(cabeca["state_timer"] * 0.1 + e["index"]) * 100

    elif e["boss_type"] == "skeletron_arm_upper":
        if e.get("hp", 1) <= 0:
            e["remove_me"] = True
            return
        cabeca = e["cabeca_vinculada"]
        e["x"] = cabeca["x"] + e["lado"] * 150
        e["y"] = cabeca["y"] + 50

    elif e["boss_type"] == "skeletron_arm_lower":
        if e.get("hp", 1) <= 0:
            e["remove_me"] = True
            return
        parent = e["parent"]
        e["x"] = parent["x"] + parent["lado"] * 60
        e["y"] = parent["y"] + 60

    elif e["boss_type"] == "skeletron_hand_full":
        if e.get("hp", 1) <= 0:
            e["remove_me"] = True
            return
        parent = e["parent"]
        lado = parent["parent"]["lado"]
        e["x"] = parent["x"] + lado * 40
        e["y"] = parent["y"] + 40

        cabeca = parent["parent"]["cabeca_vinculada"]
        if cabeca["state"] == "ARM_ATTACK":
            dx, dy = player["x"] - e["x"], player["y"] - e["y"]
            e["x"] += dx * 0.2
            e["y"] += dy * 0.2

def get_boss_visuals(e, frame_count):
    visuals = []

    # Efeito de Morte dramática
    if e.get("state") == "DEATH_SEQUENCE":
        visuals.append(("🔴", e["x"], e["y"], 100))
        for _ in range(6):
            visuals.append(("💥", e["x"] + random.randint(-80, 80),
                                e["y"] + random.randint(-80, 80), 30))

    # Efeito de Morte final
    if e.get("state") == "DYING":
        if frame_count % 5 < 3:
            visuals.append(("💥", e["x"] + random.randint(-50, 50),
                                e["y"] + random.randint(-50, 50), 30))

    # Cabeça
    if e["boss_type"] == "skeletron_head":
        visuals.append(("💀", e["x"], e["y"], 100))

    # Ossos orbitando
    elif e["boss_type"] == "skeletron_hand":
        visuals.append(("🦴", e["x"], e["y"], 100))
        if e.get("girando"):
            visuals.append(("⚡", e["x"], e["y"] - 30, 20))

    # Braço superior
    elif e["boss_type"] == "skeletron_arm_upper":
        if e["lado"] == -1:  # braço esquerdo
            visuals.append(("🦴", e["x"], e["y"], 80))
        else:  # braço direito "espelhado" via offset
            visuals.append(("🦴", e["x"] - 40, e["y"], 80))

    # Antebraço
    elif e["boss_type"] == "skeletron_arm_lower":
        if e["parent"]["lado"] == -1:  # antebraço esquerdo
            visuals.append(("🦴", e["x"], e["y"], 80))
        else:  # antebraço direito "espelhado"
            visuals.append(("🦴", e["x"] - 40, e["y"], 80))

    # Mão
    elif e["boss_type"] == "skeletron_hand_full":
        if e["parent"]["parent"]["lado"] == -1:
            visuals.append(("🫳", e["x"], e["y"], 80))  # mão esquerda
        else:
            visuals.append(("🫴", e["x"], e["y"], 80))  # mão direita


    return visuals


