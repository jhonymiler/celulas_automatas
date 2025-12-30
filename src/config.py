"""
Configurações globais do algoritmo genético e visualização
"""

# === CORES (tema escuro) ===
BLACK = (15, 15, 25)
WHITE = (40, 40, 50)
GRAY = (80, 80, 90)
GREEN = (0, 70, 40)
YELLOW = (255, 200, 0)
RED = (220, 50, 50)
BLUE = (50, 100, 200)
PURPLE = (150, 50, 200)
CYAN = (50, 200, 200)
DARK_GRAY = (30, 30, 40)

# === VISUALIZAÇÃO ===
BLOCK_SIZE = 12
MARGIN = 1
HEADER = 100
GRAPH_WIDTH = 520
GRAPH_HEIGHT = 380

# === ALGORITMO GENÉTICO ===
POPULATION_SIZE = 500
NUM_GENERATIONS = 10000
MUTATION_RATE = 0.01
ELITISM_RATE = 0.1
CROSSOVER_RATE = 0.7
IMMIGRATION_RATE = 0.1
STAGNATION_THRESHOLD = 15

# === APRENDIZADO ===
# Tamanho da "memória" - quantos estados anteriores o indivíduo considera
MEMORY_SIZE = 3
# Peso do aprendizado por reforço
LEARNING_RATE = 0.1
