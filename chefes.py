import math
import random

def spawn_esqueleto_gigante(player, enemies, W, H):
    """Spawna o chefe esqueleto: uma cabeça e 4 braços vinculados."""
    cx, cy = W // 2, -100
    
    # Calculamos a vida máxima inicial para podermos usar na barra de vida depois
    hp_cabeca = 2000 + (player["level"] * 50)
    
    cabeca = {
        "x": cx, "y": cy,
        "hp": hp_cabeca,
        "hp_max": hp_cabeca, # Guardamos o HP Máximo aqui
        "base_speed": 2.5, "speed": 2.5,
        "icon": "💀", "size": 90, "damage": 15,
        "is_boss": True,
        "boss_type": "skeletron_head",
        "timer": 0,
        "bracos_vivos": 4
    }
    enemies.append(cabeca)
    
    for i in range(4):
        lado = -1 if i < 2 else 1
        distancia_base = 120 if (i % 2 == 0) else 200
        hp_braco = 600 + (player["level"] * 20)
        
        braco = {
            "x": cx + (lado * distancia_base), "y": cy + 50,
            "hp": hp_braco,
            "base_speed": 4, "speed": 4,
            "icon": "🦴", "size": 45, "damage": 8,
            "is_boss": True,
            "boss_type": "skeletron_hand",
            "lado": lado,
            "index": i,
            "cabeca_vinculada": cabeca
        }
        enemies.append(braco)


def atualizar_esqueleto(e, player, W, H):
    if e["boss_type"] == "skeletron_head":
        e["timer"] += 1
        alvo_x = player["x"]
        alvo_y = player["y"] - 180
        
        dx, dy = alvo_x - e["x"], alvo_y - e["y"]
        dist = math.sqrt(dx*dx + dy*dy) + 0.1
        
        # Se os braços morrerem, ele fica furioso e MUITO rápido
        velocidade = e["base_speed"] * 2.2 if e["bracos_vivos"] <= 0 else e["base_speed"]
        
        e["x"] += (dx / dist) * velocidade
        e["y"] += (dy / dist) * velocidade
        
        if e["timer"] % 300 > 200: 
            dx_p, dy_p = player["x"] - e["x"], player["y"] - e["y"]
            dist_p = math.sqrt(dx_p*dx_p + dy_p*dy_p) + 0.1
            e["x"] += (dx_p / dist_p) * (velocidade * 2)
            e["y"] += (dy_p / dist_p) * (velocidade * 2)

    elif e["boss_type"] == "skeletron_hand":
        cabeca = e["cabeca_vinculada"]
        if cabeca not in e["_lista_inimigos_atual"]:
            e["hp"] = 0
            return
            
        cabeca["timer"] += 0.25
        tempo = cabeca["timer"] + (e["index"] * 35)
        
        largura_ataque = 280 if (e["index"] % 2 == 0) else 450
        fase_ataque = math.sin(tempo * 0.05) 
        
        alvo_x = cabeca["x"] + (e["lado"] * largura_ataque) + (fase_ataque * 180 * e["lado"])
        alvo_y = cabeca["y"] + 100 + (math.cos(tempo * 0.07) * 60)
        
        if int(tempo) % 250 > 170:
            alvo_y = player["y"]
            alvo_x = player["x"] + (e["lado"] * 120)
            
        dx, dy = alvo_x - e["x"], alvo_y - e["y"]
        dist = math.sqrt(dx*dx + dy*dy) + 0.1
        
        e["x"] += (dx / dist) * e["base_speed"]
        e["y"] += (dy / dist) * e["base_speed"]