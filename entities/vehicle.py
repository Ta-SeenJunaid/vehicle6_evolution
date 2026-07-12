# entities/vehicle.py

# --- IMPORTS ---
import pygame  # Used for drawing the vehicle on the screen
import math    # Used for trigonometry (sin and cos) to calculate steering and angles
import random  # Used for the "genetic mutations" and random starting values

from config import STARTING_ENERGY

class Vehicle:
    # A 'class' is like a blueprint. It tells Python how to build a Vehicle object.
    
    def __init__(self, x, y, radius=15, heading=0, weights=None):
        # __init__ is the constructor. It runs the exact moment a new Vehicle is born.
        
        # --- 1. PHYSICAL BODY ---
        self.x = x                # The X coordinate on the screen
        self.y = y                # The Y coordinate on the screen
        self.radius = radius      # How big the body is
        self.heading = heading    # Which way it's facing (in radians. 0 is Right, Pi is Left)
        
        # --- 2. SENSOR PLACEMENT ---
        # The sensors are placed on the front of the vehicle, slightly out to the sides.
        # math.radians(30) means 30 degrees to the left and right of the center.
        self.sensor_offset_angle = math.radians(30) 
        self.sensor_dist = self.radius + 5 # Stick out 5 pixels past the body
        
        # --- 3. THE BRAIN (GENETICS / WEIGHTS) ---
        # The 'weights' are the DNA of the vehicle. They determine how sensors connect to motors.
        # [w_left_to_left, w_left_to_right, w_right_to_left, w_right_to_right, base_speed]
        if weights is None:
            # If no DNA is provided (like at the start of the game), make it completely random!
            # Pick 4 random numbers between -2 and 2 for the sensor connections
            self.weights = [random.uniform(-2, 2) for _ in range(4)]
            # Add a 5th number for how fast it drives naturally without any light
            self.weights.append(random.uniform(0.5, 2.0)) 
        else:
            # If DNA IS provided (like when a parent gives birth to a child), use that DNA!
            self.weights = weights
            
        # --- 4. VISUAL APPEARANCE (PHENOTYPE) ---
        # We calculate the vehicle's color based on its first 3 genes (weights).
        # This is a cool trick so you can literally "see" families and species evolving together!
        # We use max() and min() to ensure the color values stay safely between 0 and 255.
        r = max(0, min(255, int(128 + self.weights[0] * 50)))
        g = max(0, min(255, int(128 + self.weights[1] * 50)))
        b = max(0, min(255, int(128 + self.weights[2] * 50)))
        self.color = (r, g, b)

        # --- 5. METABOLISM & EVOLUTION STATS ---
        # We import the starting energy from our config file.
        self.energy = STARTING_ENERGY
        self.fitness = 0      # Score goes up the longer it lives
        self.alive = True     # It starts out alive!


    def _sensor_positions(self):
        # This function uses Trigonometry (sin and cos) to figure out exactly where 
        # the left and right sensors are in the 2D world, based on where the vehicle is pointing.
        
        angle = self.sensor_offset_angle
        cos_h = math.cos(self.heading) # Calculates the "forward/backward" multiplier
        sin_h = math.sin(self.heading) # Calculates the "left/right" multiplier
        
        # Step 1: Calculate where the sensors are relative to the center of the vehicle
        left_lx = math.cos(angle) * self.sensor_dist
        left_ly = math.sin(angle) * self.sensor_dist
        right_lx = math.cos(-angle) * self.sensor_dist
        right_ly = math.sin(-angle) * self.sensor_dist
        
        # Step 2: Convert those relative positions into actual world screen coordinates
        lx = self.x + cos_h * left_lx - sin_h * left_ly
        ly = self.y + sin_h * left_lx + cos_h * left_ly
        rx = self.x + cos_h * right_lx - sin_h * right_ly
        ry = self.y + sin_h * right_lx + cos_h * right_ly
        
        # Return a bundle of the Left (X,Y) and Right (X,Y) coordinates
        return (lx, ly), (rx, ry)


    def _intensity_at(self, px, py, lights):
        # This function calculates how much total light is hitting a specific point (px, py).
        intensity = 0
        
        for light in lights:
            # Measure the horizontal (dx) and vertical (dy) distance to the light
            dx = px - light.x
            dy = py - light.y
            
            # Distance Squared (a^2 + b^2 = c^2). 
            # We use max(1, ...) so we never accidentally divide by zero if distance is exactly 0.
            dist_sq = max(1, dx*dx + dy*dy)
            
            # The Inverse-Square Law: Light gets drastically weaker the further away you are.
            intensity += 5000.0 / dist_sq 
            
        # We cap the maximum intensity at 5.0. 
        # If we didn't do this, a vehicle driving straight over a light would calculate
        # a motor speed of 5000 and instantly teleport off the screen!
        return min(intensity, 5.0) 


    def update(self, lights, width, height):
        # This is the "Brain and Body Loop". It runs 60 times a second.
        
        # If it's dead, don't do any math. Just exit the function immediately.
        if not self.alive:
            return

        # --- 1. READ SENSORS ---
        ls, rs = self._sensor_positions()                     # Find out where sensors are
        i_left = self._intensity_at(ls[0], ls[1], lights)     # Measure light at left sensor
        i_right = self._intensity_at(rs[0], rs[1], lights)    # Measure light at right sensor
        
        # Unpack the DNA into readable variables
        w_ll, w_lr, w_rl, w_rr, base_speed = self.weights
        
        # --- 2. THE BRAIN OVERLAY (Calculate Motor Speeds) ---
        # This is Braitenberg's genius logic!
        # Left Motor = Base Speed + (Light on Left * DNA Wire) + (Light on Right * DNA Wire)
        left_motor = base_speed + (w_ll * i_left) + (w_rl * i_right)
        right_motor = base_speed + (w_lr * i_left) + (w_rr * i_right)
        
        # Speed Limits! We cap the motors so they can only go between -4 (reverse) and 4 (forward max)
        left_motor = max(-4, min(4, left_motor))
        right_motor = max(-4, min(4, right_motor))
        
        # --- 3. PHYSICS ENGINE ---
        # The overall forward speed is the average of the two tracks
        forward_speed = (left_motor + right_motor) / 2
        
        # Turning is caused by the difference between the tracks (like a tank!)
        # If right motor is 4 and left is 0, it turns sharply to the left.
        turning_rate = (right_motor - left_motor) / self.radius
        
        # Apply the physics to update the body's actual location
        self.heading += turning_rate
        self.x += forward_speed * math.cos(self.heading)
        self.y += forward_speed * math.sin(self.heading)
        
        # --- 4. METABOLISM & SURVIVAL ---
        self.energy -= 1     # Burn 1 energy per frame just to stay alive
        self.fitness += 1    # Gain 1 point of fitness for surviving another frame
        
        # EATING: Gather energy from lights
        for light in lights:
            # How far are we from this light?
            dist = math.hypot(self.x - light.x, self.y - light.y)
            
            # If the distance is smaller than the vehicle size + light size + 10 pixels...
            if dist < self.radius + light.radius + 10:
                # We are "eating" the light! Recharge our battery.
                self.energy = min(1000, self.energy + 10) # Cap max energy at 1000
                self.fitness += 5 # Big point bonus for finding food
                
        # DEATH CONDITION 1: Hit the edge of the screen ("fall off the table")
        if self.x < 0 or self.x > width or self.y < 0 or self.y > height:
            self.alive = False
            
        # DEATH CONDITION 2: Starvation
        if self.energy <= 0:
            self.alive = False


    def copy_with_mutation(self, x, y, mutation_rate):
        # This function runs when a parent gives birth. 
        # It creates a new child vehicle with slightly modified DNA.
        
        new_weights = []
        for w in self.weights:
            # Flip a coin (50% chance). 
            if random.random() < 0.5: 
                # Heads! A mutation occurs! 
                # We add a tiny random number (between -mutation_rate and +mutation_rate) to the parent's gene
                new_weights.append(w + random.uniform(-mutation_rate, mutation_rate))
            else:
                # Tails! The gene is copied perfectly from the parent with no change.
                new_weights.append(w)
                
        # Create and return the brand new baby Vehicle!
        # It spawns at the provided (x, y) with a random facing angle, and its new mutated DNA.
        return Vehicle(x, y, radius=self.radius, heading=random.uniform(0, math.pi*2), weights=new_weights)


    def draw(self, surface):
        # This function tells Pygame how to paint the vehicle on the monitor.
        
        if not self.alive:
            # Dead vehicles vanish. (We could draw graves here, but we just ignore them!)
            return
            
        # Paint the main body (a solid circle using the genetic color, then a black outline)
        # int() is used because screen pixels must be whole numbers, no decimals allowed!
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x), int(self.y)), self.radius, 2)
        
        # Paint the Sensors (Left is Dark Red, Right is Dark Green)
        ls, rs = self._sensor_positions()
        pygame.draw.circle(surface, (200, 0, 0), (int(ls[0]), int(ls[1])), 4)
        pygame.draw.circle(surface, (0, 200, 0), (int(rs[0]), int(rs[1])), 4)
        
        # Paint a small black line pointing forward so the user can see which way it's looking
        hx = self.x + math.cos(self.heading) * self.radius
        hy = self.y + math.sin(self.heading) * self.radius
        pygame.draw.line(surface, (0, 0, 0), (int(self.x), int(self.y)), (int(hx), int(hy)), 2)