import heapq
import csv


class Nodo:
    def __init__(self, state, parent=None, action=None, g=0, h=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.g = g
        self.h = h

    # implementación el operador Nodo < Nodo
    def __lt__(self, other):
        return (self.g + self.h) < (other.g + other.h)


class Mapa:
    def __init__(self, input_file):
        self.matriz = self.read_input(input_file)
        # (filas, columnas):
        self.dimensiones = (len(self.matriz), len(self.matriz[0]))

    # Returns first occurrence of a value and number of ocurrences
    def find_value(self, value: str):
        n = 0
        coord = (-1, -1)
        for i in range(self.dimensiones[0]):
            for j in range(self.dimensiones[1]):
                if self.matriz[i][j] == value and n == 0:
                    coord = i, j
                    n = n + 1
        return coord, n

    def get_coste(self, coord):
        char = self.matriz[coord[0]][coord[1]]
        try:
            integer_number = int(char)
            return integer_number
        except ValueError as e:
            if char in {'N', 'C', 'CC', 'CN', 'P'}:
                return 1
            else:
                return -1

    # Lee el csv de entrada y devuelve un objeto Mapa con la información de costes
    def read_input(self, input_file) -> list[list[str]]:
        matriz = []

        # Abrir el archivo CSV y leer los datos
        with open(input_file, newline='') as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=';')
            for fila in csv_reader:
                matriz.append(fila)

        # Devuelve la matriz
        return matriz


class Estado:
    def __init__(self, posicion, carga, asientos_c, asientos_n):
        self.posicion = posicion
        self.carga = carga
        self.asientos_c = asientos_c
        self.asientos_n = asientos_n


# Implementación del algoritmo de búsqueda informada A*
def astar_search(problema, heuristic):
    nodo_inicial = Nodo(problema.initial_state)
    abierta = []
    heapq.heappush(abierta, nodo_inicial)
    cerrada = set()

    while abierta:

        # pseudocódigo 2: comprueba que N no esté en cerrada
        while True:
            current_node = heapq.heappop(abierta)  # Quitar el primer nodo de abierta
            if current_node not in cerrada:
                break

        if problema.es_final(current_node.state):
            return current_node  # solución óptima encontrada

        cerrada.add(current_node)  # N entra en CERRADA

        # generar el conjunto de sucesores
        for action, state, cost in problema.get_successors(current_node.state):
            if state not in abierta:  # insertar en orden en ABIERTA cada sucesor de N
                new_g = current_node.g + cost
                new_h = heuristic(state, problema)
                new_nodo = Nodo(state, current_node, action, new_g, new_h)
                heapq.heappush(abierta, new_nodo)

    return None


# Implementación de la solución al problema de los Traslados
class Problema:
    def __init__(self, initial_state, goal_state):
        self.initial_state = initial_state
        self.goal_state = goal_state

    def es_final(self, state):
        return state == self.goal_state

    def get_successors(self, state):
        # Implement this method to generate successors for a given state
        pass


# Example heuristic functions (Replace these with your heuristics)
def heuristica_1(state, problem):
    # Implement your heuristic here
    pass


def heuristica_2(state, problem):
    # Implement another heuristic here
    pass


# Búsqueda no informada, equivalente a Dijkstra
def heuristica_3(state, problem):
    return 0;


# Ejemplo de uso
# -------------------------------------------------------------------------------
mapa = Mapa("ASTAR-tests/mapa.csv")
parking_coord, parking_n = mapa.find_value('P')
if parking_n > 1:
    print("Más de un parking")
carga_inicial = 50
asientos_contag = 2
asientos_totales = 10
estado_inicial = Estado(parking_coord, carga_inicial, list([0] * asientos_contag),
                        list([0] * (asientos_totales - asientos_contag)))

estado_final = Estado(parking_coord, -1, list([0] * asientos_contag),
                      list([0] * (asientos_totales - asientos_contag)))
# problema = Problema(initial_state, goal_state)
# result = astar_search(problema, heuristica_3)
# if result:
#     # Process the result
#     pass
