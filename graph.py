class Vertex:
    """Representação de um vértice no grafo do Sudoku"""
    def __init__(self, id, value=0, row=0, col=0):
        self.id = id
        self.row = row
        self.col = col
        self.value = value
        self.color = None
        self.neighbors = set()
        self.is_fixed = False # verdadeiro se é uma célula preenchida previamente
        
        # se valor!=0, a célula é fixa, não pode ser alterada e não tem domínio
        if value != 0:
            self.domain = set()
            self.color = value
            self.is_fixed = True
        else:
            self.domain = set(range(1, 10))
        
        #saturação inicial é 0
        self.saturation = 0
        
    def add_neighbor(self, neighbor):
        """Adiciona um vizinho ao vértice"""
        self.neighbors.add(neighbor)
        neighbor.neighbors.add(self)
        
    def get_available_colors(self):
        """Retorna as cores disponíveis para este vértice"""
        
        if self.is_fixed:
            return set() # não há cores disponíveis se é uma célula fixa
        
        used_colors = set()
        for neighbor in self.neighbors:
            if neighbor.color is not None:
                used_colors.add(neighbor.color)
        
        # retorna as cores não usadas pelos vizinhos 
        return self.domain - used_colors
    
    def update_saturation(self):
        """Atualiza o grau de saturação"""
        
        used_colors = set()
        for neighbor in self.neighbors:
            if neighbor.color is not None:
                used_colors.add(neighbor.color)
        
        # grau de saturação = número de cores únicas usadas pelos vizinhos
        self.saturation = len(used_colors)   
    
    def is_colored(self):
        """Verifica se o vértice está colorido"""
        return self.color is not None
    

    
class Graph:
    """Representação do grafo para coloração"""
    def __init__(self):
        self.vertices = {}
        self.edges = []
        self.size = 0
        
    def add_vertex(self, vertex):
        """Adiciona um vértice ao grafo"""
        self.vertices[vertex.id] = vertex
        self.size += 1
    
    def add_edge(self, vertex1_id, vertex2_id):
        """Adiciona uma aresta entre dois vértices"""
        if vertex1_id in self.vertices and vertex2_id in self.vertices:
            vertex1 = self.vertices[vertex1_id]
            vertex2 = self.vertices[vertex2_id]
            vertex1.add_neighbor(vertex2)
            self.edges.append((vertex1, vertex2))

    def get_uncolored_vertices(self):
        """Retorna vértices não coloridos (sem células fixas)"""
        return [v for v in self.vertices.values() if not v.is_colored() and not v.is_fixed]
    
    def update_all_saturations(self):
        """Atualiza a saturação de todos os vértices"""
        for vertex in self.vertices.values():
            vertex.update_saturation()
            
    def is_valid_coloring(self):
        """Verifica se a coloração atual é válida"""
        for vertex in self.vertices.values():
            #se o vértice está colorido, verifica se não conflita com vizinhos
            if vertex.color is not None:
                for neighbor in vertex.neighbors:
                    if neighbor.color is not None and vertex.color == neighbor.color:
                        return False
        return True