"""Contains functions for calculating VV and VT transition probabilities
"""
__author__ = 'George Oblapenko'
__license__ = "GPL"
__maintainer__ = "George Oblapenko"
__email__ = "kunstmord@kunstmord.com"
__status__ = "Development"

import numpy as np
from scipy import constants
from scipy.misc import factorial
from .errors import KineticlibError
from math import exp, cosh, atan, sinh


def fact_div_fact(start: int, end: int) -> float:
    """
    Helper function, returns end! / start!, where start and end are integers

    Parameters
    ----------
    start : int
        the start of the sequence of numbers
    end : int
        the end of the sequence of numbers

    Returns
    -------
    float
        The product of all numbers in the range `[start + 1, end]`

    Raises
    ------
    KineticlibError
        if `start >= end` or `end < 0.0`
    """
    if end < 0.0 or start >= end:
        raise KineticlibError
    else:
        return np.prod(np.arange(start + 1.0, end + 1.0, 1.0))


def svt(delta: int) -> float:
    """
    Helper function, calculates the steric factor for VT transitions

    Parameters
    ----------
    delta : int
        the change in vibrational level

    Returns
    -------
    float
        The steric factor
    """
    s = delta
    if delta < 0:
        s *= -1.0
    return 1. / (constants.pi * s)


def svv(delta: int) -> float:
    """
    Helper function, calculates the steric factor for VV transitions

    Parameters
    ----------
    delta : int
        the change in vibrational level

    Returns
    -------
    float
        The steric factor
    """
    s = delta
    if delta < 0:
        s *= -1.0
    return ((factorial(s + 3)) * ((1. + 1. / (2. ** (s - 1))) ** 4)) / ((2. ** (s + 8)) * (s + 1) * (s + 1) * 6)


def vel_avg_vt(g: float, ve_before: float, ve_after: float, mass: float) -> float:
    """Returns the arithmetic mean of the relative velocity of particles before and after
    a VT transition (using the energy conservation law) **M(i1) + P -> M(i2) + P**

    Parameters
    ----------
    g : float
        the relative dimensional velocity of the particles before the collision
    ve_before : float
        the vibrational energy of the molecule before the transition
    ve_after : float
        the vibrational energy of the molecule after the transition
    mass : float
        the collision-reduced mass :math:`m_{cd}`

    Returns
    -------
    float
        Arithmetic mean of before- and after- velocities for a VT transition

    Notes
    -----
    If the squared after-collision velocity is < 0, then the collision is impossible for such parameters and
    the function returns -1
    """
    gn_sq = (ve_before - ve_after) * (2.0 / mass) + (g ** 2)
    if gn_sq < 0:
        return -1
    else:
        return 0.5 * (g + (gn_sq ** 0.5))


def vel_avg_vv(g: float, ve_before1: float, ve_after1: float,
               ve_before2: float, ve_after2: float, mass: float) -> float:
    """Returns the arithmetic mean of the relative velocity of particles before and after
    a VV transition (using the energy conservation law) **M1(i1) + M2(k1) -> M1(i2) + M2(k2)**

    Parameters
    ----------
    g : float
        the relative dimensional velocity of the particles before the collision
    ve_before1 : float
        the vibrational energy of the molecule M1 before the transition
    ve_after1 : float
        the vibrational energy of the molecule M1 after the transition
    ve_before2 : float
        the vibrational energy of the molecule M2 before the transition
    ve_after2 : float
        the vibrational energy of the molecule M2 after the transition
    mass : float
        the collision-reduced mass :math:`m_{cd}`

    Returns
    -------
    float
        Arithmetic mean of before- and after- velocities for a VT transition

    Notes
    -----
    If the squared after-collision velocity is < 0, then the collision is impossible for such parameters and
    the function returns -1
    """
    gn_sq = (ve_before1 - ve_after1 + ve_before2 - ve_after2) * (2.0 / mass) + (g ** 2)
    if gn_sq < 0:
        return -1
    else:
        return 0.5 * (g + (gn_sq ** 0.5))


def ssh_vt_p10(T: float, mass: float, eps: float, hvc: float) -> float:
    """Returns the probability of a VT transition using the SSH model
    **M(1) + P -> M(0) + P**

    Parameters
    ----------
    T : float
        the temperature of the mixture
    mass : float
        the collision-reduced mass :math:`m_{cd}`
    hvc : float
        the harmonic coefficient in the formula for vibrational level energies
    eps : float
        the Lennard-Jones :math:`\\varepsilon_{cd}` parameter, divided by Boltzmann's constant

    Returns
    -------
    float
        VT transition probability
    """
    omega = 2 * constants.pi * hvc / constants.h
    alpha = 17.5 / (3.621 * (10 ** (-10)))
    chi = (0.5 * constants.pi**2 * mass * omega**2 / (alpha**2 * constants.k * T)) ** (1. / 3)
    p10 = 1.294 * (0.5 * (1 + chi * T / eps)**0.5 + 0.5) ** (-1. / 3)
    p10 *= (4 * constants.pi**2 * mass * omega / (alpha**2 * constants.hbar))\
           / (3. + 3.3 * eps / T)
    p10 *= exp(-3 * chi + constants.hbar * omega / (2 * constants.k * T) + eps / T)\
           * ((chi * 4 * constants.pi / 3) ** 0.5)
    return p10


def vt_probability_fho(g: float, T: float, mass: float, beta: float, ve_before: float, ve_after: float,
                       molecule_diss: float, i: int, delta: int) -> float:
    """Returns the probability of a VT transition using the FHO (Forced harmonic oscillator) model
    **M(i) + P -> M(i + delta) + P**

    Parameters
    ----------
    g : float
        the relative dimensionless velocity of the particles before the collision
    T : float
        the temperature of the mixture
    mass : float
        the collision-reduced mass :math:`m_{cd}`
    beta : float
        the IPL potential :math:`\\beta` parameter
    ve_before : float
        the vibrational energy of the molecule before the transition
    ve_after : float
        the vibrational energy of the molecule after the transition
    molecule_diss : float
        the dissociation energy of the molecule which undergoes the transition (with no offset)
    i : int
        the vibrational level of the molecule
    delta : int
        the change in vibrational level of the molecule

    Returns
    -------
    float
        VT transition probability
    """

    if delta > 0:
        s = delta * 1.0
        ns = fact_div_fact(i, i + delta)
    else:
        s = -delta * 1.0
        ns = fact_div_fact(i + delta, i)

    omega = abs((ve_before - ve_after) / delta) / constants.hbar
    if omega == 0.0:
        return 0.0
    vel = vel_avg_vt(g * (2 * constants.k * T / mass) ** 0.5, ve_before, ve_after, mass)

    if vel < 0.0:
        return 0.0
    phi = 2.0 * atan(((2.0 * molecule_diss / mass) ** 0.5) / vel)

    eps = (cosh((1.0 + phi) * omega / (beta * vel))
           / (sinh(2.0 * constants.pi * omega / (beta * vel)))) ** 2
    eps *= 4.0 * (constants.pi ** 2) * svt(delta) * omega * mass / ((beta ** 2) * constants.h)
    return ns * (eps ** s) * exp(- 2.0 * (ns ** (1.0 / s)) * eps / (s + 1)) / (factorial(s) ** 2)


def vt_prob_g_only_fho(g: float, T: float, mass: float, beta: float, ve_before: float, ve_after: float, i: int,
                       delta: int, depth: float, this_svt: float=0.33) -> float:
    """Returns the velocity-dependent part of the probability of a VT transition using
    the FHO (Forced harmonic oscillator) model **M(i) + P -> M(i + delta) + P**

    Parameters
    ----------
    g : float
        the relative dimensionless velocity of the particles before the collision
    T : float
        the temperature of the mixture
    mass : float
        the collision-reduced mass :math:`m_{cd}`
    beta : float
        the IPL potential :math:`\\beta` parameter
    ve_before : float
        the vibrational energy of the molecule before the transition
    ve_after : float
        the vibrational energy of the molecule after the transition
    i : int
        the vibrational level of the molecule
    delta : int
        the change in vibrational level of the molecule
    depth : float
        the potential well depth of the molecule
    svt : float
        the steric factor

    Returns
    -------
    float
        Velocity-dependent part of the VT transition probability
    """

    vel = vel_avg_vt(g * (2 * constants.k * T / mass) ** 0.5, ve_before, ve_after, mass)
    if vel < 0.0:
        return 0.0

    if delta == 1:
        omega = (ve_after - ve_before) / constants.hbar
        phi = 2.0 * atan(((2.0 * depth / mass) ** 0.5) / vel)

        eps = (cosh((1.0 + phi) * omega / (beta * vel))
               / (sinh(2.0 * constants.pi * omega / (beta * vel)))) ** 2
        eps *= 4.0 * this_svt * (constants.pi ** 2) * omega * mass / ((beta ** 2) * constants.h)
        return eps * exp(-(i + 1) * eps)
    elif delta == -1:
        omega = (ve_before - ve_after) / constants.hbar
        phi = 2.0 * atan(((2.0 * depth / mass) ** 0.5) / vel)

        eps = (cosh((1.0 + phi) * omega / (beta * vel))
               / (sinh(2.0 * constants.pi * omega / (beta * vel)))) ** 2
        eps *= 4.0 * this_svt * (constants.pi ** 2) * omega * mass / ((beta ** 2) * constants.h)
        return eps * exp(-i * eps)
    elif delta > 0:
        s = delta * 1.0
        omega = (ve_after - ve_before) / (s * constants.hbar)
        ns = fact_div_fact(i, i + delta)

        phi = 2.0 * atan(((2.0 * depth / mass) ** 0.5) / vel)
        eps = (cosh((1.0 + phi) * omega / (beta * vel))
               / (sinh(2.0 * constants.pi * omega / (beta * vel)))) ** 2
        eps *= 4.0 * this_svt * (constants.pi ** 2) * omega * mass / ((beta ** 2) * constants.h)
        return (eps ** s) * exp(- 2.0 * (ns ** (1.0 / s)) * eps / (s + 1))
    else:
        s = -delta * 1.0
        omega = (ve_before - ve_after) / (s * constants.hbar)
        ns = fact_div_fact(i + delta, i)

        phi = 2.0 * atan(((2.0 * depth / mass) ** 0.5) / vel)
        eps = (cosh((1.0 + phi) * omega / (beta * vel))
               / (sinh(2.0 * constants.pi * omega / (beta * vel)))) ** 2
        eps *= 4.0 * this_svt * (constants.pi ** 2) * omega * mass / ((beta ** 2) * constants.h)
        return (eps ** s) * exp(- 2.0 * (ns ** (1.0 / s)) * eps / (s + 1))


def vv_probability_fho(g: float, T: float, mass: float, beta: float, ve_before1: float, ve_after1: float,
                       ve_before2: float, ve_after2: float, i: int, k: int, i_delta: int) -> float:
    """Returns the probability of a VV transition using the FHO (Forced harmonic oscillator) model
    **M1(i) + M2(k) -> M1(i + i_delta) + M2(k - i_delta)**

    Parameters
    ----------
    g : float
        the relative dimensionless velocity of the particles before the collision
    T : float
        the temperature of the mixture
    mass : float
        the collision-reduced mass :math:`m_{cd}`
    beta : float
        the IPL :math:`\\beta` parameter
    ve_before1 : float
        the vibrational energy of the molecule M1 before the transition
    ve_after1 : float
        the vibrational energy of the molecule M1 after the transition
    ve_before2 : float
        the vibrational energy of the molecule M2 before the transition
    ve_after2 : float
        the vibrational energy of the molecule M2 after the transition
    i : int
        the vibrational level of molecule M1
    k : int
        the vibrational level of molecule M2
    i_delta : int
        the change in vibrational level of the molecule M1

    Returns
    -------
    float
        VV transition probability
    """

    if i_delta > 0:
        s = i_delta * 1.0
        ns1 = fact_div_fact(i, i + i_delta)
        ns2 = fact_div_fact(k - i_delta, k)
    else:
        s = -i_delta * 1.0
        ns1 = fact_div_fact(i + i_delta, i)
        ns2 = fact_div_fact(k, k - i_delta)

    vel = vel_avg_vv(g * (2.0 * constants.k * T / mass) ** 0.5, ve_before1, ve_after1, ve_before2, ve_after2, mass)

    if vel < 0:
        return 0.0

    omega1 = abs((ve_before1 - ve_after1) / i_delta) / constants.hbar
    omega2 = abs((ve_before2 - ve_after2) / i_delta) / constants.hbar

    if omega1 == 0.0 or omega2 == 0:
        return 0.0

    xi = 2 * abs(omega1 - omega2) / (beta * vel)
    if xi < 1.0 ** (-4):
        rhoxi = 0.25 * svv(i_delta) * ((beta * vel) ** 2) / (omega1 * omega2)
    else:
        rhoxi = svv(i_delta) * (abs(omega1 - omega2) ** 2) / (omega1 * omega2 * (sinh(xi) ** 2))

    return (rhoxi ** s) * ns1 * ns2 * exp(-2.0 * rhoxi * ((ns1 * ns2) ** (1.0 / s)) / (s + 1)) / (factorial(s) ** 2)


def vv_prob_g_only_fho(g: float, T: float, mass: float, beta: float, ve_before1: float, ve_after1: float,
                       ve_before2: float, ve_after2: float, i: int, k: int, i_delta: int, this_svv: float=0.04) -> float:
    """Returns the velocity-dependent part of the probability of a VV transition using the FHO
    (Forced harmonic oscillator) model **M1(i) + M2(k) -> M1(i + i_delta) + M2(k - i_delta)**

    Parameters
    ----------
    g : float
        the relative dimensionless velocity of the particles before the collision
    T : float
        the temperature of the mixture
    mass : float
        the collision-reduced mass :math:`m_{cd}`
    beta : float
        the IPL :math:`\\beta` parameter
    ve_before1 : float
        the vibrational energy of the molecule M1 before the transition
    ve_after1 : float
        the vibrational energy of the molecule M1 after the transition
    ve_before2 : float
        the vibrational energy of the molecule M2 before the transition
    ve_after2 : float
        the vibrational energy of the molecule M2 after the transition
    i : int
        the vibrational level of molecule M1
    k : int
        the vibrational level of molecule M2
    i_delta : int
        the change in vibrational level of the molecule M1
    svv : float
        the steric factor

    Returns
    -------
    float
        Velocity-dependent part of the VV transition probability
    """
    vel = vel_avg_vv(g * (2.0 * constants.k * T / mass) ** 0.5, ve_before1, ve_after1, ve_before2, ve_after2, mass)
    if vel < 0:
        return 0.0

    if i_delta == 1:
        omega1 = (ve_after1 - ve_before1) / constants.hbar
        omega2 = (ve_before2 - ve_after2) / constants.hbar

        xi = 2.0 * abs(omega1 - omega2) / (beta * vel)
        if xi < 1.0 ** (-10):
            rhoxi = 0.25 * this_svv * ((beta * vel) ** 2) / (omega1 * omega2)  # 0.0078125 is 0.03125 * 0.25, svv=0.03125
        else:
            rhoxi = this_svv * ((omega1 - omega2) ** 2) / (omega1 * omega2 * (sinh(xi) ** 2))

        return rhoxi * exp(-((i + 1) * k) * rhoxi)
    elif i_delta == -1:
        omega1 = (ve_before1 - ve_after1) / constants.hbar
        omega2 = (ve_after2 - ve_before2) / constants.hbar
        xi = 2.0 * abs(omega1 - omega2) / (beta * vel)

        if xi < 1.0 ** (-10):
            rhoxi = 0.25 * this_svv * ((beta * vel) ** 2) / (omega1 * omega2)  # 0.0078125 is 0.03125 * 0.25, svv=0.03125
        else:
            rhoxi = this_svv * ((omega1 - omega2) ** 2) / (omega1 * omega2 * (sinh(xi) ** 2))

        return rhoxi * exp(-(i * (k + 1)) * rhoxi)
    elif i_delta > 0:
        s = i_delta * 1.0
        omega1 = (ve_after1 - ve_before1) / (s * constants.hbar)
        omega2 = (ve_before2 - ve_after2) / (s * constants.hbar)
        xi = 2.0 * abs(omega1 - omega2) / (beta * vel)

        if xi < 1.0 ** (-10):
            rhoxi = 0.25 * this_svv * ((beta * vel) ** 2) / (omega1 * omega2)
        else:
            rhoxi = this_svv * (abs(omega1 - omega2) ** 2) / (omega1 * omega2 * (sinh(xi) ** 2))

        return (rhoxi ** s) * exp(-2.0 * ((fact_div_fact(i, i + i_delta) * fact_div_fact(k - i_delta, k)) ** (1.0 / s))
                            * rhoxi / (s + 1))
    else:
        s = -i_delta * 1.0
        omega1 = (ve_before1 - ve_after1) / (s * constants.hbar)
        omega2 = (ve_after2 - ve_before2) / (s * constants.hbar)
        xi = 2.0 * abs(omega1 - omega2) / (beta * vel)

        if xi < 1.0 ** (-10):
            rhoxi = 0.25 * this_svv * ((beta * vel) ** 2) / (omega1 * omega2)
        else:
            rhoxi = this_svv * (abs(omega1 - omega2) ** 2) / (omega1 * omega2 * (sinh(xi) ** 2))

        return (rhoxi ** s) * exp(-2.0 * ((fact_div_fact(i + i_delta, i) * fact_div_fact(k, k - i_delta)) ** (1.0 / s))
                            * rhoxi / (s + 1))