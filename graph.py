class Node:
    def __init__(self, idx, data=0):
        """
        Node class constructor.
        Represents a cell in the Sudoku board.

        Args:
            idx (int): unique numerical Id for the node (1 to 81) 
            data (any, optional): optional value associated with the node (sudoku number/color)
        
        Returns:
            None
        """
        self.id = idx
        self.data = data
        self.connected_to = set()

    def add_neighbor(self, nbr_node):
        """
        Adds a connection to a neighboring node.
        'nbr_node is expected to be a Node object.

        Args:
            nbr_node (Node): the node object of the neighbor to be connected.
        
        Returns:
            None
        """
        self.connected_to.add(nbr_node.get_id())

    def get_connections(self):
        """
        Returns a collection of the Ids of neighboring nodes.

        Args:
            None
        
        Returns:
            set: a set containing the Ids of all connected neighbor nodes.
        """
        return self.connected_to
    
    def get_id(self):
        """
        Returns the Id of this node.

        Args:
            None
        
        Returns:
            int: the Id of this node.
        """
        return self.id

    def get_data(self):
        """
        Returns the data (value/color) stored in this node.

        Args:
            None
        
        Returns:
            any: the data stored in this node.
        """
        return self.data

    def set_data(self, data):
        """
        Sets the data (value/color) for this node.

        Args:
            data (any): the new data to set for the node.

        Returns:
            None
        """

        self.data = data

    def is_connected_to(self, nbr_id):
        """
        Checks if this node is connected to a specific neighbor.

        Args:
            nbr_id (int): Id of the neighboring node to check.
        
        Returns:
            bool: True if connected, False otherwise.
        """
        return nbr_id in self.connected_to

    def __str__(self):
        """
        String representation of the node.

        Args:
            None
        
        Returns:
            str: a string representation of the node.
        """
        return f"Node {self.id} (Data: {self.data}) | Connected to: {list(self.get_connections())}"



class Graph:
    def __init__(self):
        """
        Graph class constructor.
        Manages a collection of nodes and their connections.

        Args:
            None

        Returns:
            None
        """

        self.all_nodes = {}
        self.num_vtxs = 0
    
    def add_node(self, node_id, data=0):
        """
        Adds a new node to the graph.
        If the node already exists, it returns the existing node.

        Args:
            node_id (int): the unique Id for the new node.
            data (any, optional): optional data to associate with the node.

        Returns:
            Node: the node object (either newly created or existing).
        """

        if node_id in self.all_nodes:
            print(f"Warning: Node {node_id} already exists.")
            return self.all_nodes[node_id]
        
        
        self.num_vtxs+=1
        new_node = Node(idx=node_id, data=data)
        self.all_nodes[node_id] = new_node

        return new_node

    
    def get_node(self, node_id):
        """
        Retrieves a node from the graph by its Id.

        Args:
            node_id (int): the Id of the node to retrieve.

        Returns: 
            Node or None: the node object if found, otherwise None.
        """

        return self.all_nodes.get(node_id)

    
    def add_edge(self, src_node_id, dest_node_id):
        """
        Adds an undirected edge between 2 nodes.
        If the nodes don't exist, they will be created.

        Args:
            src_node_id (int): the Id of the source node.
            dest_node_id (int): the Id of the destination node.

        Returns:
            None
        """

        if src_node_id not in self.all_nodes:
            self.add_node(src_node_id)
        if dest_node_id not in self.all_nodes:
            self.add_node(dest_node_id)

        node_src = self.all_nodes[src_node_id]
        node_dest = self.all_nodes[dest_node_id]

        node_src.add_neighbor(node_dest)
        node_dest.add_neighbor(node_src)

    
    def get_neighbors(self, node_id):
        """
        Gets all neighbors of a given node.

        Args:
            node_id (int): the Id of the node whose neighbors are to be retrieved.
        
        Returns:
            set: a set of neighbors Ids, or an empty set if the node doesn't exist/has no neighbors.
        """

        node = self.get_node(node_id)

        if node:
            return node.get_connections()
        
        return set() # Return an empty set if node not found
    

    def is_neighbor(self, node1_id, node2_id):
        """
        Checks if 2 nodes are neighbors.

        Args:
            node1_id (int): the Id of the first node.
            node2_id (int): the Id of the second node.

        Returns:
            bool: True if they are neighbors, False otherwise.
        """

        node1 = self.get_node(node1_id)

        if node1:
            return node2_id in node1.get_connections()
        
        return False #node1 doesn't exist


    def get_all_node_ids(self):
        """
        Returns an iterable of all node Ids currently in the graph.

        Args:
            None
        
        Returns:
            collections.abc.KeysView: an iterable view of all node Ids.
        """

        return self.all_nodes.keys()

    
    def get_degree(self, node_id):
        """
        Returns the degree of a given node (number of neighbors).

        Args:
            node_id (int): the Id of the node.
        
        Returns:
            int: the degree of the node, or 0 if the node doesn't exist.
        """

        node = self.get_node(node_id)
        
        if node:
            return len(node.get_connections())

        return 0


    def __str__(self):
        """
        String representation of the graph, listing all nodes and their connections.

        Args:
            None
        
        Returns:
            str: a string representation of the graph.
        """

        output = "Graph:\n"
        for node_id in self.all_nodes:
            node = self.all_nodes[node_id]
            connections = ", ".join(map(str, node.get_connections())) if node.get_connections() else "None"
            output += f" Node {node_id} (Data: {node.get_data()}) --> Neighbors: [{connections}]\n"
        
        return output
