# Desafio: Autômatos Celulares - Sobrevivência e Navegação

## Objetivo
Encontrar um caminho seguro da posição inicial **(0,0)** até a posição final **(64,84)** em uma matriz que evolui dinamicamente segundo regras de autômatos celulares. O jogador precisa **sobreviver** (não colidir com células verdes) enquanto navega pelo grid.

## Estrutura da Matriz
- **Dimensões**: 65 linhas × 85 colunas
- **Valores das células**:
  - `0` = Célula branca (livre/segura)
  - `1` = Célula verde (obstáculo/morte)
  - `3` = Posição inicial (início - canto superior esquerdo)
  - `4` = Posição final (destino - canto inferior direito)

## Regras de Propagação do Autômato Celular

A cada passo do jogador, **toda a matriz é atualizada** segundo estas regras (vizinhança de Moore - 8 vizinhos):

### Célula Verde (valor 1) → Sobrevive se:
```
4 ≤ vizinhos_verdes ≤ 5
```
- Se tiver **menos de 4** ou **mais de 5** vizinhos verdes → **morre** (vira branca)

### Célula Branca (valor 0) → Nasce se:
```
2 ≤ vizinhos_verdes ≤ 4
```
- Se tiver entre **2 e 4** vizinhos verdes (inclusive) → **nasce** (vira verde)

### Células Especiais (Posições Fixas)
- A posição **(0,0)** e **(64,84)** **nunca são alteradas** pelas regras

## Condições de Vitória e Derrota

| Condição | Resultado |
|----------|-----------|
| Jogador chega à posição (64,84) | ✅ **Vitória** |
| Jogador colide com célula verde | ❌ **Derrota** |
| Jogador sai dos limites da matriz | ❌ **Derrota** |

## Movimentos Permitidos
- **U** = Cima (y - 1)
- **D** = Baixo (y + 1)
- **R** = Direita (x + 1)
- **L** = Esquerda (x - 1)

## Desafio Principal
O autômato celular se **propaga/evolui a cada turno**, criando um cenário dinâmico onde:
1. O caminho que era seguro pode se tornar bloqueado
2. Novos caminhos podem abrir conforme células morrem
3. É necessário prever a evolução futura do grid para planejar a rota

---

## Abordagens Tentadas

### 1. Algoritmo A* (`app_puro.py` e `app_com_tela.py`)
- Usa busca A* com heurística Manhattan
- Atualiza a matriz a cada expansão de estado
- **Problema**: O espaço de estados é muito grande e a matriz muda a cada movimento

### 2. Algoritmo Genético (`algoritimo_genetico.py`)
- População de indivíduos com sequências de movimentos aleatórios
- Função de fitness baseada em distância ao objetivo
- Crossover uniforme e mutação por inversão
- **Problema**: Convergência lenta devido à alta dimensionalidade do espaço de busca

---

## Visualização da Evolução

```
Turno 0      →      Turno 1      →      Turno 2
[Jogador]           [Jogador]           [Jogador]
    🟢🟢               🟢🟢🟢              🟢🟢🟢🟢
   🟢🟢🟢            🟢🟢🟢🟢           🟢🟢  🟢🟢
  🟢🟢🟢🟢          🟢🟢  🟢🟢         🟢      🟢
                         ↑                  ↑
              (células morrem/nascem conforme regras)
```

## Pseudocódigo das Regras

```python
def propagar(grid):
    nova_grid = copiar(grid)
    
    for cada célula (i, j):
        vizinhos_verdes = contar_vizinhos_verdes(grid, i, j)
        
        if grid[i][j] == 1:  # Verde
            # Sobrevive apenas com 4 ou 5 vizinhos
            if vizinhos_verdes < 4 or vizinhos_verdes > 5:
                nova_grid[i][j] = 0  # Morre
        else:  # Branca
            # Nasce com 2, 3 ou 4 vizinhos
            if vizinhos_verdes > 1 and vizinhos_verdes < 5:
                nova_grid[i][j] = 1  # Nasce
    
    return nova_grid
```
