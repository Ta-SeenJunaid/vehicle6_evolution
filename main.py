# main.py

# --- IMPORTS ---
# We bring in external toolboxes that have pre-written code we need.
import pygame  # The main toolbox for creating games (draws graphics, reads keyboard/mouse)
import random  # Allows us to pick random numbers (crucial for mutations and spawning)
import math    # Gives us math formulas (like calculating distance between points)

# We bring in our own custom settings and objects from other files in our folder.
from config import WIDTH, HEIGHT, FPS, POPULATION_SIZE, MUTATION_RATE
from entities.vehicle import Vehicle
from entities.light import Light

def main():
    # --- SETUP & INITIALIZATION ---
    # 1. Turn on the Pygame engine. This must be done before using any Pygame features.
    pygame.init()
    
    # 2. Create the actual window the user will see, using the WIDTH and HEIGHT from config.py.
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Vehicle 6: Evolution Data HUD") # The title at the top of the window
    
    # 3. Create a Clock. This acts like a metronome to ensure the game doesn't run too fast.
    clock = pygame.time.Clock()
    
    # 4. Load a font so we can draw text on the screen later.
    # "consolas" is a clean, typewriter-style font. "14" is the size.
    font = pygame.font.SysFont("consolas", 14)

    # --- CREATING THE WORLD ---
    # Create a list containing exactly one Light object, placed dead center in the screen.
    # The "//" means "divide and round down to a whole number" (since pixels can't be fractions).
    lights = [Light(WIDTH // 2, HEIGHT // 2, radius=20)]
    
    # Create our starting population of Vehicles.
    # We use a "List Comprehension" here (the [ ... for _ in range(...) ] syntax).
    # It loops POPULATION_SIZE times (e.g., 30 times) and creates a vehicle at a random location.
    population = [
        Vehicle(
            x=random.randint(100, WIDTH-100),       # Random X position (kept away from edges)
            y=random.randint(100, HEIGHT-100),      # Random Y position (kept away from edges)
            heading=random.uniform(0, math.pi*2)    # Random starting angle (in radians, 0 to 2*Pi is a full circle)
        )
        for _ in range(POPULATION_SIZE)
    ]
    
    # --- TRACKING VARIABLES (STATISTICS) ---
    # These variables will act as scorekeepers while the simulation runs.
    total_spawned = POPULATION_SIZE # We just spawned our first batch, so we start at 30.
    total_deaths = 0                # No one has died yet.
    sim_frames = 0                  # Counts how many times the screen has refreshed.
    
    best_fitness = 0                # Highest score achieved by any vehicle ever.
    best_genome = [0, 0, 0, 0, 0]   # The DNA of the best vehicle.
    best_spawn_id = 0               # Which exact vehicle was the best one? (e.g., Vehicle #42)

    # A simple True/False switch. We will use this to hide/show the big text box.
    show_full_hud = False

    # --- THE MAIN GAME LOOP ---
    running = True # As long as this is True, the simulation keeps playing.
    while running:
        
        # 1. WIPE THE SCREEN CLEAN
        # Every frame, we paint the whole screen light gray (R=240, G=240, B=240).
        # If we didn't do this, the moving vehicles would leave a smeared trail behind them.
        screen.fill((240, 240, 240))
        sim_frames += 1 # Add 1 to our "time" counter
        
        # 2. CHECK FOR USER INPUT (MOUSE & KEYBOARD)
        # We ask Pygame for a list of everything the user just did (clicked, typed, etc.)
        for event in pygame.event.get():
            
            # Did they click the red 'X' on the window? If yes, break the loop.
            if event.type == pygame.QUIT:
                running = False
            
            # Did they press a key on the keyboard?
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:  # If the key was 'H'...
                    # Flip the switch! If it was True, make it False. If False, make it True.
                    show_full_hud = not show_full_hud

            # Did they click a mouse button?
            elif event.type == pygame.MOUSEBUTTONDOWN:
                
                # event.button == 1 means "Left Click"
                if event.button == 1: 
                    # Add a new light to our list exactly where the mouse was clicked (event.pos)
                    lights.append(Light(event.pos[0], event.pos[1], radius=20))
                
                # event.button == 3 means "Right Click"
                elif event.button == 3: 
                    click_x, click_y = event.pos # Grab the exact X, Y coordinates of the mouse
                    
                    # We loop through our lights backwards. Why? 
                    # If we delete items from a list while moving forwards, the list shrinks and we get errors!
                    for i in range(len(lights)-1, -1, -1):
                        light = lights[i]
                        
                        # math.hypot measures the straight-line distance between the mouse and the light.
                        # It's the Pythagorean theorem (a^2 + b^2 = c^2) done for you!
                        dist = math.hypot(light.x - click_x, light.y - click_y)
                        
                        # If the distance is smaller than the light's radius, we clicked inside it!
                        if dist <= light.radius:
                            lights.pop(i) # Delete this specific light from the list
                            break         # Stop looking (only delete one light per click)

        # 3. DRAW ALL THE LIGHTS
        for light in lights:
            light.draw(screen)

        # 4. UPDATE AND DRAW ALL THE VEHICLES
        living_vehicles = [] # We create a temporary empty list to track who is still alive
        
        for vehicle in population:
            if vehicle.alive:
                # If the vehicle hasn't starved or crashed, do its math and draw it
                vehicle.update(lights, WIDTH, HEIGHT)
                vehicle.draw(screen)
                living_vehicles.append(vehicle) # Add it to our temporary "alive" list
                
                # Check if this vehicle just broke the all-time high score!
                if vehicle.fitness > best_fitness:
                    best_fitness = vehicle.fitness
                    best_genome = vehicle.weights.copy() # .copy() ensures we take a snapshot, not a linked reference
                    
                    # Math trick to estimate which vehicle number this is
                    best_spawn_id = total_spawned - (POPULATION_SIZE - len(living_vehicles))

        # 5. THE EVOLUTION ENGINE (DEATH & REBIRTH)
        # If the number of living vehicles drops below our max population, we need to breed replacements!
        while len(living_vehicles) < POPULATION_SIZE:
            
            # Step A: Pick a parent
            if living_vehicles:
                # "Tournament Selection": We grab 3 random living vehicles...
                tournament_size = min(3, len(living_vehicles))
                candidates = random.sample(living_vehicles, tournament_size)
                
                # ...and whichever of those 3 has the highest fitness score gets to be the parent!
                parent = max(candidates, key=lambda v: v.fitness)
            else:
                # Fallback: If EVERYTHING died (extinction), just pick a random dead body to clone
                parent = random.choice(population) 
            
            # Step B: Spawn the child
            # We pick a random spot near the middle of the screen so it doesn't instantly die on the edge
            child_x = WIDTH // 2 + random.randint(-150, 150)
            child_y = HEIGHT // 2 + random.randint(-150, 150)
            
            # We ask the parent to make a copy of itself, but with slight random errors (mutations)
            child = parent.copy_with_mutation(child_x, child_y, MUTATION_RATE)
            
            # Step C: Replace a dead vehicle with the new child
            for i in range(len(population)):
                if not population[i].alive:     # Find the first dead body in the list
                    population[i] = child       # Replace it with the newborn child!
                    total_spawned += 1          # Update our stats
                    total_deaths += 1           
                    living_vehicles.append(child) # Add child to the living list to eventually break the while loop
                    break # Stop looking for dead bodies, we only needed to replace one this time
                    
        # 6. DRAW THE HEADS-UP DISPLAY (HUD)
        # Calculate how many actual seconds have passed (frames divided by 60 frames per second)
        sim_time_sec = sim_frames // FPS
        
        if show_full_hud:
            # --- FULL HUD MODE ---
            
            # Format the genome list to look pretty. e.g., instead of 1.234567, make it +1.2
            genome_str = ", ".join([f"{w:+.1f}" for w in best_genome])
            
            # This is a list of all the lines of text we want to print
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
                "[ H ]         Hide HUD"
            ]
            
            # Create a transparent background box to put behind the text so it's easy to read
            hud_height = len(info_text) * 18 + 20 # Calculate how tall the box needs to be
            hud_surface = pygame.Surface((310, hud_height))
            hud_surface.set_alpha(210)  # Make it slightly see-through (0 is invisible, 255 is solid)
            hud_surface.fill((255, 255, 255)) # Color it white
            
            # "Blit" means "draw one image onto another". We stamp our white box onto the screen.
            screen.blit(hud_surface, (10, 10))
            
            # Loop through our text lines and stamp them on top of the white box one by one
            for i, text in enumerate(info_text):
                rendered = font.render(text, True, (20, 20, 20)) # True turns on anti-aliasing (smooth edges)
                screen.blit(rendered, (20, 20 + i * 18)) # Stamp it, moving down 18 pixels each line
                
        else:
            # --- MINIMAL HUD MODE ---
            # If the user pressed H, we only show this one tiny line of text
            minimal_text = f" Pop: {len(living_vehicles)}/{POPULATION_SIZE} | Best Fit: {best_fitness} | [H] Show Details "
            
            rendered_min = font.render(minimal_text, True, (20, 20, 20))
            min_surface = pygame.Surface((rendered_min.get_width() + 10, rendered_min.get_height() + 6))
            min_surface.set_alpha(180)
            min_surface.fill((255, 255, 255))
            
            screen.blit(min_surface, (10, 10))
            screen.blit(rendered_min, (15, 13))

        # 7. UPDATE THE DISPLAY & TICK THE CLOCK
        # All of our drawing up above happened invisibly in the computer's memory.
        # display.flip() takes that invisible drawing and instantly slaps it onto the actual monitor.
        pygame.display.flip()
        
        # Tell the game to pause for a few milliseconds to ensure it runs exactly at the FPS we set (60)
        clock.tick(FPS)

# Cleanly close Pygame when the loop breaks
    pygame.quit()

# This is a standard Python trick. It basically says:
# "Only run the main() function if I am running this file directly."
if __name__ == "__main__":
    main()
    