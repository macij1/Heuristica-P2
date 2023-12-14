import heapq
import csv


class Nodo:
    def __init__(self, estado, padre=None, g=0, h=0):
        self.estado = estado
        self.padre = padre
        self.g = g
        self.h = h

    # implementación el operador Nodo < Nodo
    def __lt__(self, other):
        if (self.g + self.h) == (other.g + other.h):
            return self.h < other.h
        else:
            return (self.g + self.h) < (other.g + other.h)

    def __eq__(self, other):
        return self.estado == other.estado and \
            self.padre == self.padre


class Estado:
    def __init__(self, posicion, carga, asientos_c, asientos_n, pac_restantes, pac_recogidos):
        self.posicion = posicion
        self.carga = carga
        self.asientos_c = asientos_c
        self.asientos_n = asientos_n
        self.pac_restantes = pac_restantes  # pacientes restantes
        self.pac_recogidos = pac_recogidos

    def __str__(self):
        print("ESTADO:")
        print("\t"+str(self.posicion)+", "+str(self.carga) + ", restantes: " + str(self.pac_restantes))
        print(self.asientos_c)
        print(self.asientos_n)
        print("Recogidos" + str(self.pac_recogidos))

    def __eq__(self, other):
        return self.posicion == other.posicion and \
        self.carga == other.carga and \
        self.asientos_c == other.asientos_c and \
        self.asientos_n == other.asientos_n and \
        self.pac_restantes == other.pac_restantes and \
        self.pac_recogidos == other.pac_recogidos

    # Intenta añadir un C al bus. Si no hay sitio, devuelve 0. En caso de éxito, devuelve 1
    def añadir_c(self):
        for i in range(len(self.asientos_c)):
            if self.asientos_c[i] == '0':
                self.asientos_c[i] = 'C'
                return 1
        return 0  # Zona de contagiados llena

    # Intenta añadir un N al bus. Si no hay sitio, devuelve 0. En caso de éxito, devuelve 1
    def añadir_n(self):
        for i in range(len(self.asientos_n)):
            if self.asientos_n[i] == '0':
                self.asientos_n[i] = 'N'
                return 1  # Se sienta en un asiento normal
        for i in range(len(self.asientos_c)):
            if self.asientos_c[i] == '0':
                self.asientos_n[i] = 'N'
                return 1  # Se sienta en un asiento especial
        return 0  # Bus lleno

    # Intenta dejar pacientes con enfermedad contagiosa en un centro CC.
    def dejar_cc(self):
        ret = 0
        for i in range(len(self.asientos_c)):
            if self.asientos_c[i] == 'C':  # Se bajan del bus todos los Cs
                self.asientos_c[i] = '0'
                self.pac_restantes = self.pac_restantes - 1
                ret = ret + 1
        return ret

    # Intenta dejar Cs en un centro CN.
    # ¡Los Cs deben ser los últimos en subirse y los primeros en bajarse!
    def dejar_cn(self):
        ret = 0
        for i in range(len(self.asientos_c)):
            if self.asientos_c[i] == 'N':  # Se bajan del bus todos los Ns
                self.asientos_c[i] = '0'
                self.pac_restantes = self.pac_restantes - 1
                ret = ret + 1
        for i in range(len(self.asientos_n)):
            if self.asientos_n[i] == 'N':  # Se bajan del bus todos los Ns
                self.asientos_n[i] = '0'
                self.pac_restantes = self.pac_restantes - 1
                ret = ret + 1
        return ret


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
                if self.matriz[i][j] == value:
                    if n == 0:
                        coord = i, j
                    n = n + 1
        return coord, n

    # Devuelve el tipo de casilla en coord y su coste correspondiente
    def get_casilla(self, coord):
        if coord[0] < 0 or coord[0] >= self.dimensiones[0] or coord[1] < 0 or coord[1] >= self.dimensiones[1]:
            # print("Error, index out of bounds")
            return "!", -1
        char = self.matriz[coord[0]][coord[1]]
        try:
            integer_number = int(char)
            return char, integer_number
        except ValueError as e:
            if char in {'N', 'C', 'CC', 'CN', 'P'}:
                return char, 1
            else:
                return char, -1  # 'X' o fuera del recinto

    # Lee el csv de entrada y devuelve un objeto Mapa con la información de costes
    def read_input(self, input_file) -> list[list[str]]:
        matriz = []

        # Abrir el archivo CSV y leer los datos
        with open(input_file, newline='') as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=';')
            for fila in csv_reader:
                matriz.append(fila)

        return matriz


# Implementación del algoritmo de búsqueda informada A*
def astar_search(problema, heuristic) -> Nodo:
    
    def is_in_abierta(nodo):
        for a in abierta:
            if a.estado == nodo.estado and (a.h + a.g < nodo.h + nodo.g):
                return True

    nodo_inicial = Nodo(problema.estado_inicial, None, 0, 0)
    abierta = []
    heapq.heappush(abierta, nodo_inicial)
    cerrada = []
    nodos_expandidos = 0

    while abierta:
        # pseudocódigo 2: comprueba que N no esté en cerrada
        while True:
            current_node = heapq.heappop(abierta)  # Quitar el primer nodo de abierta
            if problema.test_meta(current_node.estado):
                print("Coste: " + str(current_node.g))
                print("Nodos expandidos: " + str(nodos_expandidos))
                return current_node  # solución óptima encontrada: nodo meta expandido
            elif current_node not in cerrada:  # Aquí podríamos descartar nodos (Alvaro)
                break

        cerrada.append(current_node)  # N entra en CERRADA
        sucesores = problema.get_sucesores(current_node.estado)
        # generar el conjunto de sucesores
        for estado, coste in sucesores:
            new_g = current_node.g + coste
            new_h = heuristic(estado, problema)
            new_nodo = Nodo(estado, current_node, new_g, new_h)
            if not is_in_abierta(new_nodo):  # insertar en orden en ABIERTA cada sucesor de N
                heapq.heappush(abierta, new_nodo)
                nodos_expandidos = nodos_expandidos + 1
                print(nodos_expandidos)

    return None


# Implementación de la solución al problema de los Traslados
class Problema:
    def __init__(self, estado_inicial, mapa):
        self.estado_inicial = estado_inicial
        self.mapa = mapa

    def test_meta(self, estado):
        return (estado.posicion == self.mapa.find_value('P')[0]) and estado.pac_restantes == 0

    # Genera el conjunto de sucesores a nivel estado
    def get_sucesores(self, estado):
        sucesores = []
        for i, j in {(1, 0), (0, 1), (-1, 0), (0, -1)}:  # Arriba, derecha, abajo, izquierda
            pos = (estado.posicion[0] - i, estado.posicion[1] - j)
            tipo, coste = self.mapa.get_casilla(pos)

            if coste == -1:
                continue  # Estado inválido: 'X' o out-of-bounds

            # Creación de estado sucesor
            nuevo_estado = Estado(pos, estado.carga - coste, estado.asientos_c[:], estado.asientos_n[:],
                                  estado.pac_restantes, estado.pac_recogidos[:])

            if nuevo_estado.carga == 0 and tipo != 'P':
                break  # Estado inválido, la ambulancia se ha quedado sin energía

            # Actualizar carga
            if tipo == 'P':
                nuevo_estado.carga = 50  # Recarga de energía

            # Movimiento de pacientes:

            if tipo == 'C':
                # Se prohíbe pasar por el domicilio de un paciente recogido
                if pos in nuevo_estado.pac_recogidos:
                    continue
                if nuevo_estado.añadir_c() == 1:  # Intenta añadir un paciente con enfermedad contagiosa
                    nuevo_estado.pac_recogidos.append(pos)

            elif tipo == 'N':
                for a in range(len(estado.asientos_c)):
                    if estado.asientos_c[a] == 'C':  # Si hay algún C, no se pueden recoger Ns hasta que bajen los Cs
                        continue  # Estado inválido
                # Se prohíbe pasar por el domicilio de un paciente recogido
                if pos in nuevo_estado.pac_recogidos:
                    continue
                if nuevo_estado.añadir_n() == 1:  # Intenta añadir un paciente sin enfermedad contagiosa
                    nuevo_estado.pac_recogidos.append(pos)

            elif tipo == 'CC':
                if nuevo_estado.dejar_cc() == 0:  # Intenta dejar pacientes C en su centro
                    continue  # Estado inválido

            elif tipo == 'CN':
                for a in range(len(estado.asientos_c)):
                    if estado.asientos_n[a] == 'C':  # Si hay algún C, no se pueden bajar Ns hasta que bajen los Cs
                        continue  # Estado inválido
                if nuevo_estado.dejar_cn() == 0:  # Intenta dejar pacientes N en su centro
                    continue  # Estado inválido

            sucesores.append((nuevo_estado, coste))

        return sucesores
            

def heuristica_1(estado, problema):
    pass


def heuristica_2(estado, problema):
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
    exit(-1)
carga_inicial = 50
asientos_contag = 2
asientos_totales = 10
pacientes_restantes = mapa.find_value('C')[1] + mapa.find_value('N')[1]
paciente_recogidos = []
estado_inicial = Estado(parking_coord, carga_inicial, list(['0'] * asientos_contag),
                        list(['0'] * (asientos_totales - asientos_contag)), pacientes_restantes, paciente_recogidos)
problema = Problema(estado_inicial, mapa)
result = astar_search(problema, heuristica_3)
current = result
result_list = []
while current:
    result_list.append(current)
    current = current.padre
print("END")
while True:
    pass
# if result:
#     # Process the result
#     pass
