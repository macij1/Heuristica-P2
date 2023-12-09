# !/usr/bin/env python
# -*- coding: utf-8 -*-
from constraint import *
import sys
import csv


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
        ambulancias = list((int(amb[0]), True if amb[1] == 'TSU' else False, True if amb[2] == 'C' else False)
                           for amb in ambulancias_str)
        return dimensiones, ambulancias, plazas_electric_index


# Lectura de fichero. Escribe en un archivo csv los resultados de la
# primera solución obtenida
def write_output(name, solution, dimensions):
    with open(name, 'w') as output_file:
        # Preparación de datos solución
        data = [["-" for _ in range(dimensions[1])] for _ in range(dimensions[0])]
        if len(solution) != 0:
            for i in range(1, dimensions[0]+1):
                for j in range(1, dimensions[1]+1):
                    n = get_casilla(i, j, dimensions)
                    for clave, valor in solution[0].items():  # Solamente escribimos la primera solución
                        if n == valor:
                            data[i-1][j-1] = clave + '-' + ('TSU' if ambulancias[int(clave)-1][1] else 'TNU')\
                                             + '-' + ('C' if ambulancias[int(clave)-1][2] else 'X')
        # Escritura en archivo .csv
        csv_writer = csv.writer(output_file)
        output_file.write('N.Sol:' + "," + str(len(solution)) + "\n")
        for row in data:
            csv_writer.writerow(row)


if __name__ == '__main__':
    # Argumentos pasados al script
    argumentos = sys.argv[1:]
    if len(argumentos) != 1:
        print("Error en los argumentos")
        exit(-1)
    input_file = argumentos[0]

    # Lectura de fichero de entrada y escritura de datos necesarios
    dimensiones, ambulancias, plazas_electric_index = read_input(input_file)

    # Creación del nuevo problema
    problem = Problem()

    # Declaración de variables
    # -------------------------------------------------------------------------
    # Una variable por ambulancia: "AmbX"
    # Dominio: casillas (numeradas por filas)
    names = [str(amb[0]) for amb in ambulancias]
    domain = list(range(1, dimensiones[0] * dimensiones[1] + 1))
    problem.addVariables(names, domain)

    # Creación de restricciones
    # -------------------------------------------------------------------------

    # Restricción 1: Implícita. Una instanciación asigna a cada variable un
    # único valor

    # Restricción 2:
    # No puede haber dos ambulancias en la misma casilla
    problem.addConstraint(AllDifferentConstraint())

    # Restricción 3:
    # Una ambulancia con congelador está bien asignada si y solo sí su casilla
    # dispone de conexión eléctrica
    def congelador_con_conexion(arg):
        if arg not in plazas_electric_index:
            return False
        else:
            return True

    for i in range(len(names)):
        if ambulancias[i][2]:  # Ambulancias con congelador
            problem.addConstraint(congelador_con_conexion, names[i])

    # Restricción 4:
    # Una ambulancia de tipo TSU no deben tener ninguna ambulancia de tipo TNU
    # en la misma fila, en una columna posterior a la suya
    def prioridad_TSU(tsu, tnu):
        coord_tsu = get_coord(tsu, dimensiones)
        coord_tnu = get_coord(tnu, dimensiones)
        if coord_tsu[0] == coord_tnu[0] and coord_tnu[1] > coord_tsu[1]:
            return False # Misma fila, tnu delante de tsu
        return True

    tsu_amb = []
    tnu_amb = []
    for i in range(len(names)):
        if ambulancias[i][1]:
            tsu_amb.append(names[i])
        else:
            tnu_amb.append(names[i])
    for prior in tsu_amb:
        for non_prior in tnu_amb:
            problem.addConstraint(prioridad_TSU, (prior, non_prior))

    # Restricción 5:
    # Una ambulancia no puede estar situada sobre o debajo de otra ambulancia
    def maniobrabilidad(a, b):
        coord_a = get_coord(a, dimensiones)
        coord_b = get_coord(b, dimensiones)
        if coord_a[1] == coord_b[1] and abs(coord_a[0]-coord_b[0]) == 1:
            return False  # Misma columna, filas contiguas
        else:
            return True

    for i in range(len(names)):
        for j in range(len(names)):
            problem.addConstraint(maniobrabilidad, (names[i], names[j]))  # Producto cartesiano

    # Cálculo de las soluciones
    # -------------------------------------------------------------------------
    print("Calculando una solución...")
    print(problem.getSolution())
    print("Calculando todas las soluciones...")
    solutions = problem.getSolutions()
    print(" #{0} solutions have been found: ".format(len(solutions)))

    # Escritura en consola de las primeras 5 soluciones
    for sol in solutions[0:5]:
        print(str(sol) + '\n')

    # Escritura en archivo de salida .csv
    output_file = input_file.split('.')[0] + '.csv'
    write_output(output_file, solutions, dimensiones)
