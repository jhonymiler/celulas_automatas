#!/usr/bin/env python3
"""
Algoritmo Genético para Células Autômatas
Ponto de entrada principal

Uso:
    python main.py              # Inicia do zero
    python main.py --load       # Carrega último checkpoint
    python main.py --load checkpoint_xxx.json  # Carrega checkpoint específico
    python main.py --list       # Lista checkpoints disponíveis
"""
import random
import sys
from src.config import *
from src.cellular import read_matrix, propagar
from src.genetic import (
    create_individual, create_population, movimentar, fitness_function,
    tournament_selection, crossover, mutate, calculate_diversity,
    adaptive_mutation_rate
)
from src.visualization import Visualizer
from src.persistence import (
    save_checkpoint, load_checkpoint, restore_population, 
    list_checkpoints
)

# Intervalo de auto-save (gerações)
AUTOSAVE_INTERVAL = 50


def run(load_file=None):
    """Loop principal do algoritmo genético"""
    
    # Carrega matriz
    matrix_original = read_matrix('matrix.txt')
    width = len(matrix_original)
    height = len(matrix_original[0])
    end_pos = (height - 1, width - 1)
    
    print(f"Matriz: {width}x{height}")
    print(f"Objetivo: {end_pos}")
    print(f"Populacao: {POPULATION_SIZE}")
    print("-" * 50)
    
    # Inicializa visualização
    viz = Visualizer(width, height)
    
    # Variáveis de controle
    best_fitness_ever = 0
    best_individual = None
    last_best = 0
    stagnation = 0
    geracao = 0
    
    # Tenta carregar checkpoint se solicitado
    if load_file:
        if load_file == True:
            checkpoints = list_checkpoints()
            if checkpoints:
                load_file = checkpoints[0]['filename']
                print(f"Usando checkpoint mais recente: {load_file}")
            else:
                print("Nenhum checkpoint encontrado. Iniciando do zero.")
                load_file = None
        
        if load_file:
            pop_data, state = load_checkpoint(load_file)
            if pop_data:
                population = restore_population(pop_data, width, height)
                geracao = state.get('geracao', 0)
                best_fitness_ever = state.get('best_fitness', 0)
                last_best = state.get('last_best', 0)
                stagnation = state.get('stagnation', 0)
                print(f"Continuando da geracao {geracao}...")
            else:
                population = create_population(width, height)
        else:
            population = create_population(width, height)
    else:
        population = create_population(width, height)
    
    import pygame
    clock = pygame.time.Clock()
    
    try:
        while geracao < NUM_GENERATIONS:
            # Verifica eventos (fecha janela, etc)
            if not viz.check_events():
                print("\n[!] Janela fechada pelo usuario.")
                break
            
            # Reset da matriz para cada geração
            matrix = [row[:] for row in matrix_original]
            
            # Reset dos indivíduos
            for ind in population:
                ind['posicao'] = {'x': 0, 'y': 0}
                ind['passos'] = 0
                ind['vivo'] = True
                ind['fitness'] = 0
                ind['colidiu'] = False
                ind['max_progresso'] = 0
                ind['caminho'] = []
            
            # Simula geração
            vivos = len(population)
            iteracao = 0
            max_iter = 3 * (width + height)
            
            while vivos > 0 and iteracao < max_iter:
                # Verifica eventos durante simulação também
                if not viz.check_events():
                    raise KeyboardInterrupt("Janela fechada")
                
                # Propaga autômato celular
                if iteracao > 0:
                    matrix = propagar(matrix)
                
                # Move indivíduos
                for ind in population:
                    if ind['vivo']:
                        movimentar(matrix, ind, end_pos)
                        if not ind['vivo']:
                            ind['fitness'] = fitness_function(ind, end_pos, width, height)
                            vivos -= 1
                
                # Calcula estatísticas para exibição
                if iteracao % 10 == 0:
                    diversity = calculate_diversity(population)
                else:
                    diversity = viz.history['diversity'][-1] if viz.history['diversity'] else 0.5
                
                current_mut = adaptive_mutation_rate(MUTATION_RATE, diversity, stagnation)
                
                avg_progress = sum(ind['max_progresso'] for ind in population) / len(population)
                avg_progress_norm = avg_progress / (width + height)
                
                all_fitness = [ind['fitness'] for ind in population if ind['fitness'] > 0]
                current_best = max(all_fitness) if all_fitness else 0
                avg_fitness = sum(all_fitness) / len(all_fitness) if all_fitness else 0
                
                if current_best > best_fitness_ever:
                    best_fitness_ever = current_best
                    best_individual = max(population, key=lambda x: x['fitness'])
                
                stats = {
                    'geracao': geracao,
                    'iteracao': iteracao,
                    'vivos': vivos,
                    'best': best_fitness_ever,
                    'avg': avg_fitness,
                    'diversity': diversity,
                    'mutation': current_mut,
                    'stagnation': stagnation,
                    'progress': avg_progress_norm,
                }
                
                viz.draw(matrix, population, stats)
                clock.tick(60)
                iteracao += 1
            
            # Calcula fitness final para todos
            for ind in population:
                if ind['fitness'] == 0:
                    ind['fitness'] = fitness_function(ind, end_pos, width, height)
            
            # Análise de diversidade e estagnação
            diversity = calculate_diversity(population)
            all_fitness = [ind['fitness'] for ind in population]
            current_best = max(all_fitness)
            avg_fitness = sum(all_fitness) / len(all_fitness)
            
            if current_best <= last_best:
                stagnation += 1
            else:
                stagnation = 0
                last_best = current_best
            
            current_mut = adaptive_mutation_rate(MUTATION_RATE, diversity, stagnation)
            
            # Atualiza histórico e gráficos
            avg_progress = sum(ind['max_progresso'] for ind in population) / len(population)
            avg_progress_norm = avg_progress / (width + height)
            
            viz.update_history(geracao, best_fitness_ever, avg_fitness, diversity, current_mut, avg_progress_norm)
            
            if geracao % 5 == 0:
                viz.update_plots()
            
            # === SELEÇÃO E REPRODUÇÃO ===
            population = sorted(population, key=lambda x: x['fitness'], reverse=True)
            
            new_population = []
            
            # Elitismo
            num_elite = max(2, int(POPULATION_SIZE * ELITISM_RATE))
            for i in range(num_elite):
                elite = create_individual(width, height)
                elite['historico_movimento'] = population[i]['historico_movimento'][:]
                elite['aprendizado'] = population[i]['aprendizado'].copy()
                new_population.append(elite)
            
            # Imigração (aumenta se estagnado)
            num_immigrants = int(POPULATION_SIZE * IMMIGRATION_RATE)
            if stagnation > STAGNATION_THRESHOLD:
                num_immigrants = int(POPULATION_SIZE * 0.3)
                print(f"[!] Estagnacao! Injetando {num_immigrants} novos individuos...")
                stagnation = 0
            
            for _ in range(num_immigrants):
                new_population.append(create_individual(width, height, biased=random.random() < 0.5))
            
            # Crossover
            while len(new_population) < POPULATION_SIZE:
                pai = tournament_selection(population)
                mae = tournament_selection(population, exclude=pai)
                
                if random.random() < CROSSOVER_RATE:
                    filho1, filho2 = crossover(pai, mae, width, height)
                else:
                    filho1 = create_individual(width, height)
                    filho1['historico_movimento'] = pai['historico_movimento'][:]
                    filho2 = create_individual(width, height)
                    filho2['historico_movimento'] = mae['historico_movimento'][:]
                
                # Mutação adaptativa
                if random.random() < current_mut:
                    filho1 = mutate(filho1, current_mut)
                if random.random() < current_mut:
                    filho2 = mutate(filho2, current_mut)
                
                new_population.append(filho1)
                if len(new_population) < POPULATION_SIZE:
                    new_population.append(filho2)
            
            population = new_population
            geracao += 1
            
            # Auto-save a cada AUTOSAVE_INTERVAL gerações
            if geracao % AUTOSAVE_INTERVAL == 0:
                state = {
                    'geracao': geracao,
                    'best_fitness': best_fitness_ever,
                    'last_best': last_best,
                    'stagnation': stagnation,
                }
                save_checkpoint(population, state, f"checkpoint_gen{geracao}.json")
            
            # Log
            if geracao % 10 == 0:
                print(f"Gen {geracao}: Best={best_fitness_ever:.1f} Avg={avg_fitness:.1f} Div={diversity:.2f} Mut={current_mut:.2f}")
    
    except KeyboardInterrupt:
        print("\n[!] Interrompido!")
    
    finally:
        # Salva checkpoint ao sair (sempre!)
        if geracao > 0:
            state = {
                'geracao': geracao,
                'best_fitness': best_fitness_ever,
                'last_best': last_best,
                'stagnation': stagnation,
            }
            save_checkpoint(population, state, f"checkpoint_gen{geracao}.json")
            
            print("\n" + "=" * 50)
            print("Evolucao pausada/concluida!")
            print(f"Melhor fitness: {best_fitness_ever:.2f}")
            print(f"Checkpoint salvo: checkpoint_gen{geracao}.json")
            print(f"Para continuar: python main.py --load")
        
        viz.quit()


if __name__ == '__main__':
    load_file = None
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--load':
            if len(sys.argv) > 2:
                load_file = sys.argv[2]
            else:
                load_file = True
        elif sys.argv[1] == '--list':
            print("Checkpoints disponiveis:")
            checkpoints = list_checkpoints()
            if checkpoints:
                for cp in checkpoints:
                    print(f"  {cp['filename']}: Gen {cp['geracao']}, Best={cp['best_fitness']:.1f}")
            else:
                print("  Nenhum checkpoint encontrado.")
            sys.exit(0)
        elif sys.argv[1] == '--help':
            print(__doc__)
            sys.exit(0)
    
    run(load_file)
