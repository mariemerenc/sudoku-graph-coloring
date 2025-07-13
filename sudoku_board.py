from graph import Graph, Vertex

class SudokuBoard:
    """Classe para representar um tabuleiro de Sudoku"""
    
    def __init__(self, grid=None):
        self.grid = grid if grid else [[0 for _ in range(9)] for _ in range(9)]
        self.graph = None
        self.original_grid = None  #estado original da grade
        
    
    def load_from_string(self, sudoku_string):
        """Carrega o tabuleiro a partir de uma string"""
        lines = sudoku_string.strip().split('\n')
        self.grid = []
        
        for line in lines:
            row = []
            
            for char in line:
                if char.isdigit():
                    row.append(int(char))
                else:
                    row.append(0)  #troca caracteres não numéricos por 0
                    
            #garante que a linha tenha exatamente 9 elementos
            while len(row) < 9:
                row.append(0)
            if len(row) > 9:
                row = row[:9]
                
            self.grid.append(row)
        
        #garante que a grade tenha exatamente 9 linhas
        while len(self.grid) < 9:
            self.grid.append([0] * 9)
        if len(self.grid) > 9:
            self.grid = self.grid[:9]
            
        #estado original da grade
        self.original_grid = [row[:] for row in self.grid]
        
        
    def set_cell(self, row, col, value):
        self.grid[row][col] = value
        
    
    def is_empty(self, row, col):
        """Verifica se uma célula está vazia"""
        return self.grid[row][col] == 0
    
    
    def get_row_values(self, row):
        """Retorna os valores de uma linha"""
        if not (0 <= row < 9):
            return []
        return [val for val in self.grid[row] if val != 0]
    
    
    def get_col_values(self, col):
        """Retorna os valores de uma coluna"""
        if not (0 <= col < 9):
            return []
        return [self.grid[row][col] for row in range(9) if self.grid[row][col] != 0]
    
    
    def get_box_values(self, row, col):
        """Retorna os valores de um bloco 3x3"""
        if not (0 <= row < 9 and 0 <= col < 9):
            return []
            
        box_row = (row // 3) * 3
        box_col = (col // 3) * 3
        values = []
        
        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                if self.grid[r][c] != 0:
                    values.append(self.grid[r][c])
                    
        return values
    
    
    def is_valid_placement(self, row, col, value):
        """Verifica se um valor pode ser colocado em uma posição"""
        if not (0 <= row < 9 and 0 <= col < 9):
            return False
        if not (1 <= value <= 9):
            return False
            
        # verifica se o valor já está presente na linha
        if value in self.get_row_values(row):
            return False
        
        # verifica se o valor já está presente na coluna
        if value in self.get_col_values(col):
            return False
        
        # verifica se o valor já está presente no bloco 3x3
        if value in self.get_box_values(row, col):
            return False
        
        return True
    
    
    def is_valid(self):
        """Verifica se o estado atual do tabuleiro é válido"""
        for row in range(9):
            for col in range(9):
                if not self.is_empty(row, col):
                    value = self.grid[row][col]
                    # temporariamente remove o valor para verificar a validade
                    self.grid[row][col] = 0
                    if not self.is_valid_placement(row, col, value):
                        self.grid[row][col] = value
                        return False
                    
                    self.grid[row][col] = value
        
        return True
    
    
    def is_complete(self):
        """Verifica se o tabuleiro está completamente preenchido"""
        return all(self.grid[row][col] != 0 for row in range(9) for col in range(9))
    
    
    def is_solved(self):
        """Verifica se o tabuleiro está resolvido"""
        return self.is_complete() and self.is_valid()

        
    def copy(self):
        """Cria uma cópia do tabuleiro"""
        new_board = SudokuBoard()
        new_board.grid = [row[:] for row in self.grid]
        if self.original_grid is not None:
            new_board.original_grid = [row[:] for row in self.original_grid]
        return new_board
    
    
    def to_graph(self):
        """Converte o tabuleiro para um grafo"""
        self.graph = Graph()
        
        # add todos os vértices
        for row in range(9):
            for col in range(9):
                vertex_id = row * 9 + col
                value = self.grid[row][col]
                vertex = Vertex(vertex_id, value, row, col)
                
                #se a célula já tem valor, define como cor
                if value != 0:
                    vertex.color = value
                
                self.graph.add_vertex(vertex)
                
        
        #add arestas (entre células que não podem ter o mesmo valor)
        for row in range(9):
            for col in range(9):
                vertex_id = row * 9 + col
                
                # conecta com outras células na mesma linha
                for c in range(9):
                    if c != col:
                        neighbor_id = row * 9 + c
                        self.graph.add_edge(vertex_id, neighbor_id)
                        
                # conecta com outras células na mesma coluna
                for r in range(9):
                    if r != row:
                        neighbor_id = r * 9 + col
                        self.graph.add_edge(vertex_id, neighbor_id)
                        
                # conecta com outras células no mesmo bloco
                box_row = (row // 3) * 3
                box_col = (col // 3) * 3
                for r in range(box_row, box_row + 3):
                    for c in range(box_col, box_col + 3):
                        if r != row or c != col:
                            neighbor_id = r * 9 + c
                            self.graph.add_edge(vertex_id, neighbor_id)
                            
                            
        return self.graph 
    

    def update_from_graph(self, graph):
        """Atualiza o tabuleiro a partir de um grafo colorido"""
        for vertex in graph.vertices.values():
            if vertex.color is not None and hasattr(vertex, 'row') and hasattr(vertex, 'col'):
                if 0 <= vertex.row < 9 and 0 <= vertex.col < 9:
                    self.grid[vertex.row][vertex.col] = vertex.color
