# entities/vehicle.py
import pygame
import math
import random

class Vehicle:
    def __init__(self, x, y, radius=15, heading=0, weights=None):
        self.x = x
        self.y = y
        self.radius = radius
        self.heading = heading
        
        self.sensor_offset_angle = math.radians(30)
        self.sensor_dist = self.radius + 5
        
        # Genes (Weights): [w_left_to_left, w_left_to_right, w_right_to_left, w_right_to_right, base_speed]
        # Positive weights = excitatory (Love/Aggression), Negative weights = inhibitory (Fear/Exploration)
        if weights is None:
            self.weights = [random.uniform(-2, 2) for _ in range(4)]
            self.weights.append(random.uniform(0.5, 2.0)) # base speed
        else:
            self.weights = weights
            
        # Color reflects genetics so you can visually identify 'species'
        r = max(0, min(255, int(128 + self.weights[0] * 50)))
        g = max(0, min(255, int(128 + self.weights[1] * 50)))
        b = max(0, min(255, int(128 + self.weights[2] * 50)))
        self.color = (r, g, b)

        from config import STARTING_ENERGY
        self.energy = STARTING_ENERGY
        self.fitness = 0
        self.alive = True

    def _sensor_positions(self):
        angle = self.sensor_offset_angle
        cos_h = math.cos(self.heading)
        sin_h = math.sin(self.heading)
        
        left_lx = math.cos(angle) * self.sensor_dist
        left_ly = math.sin(angle) * self.sensor_dist
        right_lx = math.cos(-angle) * self.sensor_dist
        right_ly = math.sin(-angle) * self.sensor_dist
        
        lx = self.x + cos_h * left_lx - sin_h * left_ly
        ly = self.y + sin_h * left_lx + cos_h * left_ly
        rx = self.x + cos_h * right_lx - sin_h * right_ly
        ry = self.y + sin_h * right_lx + cos_h * right_ly
        
        return (lx, ly), (rx, ry)

    def _intensity_at(self, px, py, lights):
        intensity = 0
        for light in lights:
            dx = px - light.x
            dy = py - light.y
            dist_sq = max(1, dx*dx + dy*dy)
            intensity += 5000.0 / dist_sq # Inverse square law
        return min(intensity, 5.0) # Cap intensity to avoid physics glitches

    def update(self, lights, width, height):
        if not self.alive:
            return

        ls, rs = self._sensor_positions()
        i_left = self._intensity_at(ls[0], ls[1], lights)
        i_right = self._intensity_at(rs[0], rs[1], lights)
        
        w_ll, w_lr, w_rl, w_rr, base_speed = self.weights
        
        # Calculate motor speeds applying genetic weights
        left_motor = base_speed + (w_ll * i_left) + (w_rl * i_right)
        right_motor = base_speed + (w_lr * i_left) + (w_rr * i_right)
        
        # Cap max speeds
        left_motor = max(-4, min(4, left_motor))
        right_motor = max(-4, min(4, right_motor))
        
        forward_speed = (left_motor + right_motor) / 2
        turning_rate = (right_motor - left_motor) / self.radius
        
        self.heading += turning_rate
        self.x += forward_speed * math.cos(self.heading)
        self.y += forward_speed * math.sin(self.heading)
        
        # Evolution mechanics
        self.energy -= 1 
        self.fitness += 1 # Living longer increases fitness
        
        # Gather energy from lights
        for light in lights:
            dist = math.hypot(self.x - light.x, self.y - light.y)
            if dist < self.radius + light.radius + 10:
                self.energy = min(1000, self.energy + 10) 
                self.fitness += 5 
                
        # Death Condition 1: Hit the edge ("fall off the table")
        if self.x < 0 or self.x > width or self.y < 0 or self.y > height:
            self.alive = False
            
        # Death Condition 2: Starvation
        if self.energy <= 0:
            self.alive = False

    def copy_with_mutation(self, x, y, mutation_rate):
        new_weights = []
        for w in self.weights:
            if random.random() < 0.5: # 50% chance to mutate a specific gene
                new_weights.append(w + random.uniform(-mutation_rate, mutation_rate))
            else:
                new_weights.append(w)
        return Vehicle(x, y, radius=self.radius, heading=random.uniform(0, math.pi*2), weights=new_weights)

    def draw(self, surface):
        if not self.alive:
            return
        # Body
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x), int(self.y)), self.radius, 2)
        
        # Sensors
        ls, rs = self._sensor_positions()
        pygame.draw.circle(surface, (200, 0, 0), (int(ls[0]), int(ls[1])), 4)
        pygame.draw.circle(surface, (0, 200, 0), (int(rs[0]), int(rs[1])), 4)
        
        # Heading Indicator
        hx = self.x + math.cos(self.heading) * self.radius
        hy = self.y + math.sin(self.heading) * self.radius
        pygame.draw.line(surface, (0, 0, 0), (int(self.x), int(self.y)), (int(hx), int(hy)), 2)