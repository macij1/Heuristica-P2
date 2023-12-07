# !/usr/bin/env python
# -*- coding: utf-8 -*-
from constraint import *


def get_casilla(x, y, dim) -> int:
    if x < 1 or x > dim[0] or y < 1 or y > dim[1]:
        return -1
    return y + (x - 1) * dim[1]


def get_coord(n, dim) -> tuple[int, int]:
    if n < 1 or n > (dim[0] * dim[1]):
        return -1, -1
    x = (n - 1) // dim[1] + 1
    y = (n - 1) % dim[1] + 1
    return x, y


# Lectura de fichero. Devuelve los datos iniciales del problema
#    dimensiones: dupla de enteros
#    plazas_electric: lista de casillas con conexión
#    ambulancias: lista de tuples (ID, Urgente?, Congelador?)
#         Urgente?: True si es TSU, False si es TNU
#         Congelador?: True si es C, False si es X
def read_input(name):
    with open(name, 'r') as input_file:
        # Dimensiones
        buffer = input_file.readline()
        buffer = buffer.strip('\n')
        dimensiones_str = buffer.split('x')
        dimensiones = tuple(map(int, dimensiones_str))

        # Listado de plazas con conexión eléctrica
        buffer = input_file.readline()
        # Eliminar 'PE:' y dividir la cadena en pares de números
        buffer = buffer.strip('\n')
        pares = buffer.replace("PE:", "").split(")(")
        plazas_electric_coord = [tuple(map(int, par.strip("()").split(","))) for par in pares]
        plazas_electric_index = set(get_casilla(coord[0], coord[1], dimensiones) for coord in plazas_electric_coord)

        # Ambulancias
        lineas = input_file.readlines()
        ambulancias_str = list(linea.strip('\n').split("-") for linea in lineas)
        # Conversion de TSU/TNU y C/X a bool
        ambulancias = list((int(amb[0])-1, True if amb[1] == 'TSU' else False, True if amb[2] == 'C' else False)
                           for amb in ambulancias_str)
        return dimensiones, ambulancias, plazas_electric_index


if __name__ == '__main__':
    # Lectura de fichero de entrada y escritura de datos necesarios
    dimensiones, ambulancias, plazas_electric_index = read_input('CSP-tests/parking04.txt')

    # Creación del nuevo problema
    problem = Problem()

    # Declaración de variables
    # -------------------------------------------------------------------------
    # Una variable por ambulancia: "AmbX"
    # Dominio: casillas (numeradas por filas)
    names = ["Amb" + str(amb[0]+1) for amb in ambulancias]
    domain = list(range(1, dimensiones[0] * dimensiones[1] + 1))
    problem.addVariables(names, domain)
    print(plazas_electric_index)
    # Creación de restricciones
    # -------------------------------------------------------------------------
    # Funcion auxiliar:
    # Si en la casilla hay una ambulancia asignada, devuelve (True, id de la variable)
    # De lo contrario, (False, -1)

    def is_taken(args, casilla):
        for i in range(0, len(args)-1):
            if args[i] == casilla:
                return True, i
        return False, -1
    # Restricción 1: Implícita. Una instanciación asigna a cada variable un
    # único valor

    # Restricción 2:
    # No puede haber dos ambulancias en la misma casilla
    problem.addConstraint(AllDifferentConstraint())

    # Restricción 3:
    # Una ambulancia con congelador está bien asignada si y solo sí su casilla
    # dispone de conexión eléctrica
    def congelador_con_conexion(* args):
        for i in range(len(args)):
            print("Congelador VAR " + str(i))
            if ambulancias[i][2] and args[i] not in plazas_electric_index:
                return False
        return True
    problem.addConstraint(congelador_con_conexion, names)

    # Restricción 4:
    # Una ambulancia de tipo TSU no deben tener ninguna ambulancia de tipo TNU
    # en la misma fila, en una columna posterior a la suya
    def prioridad_TSU(* args):
        for i in range(0, len(args)-1):
            if ambulancias[i][1]:  # TSU
                coord = get_coord(i, dimensiones)
                col = coord[1]
                for posterior in range(col + 1, dimensiones[1]+1):  # Todas las casillas posteriores de su fila
                    taken, var_id = is_taken(args, posterior)
                    if taken and not ambulancias[var_id][1]:  # TNU delante => Inválido
                        return False
        return True
    problem.addConstraint(prioridad_TSU, names)

    # Restricción 5:
    # Una ambulancia no puede estar situada sobre o debajo de otra ambulancia
    def maniobrabilidad(* args):
        for i in range(0, len(args)-1):
            coord = get_coord(i, dimensiones)
            upper = get_casilla(coord[0]+1, coord[1], dimensiones)
            lower = get_casilla(coord[0]-1, coord[1], dimensiones)
            if is_taken(args, upper)[0] or is_taken(args, lower)[0]:
                return False
        return True
    problem.addConstraint(maniobrabilidad, names)

    # Cálculo de las soluciones
    # -------------------------------------------------------------------------
    print("Calculando una solución...")
    print(problem.getSolution())
    # # compute the solutions
    # solutions = problem.getSolutions()
    # # and show them on the standard output
    # print(" #{0} solutions have been found: ".format(len(solutions)))
    # for sol in solutions[0:5]:
    #     print(str(sol) + '\n')
    # # problem.getSolutions()
