



import queue
import time
import pygame

import heapq
# Define as cores

BLACK = (50, 50, 50)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
# Define o tamanho do bloco e da margem
BLOCK_SIZE = 10
MARGIN = 1





def atualizar_matriz(matrix):
    nova_matrix = [[0 for j in range(len(matrix[0]))] for i in range(len(matrix))]
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            if (i, j) == (0, 0) or (i, j) == (len(matrix)-1, len(matrix[0])-1):
                # As células (0,0) e (64,84) não são alteradas
                nova_matrix[i][j] = matrix[i][j]
            elif matrix[i][j] == 1:
                num_verdes = 0
                for r in range(max(0, i-1), min(len(matrix), i+2)):
                    for c in range(max(0, j-1), min(len(matrix[0]), j+2)):
                        if matrix[r][c] == 1 and (r != i or c != j):
                            num_verdes += 1
                if num_verdes > 3 and num_verdes < 6:
                    nova_matrix[i][j] = 1
            else:
                num_verdes = 0
                for r in range(max(0, i-1), min(len(matrix), i+2)):
                    for c in range(max(0, j-1), min(len(matrix[0]), j+2)):
                        if matrix[r][c] == 1:
                            num_verdes += 1
                if num_verdes > 1 and num_verdes < 5:
                    nova_matrix[i][j] = 1
 

    return nova_matrix



# Define uma classe para representar um estado no labirinto
class Estado:
    def __init__(self, matriz, posicao):
        self.matriz = matriz
        self.posicao = posicao

    # Define as funções necessárias para usar a classe Estado como chave no heap
    def __eq__(self, outro):
        return self.posicao == outro.posicao

    def __lt__(self, outro):
        return False  # Sempre retorna False para usar a ordem de inserção no heap

    def __hash__(self):
        return hash(self.posicao)

# Define a função heurística para o algoritmo A*
def heuristica(atual, objetivo):
    return abs(objetivo[0] - atual[0]) + abs(objetivo[1] - atual[1])

def get_direcao(coord_atual, prox_coord):
    """
    Retorna a direção da próxima coordenada em relação à coordenada atual.
    """
    x_atual, y_atual = coord_atual
    x_prox, y_prox = prox_coord
    
    if x_prox < x_atual:
        return "U"
    elif x_prox > x_atual:
        return "D"
    elif y_prox < y_atual:
        return "L"
    elif y_prox > y_atual:
        return "R"
    else:
        return None  # se a próxima coordenada for a mesma que a atual, não há direção definida


# Define a função para encontrar a melhor rota com A*
def encontrar_melhor_rota(estado_inicial):
    objetivo = (len(estado_inicial.matriz) - 1, len(estado_inicial.matriz[0]) - 1)
    heap = [(heuristica(estado_inicial.posicao, objetivo), estado_inicial)]
    visitados = set()
    distancia = {estado_inicial: 0}
    caminho = {estado_inicial: []}
    melhor_caminho = {estado_inicial: []}
    melhor = []

    while heap:
        atual = heapq.heappop(heap)[1]
        if atual.posicao == objetivo:
            for i in range(len(melhor_caminho[atual]) - 1):
                direcao = get_direcao(melhor_caminho[atual][i], melhor_caminho[atual][i+1])
                melhor += [(melhor_caminho[atual][i],direcao)]
            return melhor
        
        visitados.add(atual)
        
        matriz = atualizar_matriz(atual.matriz)

        for jogada in range(1, 5):
            
               
            nova_posicao = (atual.posicao[0] + (jogada == 3) - (jogada == 4), atual.posicao[1] + (jogada == 2) - (jogada == 1))
            novo_estado = Estado(matriz, nova_posicao)
            nova_distancia = distancia[atual] + 1


            if novo_estado in visitados:
                continue
            if novo_estado not in distancia or nova_distancia < distancia[novo_estado]:
                distancia[novo_estado] = nova_distancia
                prioridade = nova_distancia + heuristica(novo_estado.posicao, objetivo)
                heapq.heappush(heap, (prioridade, novo_estado))
                caminho[novo_estado] = caminho[atual] + [jogada]
                melhor_caminho[novo_estado] = melhor_caminho[atual] + [novo_estado.posicao]
                
                
    return None

def draw_board(matrix, X,Y):
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            cell_color = None
            if i == 0 and j == 0 or i == GRID_ROWS and j == GRID_COLS:
                cell_color = YELLOW
            elif matrix[i][j] == 0:
                cell_color = WHITE
            elif matrix[i][j] == 1:
                cell_color = GREEN
                
            pygame.draw.rect(SCREEN, cell_color, [j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE], 0)
            pygame.draw.rect(SCREEN, BLACK, [j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE], MARGIN)

            # Atualizar outras informações do indivíduo aqui
            pygame.draw.rect(SCREEN,RED, [Y * BLOCK_SIZE, X * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE], 0)
            pygame.draw.rect(SCREEN, BLACK, [Y * BLOCK_SIZE, X * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE], MARGIN)

    pygame.display.flip()
 
    
#matriz com 65 linhas e 85 colunas preenchida com zeros e uns
matrix_file = open("matrix.txt", "r")
matrix_list = matrix_file.readlines()
matrix_file.close()
matrix = []
for row in matrix_list:
        matrix.append(list(map(int, row.split())))
        

GRID_COLS = len(matrix[0])-1
GRID_ROWS = len(matrix)-1


estado_inicial = Estado(matrix, (0, 0))
melhor_rota = encontrar_melhor_rota(estado_inicial)

print(melhor_rota)
d = []
for posicao, direcao in melhor_rota:
    d.append(direcao)

print(d)  
with open('historico.txt', 'a') as f:
    historico = ' '.join(d)
    f.write(str(historico))

#melhor_rota = [((0, 1), 'R'), ((0, 2), 'R'), ((0, 3), 'D'), ((1, 3), 'R'), ((1, 4), 'R'), ((1, 5), 'D'), ((2, 5), 'D'), ((3, 5), 'R'), ((3, 6), 'R'), ((3, 7), 'R'), ((3, 8), 'R'), ((3, 9), 'R'), ((3, 10), 'D'), ((4, 10), 'D'), ((5, 10), 'D'), ((6, 10), 'R'), ((6, 11), 'R'), ((6, 12), 'R'), ((6, 13), 'D'), ((7, 13), 'R'), ((7, 14), 'R'), ((7, 15), 'R'), ((7, 16), 'R'), ((7, 17), 'R'), ((7, 18), 'R'), ((7, 19), 'D'), ((8, 19), 'D'), ((9, 19), 'D'), ((10, 19), 'R'), ((10, 20), 'R'), ((10, 21), 'R'), ((10, 22), 'R'), ((10, 23), 'R'), ((10, 24), 'R'), ((10, 25), 'R'), ((10, 26), 'R'), ((10, 27), 'R'), ((10, 28), 'D'), ((11, 28), 'D'), ((12, 28), 'R'), ((12, 29), 'R'), ((12, 30), 'R'), ((12, 31), 'R'), ((12, 32), 'R'), ((12, 33), 'R'), ((12, 34), 'R'), ((12, 35), 'R'), ((12, 36), 'R'), ((12, 37), 'R'), ((12, 38), 'R'), ((12, 39), 'R'), ((12, 40), 'R'), ((12, 41), 'R'), ((12, 42), 'R'), ((12, 43), 'R'), ((12, 44), 'R'), ((12, 45), 'R'), ((12, 46), 'R'), ((12, 47), 'R'), ((12, 48), 'R'), ((12, 49), 'R'), ((12, 50), 'R'), ((12, 51), 'R'), ((12, 52), 'R'), ((12, 53), 'R'), ((12, 54), 'R'), ((12, 55), 'R'), ((12, 56), 'R'), ((12, 57), 'R'), ((12, 58), 'R'), ((12, 59), 'R'), ((12, 60), 'R'), ((12, 61), 'R'), ((12, 62), 'D'), ((13, 62), 'R'), ((13, 63), 'R'), ((13, 64), 'R'), ((13, 65), 'R'), ((13, 66), 'R'), ((13, 67), 'R'), ((13, 68), 'R'), ((13, 69), 'R'), ((13, 70), 'R'), ((13, 71), 'R'), ((13, 72), 'R'), ((13, 73), 'R'), ((13, 74), 'R'), ((13, 75), 'D'), ((14, 75), 'R'), ((14, 76), 'R'), ((14, 77), 'R'), ((14, 78), 'D'), ((15, 78), 'D'), ((16, 78), 'D'), ((17, 78), 'D'), ((18, 78), 'D'), ((19, 78), 'D'), ((20, 78), 'D'), ((21, 78), 'D'), ((22, 78), 'D'), ((23, 78), 'D'), ((24, 78), 'R'), ((24, 79), 'D'), ((25, 79), 'R'), ((25, 80), 'D'), ((26, 80), 'D'), ((27, 80), 'D'), ((28, 80), 'R'), ((28, 81), 'D'), ((29, 81), 'R'), ((29, 82), 'R'), ((29, 83), 'R'), ((29, 84), 'D'), ((30, 84), 'D'), ((31, 84), 'D'), ((32, 84), 'D'), ((33, 84), 'D'), ((34, 84), 'D'), ((35, 84), 'D'), ((36, 84), 'D'), ((37, 84), 'D'), ((38, 84), 'D'), ((39, 84), 'D'), ((40, 84), 'D'), ((41, 84), 'D'), ((42, 84), 'D'), ((43, 84), 'D'), ((44, 84), 'D'), ((45, 84), 'D'), ((46, 84), 'D'), ((47, 84), 'D'), ((48, 84), 'D'), ((49, 84), 'D'), ((50, 84), 'D'), ((51, 84), 'D'), ((52, 84), 'D'), ((53, 84), 'D'), ((54, 84), 'D'), ((55, 84), 'D'), ((56, 84), 'D'), ((57, 84), 'D'), ((58, 84), 'D'), ((59, 84), 'D'), ((60, 84), 'D'), ((61, 84), 'D'), ((62, 84), 'D'), ((63, 84), 'D')]

pygame.init()

SCREEN = pygame.display.set_mode(((GRID_COLS+1) * BLOCK_SIZE,  (GRID_ROWS+1) * BLOCK_SIZE ))
pygame.display.set_caption("CELULAS AUTOMATAS")
SCREEN.fill(WHITE)

caminho = []
for posicao,direcao in melhor_rota:
    matrix = atualizar_matriz(matrix)
    x,y = posicao
    draw_board(matrix, x,y)
    copia = matrix.copy()
    copia[x][y] = '#'
    caminho.append(copia)
    #time.sleep(0.5)
    if matrix[x][y] == 1:
        print('Morto')
        print((x,y),caminho)
        break





