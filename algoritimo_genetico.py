import random
import pygame
import json
import time
import math
import matplotlib
matplotlib.use('Agg')  # Backend não-interativo (funciona sem tkinter)
import matplotlib.pyplot as plt
from collections import deque
    
# Define as cores (tema escuro)
BLACK = (15, 15, 25)
WHITE = (40, 40, 50)
GREEN = (0, 180, 80)
YELLOW = (255, 200, 0)
RED = (220, 50, 50)
BLUE = (50, 100, 200)
PURPLE = (150, 50, 200)
DARK_GRAY = (30, 30, 40)
MATRIX = []
# Define o tamanho do bloco e da margem
BLOCK_SIZE = 12
MARGIN = 1
HEADER = 80
# define o tamanho do tabuleiro
WIDTH = 65
HEIGHT = 85
# define a posição inicial da partícula
START_POS = (0, 0)
# define a posição final da partícula
END_POS = (HEIGHT, WIDTH)
# define o tamanho da população
POPULATION_SIZE = 100
# define o número de gerações
NUM_GENERATIONS = 10000
# define a taxa de mutação
MUTATION_RATE = 0.1
# define a taxa de elitismo (melhores que passam direto)
ELITISM_RATE = 0.1
# taxa de crossover
CROSSOVER_RATE = 0.7
# taxa de imigração (novos indivíduos aleatórios por geração)
IMMIGRATION_RATE = 0.1
# gerações sem melhoria para aumentar mutação
STAGNATION_THRESHOLD = 20
CONTINUAR = True
BEST_FITNESS_EVER = 0
BEST_INDIVIDUAL = None
GERACOES_SEM_MELHORIA = 0
LAST_BEST_FITNESS = 0

# Histórico para gráficos (limitado para performance)
HISTORY_SIZE = 500
history = {
    'geracao': deque(maxlen=HISTORY_SIZE),
    'best_fitness': deque(maxlen=HISTORY_SIZE),
    'avg_fitness': deque(maxlen=HISTORY_SIZE),
    'min_fitness': deque(maxlen=HISTORY_SIZE),
    'diversity': deque(maxlen=HISTORY_SIZE),
    'mutation_rate': deque(maxlen=HISTORY_SIZE),
    'alive_ratio': deque(maxlen=HISTORY_SIZE),
}

# Tamanho do painel de gráficos
GRAPH_WIDTH = 500
GRAPH_HEIGHT = 350

pygame.init()

# Janela maior: tabuleiro + espaço para gráficos
WINDOW_WIDTH = HEIGHT * BLOCK_SIZE + GRAPH_WIDTH + 20
WINDOW_HEIGHT = max(WIDTH * BLOCK_SIZE + HEADER, GRAPH_HEIGHT + 100)
SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
TEXT = pygame.font.SysFont(None, 28)
TEXT_SMALL = pygame.font.SysFont(None, 22)
pygame.display.set_caption("Algoritmo Genetico - Celulas Automatas")
SCREEN.fill(BLACK)

def read_MATRIX(filename):
    global MATRIX, WIDTH, HEIGHT
    matrix_file = open(filename, "r")
    matrix_list = matrix_file.readlines()
    matrix_file.close()
    for row in matrix_list:
        MATRIX.append(list(map(int, row.split())))
    WIDTH = len(MATRIX)
    HEIGHT = len(MATRIX[0])

def create_individual(biased=False):
    """
    Cria um indivíduo com histórico de movimentos.
    
    Args:
        biased: Se True, cria movimentos com tendência para o objetivo (D e R)
    """
    global WIDTH, HEIGHT
    
    # Tamanho do gene: ~3x o caminho mínimo (permite desvios de obstáculos)
    gene_size = 3 * (WIDTH + HEIGHT)
    
    direcoes = []
    
    if biased:
        # Movimentos com viés para o objetivo (mais D e R)
        # O objetivo está em (HEIGHT-1, WIDTH-1), então precisamos ir para baixo (D) e direita (R)
        weighted_choices = ['D', 'D', 'D', 'R', 'R', 'R', 'U', 'L']  # 3/8 D, 3/8 R, 1/8 U, 1/8 L
        for i in range(gene_size):
            direcoes.append(random.choice(weighted_choices))
    else:
        # Movimentos aleatórios uniformes
        for i in range(gene_size):
            direcoes.append(random.choice(['U', 'D', 'R', 'L']))

    distancia = abs(WIDTH - 0) + abs(HEIGHT - 0)
    individuo = {
        'direcao': {'x': 0, 'y': 0},
        'posicao_matrix': {'x': 0, 'y': 0},
        'passos': 0,
        'proxima_direcao': '',
        'distancia': distancia,
        'vivo': True,
        'fitness': 0,
        'colidiu': False,
        'historico_movimento': direcoes,
        'cor': (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    }
    return individuo

def create_population():
    """
    Cria população inicial com diversidade:
    - 30% com viés para o objetivo (indivíduos "espertos")
    - 70% aleatórios (diversidade genética)
    """
    population = []
    num_biased = int(POPULATION_SIZE * 0.3)  # 30% com viés
    
    # Cria indivíduos com viés (tendem a ir para o objetivo)
    for i in range(num_biased):
        individual = create_individual(biased=True)
        population.append(individual)
    
    # Cria indivíduos aleatórios (diversidade)
    for i in range(POPULATION_SIZE - num_biased):
        individual = create_individual(biased=False)
        population.append(individual)
    
    # Embaralha para misturar
    random.shuffle(population)
    return population


def draw_board(matrix,population):
    global WIDTH, HEIGHT, BLOCK_SIZE, MARGIN
    

    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            cell_color = None
            if i == 0 and j == 0 or i == WIDTH - 1 and j == HEIGHT - 1:
                cell_color = YELLOW
            elif matrix[i][j] == 0:
                cell_color = WHITE
            elif matrix[i][j] == 1:
                cell_color = GREEN
            pygame.draw.rect(SCREEN, cell_color, [j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE], 0)
            pygame.draw.rect(SCREEN, BLACK, [j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE], MARGIN)

    for individuo in population:
        if individuo['vivo'] == True:
            # Atualizar outras informações do indivíduo aqui
            pygame.draw.rect(SCREEN,individuo['cor'], [individuo['posicao_matrix']['x'] * BLOCK_SIZE, individuo['posicao_matrix']['y'] * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE], 0)
            pygame.draw.rect(SCREEN, BLACK, [individuo['posicao_matrix']['x'] * BLOCK_SIZE, individuo['posicao_matrix']['y'] * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE], MARGIN)

    pygame.display.flip()

     
def propagar(grid):
    # Copia a grade original para evitar alterar a grade original durante a propagação
    new_grid = [[cell for cell in row] for row in grid]
    
    # Define os limites da grade
    rows = len(grid)
    cols = len(grid[0])
    
    # Cria uma lista para armazenar as células a serem atualizadas
    to_update = []
    
    # Percorre a grade
    for i in range(rows):
        for j in range(cols):
            green_neighbors = 0
            
            # Verifica as células adjacentes
            for x in range(-1, 2):
                for y in range(-1, 2):
                    if x == 0 and y == 0:
                        continue
                    if i+x < 0 or i+x >= rows or j+y < 0 or j+y >= cols:
                        continue
                    if grid[i+x][j+y] == 1:
                        green_neighbors += 1
            
            # Regra para células brancas
            if grid[i][j] == 0 and green_neighbors > 1 and green_neighbors < 5:
                to_update.append((i, j, 1))
            
            # Regra para células verdes
            if grid[i][j] == 1 and (green_neighbors < 4 or green_neighbors > 5):
                to_update.append((i, j, 0))
    
    # Atualiza as células na nova grade
    for i, j, val in to_update:
        new_grid[i][j] = val
    
    # Retorna a nova grade atualizada
    return new_grid



def direcao(individuo):
    passos = individuo['passos']
    historico = individuo['historico_movimento']
    
    # Verifica se ainda há movimentos no histórico
    if passos >= len(historico):
        escolha = individuo['proxima_direcao'] if individuo['proxima_direcao'] else random.choice(['U', 'D', 'R', 'L'])
    else:
        escolha = historico[passos]

    x, y = 0, 0

    if escolha == 'U':
        y -= 1
    elif escolha == 'D':
        y += 1
    elif escolha == 'R':
        x += 1
    elif escolha == 'L':
        x -= 1
    
    # Define próxima direção de forma segura
    if passos + 1 < len(historico):
        individuo['proxima_direcao'] = historico[passos + 1]
    else:
        individuo['proxima_direcao'] = random.choice(['U', 'D', 'R', 'L'])
        
    individuo['direcao'] = {'x': x, 'y': y}
    return individuo


# Função para pegar o ângulo entre dois pontos
def get_angle(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    angulo = math.atan2(dy, dx) * 180 / math.pi
    # Calcula a distância entre o ponto atual e o alvo
    distance = math.sqrt(dx**2 + dy**2)
    
    # Calcula a diferença de ângulo entre o ponto atual e o alvo
    target_angle = math.atan2(dy, dx)
    return abs(target_angle - angulo), distance
     
def movimentar(matrix,individuo):
    individuo = direcao(individuo)
    new_pos = [individuo['posicao_matrix']['x'] + individuo['direcao']['x'], individuo['posicao_matrix']['y'] + individuo['direcao']['y']]
    if new_pos[0] < 0 or new_pos[0] >= len(matrix[0]) or new_pos[1] < 0 or new_pos[1] >= len(matrix):
        individuo['vivo'] = False
        individuo['colidiu'] = True
    elif matrix[new_pos[1]][new_pos[0]] == 1:
        individuo['vivo'] = False
    elif matrix[new_pos[1]][new_pos[0]] == 4:
        # salva em um arquivo o histórico de movimentos do indivíduo
        with open('historico.txt', 'a') as f:
            historico = ' '.join(individuo['historico_movimento'])
            f.write(str(historico))
        
        CONTINUAR = False
    
    else:
        individuo['passos'] += 1

    individuo['posicao_matrix']['x'] = new_pos[0]
    individuo['posicao_matrix']['y'] = new_pos[1]
    
    return individuo
 

def mutation(individuo):
     
    global MUTATION_RATE
    individuo['historico_movimento'][individuo['passos']-10] = random.choice(['U', 'D', 'R', 'L'])
    return individuo 

def fitness_function(individuo):
    global END_POS, WIDTH, HEIGHT
    
    # Calcula distância Manhattan até o objetivo
    dist_x = abs(END_POS[0] - individuo['posicao_matrix']['x'])
    dist_y = abs(END_POS[1] - individuo['posicao_matrix']['y'])
    distancia_manhattan = dist_x + dist_y
    
    # Calcula distância euclidiana
    distancia_euclidiana = math.sqrt(dist_x**2 + dist_y**2)
    
    # Distância máxima possível (para normalizar)
    max_distancia = math.sqrt(WIDTH**2 + HEIGHT**2)
    
    # Normaliza a distância (0 = longe, 1 = perto)
    distancia_normalizada = 1 - (distancia_euclidiana / max_distancia)
    
    # Bônus por estar mais próximo do objetivo
    bonus_proximidade = distancia_normalizada ** 2 * 100
    
    # Bônus por sobreviver mais tempo
    bonus_sobrevivencia = min(individuo['passos'] / 50, 1) * 20
    
    # Penalidade por colidir com parede (fora do mapa)
    penalidade_colisao = 50 if individuo['colidiu'] else 0
    
    # Penalidade por morrer muito cedo
    penalidade_morte_precoce = 30 if individuo['passos'] < 10 else 0
    
    # Bônus extra se chegou muito perto
    bonus_chegada = 0
    if distancia_manhattan < 5:
        bonus_chegada = (5 - distancia_manhattan) * 50
    
    fitness = bonus_proximidade + bonus_sobrevivencia + bonus_chegada - penalidade_colisao - penalidade_morte_precoce
    
    individuo['distancia'] = distancia_euclidiana
    individuo['fitness'] = max(fitness, 0.01)  # Evita fitness zero ou negativo
    
    return individuo['fitness']

def tournament_selection(population, pai=None, tournament_size=5):
    """Seleção por torneio: escolhe os melhores de um subconjunto aleatório"""
    # Filtra população válida
    filtered_population = [ind for ind in population if ind['passos'] > 3 and ind != pai]
    
    if len(filtered_population) < tournament_size:
        filtered_population = [ind for ind in population if ind != pai]
    
    if not filtered_population:
        return random.choice(population)
    
    # Seleciona candidatos aleatórios para o torneio
    tournament_size = min(tournament_size, len(filtered_population))
    candidatos = random.sample(filtered_population, tournament_size)
    
    # Retorna o melhor candidato (maior fitness)
    vencedor = max(candidatos, key=lambda x: x['fitness'])
    return vencedor


def roulette_selection(population, pai=None):
    """Seleção por roleta: probabilidade proporcional ao fitness"""
    filtered_population = [ind for ind in population if ind != pai and ind['fitness'] > 0]
    
    if not filtered_population:
        return random.choice(population)
    
    total_fitness = sum(ind['fitness'] for ind in filtered_population)
    
    if total_fitness == 0:
        return random.choice(filtered_population)
    
    pick = random.uniform(0, total_fitness)
    current = 0
    
    for ind in filtered_population:
        current += ind['fitness']
        if current >= pick:
            return ind
    
    return filtered_population[-1]
     

def uniform_crossover(pai, mae):
    """Crossover uniforme melhorado com mutação adaptativa"""
    filho1 = create_individual()
    filho2 = create_individual()
    
    # Herda os melhores genes dos pais
    for i in range(len(pai['historico_movimento'])):
        if random.random() < 0.5:
            filho1['historico_movimento'][i] = pai['historico_movimento'][i]
            filho2['historico_movimento'][i] = mae['historico_movimento'][i]
        else:
            filho1['historico_movimento'][i] = mae['historico_movimento'][i]
            filho2['historico_movimento'][i] = pai['historico_movimento'][i]
    
    # Aplica mutação nos filhos
    if random.random() < MUTATION_RATE:
        filho1 = apply_mutation(filho1)
    if random.random() < MUTATION_RATE:
        filho2 = apply_mutation(filho2)
    
    return filho1, filho2


def two_point_crossover(pai, mae):
    """Crossover de dois pontos"""
    filho1 = create_individual()
    filho2 = create_individual()
    
    size = len(pai['historico_movimento'])
    ponto1 = random.randint(0, size // 2)
    ponto2 = random.randint(size // 2, size - 1)
    
    for i in range(size):
        if ponto1 <= i <= ponto2:
            filho1['historico_movimento'][i] = mae['historico_movimento'][i]
            filho2['historico_movimento'][i] = pai['historico_movimento'][i]
        else:
            filho1['historico_movimento'][i] = pai['historico_movimento'][i]
            filho2['historico_movimento'][i] = mae['historico_movimento'][i]
    
    # Aplica mutação
    if random.random() < MUTATION_RATE:
        filho1 = apply_mutation(filho1)
    if random.random() < MUTATION_RATE:
        filho2 = apply_mutation(filho2)
    
    return filho1, filho2


def calculate_diversity(population):
    """
    Calcula a diversidade genética da população.
    Retorna um valor entre 0 (todos iguais) e 1 (todos diferentes).
    """
    if len(population) < 2:
        return 1.0
    
    # Amostra alguns pares para comparar (para performance)
    sample_size = min(20, len(population))
    sample = random.sample(population, sample_size)
    
    total_diff = 0
    comparisons = 0
    
    for i in range(len(sample)):
        for j in range(i + 1, len(sample)):
            hist1 = sample[i]['historico_movimento']
            hist2 = sample[j]['historico_movimento']
            # Conta quantos genes são diferentes
            min_len = min(len(hist1), len(hist2))
            diff = sum(1 for k in range(min_len) if hist1[k] != hist2[k])
            total_diff += diff / min_len
            comparisons += 1
    
    return total_diff / comparisons if comparisons > 0 else 1.0


def get_adaptive_mutation_rate(base_rate, diversity, stagnation):
    """
    Ajusta a taxa de mutação baseado na diversidade e estagnação.
    Baixa diversidade ou estagnação = mais mutação.
    """
    # Aumenta mutação se diversidade baixa
    diversity_factor = 1.0 + (1.0 - diversity) * 2  # 1x a 3x
    
    # Aumenta mutação se estagnado
    stagnation_factor = 1.0 + (stagnation / STAGNATION_THRESHOLD) * 2  # até 3x
    
    new_rate = base_rate * diversity_factor * stagnation_factor
    return min(new_rate, 0.5)  # Limita a 50%


def apply_mutation(individuo, mutation_rate=None):
    """Aplica diferentes tipos de mutação"""
    if mutation_rate is None:
        mutation_rate = MUTATION_RATE
    
    mutation_type = random.choice(['swap', 'inversion', 'random', 'scramble'])
    
    if mutation_type == 'swap':
        # Troca duas posições
        a = random.randint(0, len(individuo['historico_movimento']) - 1)
        b = random.randint(0, len(individuo['historico_movimento']) - 1)
        individuo['historico_movimento'][a], individuo['historico_movimento'][b] = \
            individuo['historico_movimento'][b], individuo['historico_movimento'][a]
    
    elif mutation_type == 'inversion':
        individuo = inversion_mutation(individuo)
    
    elif mutation_type == 'random':
        # Muda algumas posições aleatoriamente
        num_changes = random.randint(1, 5)
        for _ in range(num_changes):
            pos = random.randint(0, len(individuo['historico_movimento']) - 1)
            individuo['historico_movimento'][pos] = random.choice(['U', 'D', 'R', 'L'])
    
    elif mutation_type == 'scramble':
        # Embaralha uma seção
        a = random.randint(0, len(individuo['historico_movimento']) - 5)
        b = min(a + random.randint(2, 5), len(individuo['historico_movimento']))
        section = individuo['historico_movimento'][a:b]
        random.shuffle(section)
        individuo['historico_movimento'][a:b] = section
    
    return individuo

def inversion_mutation(individuo):
    global MUTATION_RATE
    a = random.randint(0, len(individuo['historico_movimento'])-1)
    b = random.randint(a+1, len(individuo['historico_movimento']))
    individuo['historico_movimento'][a:b] = reversed(individuo['historico_movimento'][a:b])
    return individuo


def setup_plots():
    """Configura os gráficos (salva em arquivo PNG)"""
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), dpi=100)
    fig.suptitle('Evolucao do Algoritmo Genetico', fontsize=14, fontweight='bold', color='white')
    
    # Configura cores escuras
    fig.patch.set_facecolor('#1a1a2e')
    for ax in axes.flat:
        ax.set_facecolor('#16213e')
        ax.tick_params(colors='white')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.title.set_color('white')
        for spine in ax.spines.values():
            spine.set_color('#404040')
    
    plt.tight_layout()
    return fig, axes


def update_plots(fig, axes):
    """Atualiza os gráficos e salva em arquivo PNG"""
    if len(history['geracao']) < 2:
        return
    
    geracoes = list(history['geracao'])
    
    # Gráfico 1: Fitness (Best, Média, Mínimo)
    ax1 = axes[0, 0]
    ax1.clear()
    ax1.set_facecolor('#16213e')
    ax1.plot(geracoes, list(history['best_fitness']), 'g-', linewidth=2, label='Melhor')
    ax1.plot(geracoes, list(history['avg_fitness']), 'y-', linewidth=1.5, label='Media')
    ax1.plot(geracoes, list(history['min_fitness']), 'r-', linewidth=1, alpha=0.5, label='Minimo')
    ax1.fill_between(geracoes, list(history['min_fitness']), list(history['best_fitness']), 
                     alpha=0.2, color='cyan')
    ax1.set_xlabel('Geracao')
    ax1.set_ylabel('Fitness')
    ax1.set_title('Evolucao do Fitness')
    ax1.legend(loc='upper left', facecolor='#16213e', labelcolor='white')
    ax1.grid(True, alpha=0.3, color='gray')
    
    # Gráfico 2: Diversidade Genética
    ax2 = axes[0, 1]
    ax2.clear()
    ax2.set_facecolor('#16213e')
    diversity_data = list(history['diversity'])
    colors = ['#ff6b6b' if d < 0.3 else '#ffd93d' if d < 0.5 else '#6bcb77' for d in diversity_data]
    ax2.bar(geracoes, diversity_data, color=colors, alpha=0.7, width=1.0)
    ax2.axhline(y=0.3, color='red', linestyle='--', alpha=0.7, label='Baixa')
    ax2.axhline(y=0.5, color='yellow', linestyle='--', alpha=0.7, label='Media')
    ax2.set_xlabel('Geracao')
    ax2.set_ylabel('Diversidade')
    ax2.set_title('Diversidade Genetica')
    ax2.set_ylim(0, 1)
    ax2.legend(loc='upper right', facecolor='#16213e', labelcolor='white', fontsize=8)
    ax2.grid(True, alpha=0.3, color='gray')
    
    # Gráfico 3: Taxa de Mutação Adaptativa
    ax3 = axes[1, 0]
    ax3.clear()
    ax3.set_facecolor('#16213e')
    ax3.plot(geracoes, list(history['mutation_rate']), 'm-', linewidth=2)
    ax3.fill_between(geracoes, 0, list(history['mutation_rate']), alpha=0.3, color='magenta')
    ax3.axhline(y=MUTATION_RATE, color='white', linestyle='--', alpha=0.5, label=f'Base ({MUTATION_RATE})')
    ax3.set_xlabel('Geracao')
    ax3.set_ylabel('Taxa de Mutacao')
    ax3.set_title('Mutacao Adaptativa')
    ax3.set_ylim(0, 0.6)
    ax3.legend(loc='upper right', facecolor='#16213e', labelcolor='white')
    ax3.grid(True, alpha=0.3, color='gray')
    
    # Gráfico 4: Taxa de Sobrevivência
    ax4 = axes[1, 1]
    ax4.clear()
    ax4.set_facecolor('#16213e')
    alive_data = [r * 100 for r in history['alive_ratio']]
    ax4.plot(geracoes, alive_data, 'c-', linewidth=2)
    ax4.fill_between(geracoes, 0, alive_data, alpha=0.3, color='cyan')
    ax4.set_xlabel('Geracao')
    ax4.set_ylabel('Sobrevivencia (%)')
    ax4.set_title('Tempo de Sobrevivencia')
    ax4.set_ylim(0, 100)
    ax4.grid(True, alpha=0.3, color='gray')
    
    # Atualiza estilos
    for ax in axes.flat:
        ax.tick_params(colors='white')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.title.set_color('white')
    
    plt.tight_layout()
    
    # Salva em arquivo PNG
    fig.savefig('grafico_evolucao.png', facecolor='#1a1a2e', edgecolor='none')


def load_graph_surface():
    """Carrega o gráfico PNG como superfície do pygame"""
    try:
        return pygame.image.load('grafico_evolucao.png')
    except:
        return None

            
def run():
    global CONTINUAR, BEST_FITNESS_EVER, BEST_INDIVIDUAL, GERACOES_SEM_MELHORIA, LAST_BEST_FITNESS
    global SCREEN, TEXT, MATRIX, WHITE, BLACK, POPULATION_SIZE, NUM_GENERATIONS, MUTATION_RATE, END_POS, WIDTH, HEIGHT, BLOCK_SIZE, MARGIN, ELITISM_RATE
    
    read_MATRIX('matrix.txt')
    population = create_population()
    END_POS = (HEIGHT - 1, WIDTH - 1)  # Atualiza posição final baseada na matriz
    
    # Configura gráficos
    fig, axes = setup_plots()
    
    clock = pygame.time.Clock()
    running = True
    geracao = 0
    
    while running and geracao < NUM_GENERATIONS:
        # Processa eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                return
        
        # Reset da matriz para cada geração
        matrix = [row[:] for row in MATRIX]
        
        # Cria nova população se necessário
        nova_populacao = population
        
        # Simula a geração atual
        qtd_vivos = len([ind for ind in nova_populacao if ind['vivo']])
        iteracao = 0
        max_iteracoes = WIDTH * HEIGHT  # Limite de iterações
        
        while qtd_vivos > 0 and iteracao < max_iteracoes:
            # Propaga o autômato celular
            if iteracao > 0:
                matrix = propagar(matrix)
            
            # Move cada indivíduo vivo
            for index, individuo in enumerate(nova_populacao):
                if individuo['vivo']:
                    nova_populacao[index] = movimentar(matrix, individuo)
                    if not nova_populacao[index]['vivo']:
                        nova_populacao[index]['fitness'] = fitness_function(nova_populacao[index])
                        qtd_vivos -= 1
            
            # Atualiza tela
            SCREEN.fill(BLACK)
            
            # Encontra melhor fitness da geração
            fitness_atual = max((ind['fitness'] for ind in nova_populacao), default=0)
            if fitness_atual > BEST_FITNESS_EVER:
                BEST_FITNESS_EVER = fitness_atual
                BEST_INDIVIDUAL = max(nova_populacao, key=lambda x: x['fitness'])
            
            # Desenha informações no header (abaixo do tabuleiro)
            info_y = WIDTH * BLOCK_SIZE + 10
            SCREEN.blit(TEXT.render(f'Geracao: {geracao}', True, YELLOW), (10, info_y))
            SCREEN.blit(TEXT.render(f'Iter: {iteracao}', True, WHITE), (150, info_y))
            SCREEN.blit(TEXT.render(f'Vivos: {qtd_vivos}', True, GREEN if qtd_vivos > 10 else RED), (270, info_y))
            SCREEN.blit(TEXT.render(f'Best: {BEST_FITNESS_EVER:.2f}', True, PURPLE), (400, info_y))
            
            # Segunda linha de info
            info_y2 = info_y + 30
            if len(history['diversity']) > 0:
                last_div = history['diversity'][-1] if history['diversity'] else 0
                last_mut = history['mutation_rate'][-1] if history['mutation_rate'] else MUTATION_RATE
                div_color = GREEN if last_div > 0.5 else YELLOW if last_div > 0.3 else RED
                SCREEN.blit(TEXT_SMALL.render(f'Diversidade: {last_div:.2f}', True, div_color), (10, info_y2))
                SCREEN.blit(TEXT_SMALL.render(f'Mutacao: {last_mut:.2f}', True, PURPLE), (180, info_y2))
                SCREEN.blit(TEXT_SMALL.render(f'Estagnacao: {GERACOES_SEM_MELHORIA}', True, RED if GERACOES_SEM_MELHORIA > 10 else WHITE), (330, info_y2))
            
            # Desenha gráfico na lateral direita
            graph_surface = load_graph_surface()
            if graph_surface:
                # Redimensiona para caber
                graph_scaled = pygame.transform.scale(graph_surface, (GRAPH_WIDTH, GRAPH_HEIGHT))
                SCREEN.blit(graph_scaled, (HEIGHT * BLOCK_SIZE + 10, 10))
            
            draw_board(matrix, nova_populacao)
            clock.tick(60)  # Limita FPS
            iteracao += 1
        
        # Calcula fitness para todos que ainda não calcularam
        for ind in nova_populacao:
            if ind['fitness'] == 0:
                ind['fitness'] = fitness_function(ind)
        
        # === ANÁLISE DE DIVERSIDADE ===
        diversity = calculate_diversity(nova_populacao)
        
        # Detecta estagnação
        current_best = max(ind['fitness'] for ind in nova_populacao)
        if current_best <= LAST_BEST_FITNESS:
            GERACOES_SEM_MELHORIA += 1
        else:
            GERACOES_SEM_MELHORIA = 0
            LAST_BEST_FITNESS = current_best
        
        # Taxa de mutação adaptativa
        current_mutation_rate = get_adaptive_mutation_rate(
            MUTATION_RATE, diversity, GERACOES_SEM_MELHORIA
        )
        
        # === SELEÇÃO E REPRODUÇÃO ===
        
        # Ordena por fitness (maior = melhor)
        nova_populacao = sorted(nova_populacao, key=lambda x: x['fitness'], reverse=True)
        
        # Elitismo: preserva os melhores
        num_elite = max(2, int(POPULATION_SIZE * ELITISM_RATE))
        new_population = []
        
        # Adiciona elite (recria indivíduos com mesmo histórico)
        for i in range(num_elite):
            elite_clone = create_individual()
            elite_clone['historico_movimento'] = nova_populacao[i]['historico_movimento'][:]
            new_population.append(elite_clone)
        
        # === IMIGRAÇÃO: adiciona indivíduos novos aleatórios ===
        num_immigrants = int(POPULATION_SIZE * IMMIGRATION_RATE)
        
        # Se estagnado, aumenta imigração
        if GERACOES_SEM_MELHORIA > STAGNATION_THRESHOLD:
            num_immigrants = int(POPULATION_SIZE * 0.3)  # 30% de novos
            print(f"⚠️ Estagnação detectada! Injetando {num_immigrants} novos indivíduos...")
            GERACOES_SEM_MELHORIA = 0  # Reset
        
        for _ in range(num_immigrants):
            # Alterna entre aleatório e com viés
            new_population.append(create_individual(biased=random.random() < 0.5))
        
        # Gera o resto da população por crossover
        while len(new_population) < POPULATION_SIZE:
            # Seleciona pais usando torneio ou roleta
            if random.random() < 0.7:
                pai = tournament_selection(nova_populacao)
                mae = tournament_selection(nova_populacao, pai)
            else:
                pai = roulette_selection(nova_populacao)
                mae = roulette_selection(nova_populacao, pai)
            
            # Crossover
            if random.random() < CROSSOVER_RATE:
                if random.random() < 0.5:
                    filho1, filho2 = uniform_crossover(pai, mae)
                else:
                    filho1, filho2 = two_point_crossover(pai, mae)
            else:
                filho1 = create_individual()
                filho1['historico_movimento'] = pai['historico_movimento'][:]
                filho2 = create_individual()
                filho2['historico_movimento'] = mae['historico_movimento'][:]
            
            # Aplica mutação com taxa adaptativa
            if random.random() < current_mutation_rate:
                filho1 = apply_mutation(filho1, current_mutation_rate)
            if random.random() < current_mutation_rate:
                filho2 = apply_mutation(filho2, current_mutation_rate)
            
            new_population.append(filho1)
            if len(new_population) < POPULATION_SIZE:
                new_population.append(filho2)
        
        population = new_population
        geracao += 1
        
        # === COLETA DE MÉTRICAS PARA GRÁFICOS ===
        all_fitness = [ind['fitness'] for ind in nova_populacao]
        avg_fitness = sum(all_fitness) / len(all_fitness) if all_fitness else 0
        min_fitness = min(all_fitness) if all_fitness else 0
        
        # Calcula taxa de sobrevivência média (baseado em passos dados)
        max_passos = 3 * (WIDTH + HEIGHT)  # tamanho do gene
        avg_passos = sum(ind['passos'] for ind in nova_populacao) / len(nova_populacao)
        alive_ratio = avg_passos / max_passos
        
        # Salva no histórico
        history['geracao'].append(geracao)
        history['best_fitness'].append(BEST_FITNESS_EVER)
        history['avg_fitness'].append(avg_fitness)
        history['min_fitness'].append(min_fitness)
        history['diversity'].append(diversity)
        history['mutation_rate'].append(current_mutation_rate)
        history['alive_ratio'].append(alive_ratio)
        
        # Atualiza gráficos a cada 5 gerações
        if geracao % 5 == 0:
            try:
                update_plots(fig, axes)
            except Exception as e:
                print(f"Erro ao atualizar gráfico: {e}")
        
        # Log de progresso
        if geracao % 10 == 0:
            print(f"Geracao {geracao}: Best={BEST_FITNESS_EVER:.2f} | Avg={avg_fitness:.2f} | Div={diversity:.2f} | Mut={current_mutation_rate:.2f}")
    
    # Finalização
    print("\n Evolucao concluida!")
    print(f"Melhor fitness alcancado: {BEST_FITNESS_EVER:.4f}")
    print("Grafico salvo em: grafico_evolucao.png")
                
        
if __name__ == '__main__':
    run()