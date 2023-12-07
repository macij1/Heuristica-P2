# !/usr/bin/env python
# -*- coding: utf-8 -*-
from constraint import *

"""
Lectura de fichero. Resultados:
   dimensiones: dupla de enteros
   Plazas_electric: lista de coordenadas de las plazas con conexsión
   Ambulancias: lista de tuplas (ID, Urgente?, Congelador?)
       Urgente?: True si es TSU, False si es TNU
      Congelador?: True si es C, False si es X
"""
with open('CSP-tests/parking01.txt', 'r') as input_file:
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
    plazas_electric = [tuple(map(int, par.strip("()").split(","))) for par in pares]

    # Ambulancias
    lineas = input_file.readlines()
    ambulancias_str = list(linea.strip('\n').split("-") for linea in lineas)
    # Conversion de TSU/TNU y C/X a bool
    ambulancias = list((amb[0], True if amb[1] == 'TSU' else False, True if amb[2] == 'C' else False)
                   for amb in ambulancias_str)


def get_casilla(x, y, dim):
    if x < 1 or x > dim[0] or y < 1 or y > dim[1]:
        return "Error"
    return x + (y-1) * dim[1]


def get_coord(n, dim):
    if n < 1 or n > (dim[0]*dim[1]):
        return "Error"
    x = (n-1) // dim[1] +1
    y = (n-1) % dim[1] +1
    return x, y

# create a new problem
problem = Problem()
# Declaración de variables
# Vamos a numerar las casillas por filas
names = ["Amb"+amb[0] for amb in ambulancias]
domain = list(range(1, dimensiones[0]*dimensiones[1]))
problem.addVariables(names, domain)
# ...


