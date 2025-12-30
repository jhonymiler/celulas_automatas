# 🤖 Autômatos Celulares + Algoritmo Genético

![Demo do Algoritmo Genético](image.png)

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![Pygame](https://img.shields.io/badge/pygame-2.0+-green.svg)](https://pygame.org)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> Projeto experimental usando **Algoritmo Genético** para resolver navegação em ambientes dinâmicos com **Autômatos Celulares**.

![Demo](https://img.shields.io/badge/Status-Em%20Desenvolvimento-yellow)

## 🎯 Objetivo
Encontrar um caminho seguro da posição inicial **(0,0)** até a posição final **(64,84)** em uma matriz que evolui dinamicamente segundo regras de autômatos celulares. O agente deve **sobreviver** (não colidir com células verdes) enquanto navega pelo grid em constante transformação.

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
---

## 📁 Estrutura do Código

```
celulas_automatas/
├── main.py                 # Ponto de entrada principal
├── matrix.txt              # Matriz inicial do ambiente
├── grafico_evolucao.png    # Gráfico gerado em tempo real
├── src/
│   ├── config.py           # Configurações globais
│   ├── cellular.py         # Lógica do autômato celular
│   ├── genetic.py          # Algoritmo genético
│   └── visualization.py    # Visualização (Pygame + Matplotlib)
```

## � Instalação

### Pré-requisitos
- Python 3.8+
- pip

### Dependências
```bash
# Instalar dependências
pip install pygame matplotlib numpy

# Ou usando requirements (se disponível)
pip install -r requirements.txt
```

## 🚀 Como Executar

### Comandos disponíveis:

```bash
# Iniciar simulação do zero
python main.py

# Carregar último checkpoint
python main.py --load

# Carregar checkpoint específico
python main.py --load checkpoint_gen100.json

# Listar checkpoints disponíveis
python main.py --list

# Ajuda
python main.py --help
```

### Durante a execução:
- **ESC** ou **fechar janela** → Pausa e salva checkpoint
- Os gráficos são atualizados em tempo real
- Checkpoints automáticos a cada 50 gerações

## 🧬 Características do Algoritmo Genético

### 🎲 Estratégias Evolutivas
- **Seleção por Torneio**: Competição entre indivíduos
- **Crossover de Dois Pontos**: Herança genética inteligente
- **4 Tipos de Mutação**: Swap, Random, Scramble, Insert
- **Elitismo (10%)**: Preserva os melhores da geração
- **Imigração (10%)**: Injeta novos indivíduos

### 🧠 Aprendizado e Adaptação
- **Memória de Estados**: Indivíduos lembram situações anteriores
- **Tabela de Aprendizado**: Mapeamento estado → ação
- **Mutação Adaptativa**: Taxa aumenta com estagnação ou baixa diversidade
- **Detecção de Estagnação**: Auto-correção após 15 gerações sem melhoria

### 📊 Métricas em Tempo Real
- **Fitness**: Progresso + sobrevivência + eficiência
- **Diversidade Genética**: Shannon entropy dos genes
- **Taxa de Mutação Atual**: Adaptação dinâmica
- **Indivíduos Vivos**: Quantos ainda estão navegando

## ⚙️ Configurações (src/config.py)

| Parâmetro | Padrão | Descrição |
|-----------|--------|-----------||
| POPULATION_SIZE | 100 | Tamanho da população |
| MUTATION_RATE | 0.1 | Taxa base de mutação |
| STAGNATION_THRESHOLD | 15 | Gerações para detectar estagnação |
| ELITISM_RATE | 0.1 | Porcentagem de elite preservada |
| CROSSOVER_RATE | 0.7 | Probabilidade de crossover |
| IMMIGRATION_RATE | 0.1 | Taxa de novos indivíduos por geração |

## 📁 Arquivos Gerados

- **checkpoint_genXXX.json**: Salvamento automático da população
- **grafico_evolucao.png**: Gráficos de aprendizado (fitness, diversidade, mutação, sobrevivência)
- **logs/**: Histórico detalhado das execuções

## 🔬 Análise dos Resultados

O sistema gera **4 gráficos simultâneos**:

1. **Evolução do Fitness**: Melhor vs Médio ao longo das gerações
2. **Diversidade Genética**: Shannon entropy da população
3. **Taxa de Mutação**: Adaptação dinâmica da taxa
4. **Taxa de Sobrevivência**: % de indivíduos que completam a navegação

## 🐛 Solução de Problemas

### Erros comuns:
```bash
# Erro: Pygame não inicializado
sudo apt-get install python3-pygame  # Linux
brew install pygame                  # macOS

# Erro: Matplotlib backend
export MPLBACKEND=Agg  # Para sistemas sem display
```

### Performance:
- Para mapas grandes: Reduza `POPULATION_SIZE`
- Para convergência lenta: Aumente `MUTATION_RATE`
- Para diversidade: Aumente `IMMIGRATION_RATE`

---

## 📈 Status do Projeto

- ✅ Algoritmo genético implementado
- ✅ Visualização em tempo real
- ✅ Sistema de checkpoints
- ✅ Mutação adaptativa
- ✅ Análise de diversidade
- 🔄 Otimização de performance
- 🔄 Algoritmos alternativos (A*, NEAT)

---

**Contribuições são bem-vindas!** 🚀