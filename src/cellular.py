"""
Lógica do autômato celular e manipulação da matriz
"""

def read_matrix(filename):
    """Lê a matriz do arquivo"""
    matrix = []
    with open(filename, "r") as f:
        for row in f.readlines():
            matrix.append(list(map(int, row.split())))
    return matrix


def propagar(grid):
    """
    Propaga o autômato celular (células verdes se espalham/morrem).
    Regras:
    - Célula branca com 2-4 vizinhos verdes vira verde
    - Célula verde com <4 ou >5 vizinhos verdes morre
    """
    rows = len(grid)
    cols = len(grid[0])
    new_grid = [[cell for cell in row] for row in grid]
    
    for i in range(rows):
        for j in range(cols):
            green_neighbors = 0
            
            # Conta vizinhos verdes (8 direções)
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    if dx == 0 and dy == 0:
                        continue
                    ni, nj = i + dx, j + dy
                    if 0 <= ni < rows and 0 <= nj < cols and grid[ni][nj] == 1:
                        green_neighbors += 1
            
            # Aplica regras
            if grid[i][j] == 0 and 1 < green_neighbors < 5:
                new_grid[i][j] = 1
            elif grid[i][j] == 1 and (green_neighbors < 4 or green_neighbors > 5):
                new_grid[i][j] = 0
    
    return new_grid


def get_local_state(matrix, x, y, radius=2):
    """
    Obtém o estado local ao redor de uma posição.
    Usado para o indivíduo "perceber" o ambiente sem conhecer as regras.
    Retorna uma tupla representando o estado local.
    """
    rows = len(matrix)
    cols = len(matrix[0])
    state = []
    
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            ni, nj = y + dy, x + dx
            if 0 <= ni < rows and 0 <= nj < cols:
                state.append(matrix[ni][nj])
            else:
                state.append(-1)  # Fora do mapa
    
    return tuple(state)


def is_safe_position(matrix, x, y):
    """Verifica se uma posição é segura (não é obstáculo e está dentro do mapa)"""
    rows = len(matrix)
    cols = len(matrix[0])
    
    if x < 0 or x >= cols or y < 0 or y >= rows:
        return False
    return matrix[y][x] != 1


def count_safe_neighbors(matrix, x, y):
    """Conta quantos vizinhos seguros existem ao redor"""
    rows = len(matrix)
    cols = len(matrix[0])
    safe = 0
    
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        ni, nj = y + dy, x + dx
        if 0 <= ni < rows and 0 <= nj < cols and matrix[ni][nj] != 1:
            safe += 1
    
    return safe
