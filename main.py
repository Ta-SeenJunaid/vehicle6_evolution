# main.py
import pygame
import random
import math
from config import WIDTH, HEIGHT, FPS, POPULATION_SIZE, MUTATION_RATE
from entities.vehicle import Vehicle
from entities.light import Light

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Vehicle 6: Evolution Data HUD")
    clock = pygame.time.Clock()
    
    font = pygame.font.SysFont("consolas", 14)

    lights = [Light(WIDTH // 2, HEIGHT // 2, radius=20)]
    
    population = [
        Vehicle(random.randint(100, WIDTH-100), random.randint(100, HEIGHT-100), heading=random.uniform(0, math.pi*2))
        for _ in range(POPULATION_SIZE)
    ]
    
    total_spawned = POPULATION_SIZE
    total_deaths = 0
    sim_frames = 0
    
    best_fitness = 0
    best_genome = [0, 0, 0, 0, 0]
    best_spawn_id = 0 

    # --- NEW: HUD State Toggle ---
    show_full_hud = True 

    running = True
    while running:
        screen.fill((240, 240, 240))
        sim_frames += 1
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # --- NEW: Keyboard Controls ---
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:  # Press 'H' to toggle HUD
                    show_full_hud = not show_full_hud

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    lights.append(Light(event.pos[0], event.pos[1], radius=20))
                elif event.button == 3: 
                    click_x, click_y = event.pos
                    for i in range(len(lights)-1, -1, -1):
                        light = lights[i]
                        dist = math.hypot(light.x - click_x, light.y - click_y)
                        if dist <= light.radius:
                            lights.pop(i)
                            break 

        for light in lights:
            light.draw(screen)

        living_vehicles = []
        for vehicle in population:
            if vehicle.alive:
                vehicle.update(lights, WIDTH, HEIGHT)
                vehicle.draw(screen)
                living_vehicles.append(vehicle)
                
                if vehicle.fitness > best_fitness:
                    best_fitness = vehicle.fitness
                    best_genome = vehicle.weights.copy()
                    best_spawn_id = total_spawned - (POPULATION_SIZE - len(living_vehicles))

        while len(living_vehicles) < POPULATION_SIZE:
            if living_vehicles:
                tournament_size = min(3, len(living_vehicles))
                candidates = random.sample(living_vehicles, tournament_size)
                parent = max(candidates, key=lambda v: v.fitness)
            else:
                parent = random.choice(population) 
            
            child_x = WIDTH // 2 + random.randint(-150, 150)
            child_y = HEIGHT // 2 + random.randint(-150, 150)
            child = parent.copy_with_mutation(child_x, child_y, MUTATION_RATE)
            
            for i in range(len(population)):
                if not population[i].alive:
                    population[i] = child
                    total_spawned += 1
                    total_deaths += 1
                    living_vehicles.append(child) 
                    break
                    
        # --- DRAW UI OVERLAYS ---
        sim_time_sec = sim_frames // FPS
        
        if show_full_hud:
            # --- FULL HUD ---
            genome_str = ", ".join([f"{w:+.1f}" for w in best_genome])
            info_text = [
                "=== SIMULATION STATUS ===",
                f"Time Elapsed   : {sim_time_sec} sec",
                f"Active Lights  : {len(lights)}",
                "",
                "=== POPULATION DYNAMICS ===",
                f"Living Vehicles: {len(living_vehicles)} / {POPULATION_SIZE}",
                f"Total Spawned  : {total_spawned}",
                f"Total Deaths   : {total_deaths}",
                "",
                "=== ALL-TIME BEST SPECIMEN ===",
                f"Spawn ID       : #{best_spawn_id}",
                f"Max Fitness    : {best_fitness}",
                "Genome Weights : [LL, LR, RL, RR, Base]",
                f"                 [{genome_str}]",
                "",
                "=== CONTROLS ===",
                "[Left Click]  Add Light",
                "[Right Click] Remove Light",
                "[ H ]         Hide HUD" # Added instruction
            ]
            
            hud_height = len(info_text) * 18 + 20
            hud_surface = pygame.Surface((310, hud_height))
            hud_surface.set_alpha(210) 
            hud_surface.fill((255, 255, 255))
            screen.blit(hud_surface, (10, 10))
            
            for i, text in enumerate(info_text):
                rendered = font.render(text, True, (20, 20, 20))
                screen.blit(rendered, (20, 20 + i * 18))
                
        else:
            # --- MINIMAL HUD ---
            # Just a tiny strip of essential info when the big box is hidden
            minimal_text = f" Pop: {len(living_vehicles)}/{POPULATION_SIZE} | Best Fit: {best_fitness} | [H] Show Details "
            
            # Semi-transparent backing for just the single line
            rendered_min = font.render(minimal_text, True, (20, 20, 20))
            min_surface = pygame.Surface((rendered_min.get_width() + 10, rendered_min.get_height() + 6))
            min_surface.set_alpha(180)
            min_surface.fill((255, 255, 255))
            
            screen.blit(min_surface, (10, 10))
            screen.blit(rendered_min, (15, 13))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()