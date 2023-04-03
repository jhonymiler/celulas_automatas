import heapq

def atualizar_matriz(matrix):
    # Atualiza a matriz de acordo com as regras do problema
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

class Estado:
    def __init__(self, matriz, posicao):
        # Representa um estado no labirinto, com uma matriz e uma posição
        self.matriz = matriz
        self.posicao = posicao

    # Define as funções necessárias para usar a classe Estado como chave no heap
    def __eq__(self, outro):
        return self.posicao == outro.posicao

    def __lt__(self, outro):
        return False  # Sempre retorna False para usar a ordem de inserção no heap

    def __hash__(self):
        return hash(self.posicao)

def heuristica(atual, objetivo):
    # Define a função heurística para o algoritmo A*
    return abs(objetivo[0] - atual[0]) + abs(objetivo[1] - atual[1])

def get_caminho(caminho, direcao):
    # Retorna uma tupla com o caminho e a direção correspondente
    retorno = None
    if direcao == 1:
        retorno = (caminho,'U')
    elif direcao == 2:
        retorno = (caminho,'R')
    elif direcao == 3:
        retorno = (caminho,'L')
    elif direcao == 4:
        retorno = (caminho,'D')
    return retorno

def get_direcao(coord_atual, prox_coord):
    """
    Retorna a direção da próxima coordenada em relação à coordenada atual.
    """
    x_atual, y_atual = coord_atual
    x_prox, y_prox = prox_coord
    
    if x_prox < x_atual:
        return "L"
    elif x_prox > x_atual:
        return "R"
    elif y_prox < y_atual:
        return "U"
    elif y_prox > y_atual:
        return "D"
    else:
        return None  # se a próxima coordenada for a mesma que a atual, não há direção definida


# Define a função para encontrar a melhor rota com A*
def encontrar_melhor_rota(estado_inicial):
    # Define o estado objetivo como a posição no canto inferior direito da matriz
    objetivo = (len(estado_inicial.matriz) - 1, len(estado_inicial.matriz[0]) - 1)
    
    # Cria um heap com a heurística do estado inicial e o próprio estado inicial
    heap = [(heuristica(estado_inicial.posicao, objetivo), estado_inicial)]
    
    # Cria um conjunto de estados visitados
    visitados = set()
    
    # Cria um dicionário de distâncias, inicialmente com o estado inicial
    distancia = {estado_inicial: 0}
    
    # Cria um dicionário de caminhos, inicialmente com o estado inicial
    caminho = {estado_inicial: []}
    
    # Cria um dicionário do melhor caminho, inicialmente com o estado inicial
    melhor_caminho = {estado_inicial: []}
    
    # Enquanto houver estados no heap
    while heap:
        # Remove o estado com menor heurística do heap
        atual = heapq.heappop(heap)[1]
        
        # Se o estado atual for o objetivo, retorna o melhor caminho
        if atual.posicao == objetivo:
            for i in range(len(melhor_caminho[atual]) - 1):
                direcao = get_direcao(melhor_caminho[atual][i], melhor_caminho[atual][i+1])
                melhor += [(melhor_caminho[atual][i],direcao)]
            return melhor
        
        # Adiciona o estado atual ao conjunto de estados visitados
        visitados.add(atual)
        
        # Atualiza a matriz atual com as informações do estado atual
        matriz = atualizar_matriz(atual.matriz)

        # Para cada jogada possível (1, 2, 3, 4)
        for jogada in range(1, 5):
            # Calcula a nova posição do estado atual após a jogada
            nova_posicao = (atual.posicao[0] + (jogada == 3) - (jogada == 4),
                            atual.posicao[1] + (jogada == 2) - (jogada == 1))
            # Cria um novo estado com a nova posição e a matriz atualizada
            novo_estado = Estado(matriz, nova_posicao)
            # Calcula a nova distância do estado atual até o novo estado
            nova_distancia = distancia[atual] + 1

            # Se o novo estado já foi visitado, continua o loop sem fazer nada
            if novo_estado in visitados:
                continue
            # Se o novo estado ainda não está no dicionário de distâncias
            # ou a nova distância é menor que a anterior, atualiza o dicionário de distâncias
            # e adiciona o novo estado ao heap com a nova prioridade
            if novo_estado not in distancia or nova_distancia < distancia[novo_estado]:
                distancia[novo_estado] = nova_distancia
                prioridade = nova_distancia + heuristica(novo_estado.posicao, objetivo)
                heapq.heappush(heap, (prioridade, novo_estado))
                # Atualiza o dicionário de caminhos e o dicionário do melhor caminho
                caminho[novo_estado] = caminho[atual] + [jogada]
                melhor_caminho[novo_estado] = melhor_caminho[atual] + [get_caminho(novo_estado.posicao,jogada)]
    # Se não houver
    return None


# matriz com 65 linhas e 85 colunas preenchida com zeros e uns
matrix_file = open("matrix.txt", "r")
matrix_list = matrix_file.readlines()
matrix_file.close()
matrix = []
for row in matrix_list:
        matrix.append(list(map(int, row.split())))

estado_inicial = Estado(matrix, (0, 0))
melhor_rota = encontrar_melhor_rota(estado_inicial)

d = []
for posicao, direcao in melhor_rota:
    d.append(direcao)

print(len(d))  
with open('historico.txt', 'a') as f:
    historico = ' '.join(d)
    f.write(str(historico))







