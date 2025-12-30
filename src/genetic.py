"""
Algoritmo Genético - Indivíduos, População, Seleção, Crossover e Mutação
"""
import random
import math
from collections import defaultdict
from .config import *


def create_individual(width, height, biased=False):
    """
    Cria um indivíduo com:
    - Histórico de movimentos (genes)
    - Tabela de aprendizado (mapeia estados locais para preferências de direção)
    """
    gene_size = 3 * (width + height)
    
    if biased:
        # Movimentos com viés para o objetivo (D e R)
        weighted = ['D', 'D', 'D', 'R', 'R', 'R', 'U', 'L']
        direcoes = [random.choice(weighted) for _ in range(gene_size)]
    else:
        direcoes = [random.choice(['U', 'D', 'R', 'L']) for _ in range(gene_size)]
    
    return {
        'posicao': {'x': 0, 'y': 0},
        'passos': 0,
        'distancia': width + height,
        'max_progresso': 0,  # Máximo progresso em direção ao objetivo
        'vivo': True,
        'fitness': 0,
        'colidiu': False,
        'historico_movimento': direcoes,
        'aprendizado': defaultdict(lambda: {'U': 0, 'D': 0, 'R': 0, 'L': 0}),
        'cor': (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255)),
        'caminho': [],  # Histórico de posições visitadas
    }


def create_population(width, height, size=POPULATION_SIZE):
    """Cria população inicial com diversidade"""
    population = []
    num_biased = int(size * 0.3)
    
    for i in range(num_biased):
        population.append(create_individual(width, height, biased=True))
    
    for i in range(size - num_biased):
        population.append(create_individual(width, height, biased=False))
    
    random.shuffle(population)
    return population


def get_direction_from_learning(individuo, state, matrix, x, y, end_pos):
    """
    Escolhe direção baseado no aprendizado + heurística.
    O indivíduo aprende quais direções funcionam melhor em cada estado local.
    """
    passos = individuo['passos']
    hist = individuo['historico_movimento']
    
    # Se ainda tem movimentos no gene, usa com probabilidade
    if passos < len(hist):
        gene_move = hist[passos]
        
        # Verifica se o movimento do gene é seguro
        dx, dy = {'U': (0, -1), 'D': (0, 1), 'R': (1, 0), 'L': (-1, 0)}[gene_move]
        new_x, new_y = x + dx, y + dy
        
        rows, cols = len(matrix), len(matrix[0])
        if 0 <= new_x < cols and 0 <= new_y < rows and matrix[new_y][new_x] != 1:
            return gene_move
    
    # Caso contrário, usa heurística gulosa (vai em direção ao objetivo evitando obstáculos)
    moves = []
    for move, (dx, dy) in [('R', (1, 0)), ('D', (0, 1)), ('L', (-1, 0)), ('U', (0, -1))]:
        new_x, new_y = x + dx, y + dy
        rows, cols = len(matrix), len(matrix[0])
        
        if 0 <= new_x < cols and 0 <= new_y < rows and matrix[new_y][new_x] != 1:
            # Calcula distância ao objetivo
            dist = abs(end_pos[0] - new_x) + abs(end_pos[1] - new_y)
            moves.append((move, dist))
    
    if moves:
        # Ordena por distância (menor = melhor) e adiciona aleatoriedade
        moves.sort(key=lambda m: m[1])
        # 70% escolhe o melhor, 30% escolhe aleatório entre os seguros
        if random.random() < 0.7:
            return moves[0][0]
        else:
            return random.choice(moves)[0]
    
    # Se não há movimento seguro, tenta o gene
    if passos < len(hist):
        return hist[passos]
    
    return random.choice(['U', 'D', 'R', 'L'])


def movimentar(matrix, individuo, end_pos):
    """Move o indivíduo e atualiza seu estado"""
    from .cellular import get_local_state
    
    x, y = individuo['posicao']['x'], individuo['posicao']['y']
    
    # Obtém estado local
    state = get_local_state(matrix, x, y)
    
    # Escolhe direção
    direcao = get_direction_from_learning(individuo, state, matrix, x, y, end_pos)
    
    # Calcula nova posição
    dx, dy = {'U': (0, -1), 'D': (0, 1), 'R': (1, 0), 'L': (-1, 0)}[direcao]
    new_x, new_y = x + dx, y + dy
    
    rows, cols = len(matrix), len(matrix[0])
    
    # Verifica colisão
    if new_x < 0 or new_x >= cols or new_y < 0 or new_y >= rows:
        individuo['vivo'] = False
        individuo['colidiu'] = True
        # Aprendizado negativo: evitar essa direção neste estado
        individuo['aprendizado'][state][direcao] -= LEARNING_RATE
    elif matrix[new_y][new_x] == 1:
        individuo['vivo'] = False
        individuo['aprendizado'][state][direcao] -= LEARNING_RATE
    else:
        # Movimento válido
        individuo['posicao']['x'] = new_x
        individuo['posicao']['y'] = new_y
        individuo['passos'] += 1
        individuo['caminho'].append((new_x, new_y))
        
        # Calcula progresso (distância inicial - distância atual)
        dist_atual = abs(end_pos[0] - new_x) + abs(end_pos[1] - new_y)
        progresso = (individuo['distancia'] - dist_atual)
        
        if progresso > individuo['max_progresso']:
            individuo['max_progresso'] = progresso
            # Aprendizado positivo
            individuo['aprendizado'][state][direcao] += LEARNING_RATE
        
        # Chegou ao objetivo?
        if new_x == end_pos[0] and new_y == end_pos[1]:
            individuo['vivo'] = False
            individuo['fitness'] = 1000 + (1000 / individuo['passos'])  # Bônus por chegar rápido
    
    return individuo


def fitness_function(individuo, end_pos, width, height):
    """Calcula fitness baseado em progresso, não apenas distância final"""
    x, y = individuo['posicao']['x'], individuo['posicao']['y']
    
    # Distância ao objetivo
    dist = math.sqrt((end_pos[0] - x)**2 + (end_pos[1] - y)**2)
    max_dist = math.sqrt(width**2 + height**2)
    
    # Normaliza (0 = longe, 1 = perto)
    proximidade = 1 - (dist / max_dist)
    
    # Bônus por progresso máximo alcançado
    progresso = individuo['max_progresso'] / (width + height)
    
    # Bônus por sobrevivência
    sobrevivencia = min(individuo['passos'] / 100, 1)
    
    # Penalidades
    penalidade = 0
    if individuo['colidiu']:
        penalidade += 0.3
    if individuo['passos'] < 5:
        penalidade += 0.2
    
    # Fitness final
    fitness = (proximidade * 50) + (progresso * 30) + (sobrevivencia * 20) - (penalidade * 20)
    
    return max(fitness, 0.1)


def tournament_selection(population, exclude=None, tournament_size=5):
    """Seleção por torneio"""
    candidates = [ind for ind in population if ind != exclude and ind['fitness'] > 0]
    
    if len(candidates) < tournament_size:
        candidates = [ind for ind in population if ind != exclude]
    
    if not candidates:
        return random.choice(population)
    
    tournament = random.sample(candidates, min(tournament_size, len(candidates)))
    return max(tournament, key=lambda x: x['fitness'])


def crossover(pai, mae, width, height):
    """Crossover de dois pontos com herança de aprendizado"""
    filho1 = create_individual(width, height)
    filho2 = create_individual(width, height)
    
    size = len(pai['historico_movimento'])
    
    # Crossover de dois pontos
    p1 = random.randint(0, size // 3)
    p2 = random.randint(2 * size // 3, size - 1)
    
    for i in range(size):
        if p1 <= i <= p2:
            filho1['historico_movimento'][i] = mae['historico_movimento'][i]
            filho2['historico_movimento'][i] = pai['historico_movimento'][i]
        else:
            filho1['historico_movimento'][i] = pai['historico_movimento'][i]
            filho2['historico_movimento'][i] = mae['historico_movimento'][i]
    
    # Herda parte do aprendizado dos pais (Lamarckismo leve)
    for state in pai['aprendizado']:
        for dir in pai['aprendizado'][state]:
            filho1['aprendizado'][state][dir] = pai['aprendizado'][state][dir] * 0.5
    
    for state in mae['aprendizado']:
        for dir in mae['aprendizado'][state]:
            filho2['aprendizado'][state][dir] = mae['aprendizado'][state][dir] * 0.5
    
    return filho1, filho2


def mutate(individuo, rate=MUTATION_RATE):
    """Aplica mutação"""
    mutation_type = random.choice(['swap', 'random', 'scramble', 'insert'])
    hist = individuo['historico_movimento']
    size = len(hist)
    
    if mutation_type == 'swap':
        a, b = random.sample(range(size), 2)
        hist[a], hist[b] = hist[b], hist[a]
    
    elif mutation_type == 'random':
        for _ in range(random.randint(1, 5)):
            pos = random.randint(0, size - 1)
            hist[pos] = random.choice(['U', 'D', 'R', 'L'])
    
    elif mutation_type == 'scramble':
        a = random.randint(0, size - 10)
        b = a + random.randint(3, 10)
        section = hist[a:b]
        random.shuffle(section)
        hist[a:b] = section
    
    elif mutation_type == 'insert':
        # Remove de um lugar e insere em outro
        a = random.randint(0, size - 1)
        gene = hist.pop(a)
        b = random.randint(0, len(hist))
        hist.insert(b, gene)
    
    return individuo


def calculate_diversity(population, sample_size=20):
    """Calcula diversidade genética"""
    if len(population) < 2:
        return 1.0
    
    sample = random.sample(population, min(sample_size, len(population)))
    total_diff = 0
    comparisons = 0
    
    for i in range(len(sample)):
        for j in range(i + 1, len(sample)):
            h1 = sample[i]['historico_movimento']
            h2 = sample[j]['historico_movimento']
            min_len = min(len(h1), len(h2))
            diff = sum(1 for k in range(min_len) if h1[k] != h2[k])
            total_diff += diff / min_len
            comparisons += 1
    
    return total_diff / comparisons if comparisons > 0 else 1.0


def adaptive_mutation_rate(base_rate, diversity, stagnation, threshold=STAGNATION_THRESHOLD):
    """Taxa de mutação adaptativa"""
    diversity_factor = 1.0 + (1.0 - diversity) * 2
    stagnation_factor = 1.0 + (stagnation / threshold) * 2
    
    return min(base_rate * diversity_factor * stagnation_factor, 0.5)
