# entities/light.py

# --- IMPORTS ---
# We bring in the pygame library because we need its drawing tools to paint 
# the light bulb onto the screen.
import pygame

class Light:
    # A 'class' is like a cookie cutter or a blueprint. 
    # It doesn't create a light right away, but it tells Python EXACTLY how 
    # to build one whenever we ask for it in our main.py file.
    
    def __init__(self, x, y, radius=15):
        # The __init__ function is the "constructor". It runs automatically 
        # the exact millisecond a new Light is created.
        # Think of 'self' as the specific light bulb we are currently building.
        
        # We store the starting X and Y coordinates so the light remembers where it is.
        self.x = x
        self.y = y
        
        # We store how big the light is. 
        # Notice we said 'radius=15' up top. That makes 15 the "default" size.
        # If we create a Light without telling it a size, it will automatically be 15.
        self.radius = radius

    def move(self, new_position):
        # This is a custom action (called a 'method') that the light can perform.
        # We use this when the user clicks the mouse to drag the light around.
        
        # 'new_position' is expected to be a bundle (a tuple) of two numbers: (X, Y).
        # Python is smart enough to unpack that bundle and assign the first number 
        # to self.x and the second number to self.y all in one line!
        self.x, self.y = new_position

    @property
    def pos(self):
        # This is a cool Python trick! The '@property' is called a "decorator".
        # Normally, to run a function, you have to use parentheses, like: light.pos()
        # By adding @property, Python lets us treat this function like a regular variable.
        # We can just type 'light.pos' without parentheses, making our code look cleaner.
        
        # It returns the current X and Y coordinates bundled together in a tuple.
        return (self.x, self.y)

    def draw(self, surface):
        # This function tells Pygame exactly how to paint this light onto the monitor.
        # 'surface' is the screen (or piece of digital paper) we are drawing on.
        
        # --- Draw the glowing yellow center ---
        # 1. 'surface' -> Where to draw it
        # 2. (255, 220, 0) -> What color? This is an RGB code for a bright, warm Yellow.
        # 3. (int(self.x), int(self.y)) -> Where to put it? We use int() because screen pixels must be whole numbers.
        # 4. self.radius -> How big to draw it.
        pygame.draw.circle(surface, (255, 220, 0), (int(self.x), int(self.y)), self.radius)
        
        # --- Draw a black outline (so it pops out from the background) ---
        # The arguments are exactly the same as above, but with two changes:
        # 1. Color is (0, 0, 0) which is pure Black.
        # 2. We add a '2' at the very end. This tells Pygame NOT to fill the circle in solid,
        #    but instead to just draw a border outline that is exactly 2 pixels thick.
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x), int(self.y)), self.radius, 2)