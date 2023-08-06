#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Authors:  Dominik Gresch <greschd@ethz.ch>, Gabriel Autes
# Date:    27.09.2014 21:27:27 CEST
# File:    kpts.py
r"""
A collection of functions for creating k-points input for different 
first-principles codes.

All functions have the same calling structure as :func:`prototype`.
"""


def prototype(start_point, last_point, end_point, N):
    r"""
    Specifies the interface

    :param start_point:     First point in the string of k-points
    :type start_point:      list (length: 3)
    :param last_point:      Last point in the string of k-points
    :type last_point:       list(length: 3)
    :param end_point:       End point of the string of k-points. This 
        k-point is connected to ``start_point`` by a reciprocal lattice vector 
        in the direction of the string of k-points. ``end_point`` itself should 
        not be used in the calculation.
    :type end_point:        list(length: 3)
    :param N:               Number of k-points in the string
    :type N:                int
    """
    raise NotImplementedError('This is only the prototype for kpts')


def abinit(start_point, last_point, end_point, N):
    """
    Creates a k-point input for **ABINIT**. It uses ``kptopt -1`` and
    specifies the k-points string using ``ndivk`` and ``kptbounds``.
    """
    for point in [start_point, last_point, end_point]:
        if len(point) != 3:
            raise ValueError('dimension of point != 3')

    string = "\nkptopt -1\nndivk " + str(int(N - 1)) + '\nkptbounds '
    for coord in start_point:
        string += str(coord).replace('e', 'd') + ' '
    string += '\n'
    for coord in last_point:
        string += str(coord).replace('e', 'd') + ' '
    string += '\n'
    return string


def qe(start_point, last_point, end_point, N):
    """
    Creates a k-point input for  **Quantum Espresso**.
    """
    for point in [start_point, last_point, end_point]:
        if len(point) != 3:
            raise ValueError('dimension of point != 3')

    string = "\nK_POINTS crystal_b\n 2 \n"
    for coord in start_point:
        string += str(coord).replace('e', 'd') + ' '
    string += str(N-1)+'\n'
    for coord in last_point:
        string += str(coord).replace('e', 'd') + ' '
    string += str(1)+'\n'
    return string


def wannier90(start_point, last_point, end_point, N):
    """
    Creates a k-point input for **Wannier90**. It can be useful when the
    first-principles code does not generate the k-points in
    ``wannier90.win`` (e.g. with Quantum Espresso).
    """
    for point in [start_point, last_point, end_point]:
        if len(point) != 3:
            raise ValueError('dimension of point != 3')

    string = "mp_grid: " + str(int(N)) + " 1 1 \nbegin kpoints"
    for i in range(N):
        string += '\n'
        point = start_point
        for j, coord in enumerate(point):
            coord += float(i)/float(N-1) * (last_point[j] - start_point[j])
            string += str(coord).replace('e', 'd') + ' '
    string += '\nend kpoints\n'
    return string

def vasp(start_point, last_point, end_point, N):
    """
    Creates a k-point input for  **VASP**. It uses the automatic
    generation scheme with a Gamma centered grid.
    """
    # N or N - 1?
    string = 'Automatic mesh\n0              ! number of k-points = 0 ->automatic generation scheme\nGamma          ! generate a Gamma centered grid\n'
    for i in range(3):
        if(abs(end_point[i] - start_point[i]) > 0.8):
            string += str(N)
        else:
            string += '1'
        string += ' '
    string += '        ! subdivisions\n'
    for coord in start_point:
            string += str(coord).replace('e', 'd') + ' '
    string += '         ! shift\n'
    return string
