import heapq
import csv
import sys
import time


class Nodo:
    def __init__(self, estado, padre=None, g=0, h=0):
        self.estado = estado
        self.padre = padre
        self.g = g
        self.h = h

    # Implementación el operador Nodo < Nodo
    def __lt__(self, other):
        if (self.g + self.h) == (other.g + other.h):
            return self.h < other.h  # Criterio de empate en abierta: mejor h
        else:
            return (self.g + self.h) < (other.g + other.h)

    def __eq__(self, other):
        if (other.padre is None) or (self.padre is None):
            return False
        return self.estado == other.estado and self.padre == other.padre


class Estado:
    def __init__(self, posicion, carga, asientos_c, asientos_n, pac_restantes, pac_recogidos):
        self.posicion = posicion
        self.carga = carga
        self.asientos_c = asientos_c
        self.asientos_n = asientos_n
        self.pac_restantes = pac_restantes  # pacientes restantes
        self.pac_recogidos = pac_recogidos

    def __str__(self):
        return "ESTADO:\n" + "\t" + str(self.posicion) + ", " + str(self.carga)  # \
        # + ", restantes: " + str(self.pac_restantes) + "\n" +str(self.asientos_c) + \
        # "\n" +str(self.asientos_n) + "\n" + "Recogidos" + str(self.pac_recogidos)

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

    def lleva_infectados(self):
        for a in range(len(self.asientos_c)):
            if self.asientos_c[a] == 'C':  # Hay algún C
                return True
        return False


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
                return char, -1  # 'X'

    # Lee el csv de entrada y devuelve un objeto Mapa con la información de costes
    def read_input(self, input) -> list[list[str]]:
        matriz = []

        # Abrir el archivo CSV y leer los datos
        with open(input, newline='') as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=';')
            for fila in csv_reader:
                matriz.append(fila)

        return matriz


# Implementación del algoritmo de búsqueda informada A*
def astar_search(problema, heuristica) -> Nodo:
    def is_in_abierta(nodo):  # búsqueda lineal en el heap
        for a in abierta:
            # Se descarta el mismo estado con un coste mayor. Se entiende como repetición de movimientos
            if a.estado == nodo.estado and (a.h + a.g <= nodo.h + nodo.g):
                return True
        return False

    def is_in_cerrada(nodo):  # búsqueda lineal en el heap
        for a in cerrada:
            # Se descarta el mismo estado
            if a.estado == nodo.estado:
                return True
        return False

    nodo_inicial = Nodo(problema.estado_inicial, None, 0, 0)
    abierta = []
    heapq.heappush(abierta, nodo_inicial)
    cerrada = []
    nodos_expandidos = 0

    while abierta:
        current_node = heapq.heappop(abierta)  # Quitar el primer nodo de abierta
        if problema.test_meta(current_node.estado):
            print("Coste: " + str(current_node.g))
            print("Nodos expandidos: " + str(nodos_expandidos))
            return current_node  # solución óptima encontrada: nodo meta expandido
        elif is_in_cerrada(current_node):  # pseudocódigo 2: comprueba que N no esté en cerrada
            continue

        cerrada.append(current_node)  # N entra en CERRADA
        sucesores = problema.get_sucesores(current_node.estado)  # generar el conjunto de sucesores

        for estado, coste in sucesores:
            new_g = current_node.g + coste
            new_h = heuristica(estado, problema)
            new_nodo = Nodo(estado, current_node, new_g, new_h)
            if not is_in_abierta(new_nodo):  # insertar en orden en ABIERTA cada sucesor de N
                heapq.heappush(abierta, new_nodo)
                nodos_expandidos = nodos_expandidos + 1
                print(nodos_expandidos)

    print("El Problema no tiene solución")
    return None


# Implementación de la solución al problema de los Traslados
class Problema:
    def __init__(self, input_file):
        # Lectura del archivo de entrada
        self.mapa = Mapa(input_file)

        # Datos relevantes para realizar una búsqueda informada
        self.pacientes_totales = self.mapa.find_value('C')[1] + self.mapa.find_value('N')[1]
        self.parking_coord = self.mapa.find_value('P')[0]
        self.cc_coord = self.mapa.find_value('CC')[0]
        self.cn_coord = self.mapa.find_value('CN')[0]
        # Se asume que hay solamente un 'P', un 'CC' y un 'CN'

        # Estado inicial:
        carga_inicial = 50
        asientos_contag = 2
        asientos_totales = 10
        self.estado_inicial = Estado(self.parking_coord, carga_inicial, list(['0'] * asientos_contag),
                                     list(['0'] * (asientos_totales - asientos_contag)), self.pacientes_totales, [])

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

            # Podado: si tiene menos energía que casillas para volver al parking, se descarta
            if (nuevo_estado.carga < dis_manhattan(estado.posicion, self.parking_coord)) or \
                    (nuevo_estado.carga == 0 and tipo != 'P'):
                continue  # Estado inválido, la ambulancia se ha quedado sin energía

            # Actualizar carga
            if tipo == 'P':
                nuevo_estado.carga = 50  # Recarga de energía

            # Movimiento de pacientes:

            if tipo == 'C':
                if pos in nuevo_estado.pac_recogidos:
                    continue  # Estado inválido: se prohíbe pasar por el domicilio de un paciente recogido
                if nuevo_estado.añadir_c() == 1:  # Intenta añadir un paciente con enfermedad contagiosa
                    nuevo_estado.pac_recogidos.append(pos)
                else:
                    continue  # Estado inválido, no puede pasar sin recoger

            elif tipo == 'N':
                if nuevo_estado.lleva_infectados():
                    continue  # Estado inválido
                if pos in nuevo_estado.pac_recogidos:
                    continue  # Se prohíbe pasar por el domicilio de un paciente ya recogido
                if nuevo_estado.añadir_n() == 1:  # Intenta añadir un paciente sin enfermedad contagiosa
                    nuevo_estado.pac_recogidos.append(pos)
                else:
                    continue  # Estado inválido, no puede pasar sin recoger

            elif tipo == 'CC':
                if nuevo_estado.dejar_cc() == 0:  # Intenta dejar pacientes C en su centro
                    continue  # Estado inválido

            elif tipo == 'CN':
                if nuevo_estado.lleva_infectados():
                    continue  # Estado inválido
                if nuevo_estado.dejar_cn() == 0:  # Intenta dejar pacientes N en su centro
                    continue  # Estado inválido, no deja pacientes

            sucesores.append((nuevo_estado, coste))

        return sucesores


def write_solution(self, result):
    pass
    # TODO


def dis_manhattan(pos1, pos2):
    x1, y1 = pos1
    x2, y2 = pos2
    distancia = abs(x1 - x2) + abs(y1 - y2)
    return distancia


# Búsqueda no informada, equivalente a Dijkstra
def heuristica_0(state, problem):
    return 0;


# Heurística basada 4 casos: (volviendo a 'P', lleva infectados, lleva pasajeros normales, default)
# Usa la distancia de Manhattan tanto al parking como a centros de salud
def heuristica_1(estado, problema):
    h = 0
    if estado.pac_restantes == 0:  # volviendo a 'P'
        return dis_manhattan(estado.posicion, problema.parking_coord)
    elif estado.lleva_infectados():  # lleva infectados
        return dis_manhattan(estado.posicion, problema.cc_coord) + \
            dis_manhattan(problema.cc_coord, problema.parking_coord)
    else:
        for n in estado.asientos_n:
            if n != '0':  # lleva pasajeros normales
                return dis_manhattan(estado.posicion, problema.cn_coord) +\
                    dis_manhattan(problema.cn_coord, problema.parking_coord)
    # default
    return min(dis_manhattan(estado.posicion, problema.cc_coord) +
               dis_manhattan(problema.cc_coord, problema.parking_coord),
               dis_manhattan(estado.posicion, problema.cn_coord) +
               dis_manhattan(problema.cn_coord, problema.parking_coord))


# Heurística muy simple basada en la distancia de Manhattan al parking (admisible, no muy buena)
def heuristica_2(estado, problema):
    parking_coord = problema.mapa.find_value('P')[0]
    return dis_manhattan(estado.posicion, parking_coord)


def heuristica_3(estado, problema):  # "Apostar por los que van bien"
    # Si a un estado le quedan pocos pacientes por recoger => buena heurística
    # h será [0, dis_manhattan(pos, P)]
    # TODO: memoria, tales
    return (estado.pac_restantes // problema.pacientes_totales) * \
        dis_manhattan(estado.posicion, problema.parking_coord)


# Ejemplo de uso
# -------------------------------------------------------------------------------

if __name__ == '__main__':
    # Argumentos pasados al script
    argumentos = sys.argv[1:]
    if len(argumentos) != 2:
        print("Error en los argumentos")
        exit(-1)
    input_file = argumentos[0]
    h_dict = {0: heuristica_0, 1: heuristica_1, 2: heuristica_2, 3: heuristica_3}

    try:
        h_id = int(argumentos[1])
    except ValueError as e:
        print("Error en los argumentos")
        exit(-1)
    if h_id not in h_dict:
        print("Error: Elija una heurística implementada:")
        print(str(h_dict))

problema = Problema(input_file)

# Iniciar el temporizador
inicio = time.time()
result = astar_search(problema, h_dict[h_id])
# Detener el temporizador y obtener el tiempo transcurrido
tiempo_transcurrido = time.time() - inicio

print("Tiempo: " + str(tiempo_transcurrido))
current = result
result_list = []
while current:
    result_list.append(current)
    print(str(current.estado))
    current = current.padre
print("END")
