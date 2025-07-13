import time
from typing import List, Optional, Tuple
from graph import Graph, Vertex
from sudoku_board import SudokuBoard


class SimpleSudokuSolver:
    """Classe para resolver Sudoku usando backtracking simples"""
    
    def __init__(self):
        self.nodes_explored = 0
        self.backtrack_count = 0
        self.start_time = 0
        self.solution_time = 0
        
    def reset_counters(self):
        """Reseta os contadores de performance"""
        self.nodes_explored = 0
        self.backtrack_count = 0
        self.start_time = 0
        self.solution_time = 0
    
    def solve(self, board: SudokuBoard) -> Tuple[bool, float]:
        """Resolve o Sudoku usando backtracking simples"""
        self.reset_counters()
        self.start_time = time.time()
        
        # verifica se o estado inicial é válido
        if not board.is_valid():
            self.solution_time = time.time() - self.start_time
            return False, self.solution_time
        
        # backtracking simples
        success = self.backtrack_solve(board)
        
        self.solution_time = time.time() - self.start_time
        return success, self.solution_time
    
    def backtrack_solve(self, board: SudokuBoard) -> bool:
        """Algoritmo de backtracking simples para resolver o Sudoku"""
        # encontra a próxima célula vazia
        empty_cell = self.find_next_empty_cell(board)
        if empty_cell is None:
            return True  #caso todas as células estejam preenchidas
        
        row, col = empty_cell
        self.nodes_explored += 1
        
        #tentativa de colocar valores de 1 a 9
        for value in range(1, 10):
            if board.is_valid_placement(row, col, value):
                #coloca o valor
                board.set_cell(row, col, value)
                
                #recursão
                if self.backtrack_solve(board):
                    return True
                
                # backtrack
                board.set_cell(row, col, 0)
                self.backtrack_count += 1
        
        return False
    
    def find_next_empty_cell(self, board: SudokuBoard) -> Optional[Tuple[int, int]]:
        """Encontra a próxima célula vazia em sequência"""
        for row in range(9):
            for col in range(9):
                if board.is_empty(row, col):
                    return (row, col)
        return None
    
    def get_stats(self):
        """Estatísticas da resolução"""
        return {
            'nodes_explored': self.nodes_explored,
            'backtrack_count': self.backtrack_count,
            'solution_time': self.solution_time
        }


class DSATURSudokuSolver:
    """Classe para resolver Sudoku usando backtracking orientado pelo algoritmo DSATUR"""
    def __init__(self):
        self.nodes_explored = 0
        self.backtrack_count = 0
        self.start_time = 0
        self.solution_time = 0
        
    def reset_counters(self):
        """Reseta os contadores de performance"""
        self.nodes_explored = 0
        self.backtrack_count = 0
        self.start_time = 0
        self.solution_time = 0
    
    def solve(self, board: SudokuBoard) -> Tuple[bool, float]:
        """Resolve o Sudoku usando backtracking com DSATUR"""
        self.reset_counters()
        self.start_time = time.time()
        
        # transforma o tabuleiro em grafo
        graph = board.to_graph()
        
        # verifica se o estado inicial é válido
        if not graph.is_valid_coloring():
            self.solution_time = time.time() - self.start_time
            return False, self.solution_time
        
        # DSATUR com backtracking
        success = self.dsatur_backtrack(graph)
        
        # att o tabuleiro
        if success:
            board.update_from_graph(graph)
        
        self.solution_time = time.time() - self.start_time
        return success, self.solution_time
    
    def dsatur_backtrack(self, graph: Graph) -> bool:
        """Algoritmo DSATUR com backtracking"""
        #verifica se todos os vértices estão coloridos
        uncolored = graph.get_uncolored_vertices()
        if not uncolored:
            return graph.is_valid_coloring()
        
        #escolha do próx vértice usando DSATUR
        vertex = self.select_vertex_dsatur(graph, uncolored)
        self.nodes_explored += 1
        
        #tenta cada cor possível
        available_colors = vertex.get_available_colors()
        
        #se não há cores disponíveis, falha
        if not available_colors:
            return False
            
        for color in sorted(available_colors):
            #atribui a cor
            vertex.color = color
            
            #verifica se a coloração é válida
            if self.is_valid_coloring_local(vertex):
                #att saturações
                graph.update_all_saturations()
                
                #recursão
                if self.dsatur_backtrack(graph):
                    return True
            
            #backtrack
            vertex.color = None
            self.backtrack_count += 1
        
        return False
    
    def select_vertex_dsatur(self, graph: Graph, uncolored: List[Vertex]) -> Vertex:
        """
        Seleciona o próximo vértice usando a heurística DSATUR
        1. Maior grau de saturação
        2. Em caso de empate, maior grau
        3. Em caso de empate, menor domínio
        """
        # att saturações
        graph.update_all_saturations()
        
        def dsatur_key(vertex):
            available_colors = len(vertex.get_available_colors())
            return (
                -vertex.saturation,        # maior saturação
                -len(vertex.neighbors),    # maior grau
                available_colors           # menor domínio
            )
        
        return min(uncolored, key=dsatur_key)
    
    def is_valid_coloring_local(self, vertex: Vertex) -> bool:
        """Verifica se a coloração de um vértice é válida"""
        if vertex.color is None:
            return True
        
        for neighbor in vertex.neighbors:
            if neighbor.color == vertex.color:
                return False
        
        return True
    
    def get_stats(self):
        """Estatísticas da resolução"""
        return {
            'nodes_explored': self.nodes_explored,
            'backtrack_count': self.backtrack_count,
            'solution_time': self.solution_time
        }


def solve_sudoku_simple(board: SudokuBoard) -> Tuple[bool, float]:
    """Função para resolver Sudoku com backtracking simples"""
    solver = SimpleSudokuSolver()
    return solver.solve(board)


def solve_sudoku_dsatur(board: SudokuBoard) -> Tuple[bool, float]:
    """Função para resolver Sudoku com DSATUR"""
    solver = DSATURSudokuSolver()
    return solver.solve(board)
