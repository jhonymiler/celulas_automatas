

import pygame

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
 
def move_particle(filename, matrix):
    # abre o arquivo e lê as direções
    with open(filename, 'r') as file:
        directions = file.read().split()

    # posição inicial da partícula
    x, y = 0, 0

    # loop pelas direções e movimentação da partícula
    for direction in directions:
        if direction == 'D':
            y += 1
        elif direction == 'U':
            y -= 1
        elif direction == 'L':
            x -= 1
        elif direction == 'R':
            x += 1

        matrix = atualizar_matriz(matrix)
        draw_board(matrix, x,y)
        if matrix[x][y] == 1:
            print('Morto')
            print((x,y),direction)
            break


    return matrix

matrix_file = open("input1.txt", "r")
matrix_list = matrix_file.readlines()
matrix_file.close()
matrix = []
for row in matrix_list:
        matrix.append(list(map(int, row.split())))
        

GRID_COLS = len(matrix[0])-1
GRID_ROWS = len(matrix)-1

pygame.init()

SCREEN = pygame.display.set_mode(((GRID_COLS+1) * BLOCK_SIZE,  (GRID_ROWS+1) * BLOCK_SIZE ))
pygame.display.set_caption("CELULAS AUTOMATAS")
SCREEN.fill(WHITE)

move_particle('output1.txt', matrix)
