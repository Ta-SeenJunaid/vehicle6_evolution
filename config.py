# config.py

# ==========================================
# 1. WORLD SETTINGS (The Environment)
# ==========================================

# These dictate the size of the digital window that opens on your screen.
# 800 pixels wide by 600 pixels tall is a standard, classic window size.
WIDTH = 800
HEIGHT = 600

# FPS stands for "Frames Per Second". 
# This is the speed limit of your universe. 
# At 60 FPS, the simulation calculates physics and redraws the screen 60 times every single second.
# If you change this to 10, the vehicles will look choppy and move in slow motion.
# If you change it to 120 (and your computer is fast enough), evolution will happen twice as fast!
FPS = 60


# ==========================================
# 2. EVOLUTIONARY PARAMETERS (The Biology)
# ==========================================

# How many vehicles are allowed to exist at the exact same time?
# If you set this to 100, the swarm will be massive, but older computers might lag.
# If you set this to 5, evolution will happen very slowly because there is less genetic diversity.
POPULATION_SIZE = 30

# Mutation is the engine of evolution! 
# When a parent copies its DNA to a child, this number dictates how "wild" the random mistakes can be.
# 0.0 = Perfect clones. Evolution completely stops.
# 0.2 = Small, gradual tweaks. (This is generally best for smooth evolution).
# 5.0 = Massive, crazy mutations. Children will act completely different from their parents.
MUTATION_RATE = 0.2     

# Think of this as the size of the vehicle's gas tank or stomach.
# Since they burn 1 energy per frame, at 60 FPS, a vehicle with 500 starting energy 
# will starve to death in exactly 8.3 seconds if it doesn't find a light source.
# If you make this number smaller, the vehicles have to find light MUCH faster or they die.
STARTING_ENERGY = 500