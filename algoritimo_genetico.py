import random
import pygame
import json
import time
import math
    
# Define as cores
BLACK = (50, 50, 50)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
MATRIX = []
# Define o tamanho do bloco e da margem
BLOCK_SIZE = 10
MARGIN = 1
HEADER = 50
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
MUTATION_RATE = 0.05
CONTINUAR = True

pygame.init()

SCREEN = pygame.display.set_mode((HEIGHT * BLOCK_SIZE,  WIDTH * BLOCK_SIZE + HEADER))
TEXT = pygame.font.SysFont(None, 32)
pygame.display.set_caption("Genetic Algorithm")
SCREEN.fill(WHITE)

def read_MATRIX(filename):
    global MATRIX, WIDTH, HEIGHT
    matrix_file = open(filename, "r")
    matrix_list = matrix_file.readlines()
    matrix_file.close()
    for row in matrix_list:
        MATRIX.append(list(map(int, row.split())))
    WIDTH = len(MATRIX)
    HEIGHT = len(MATRIX[0])

def create_individual():
    global WIDTH, HEIGHT

    direcoes = []
    for i in range(WIDTH * HEIGHT):
        direcoes.append(random.choice(['U', 'D', 'R', 'L']))

    distancia = abs(WIDTH - 0) + abs(HEIGHT - 0)
    individuo = {
        'direcao': {'x': 0, 'y': 0},
        'posicao_matrix': {'x': 0, 'y': 0},
        'passos': 0,
        'proxima_direcao':'',
        'distancia': distancia,
        'vivo': True,
        'fitness': 0,
        'colidiu': False,
        'historico_movimento': direcoes,
        'cor': (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    }
    return individuo

def create_population():
    population = []
    for i in range(POPULATION_SIZE):
        individual = create_individual()
        population.append(individual)
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
    
    if len(individuo['historico_movimento']) == individuo['passos']:
        escolha = individuo['proxima_direcao']
    else:
        escolha = individuo['historico_movimento'][individuo['passos']] 

    x,y = 0,0

    if escolha == 'U':
        y -= 1
    elif escolha == 'D':
        y += 1
    elif escolha == 'R':
        x += 1
    elif escolha == 'L':
        x -= 1
        
    individuo['proxima_direcao'] = random.choice(['U', 'D', 'R', 'L']) if individuo['historico_movimento'][individuo['passos']+1] else individuo['historico_movimento'][individuo['passos']+1]
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
    global END_POS
    
    distancia, angulo = get_angle(individuo['posicao_matrix']['x'], individuo['posicao_matrix']['y'], END_POS[0], END_POS[1])
    individuo['distancia'] = distancia
    individuo['angulo'] = angulo

    return 1 / ((distancia + 1) + (angulo / 100) + (individuo['passos']) + (1000 if individuo['passos'] <= 10 else 0) + (10000 if individuo['colidiu']==True else 0)) # Ajuste o número mínimo de passos aqui

def tournament_selection(population, pai):
    filtered_population = [individuo for individuo in population if individuo['passos'] > 5] # Ajuste o número mínimo de passos aqui
    individuo = min(filtered_population, key=lambda x: (-x['fitness']))
    if pai == individuo:
        filtered_population.remove(individuo)
        individuo = min(filtered_population, key=lambda x: (-x['fitness']))

    return individuo
     

def uniform_crossover(pai, mae):
    filho1 = create_individual()
    filho2 = create_individual()

    if random.random() < MUTATION_RATE: 
        pai = inversion_mutation(pai)
        mae = inversion_mutation(mae)
    for i in range(len(pai['historico_movimento'])):
        if random.random() < MUTATION_RATE:
            filho1['historico_movimento'][i] = pai['historico_movimento'][i]
            filho2['historico_movimento'][i] = mae['historico_movimento'][i]
        else:
            filho1['historico_movimento'][i] = mae['historico_movimento'][i]
            filho2['historico_movimento'][i] = pai['historico_movimento'][i]
 
    return filho1, filho2

def inversion_mutation(individuo):
    global MUTATION_RATE
    a = random.randint(0, len(individuo['historico_movimento'])-1)
    b = random.randint(a+1, len(individuo['historico_movimento']))
    individuo['historico_movimento'][a:b] = reversed(individuo['historico_movimento'][a:b])
    return individuo

            
def run():
    global CONTINUAR
    global SCREEN, TEXT, MATRIX, WHITE, BLACK,POPULATION_SIZE, NUM_GENERATIONS, MUTATION_RATE, END_POS, WIDTH, HEIGHT, BLOCK_SIZE, MARGIN
    read_MATRIX('matrix.txt')
    population = create_population()

    while CONTINUAR:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return 
            nova_populacao = population
            
            for geracao in range(NUM_GENERATIONS):
                
                matrix = propagar(MATRIX)

                draw_board(matrix,nova_populacao)
                qtd_vivos = len(nova_populacao)
                i = 0
                while qtd_vivos > 0:
                    
                    if i > 0:
                        matrix = propagar(matrix)
                        
                    for index, individuo in enumerate(nova_populacao):
                        if individuo['vivo'] == True:
                            nova_populacao[index] = movimentar(matrix,individuo)
                            if nova_populacao[index]['vivo']==False:
                                nova_populacao[index]['fitness'] = fitness_function(individuo)
                                qtd_vivos -= 1
                                
                        SCREEN.fill(BLACK)
                        SCREEN.blit(TEXT.render(f'Geracao {geracao}', True, WHITE), (10, HEIGHT * 10 - 180))
                        SCREEN.blit(TEXT.render(f'Interações {i}', True, WHITE), (180, HEIGHT * 10 - 180))
                        SCREEN.blit(TEXT.render(f'Qtd Individuos {qtd_vivos}', True, WHITE), (350, HEIGHT * 10 - 180))

                            
                    draw_board(matrix,nova_populacao)
                    #time.sleep(0.1)
                    i += 1
                    
                # criar a seleção e mutação da população
                selecao_brasileira = sorted(nova_populacao, key=lambda x: (x['distancia'], x['passos']))[:11]
                new_population = []
                for i in range(POPULATION_SIZE//2):
                    pai = tournament_selection(selecao_brasileira,False)
                    mae = tournament_selection(selecao_brasileira,pai)
                    filho1, filho2 = uniform_crossover(pai, mae)
                    new_population.append(filho1)
                    new_population.append(filho2)
                    
                nova_populacao = new_population
                draw_board(matrix,nova_populacao)
                
        
if __name__ == '__main__':
    run()