"""
Persistência - Salvar e carregar população e estado do algoritmo
"""
import json
import os
from datetime import datetime


def save_checkpoint(population, state, filename='checkpoint.json'):
    """
    Salva a população e estado atual do algoritmo.
    
    Args:
        population: Lista de indivíduos
        state: Dicionário com estado do algoritmo (geração, best_fitness, etc)
        filename: Nome do arquivo
    """
    # Prepara população para serialização
    pop_data = []
    for ind in population:
        ind_data = {
            'historico_movimento': ind['historico_movimento'],
            'cor': ind['cor'],
            # Converte defaultdict para dict normal
            'aprendizado': {str(k): dict(v) for k, v in ind.get('aprendizado', {}).items()},
        }
        pop_data.append(ind_data)
    
    checkpoint = {
        'timestamp': datetime.now().isoformat(),
        'state': state,
        'population': pop_data,
    }
    
    with open(filename, 'w') as f:
        json.dump(checkpoint, f, indent=2)
    
    print(f"[+] Checkpoint salvo: {filename} (Gen {state.get('geracao', '?')})")


def load_checkpoint(filename='checkpoint.json'):
    """
    Carrega população e estado salvos.
    
    Returns:
        tuple: (population_data, state) ou (None, None) se não existir
    """
    if not os.path.exists(filename):
        return None, None
    
    try:
        with open(filename, 'r') as f:
            checkpoint = json.load(f)
        
        print(f"[+] Checkpoint carregado: {filename}")
        print(f"    Salvo em: {checkpoint.get('timestamp', 'desconhecido')}")
        print(f"    Geracao: {checkpoint['state'].get('geracao', '?')}")
        print(f"    Best Fitness: {checkpoint['state'].get('best_fitness', '?'):.2f}")
        
        return checkpoint['population'], checkpoint['state']
    
    except Exception as e:
        print(f"[!] Erro ao carregar checkpoint: {e}")
        return None, None


def restore_population(pop_data, width, height):
    """
    Restaura a população a partir dos dados salvos.
    """
    from .genetic import create_individual
    from collections import defaultdict
    
    population = []
    
    for ind_data in pop_data:
        ind = create_individual(width, height)
        ind['historico_movimento'] = ind_data['historico_movimento']
        ind['cor'] = tuple(ind_data['cor'])
        
        # Restaura aprendizado
        if 'aprendizado' in ind_data:
            for state_str, prefs in ind_data['aprendizado'].items():
                # Converte string de volta para tupla
                try:
                    state = eval(state_str)
                except:
                    state = state_str
                ind['aprendizado'][state] = defaultdict(float, prefs)
        
        population.append(ind)
    
    return population


def list_checkpoints(directory='.'):
    """Lista todos os checkpoints disponíveis"""
    checkpoints = []
    
    for f in os.listdir(directory):
        if f.endswith('.json') and 'checkpoint' in f.lower():
            filepath = os.path.join(directory, f)
            try:
                with open(filepath, 'r') as file:
                    data = json.load(file)
                    checkpoints.append({
                        'filename': f,
                        'timestamp': data.get('timestamp', 'desconhecido'),
                        'geracao': data.get('state', {}).get('geracao', 0),
                        'best_fitness': data.get('state', {}).get('best_fitness', 0),
                    })
            except:
                pass
    
    return sorted(checkpoints, key=lambda x: x.get('geracao', 0), reverse=True)


def auto_save_filename():
    """Gera nome de arquivo com timestamp"""
    return f"checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
