"""
Visualização com Pygame e Matplotlib
"""
import pygame
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import deque
from .config import *


class Visualizer:
    """Gerencia toda a visualização do algoritmo"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # Histórico para gráficos
        self.history = {
            'geracao': deque(maxlen=500),
            'best_fitness': deque(maxlen=500),
            'avg_fitness': deque(maxlen=500),
            'diversity': deque(maxlen=500),
            'mutation_rate': deque(maxlen=500),
            'progress': deque(maxlen=500),
        }
        
        # Pygame
        pygame.init()
        self.board_width = height * BLOCK_SIZE
        self.board_height = width * BLOCK_SIZE
        
        window_width = self.board_width + GRAPH_WIDTH + 30
        window_height = max(self.board_height + HEADER, GRAPH_HEIGHT + 120)
        
        self.screen = pygame.display.set_mode((window_width, window_height))
        self.font = pygame.font.SysFont('monospace', 24)
        self.font_small = pygame.font.SysFont('monospace', 18)
        self.font_title = pygame.font.SysFont('monospace', 28, bold=True)
        pygame.display.set_caption("Algoritmo Genetico - Celulas Automatas")
        
        # Matplotlib
        self.fig, self.axes = self._setup_plots()
        self.graph_surface = None
    
    def _setup_plots(self):
        """Configura os gráficos"""
        fig, axes = plt.subplots(2, 2, figsize=(5.2, 3.8), dpi=100)
        fig.patch.set_facecolor('#1a1a2e')
        
        for ax in axes.flat:
            ax.set_facecolor('#16213e')
            ax.tick_params(colors='white', labelsize=8)
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            ax.title.set_color('white')
            for spine in ax.spines.values():
                spine.set_color('#404040')
        
        plt.tight_layout(pad=1.5)
        return fig, axes
    
    def update_history(self, geracao, best_fit, avg_fit, diversity, mut_rate, avg_progress):
        """Atualiza histórico de métricas"""
        self.history['geracao'].append(geracao)
        self.history['best_fitness'].append(best_fit)
        self.history['avg_fitness'].append(avg_fit)
        self.history['diversity'].append(diversity)
        self.history['mutation_rate'].append(mut_rate)
        self.history['progress'].append(avg_progress)
    
    def update_plots(self):
        """Atualiza e salva os gráficos"""
        if len(self.history['geracao']) < 2:
            return
        
        gens = list(self.history['geracao'])
        
        # Gráfico 1: Fitness
        ax1 = self.axes[0, 0]
        ax1.clear()
        ax1.set_facecolor('#16213e')
        ax1.plot(gens, list(self.history['best_fitness']), 'g-', lw=2, label='Best')
        ax1.plot(gens, list(self.history['avg_fitness']), 'y-', lw=1.5, label='Avg')
        ax1.fill_between(gens, list(self.history['avg_fitness']), 
                         list(self.history['best_fitness']), alpha=0.2, color='cyan')
        ax1.set_xlabel('Geracao', fontsize=9)
        ax1.set_ylabel('Fitness', fontsize=9)
        ax1.set_title('Fitness', fontsize=10, fontweight='bold')
        ax1.legend(loc='lower right', fontsize=7, facecolor='#16213e', labelcolor='white')
        ax1.grid(True, alpha=0.3, color='gray')
        ax1.tick_params(colors='white', labelsize=7)
        
        # Gráfico 2: Diversidade
        ax2 = self.axes[0, 1]
        ax2.clear()
        ax2.set_facecolor('#16213e')
        div_data = list(self.history['diversity'])
        colors = ['#ff6b6b' if d < 0.3 else '#ffd93d' if d < 0.5 else '#6bcb77' for d in div_data]
        ax2.bar(gens, div_data, color=colors, alpha=0.8, width=max(1, len(gens)//50))
        ax2.axhline(y=0.4, color='#ffd93d', linestyle='--', alpha=0.7, lw=1)
        ax2.set_xlabel('Geracao', fontsize=9)
        ax2.set_ylabel('Diversidade', fontsize=9)
        ax2.set_title('Diversidade Genetica', fontsize=10, fontweight='bold')
        ax2.set_ylim(0, 1)
        ax2.grid(True, alpha=0.3, color='gray')
        ax2.tick_params(colors='white', labelsize=7)
        
        # Gráfico 3: Mutação
        ax3 = self.axes[1, 0]
        ax3.clear()
        ax3.set_facecolor('#16213e')
        ax3.plot(gens, list(self.history['mutation_rate']), 'm-', lw=2)
        ax3.fill_between(gens, 0, list(self.history['mutation_rate']), alpha=0.3, color='magenta')
        ax3.axhline(y=MUTATION_RATE, color='white', linestyle='--', alpha=0.5, lw=1)
        ax3.set_xlabel('Geracao', fontsize=9)
        ax3.set_ylabel('Taxa', fontsize=9)
        ax3.set_title('Mutacao Adaptativa', fontsize=10, fontweight='bold')
        ax3.set_ylim(0, 0.6)
        ax3.grid(True, alpha=0.3, color='gray')
        ax3.tick_params(colors='white', labelsize=7)
        
        # Gráfico 4: Progresso
        ax4 = self.axes[1, 1]
        ax4.clear()
        ax4.set_facecolor('#16213e')
        prog_data = [p * 100 for p in self.history['progress']]
        ax4.plot(gens, prog_data, 'c-', lw=2)
        ax4.fill_between(gens, 0, prog_data, alpha=0.3, color='cyan')
        ax4.set_xlabel('Geracao', fontsize=9)
        ax4.set_ylabel('Progresso (%)', fontsize=9)
        ax4.set_title('Progresso Medio', fontsize=10, fontweight='bold')
        ax4.set_ylim(0, 100)
        ax4.grid(True, alpha=0.3, color='gray')
        ax4.tick_params(colors='white', labelsize=7)
        
        for ax in self.axes.flat:
            ax.tick_params(colors='white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            ax.title.set_color('white')
        
        plt.tight_layout(pad=1.5)
        self.fig.savefig('grafico_evolucao.png', facecolor='#1a1a2e', edgecolor='none')
        
        # Carrega como superfície pygame
        try:
            self.graph_surface = pygame.image.load('grafico_evolucao.png')
        except:
            pass
    
    def draw_board(self, matrix, population):
        """Desenha o tabuleiro e indivíduos"""
        for i in range(len(matrix)):
            for j in range(len(matrix[0])):
                if i == 0 and j == 0:
                    color = YELLOW
                elif i == len(matrix) - 1 and j == len(matrix[0]) - 1:
                    color = CYAN
                elif matrix[i][j] == 0:
                    color = WHITE
                else:
                    color = GREEN
                
                rect = (j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                pygame.draw.rect(self.screen, color, rect, 0)
                pygame.draw.rect(self.screen, BLACK, rect, MARGIN)
        
        # Desenha indivíduos vivos
        for ind in population:
            if ind['vivo']:
                x, y = ind['posicao']['x'], ind['posicao']['y']
                rect = (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                pygame.draw.rect(self.screen, ind['cor'], rect, 0)
                pygame.draw.rect(self.screen, BLACK, rect, MARGIN)
    
    def draw_info(self, stats):
        """Desenha informações na tela"""
        # Fundo do painel de info
        info_y = self.board_height + 5
        pygame.draw.rect(self.screen, DARK_GRAY, (0, info_y, self.board_width, HEADER))
        
        # Linha 1
        y1 = info_y + 10
        self.screen.blit(self.font.render(f"Geracao: {stats['geracao']}", True, YELLOW), (10, y1))
        self.screen.blit(self.font.render(f"Iter: {stats['iteracao']}", True, WHITE), (180, y1))
        vivos_color = GREEN if stats['vivos'] > 10 else RED
        self.screen.blit(self.font.render(f"Vivos: {stats['vivos']}", True, vivos_color), (310, y1))
        self.screen.blit(self.font.render(f"Best: {stats['best']:.1f}", True, PURPLE), (450, y1))
        
        # Linha 2
        y2 = y1 + 28
        div = stats['diversity']
        div_color = GREEN if div > 0.5 else YELLOW if div > 0.3 else RED
        self.screen.blit(self.font_small.render(f"Div: {div:.2f}", True, div_color), (10, y2))
        self.screen.blit(self.font_small.render(f"Mut: {stats['mutation']:.2f}", True, PURPLE), (120, y2))
        stag_color = RED if stats['stagnation'] > 10 else WHITE
        self.screen.blit(self.font_small.render(f"Stag: {stats['stagnation']}", True, stag_color), (240, y2))
        self.screen.blit(self.font_small.render(f"Prog: {stats['progress']:.0%}", True, CYAN), (360, y2))
        
        # Linha 3
        y3 = y2 + 24
        self.screen.blit(self.font_small.render(f"Avg: {stats['avg']:.1f}", True, GRAY), (10, y3))
        
        # Gráfico na lateral
        if self.graph_surface:
            scaled = pygame.transform.scale(self.graph_surface, (GRAPH_WIDTH, GRAPH_HEIGHT))
            self.screen.blit(scaled, (self.board_width + 15, 10))
    
    def draw(self, matrix, population, stats):
        """Desenha tudo"""
        self.screen.fill(BLACK)
        self.draw_board(matrix, population)
        self.draw_info(stats)
        pygame.display.flip()
    
    def check_events(self):
        """Verifica eventos do pygame"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True
    
    def quit(self):
        """Fecha pygame"""
        pygame.quit()
