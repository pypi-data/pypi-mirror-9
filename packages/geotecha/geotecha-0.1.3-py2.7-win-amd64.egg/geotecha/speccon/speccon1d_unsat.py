#!/usr/bin/env python
# geotecha - A software suite for geotechncial engineering
# Copyright (C) 2013  Rohan T. Walker (rtrwalker@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/gpl.html.

"""
Multilayer consolidation of unsaturated soil using the spectral Galerkin
method.
"""
from __future__ import division, print_function

import geotecha.plotting.one_d #import MarkersDashesColors as MarkersDashesColors
import time
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

import geotecha.speccon.speccon1d as speccon1d
import geotecha.piecewise.piecewise_linear_1d as pwise
from geotecha.piecewise.piecewise_linear_1d import PolyLine
import geotecha.speccon.integrals as integ
import geotecha.mathematics.transformations as transformations
from geotecha.inputoutput.inputoutput import GenericInputFileArgParser



class Speccon1dUnsat(speccon1d.Speccon1d):
    """Multilayer consolidation of unsaturated soil

    Features:

     - Multiple layers.
     - Unsaturated vertical drainage only.
     - Water and air phases.
     - Material properties that are constant in time but piecewsie linear with
       depth.
     - Surcharge loading.
     - Independent non-zero top and bottom pore air and pore water pressure
       boundary conditions.
     - Surcharge/Boundary Conditions vary
       with time in a piecewise-linear function multiplied by a cosine
       function of time.

       - Surcharge can also vary piecewise linear with depth.
         The depth dependence does not vary with time.
       - Mulitple loads will be combined using superposition.
     - Subset of Python syntax available in input files/strings allowing
       basic calculations within input files.
     - Output:

       - Excess pore air and pore water pressure at depth
       - Average excess pore air and pore water pressure between depths.
       - Settlement between depths of air phase, water phase and overall.
       - Charts and csv output available.
     - Program can be run as script or in a python interpreter.
     - Note there is no pumping or fixed pore pressure functionality.


    .. warning::
        The 'Parameters' and 'Attributes' sections below require further
        explanation.  The parameters listed below are not used to explicitly
        initialize the object.  Rather they are defined in either a
        multi-line string or a file-like object using python syntax; the
        file/string is then used to initialize the object using the
        `reader` parameter. As well as simple assignment statements
        (H = 1, drn = 0 etc.), the input file/string can contain basic
        calculations (z = np.linspace(0, H, 20) etc.).  Not all of the
        listed parameters are needed. The user should pick an appropriate
        combination of attributes for their analysis (minimal explicit
        checks on input data will be performed).
        Each  'parameter' will be turned into an attribute that
        can be accessed using conventional python dot notation, after the
        object has been initialised.  The attributes listed below are
        calculated values (i.e. they could be interpreted as results) which
        are accessible using dot notation after all calculations are
        complete.


    Parameters
    ----------
    H : float, optional
        Total height of soil profile. Default H=1.0. Note that even though
        this program deals with normalised depth values it is important to
        enter the correct H valu, as it is used when plotting, outputing
        data and in normalising gradient boundary conditions (see
        `bot_vs_time` below)
    mvref : float, optional
        Reference value of volume compressibility mv (used with `H` in
        settlement calculations). Default mvref=1.0.  Note this is used to
        normalise all the unsaturated volume compressibilities. It is also
        used in the porosity/saturation term.
    kwref : float, optional
        Reference value of water phase vertical permeability kw in soil
        (only used for pretty output). Default kwref=1.0.
    Daref : float, optional
        Reference value of coefficeint of transmission for the air phase
        (only used for pretty output). Default Daref=1.0. (note ka=Da*g).
    drn : {0, 1}, optional
        drainage boundary condition. Default drn=0.
        0 = Pervious top pervious bottom (PTPB).
        1 = Pervious top impoervious bottom (PTIB).
    dT : float, optional
        Convienient normaliser for time factor multiplier. Default dT=1.0.
    neig : int, optional
        Number of series terms to use in solution. Default neig=2. Don't use
        neig=1.
    dTw : float
        Vertical reference time factor multiplier for water phase.
        dTw is calculated with the chosen reference values of kw and mv:
        dTw = kwref /(mvref*gamw) / H ^ 2
    dTa : float
        Vertical reference time factor multiplier for air phase.
        dTa is calculated with the chosen reference values of Da and mv:
        dTa = Daref / (mvref) / (wa/(R*T)/ua_ / H ^ 2. Where wa=molecular
        mass of air= 28.966e-3 kg/mol for air, R=universal gas
        constant=8.31432 J/(mol.K), T = absolute
        temperature in Kelvin=273.16+t0 (K), t0=temperature in celsius, ua_=
        absolute air pressure=ua+uatm (kPa), ua=guage air pressure, uatm=
        atmospheric air pressure=101 kPa.  When ua is small or rapidly
        dissipates during consolidation ua_ can be considered a constant;
        so let ua_=uatm
    m1ka : PolyLine
        Normalised coefficient of air volume change with respect to a change
        in the net normal stress (dsig-dua), PolyLine(depth, m1ka).
    m1kw : PolyLine
        Normalised coefficient of water volume change with respect to a change
        in the net normal stress (dsig-dua), PolyLine(depth, m1kw).
    m2a : PolyLine
        Normalised coefficient of air volume change with respect to a change
        in the matirx suction (duw-dua), PolyLine(depth, m2a).
    m2w : PolyLine
        Normalised coefficient of water volume change with respect to a change
        in the matirx suction (duw-dua), PolyLine(depth, m2w).
    kw : PolyLine
        Normalised vertical permeability PolyLine(depth, kw).
    Da : PolyLine
        Normalised coefficeint of transmission for the air phase
        PolyLine(depth, Da).
    n : PolyLine
        Porosity PolyLine(depth, n). Porosity must be between 0 and 1.
    S : PolyLine
        Degree of saturation, PolyLine(depth, S). Degree of saturation
        must be between 0 and 1.
    ua_ : float, optional
        Absolute pore air pressure, assumed constant usually at
        atmospheric pressure. Default ua_=101 kPa.  This is used in the
        porosity-saturation term.
    surcharge_vs_depth : list of Polyline, optional
        Surcharge variation with depth. PolyLine(depth, multiplier).
    surcharge_vs_time : list of Polyline, optional
        Surcharge magnitude variation with time. PolyLine(time, magnitude).
    surcharge_omega_phase : list of 2 element tuples, optional
        (omega, phase) to define cyclic variation of surcharge. i.e.
        mag_vs_time * cos(omega*t + phase). If surcharge_omega_phase is None
        then cyclic component will be ignored.  If surcharge_omega_phase is a
        list then if any member is None then cyclic component will not be
        applied for that load combo.
    atop_vs_time, wtop_vs_time : list of Polyline, optional
        Top air and water p.press variation with time.
        Polyline(time, magnitude).
    atop_omega_phase, wtop_omega_phase : list of 2 element tuples, optional
        (omega, phase) to define cyclic variation of top air and water BC. i.e.
        mag_vs_time * cos(omega*t + phase). If top_omega_phase is None
        then cyclic component will be ignored.  If top_omega_phase is a
        list then if any member is None then cyclic component will not be
        applied for that load combo.
    abot_vs_time, wbot_vs_time : list of Polyline, optional
        Bottom air and water p.press variation with time.
        Polyline(time, magnitude).
        When drn=1, i.e. PTIB, bot_vs_time is equivilent to saying
        D[u(H,t), z] = bot_vs_time. Within the program the actual gradient
        will be normalised with depth by multiplying H.
    abot_omega_phase, wbot_omega_phase : list of 2 element tuples, optional
        (omega, phase) to define cyclic variation of bot air and water BC. i.e.
        mag_vs_time * cos(omega*t + phase). If bot_omega_phase is None
        then cyclic component will be ignored.  If bot_omega_phase is a
        list then if any member is None then cyclic component will not be
        applied for that load combo.
    ppress_z : list_like of float, optional
        Normalised z to calculate pore pressure at.
    avg_ppress_z_pairs : list of two element list of float, optional
        Nomalised zs to calculate average pore pressure between
        e.g. average of all profile is [[0,1]].
    settlement_z_pairs : list of two element list of float, optional
        Normalised depths to calculate normalised settlement between.
        e.g. surface settlement would be [[0, 1]].
    tvals : list of float
        Times to calculate output at.
    ppress_z_tval_indexes : list/array of int, slice, optional
        Indexes of `tvals` at which to calculate ppress_z. i.e. only calculate
        ppress_z at a subset of the `tvals` values.
        Default ppress_z_tval_indexes=slice(None, None) i.e. use all the
        `tvals`.
    avg_ppress_z_pairs_tval_indexes : list/array of int, slice, optional
        Indexes of `tvals` at which to calculate avg_ppress_z_pairs.
        i.e. only calc avg_ppress_z_pairs at a subset of the `tvals` values.
        Default avg_ppress_z_pairs_tval_indexes=slice(None, None) i.e. use
        all the `tvals`.
    settlement_z_pairs_tval_indexes : list/array of int, slice, optional
        Indexes of `tvals` at which to calculate settlement_z_pairs.
        i.e. only calc settlement_z_pairs at a subset of the `tvals` values.
        Default settlement_z_pairs_tval_indexes=slice(None, None) i.e. use
        all the `tvals`.
    implementation : ['scalar', 'vectorized','fortran'], optional
        Where possible use the stated implementation type.  'scalar'=
        python loops (slowest), 'vectorized' = numpy (fast), 'fortran' =
        fortran extension (fastest).  Note only some functions have multiple
        implementations.
    RLzero : float, optional
        Reduced level of the top of the soil layer.  If RLzero is not None
        then all depths (in plots and results) will be transformed to an RL
        by RL = RLzero - z*H.  If RLzero is None (i.e. the default) then all
        depths will be reported  z*H (i.e. positive numbers).
    plot_properties : dict of dict, optional
        Dictionary that overrides some of the plot properties.
        Each member of `plot_properties` will correspond to one of the plots.

        ==================  ============================================
        plot_properties     description
        ==================  ============================================
        porw                dict of prop to pass to water pore pressure
                            plot.
        pora                dict of prop to pass to air pore pressure
                            plot.
        avpw                dict of prop to pass to average
                            water pore pressure plot.
        avpa                dict of prop to pass to average
                            air pore pressure plot.
        set                 dict of prop to pass to settlement plot.
        seta                dict of prop to pass to air settlement
                            plot.
        setw                dict of prop to pass to water settlement
                            plot.
        load                dict of prop to pass to loads plot.
        material            dict of prop to pass to materials plot.
        ==================  ============================================
        see geotecha.plotting.one_d.plot_vs_depth and
        geotecha.plotting.one_d.plot_vs_time for options to specify in
        each plot dict.
    save_data_to_file : True/False, optional
        If True data will be saved to file.  Default save_data_to_file=False
    save_figures_to_file : True/False
        If True then figures will be saved to file.
        Default save_figures_to_file=False
    show_figures : True/False, optional
        If True the after calculation figures will be shown on screen.
        Default show_figures=False.
    directory : string, optional
        Path to directory where files should be stored.
        Default directory=None which
        will use the current working directory.  Note if you keep getting
        directory does not exist errors then try putting an r before the
        string definition. i.e. directory = r'C:\\Users\\...'
    overwrite : True/False, optional
        If True then existing files will be overwritten.
        Default overwrite=False.
    prefix : string, optional
         Filename prefix for all output files.  Default prefix= 'out'
    create_directory : True/Fase, optional
        If True a new sub-folder with name based on  `prefix` and an
        incremented number will contain the output
        files. Default create_directory=True.
    data_ext : string, optional
        File extension for data files. Default data_ext='.csv'
    input_ext : string, optional
        File extension for original and parsed input files. default = ".py"
    figure_ext : string, optional
        File extension for figures.  Can be any valid matplotlib option for
        savefig. Default figure_ext=".eps". Others include 'pdf', 'png'.
    title : str, optional
        A title for the input file.  This will appear at the top of data files.
        Default title=None, i.e. no title.
    author : str, optional
        Author of analysis. Default author='unknown'.


    Attributes
    ----------
    porw, pora : ndarray, only present if ppress_z is input
        Calculated pore pressure at depths corresponding to `ppress_z` and
        times corresponding to `tvals`.  This is an output array of
        size (len(ppress_z), len(tvals[ppress_z_tval_indexes])). porw and
        pora are pore pressure in water and air.
    avpw, avpa : ndarray, only present if avg_ppress_z_pairs is input
        Calculated average pore pressure between depths corresponding to
        `avg_ppress_z_pairs` and times corresponding to `tvals`.  This is an
        output array of size
        (len(avg_ppress_z_pairs), len(tvals[avg_ppress_z_pairs_tval_indexes])).
        avpw and avas are average pore pressure in water and air.
    set, setw, seta : ndarray, only present if settlement_z_pairs is input
        Settlement between depths corresponding to `settlement_z_pairs` and
        times corresponding to `tvals`.  This is an output array of size
        (len(avg_ppress_z_pairs), len(tvals[settlement_z_pairs_tval_indexes])).
        setw and sets are settlement in water and air. set is water + air.

    Notes
    -----
    **Gotchas**

    All the loading terms e.g. surcharge_vs_time, surcharge_vs_depth,
    surcharge_omega_phase can be either a single value or a list of values.
    The corresponding lists that define a load must have the same length
    e.g. if specifying multiple surcharge loads then surcharge_vs_time and
    surcharge_vs_depth must be lists of the same length such that
    surcharge_vs_time[0] can be paired with surcharge_vs_depth[0],
    surcharge_vs_time[1] can be paired with surcharge_vs_depth[1], etc.

    **Material and geometric properties**

     - :math:`\\sigma - u_a` is net normal stress.
     - :math:`u_a - u_w` is matric suction.
     - :math:`u_a` is air pressure.
     - :math:`u_w` is water pressure.
     - :math:`m_{1k}^a` is coefficient of air volume change with respect to a
       change in the net normal stress.
     - :math:`m_{1k}^w` is coefficient of awater volume change with respect to a
       change in the net normal stress.
     - :math:`m_2^a` is coefficient of air volume change with respect to a
       change in the matric suction.
     - :math:`m_2^a` is coefficient of air volume change with respect to a
       change in the matric suction.
     - :math:`k_w` is vertical water permeability.
     - :math:`D_a` is coefficeint of transmission for the air phase.
       :math:`D_a = k_a g`.
     - :math:`n` is porosity :math:`0>n>1`.
     - :math:`S` is degree of saturation :math:`0>S>1`.
     - :math:`\\overline{u}_a` is the absolute air pressure.
       :math:`\\overline{u}_a = u_{atm}+u_a`.
     - :math:`u_{atm}` is absolute atmospheric air pressure.
     - :math:`\\gamma_w` is the unit weight of water.
     - :math:`Z` is the nomalised depth (:math:`Z=z/H`).
     - :math:`H` is the total height of the soil profile.
     - :math:`T` is the absolute temperature in kelvin.
     - :math:`\\omega` is the molecular mass of air often taken as
       29e-3 kg/mol.
     - :math:`R` is the universal gas constant 8.314 J/(mol.K).


    **Governing equation**

    Overall strain :math:`\\varepsilon` is the sum of the air strain,
    :math:`\\varepsilon_a` and the water strain :math:`\\varepsilon_w`:

    .. math::
         \\varepsilon = \\varepsilon_a + \\varepsilon_w

    The water and air strain components are:

    .. math::
        \\varepsilon_a =
            m_{1k}^a\\left({\\sigma - u_a}\\right)
            + m_2^a\\left({u_a - u_w}\\right)

    .. math::
        \\varepsilon_w =
            m_{1k}^w\\left({\\sigma - u_a}\\right)
            + m_2^w\\left({u_a - u_w}\\right)

    Both pore air and pore water pressures are functions of normalised depth
    :math:`Z` and time :math:`t`, :math:`u\\left({Z, t}\\right)`.  The water
    and air phase partial differential equations are:

    .. math::
        \\left({\\overline{m}_{1k}^w - \\overline{m}_2^w}\\right) u_a,_t
        +  \\overline{m}_2^w u_w,_t
        + dT_w\\left({\\overline{k}_w u_w,_Z}\\right),_Z
        = \\overline{m}_{1k}^w \\sigma,_t

    .. math::
        \\left({\\overline{m}_{1k}^a
               - \\overline{m}_2^a
               - \\frac{\\left({1-S}\\right)n}{\\overline{u}_a m_{\\textrm{ref}}}
               }\\right) u_a,_t
        +  \\overline{m}_2^a u_w,_t
        + dT_a\\left({\\overline{D}_a u_a,_Z}\\right),_Z
        = \\overline{m}_{1k}^a \\sigma,_t


    where

    .. math::
        dT_w = \\frac{k_{w\\textrm{ref}}}
                     {H^2 m_{v\\textrm{ref}} \\gamma_w}

    .. math::
        dT_a = \\frac{D_{a\\textrm{ref}}}
                     {\\left({\\omega R T}\\right)
                      \\overline{u}_a m_{\\textrm{ref}}}


    The overline notation represents a depth dependent property normalised
    by the relevant reference property. e.g.
    :math:`\\overline{k}_w = k_w\\left({z}\\right) / k_{w\\textrm{ref}}`.

    A comma followed by a subscript represents differentiation with respect to
    the subscripted variable e.g.
    :math:`u,_Z = u\\left({Z,t}\\right) / \\partial Z`.

    **Non-zero Boundary conditions**

    The following two sorts of boundary conditions for the air and water
    phases can be modelled independently using:

    .. math::
        \\left.u\\left({Z,t}\\right)\\right|_{Z=0} = u^{\\textrm{top}}\\left({t}\\right)
        \\textrm{ and }
        \\left.u\\left({Z,t}\\right)\\right|_{Z=1} = u^{\\textrm{bot}}\\left({t}\\right)


    .. math::
        \\left.u\\left({Z,t}\\right)\\right|_{Z=0} = u^{\\textrm{top}}\\left({t}\\right)
        \\textrm{ and }
        \\left.u\\left({Z,t}\\right),_Z\\right|_{Z=1} = u^{\\textrm{bot}}\\left({t}\\right)


    The boundary conditions are incorporated by homogenising the governing
    equation with the following substitution:

    .. math::
        u\\left({Z,t}\\right)
        = \\hat{u}\\left({Z,t}\\right) + u_b\\left({Z,t}\\right)

    where for the two types of non zero boundary boundary conditions:

    .. math::
        u_b\\left({Z,t}\\right)
        = u^{\\textrm{top}}\\left({t}\\right) \\left({1-Z}\\right)
        + u^{\\textrm{bot}}\\left({t}\\right) Z

    .. math::
        u_b\\left({Z,t}\\right)
        = u^{\\textrm{top}}\\left({t}\\right)
        + u^{\\textrm{bot}}\\left({t}\\right) Z

    **Time and depth dependence of loads/material properties**

    Soil properties do not vary with time.


    Loads are formulated as the product of separate time and depth
    dependant functions as well as a cyclic component:

    .. math:: \\sigma\\left({Z,t}\\right)=
                \\sigma\\left({Z}\\right)
                \\sigma\\left({t}\\right)
                \\cos\\left(\\omega t + \\phi\\right)

    :math:`\\sigma\\left(t\\right)` is a piecewise linear function of time
    that within the kth loading stage is defined by the load magnitude at
    the start and end of the stage:

    .. math::
        \\sigma\\left(t\\right)
        = \\sigma_k^{\\textrm{start}}
        + \\frac{\\sigma_k^{\\textrm{end}}
                 - \\sigma_k^{\\textrm{start}}}
                {t_k^{\\textrm{end}}
                 - t_k^{\\textrm{start}}}
        \\left(t - t_k^{\\textrm{start}}\\right)

    The depth dependence of loads and material property
    :math:`a\\left(Z\\right)` is a piecewise linear function
    with respect to :math:`Z`, that within a layer are defined by:

    .. math::
        a\\left(z\\right)
        = a_t + \\frac{a_b - a_t}{z_b - z_t}\\left(z - z_t\\right)

    with :math:`t` and :math:`b` subscripts representing 'top' and 'bottom' of
    each layer respectively.



    References
    ----------
    The genesis of this work is from research carried out by
    Dr. Rohan Walker, Prof. Buddhima Indraratna and others
    at the University of Wollongong, NSW, Austrlia, [1]_, [2]_, [3]_, [4]_.

    .. [1] Walker, Rohan. 2006. 'Analytical Solutions for Modeling Soft
           Soil Consolidation by Vertical Drains'. PhD Thesis, Wollongong,
           NSW, Australia: University of Wollongong.
    .. [2] Walker, R., and B. Indraratna. 2009. 'Consolidation Analysis of
           a Stratified Soil with Vertical and Horizontal Drainage Using the
           Spectral Method'. Geotechnique 59 (5) (January): 439-449.
           doi:10.1680/geot.2007.00019.
    .. [3] Walker, Rohan, Buddhima Indraratna, and Nagaratnam Sivakugan. 2009.
           'Vertical and Radial Consolidation Analysis of Multilayered
           Soil Using the Spectral Method'. Journal of Geotechnical and
           Geoenvironmental Engineering 135 (5) (May): 657-663.
           doi:10.1061/(ASCE)GT.1943-5606.0000075.
    .. [4] Walker, Rohan T. 2011. Vertical Drain Consolidation Analysis
           in One, Two and Three Dimensions'. Computers and
           Geotechnics 38 (8) (December): 1069-1077.
           doi:10.1016/j.compgeo.2011.07.006.

    """

    def _setup(self):

        self._attributes = (
            'H drn dT neig '
            'mvref kwref Daref '
            'dTw dTa '
            'm1ka m1kw m2a m2w kw Da '
            'surcharge_vs_depth surcharge_vs_time '
            'atop_vs_time abot_vs_time '
            'wtop_vs_time wbot_vs_time '
            'ppress_z avg_ppress_z_pairs settlement_z_pairs tvals '
            'implementation ppress_z_tval_indexes '
            'avg_ppress_z_pairs_tval_indexes settlement_z_pairs_tval_indexes '
            'surcharge_omega_phase '
            'atop_omega_phase abot_omega_phase '
            'wtop_omega_phase wbot_omega_phase '
            'RLzero '
            'prefix '
            'plot_properties '
            'ua_ n S'
            ).split()

        self._attribute_defaults = {
            'H': 1.0, 'drn': 0, 'dT': 1.0, 'neig': 2, 'mvref':1.0,
            'kwref': 1.0, 'Daref': 1.0,
            'implementation': 'vectorized',
            'ppress_z_tval_indexes': slice(None, None),
            'avg_ppress_z_pairs_tval_indexes': slice(None, None),
            'settlement_z_pairs_tval_indexes': slice(None, None),
            'prefix': 'speccon1dunsat_',
            'ua_': 101
            }

        self._attributes_that_should_be_lists= (
            'surcharge_vs_depth surcharge_vs_time surcharge_omega_phase '
            'atop_vs_time atop_omega_phase '
            'abot_vs_time abot_omega_phase '
            'wtop_vs_time wtop_omega_phase '
            'wbot_vs_time wbot_omega_phase').split()

        self._attributes_that_should_have_same_x_limits = [
            'm1ka m1kw m2a m2w kw Da surcharge_vs_depth n S'.split()]

        self._attributes_that_should_have_same_len_pairs = [
            'surcharge_vs_depth surcharge_vs_time'.split(),
            'surcharge_vs_time surcharge_omega_phase'.split(),
            'atop_vs_time atop_omega_phase'.split(),
            'abot_vs_time abot_omega_phase'.split(),
            'wtop_vs_time wtop_omega_phase'.split(),
            'wbot_vs_time wbot_omega_phase'.split(),]

        self._attributes_to_force_same_len = [
            "surcharge_vs_time surcharge_omega_phase".split(),
            "atop_vs_time atop_omega_phase".split(),
            "abot_vs_time abot_omega_phase".split(),
            "wtop_vs_time wtop_omega_phase".split(),
            "wbot_vs_time wbot_omega_phase".split(),]

        self._zero_or_all = [
            'surcharge_vs_depth surcharge_vs_time'.split(),
            ]
        self._at_least_one = [
            ['dTw'],
            ['dTa'],
            ['m1ka'],
            ['m1kw'],
            ['m2a'],
            ['m2w'],
            ['kw'],
            ['Da'],
            ['n'],
            ['S'],
            ('surcharge_vs_time atop_vs_time '
                'abot_vs_time wtop_vs_time wbot_vs_time').split(),
            ['tvals'],
            'ppress_z avg_ppress_z_pairs settlement_z_pairs'.split()]

        self._one_implies_others = [
            ('surcharge_omega_phase surcharge_vs_depth '
                'surcharge_vs_time').split(),
            'atop_omega_phase atop_vs_time'.split(),
            'abot_omega_phase abot_vs_time'.split(),
            'wtop_omega_phase wtop_vs_time'.split(),
            'wbot_omega_phase wbot_vs_time'.split(),]


        #these explicit initializations are just to make coding easier
        self.H = self._attribute_defaults.get('H', None)
        self.drn = self._attribute_defaults.get('drn', None)
        self.dT = self._attribute_defaults.get('dT', None)
        self.neig = self._attribute_defaults.get('neig', None)
        self.mvref = self._attribute_defaults.get('mvref', None)
        self.kwref = self._attribute_defaults.get('kwref', None)
        self.Daref = self._attribute_defaults.get('Daref', None)
        self.dTw = None
        self.dTa = None
        self.m1ka = None
        self.m1kw = None
        self.m2a = None
        self.m2w = None
        self.kw = None
        self.Da = None
        self.surcharge_vs_depth = None
        self.surcharge_vs_time = None
        self.atop_vs_time = None
        self.abot_vs_time = None
        self.wtop_vs_time = None
        self.wbot_vs_time = None
        self.ppress_z = None
        self.avg_ppress_z_pairs = None
        self.settlement_z_pairs = None
        self.tvals = None
        self.implementation = self._attribute_defaults.get('implementation', None)
        self.ppress_z_tval_indexes = self._attribute_defaults.get('ppress_z_tval_indexes', None)
        self.avg_ppress_z_pairs_tval_indexes = self._attribute_defaults.get('avg_ppress_z_pairs_tval_indexes', None)
        self.settlement_z_pairs_tval_indexes = self._attribute_defaults.get('settlement_z_pairs_tval_indexes', None)
        self.surcharge_omega_phase = None
        self.atop_omega_phase = None
        self.abot_omega_phase = None
        self.wtop_omega_phase = None
        self.wbot_omega_phase = None
        self.RLzero = None
        self.prefix = self._attribute_defaults.get('prefix', None)
        self.ua_ = self._attribute_defaults.get('ua_', None)
        self.n = None
        self.S = None

        self.plot_properties = self._attribute_defaults.get('plot_properties',
                                                            None)



        return

    def make_time_independent_arrays(self):
        """make all time independent arrays


        See also
        --------
        self._make_m : make the basis function eigenvalues
        self._make_gam : make the mv dependent gamma matrix
        self._make_psi : make the kv, kh, et dependent psi matrix
        self._make_eigs_and_v : make eigenvalues, eigenvectors and I_gamv

        """


        self._make_m()
        self._make_gam()
        self._make_psi()
        self._make_eigs_and_v()

        return

    def make_time_dependent_arrays(self):
        """make all time dependent arrays

        See also
        --------
        self.make_E_Igamv_the()

        """
        self.tvals = np.asarray(self.tvals)
        if not self.ppress_z is None:
            self.ppress_z = np.asarray(self.ppress_z)
        self.make_E_Igamv_the()
        self.v_E_Igamv_the = np.dot(self.v, self.E_Igamv_the)
        return





    def make_output(self):
        """make all output"""

        header1 = ("program: speccon1d_vrc; geotecha version: "
            "{}; author: {}; date: {}\n").format(self.version,
                self.author, time.strftime('%Y/%m/%d %H:%M:%S'))
        if not self.title is None:
            header1+= "{}\n".format(self.title)

        self._grid_data_dicts = []
        if not self.ppress_z is None:
            self._make_por()
            z = transformations.depth_to_reduced_level(
                np.asarray(self.ppress_z), self.H, self.RLzero)
            labels = ['{:.3g}'.format(v) for v in z]
            d = {'name': '_data_porw',
                 'data': self.porw.T,
                 'row_labels': self.tvals[self.ppress_z_tval_indexes],
                 'row_labels_label': 'Time',
                 'column_labels': labels,
                 'header': header1 + 'Pore water pressure at depth'}
            self._grid_data_dicts.append(d)

            d = {'name': '_data_pora',
                 'data': self.pora.T,
                 'row_labels': self.tvals[self.ppress_z_tval_indexes],
                 'row_labels_label': 'Time',
                 'column_labels': labels,
                 'header': header1 + 'Pore air pressure at depth'}
            self._grid_data_dicts.append(d)

        if not self.avg_ppress_z_pairs is None:
            self._make_avp()
            z_pairs = transformations.depth_to_reduced_level(
                np.asarray(self.avg_ppress_z_pairs), self.H, self.RLzero)
            labels = ['{:.3g} to {:.3g}'.format(z1, z2) for z1, z2 in z_pairs]
            d = {'name': '_data_avpw',
                 'data': self.avpw.T,
                 'row_labels': self.tvals[self.avg_ppress_z_pairs_tval_indexes],
                 'row_labels_label': 'Time',
                 'column_labels': labels,
                 'header': header1 + 'Average pore water pressure between depths'}
            self._grid_data_dicts.append(d)

            d = {'name': '_data_avpa',
                 'data': self.avpa.T,
                 'row_labels': self.tvals[self.avg_ppress_z_pairs_tval_indexes],
                 'row_labels_label': 'Time',
                 'column_labels': labels,
                 'header': header1 + 'Average pore air pressure between depths'}
            self._grid_data_dicts.append(d)

        if not self.settlement_z_pairs is None:
            self._make_set()
            z_pairs = transformations.depth_to_reduced_level(
                np.asarray(self.settlement_z_pairs), self.H, self.RLzero)
            labels = ['{:.3g} to {:.3g}'.format(z1, z2) for z1, z2 in z_pairs]
            d = {'name': '_data_set',
                 'data': self.set.T,
                 'row_labels': self.tvals[self.settlement_z_pairs_tval_indexes],
                 'row_labels_label': 'Time',
                 'column_labels': labels,
                 'header': header1 + 'Settlement between depths'}
            self._grid_data_dicts.append(d)

            d = {'name': '_data_setw',
                 'data': self.setw.T,
                 'row_labels': self.tvals[self.settlement_z_pairs_tval_indexes],
                 'row_labels_label': 'Time',
                 'column_labels': labels,
                 'header': header1 + 'Water settlement between depths'}
            self._grid_data_dicts.append(d)

            d = {'name': '_data_seta',
                 'data': self.seta.T,
                 'row_labels': self.tvals[self.settlement_z_pairs_tval_indexes],
                 'row_labels_label': 'Time',
                 'column_labels': labels,
                 'header': header1 + 'Air settlement between depths'}
            self._grid_data_dicts.append(d)
        return


    def _make_m(self):
        """make the basis function eigenvalues

        m in u = sin(m * Z)

        Notes
        -----

        .. math:: m_i =\\pi*\\left(i+1-drn/2\\right)

        for :math:`i = 1\:to\:neig-1`

        """

        if sum(v is None for v in[self.neig, self.drn])!=0:
            raise ValueError('neig and/or drn is not defined')
        self.m = integ.m_from_sin_mx(np.arange(self.neig), self.drn)

        self.m_block = np.empty(2 * self.neig, dtype=float)
        self.m_block[:self.neig] = self.m
        self.m_block[self.neig:] = self.m
        return


    def _make_gam(self):
        """make the mv dependant gam matrix

        """

#        self.gam = integ.pdim1sin_af_linear(
#                        self.m, self.mv, implementation=self.implementation)
        gam_1kw = integ.pdim1sin_af_linear(
                        self.m, self.m1kw, implementation=self.implementation)
        gam_1ka = integ.pdim1sin_af_linear(
                        self.m, self.m1ka, implementation=self.implementation)
        gam_2w = integ.pdim1sin_af_linear(
                        self.m, self.m2w, implementation=self.implementation)
        gam_2a = integ.pdim1sin_af_linear(
                        self.m, self.m2a, implementation=self.implementation)
        gam_n = integ.pdim1sin_af_linear(
                        self.m, self.n, implementation=self.implementation)
        gam_n/= self.ua_ * self.mvref
        gam_sn = integ.pdim1sin_abf_linear(
                        self.m, self.n, self.S, implementation=self.implementation)
        gam_sn/= self.ua_ * self.mvref

        self.gam = np.zeros((2 * self.neig, 2 * self.neig))


        self.gam[:self.neig, :self.neig] = gam_2w
        self.gam[:self.neig, self.neig:] = (gam_1kw - gam_2w)
        self.gam[self.neig:, :self.neig] = gam_2a
        self.gam[self.neig:, self.neig:] = (gam_1ka - gam_2a - gam_n
                                                  + gam_sn)


        self.gam[np.abs(self.gam)<1e-8] = 0.0


        return


    def _make_psi(self):
        """make all the kv, kh, kvc, khc, et dependant psi matrices

        """


        psi_wv = (self.dTw / self.dT *
                integ.pdim1sin_D_aDf_linear(self.m, self.kw,
                    implementation=self.implementation))
        psi_av = (self.dTa / self.dT *
                integ.pdim1sin_D_aDf_linear(self.m, self.Da,
                    implementation=self.implementation))

        self.psi = np.zeros((2 * self.neig, 2 * self.neig))

        self.psi [:self.neig, :self.neig] = psi_wv
        self.psi [self.neig:, self.neig:] = psi_av



#        self.psi[np.abs(self.psi)<1e-8] = 0.0



        return

    def _make_eigs_and_v(self):
        """make Igam_psi, v and eigs, and Igamv



        Finds the eigenvalues, `self.eigs`, and eigenvectors, `self.v` of
        inverse(gam)*psi.  Once found the matrix inverse(gamma*v), `self.Igamv`
        is determined.

        Notes
        -----
        From the original equation

        .. math:: \\mathbf{\\Gamma}\\mathbf{A}'=\\mathbf{\\Psi A}+loading\\:terms

        `self.eigs` and `self.v` are the eigenvalues and eigenvegtors of the matrix `self.Igam_psi`

        .. math:: \\left(\\mathbf{\\Gamma}^{-1}\\mathbf{\\Psi}\\right)

        """

#        self.psi[np.abs(self.psi) < 1e-8] = 0.0
        Igam_psi = np.dot(np.linalg.inv(self.gam), self.psi)
        self.eigs, self.v = np.linalg.eig(Igam_psi)
        self.v = np.asarray(self.v)
        self.Igamv = np.linalg.inv(np.dot(self.gam, self.v))

    def print_eigs(self):
        """print eigenvalues to stdout"""
        print('eigs')
        for i, x in enumerate(self.eigs):
            if i<self.neig:
                print('water {0}, {1:3.3f}'.format(i, x))
            else:

                print('air {0}, {1:3.3f}'.format(i-self.neig, x))
        return
    def make_E_Igamv_the(self):
        """sum contributions from all loads

        Calculates all contributions to E*inverse(gam*v)*theta part of solution
        u=phi*vE*inverse(gam*v)*theta. i.e. surcharge, vacuum, top and bottom
        pore pressure boundary conditions. `make_load_matrices will create
        `self.E_Igamv_the`.  `self.E_Igamv_the`  is an array
        of size (neig, len(tvals)). So the columns are the column array
        E*inverse(gam*v)*theta calculated at each output time.  This will allow
        us later to do u = phi*v*self.E_Igamv_the

        See also
        --------
        _make_E_Igamv_the_surcharge :  surchage contribution
        _make_E_Igamv_the_BC : top boundary pore pressure contribution
        _make_E_Igamv_the_bot : bottom boundary pore pressure contribution
        """

        self.E_Igamv_the = np.zeros((2*self.neig, len(self.tvals)))

        if sum([v is None for
                v in [self.surcharge_vs_depth, self.surcharge_vs_time]])==0:
            self._make_E_Igamv_the_surcharge()
            self.E_Igamv_the += self.E_Igamv_the_surcharge
        if sum(v is None for v in[self.atop_vs_time,
                                  self.abot_vs_time,
                                  self.wtop_vs_time,
                                  self.wbot_vs_time])!=0:
            self._make_E_Igamv_the_BC()
            self.E_Igamv_the += self.E_Igamv_the_BC

        return

    def _make_E_Igamv_the_surcharge(self):
        """make the surcharge loading matrices

        Make the E*inverse(gam*v)*theta part of solution u=phi*vE*inverse(gam*v)*theta.
        The contribution of each surcharge load is added and put in
        `self.E_Igamv_the_surcharge`. `self.E_Igamv_the_surcharge` is an array
        of size (neig, len(tvals)). So the columns are the column array
        E*inverse(gam*v)*theta calculated at each output time.  This will allow
        us later to do u = phi*v*self.E_Igamv_the_surcharge

        Notes
        -----
        Assuming the load are formulated as the product of separate time and depth
        dependant functions:

        .. math:: \\sigma\\left({Z,t}\\right)=\\sigma\\left({Z}\\right)\\sigma\\left({t}\\right)

        the solution to the consolidation equation using the spectral method has
        the form:

        .. math:: u\\left(Z,t\\right)=\\mathbf{\\Phi v E}\\left(\\mathbf{\\Gamma v}\\right)^{-1}\\mathbf{\\theta}

        `_make_E_Igamv_the_surcharge` will create `self.E_Igamv_the_surcharge` which is
        the :math:`\\mathbf{E}\\left(\\mathbf{\\Gamma v}\\right)^{-1}\\mathbf{\\theta}`
        part of the solution for all surcharge loads

        """
        self.E_Igamv_the_surcharge = (
            speccon1d.dim1sin_E_Igamv_the_aDmagDt_bilinear(self.m_block,
                   self.eigs, self.tvals, self.Igamv, self.m1kw,
                   self.surcharge_vs_depth, self.surcharge_vs_time,
                   self.surcharge_omega_phase, self.dT,
                   theta_zero_indexes=slice(self.neig, None),
                   implementation=self.implementation))

        self.E_Igamv_the_surcharge += (
            speccon1d.dim1sin_E_Igamv_the_aDmagDt_bilinear(self.m_block,
                   self.eigs, self.tvals, self.Igamv, self.m1ka,
                   self.surcharge_vs_depth, self.surcharge_vs_time,
                   self.surcharge_omega_phase, self.dT,
                   theta_zero_indexes=slice(None, self.neig),
                   implementation=self.implementation))
        return




    def _normalised_bot_vs_time(self):
        """Normalise bot_vs_time when drn=1, i.e. bot_vs_time is a gradient

        Multiplie each bot_vs_time PolyLine by self.H

        Returns
        -------
        bot_vs_time : list of Polylines, or None
            bot_vs_time normalised by H

        """

        if not self.wbot_vs_time is None:
            if self.drn == 1:
                wbot_vs_time = ([vs_time * self.H for
                                vs_time in self.wbot_vs_time])
            else:
                wbot_vs_time = self.wbot_vs_time
        else:
            wbot_vs_time = None

        if not self.abot_vs_time is None:
            if self.drn == 1:
                abot_vs_time = ([vs_time * self.H for
                                vs_time in self.abot_vs_time])
            else:
                abot_vs_time = self.abot_vs_time
        else:
            abot_vs_time = None

        return wbot_vs_time, abot_vs_time

    def _make_E_Igamv_the_BC(self):
        """make the boundary condition loading matrices

        """
        self.E_Igamv_the_BC = np.zeros((2*self.neig, len(self.tvals)))
        wbot_vs_time, abot_vs_time = self._normalised_bot_vs_time()

        botzero=slice(self.neig, None)
        topzero=slice(None, self.neig)

        # top row of block
        #m2w * duw/dt component
        self.E_Igamv_the_BC -= (
            speccon1d.dim1sin_E_Igamv_the_BC_aDfDt_linear(
                self.drn, self.m_block, self.eigs, self.tvals,
                self.Igamv, self.m2w, self.wtop_vs_time, wbot_vs_time,
                self.wtop_omega_phase, self.wbot_omega_phase, self.dT,
                theta_zero_indexes=botzero,
                implementation=self.implementation))
        #m1kw * dua/dt component
        self.E_Igamv_the_BC -= (
            speccon1d.dim1sin_E_Igamv_the_BC_aDfDt_linear(
                self.drn, self.m_block, self.eigs, self.tvals,
                self.Igamv, self.m1kw, self.atop_vs_time, abot_vs_time,
                self.atop_omega_phase, self.abot_omega_phase, self.dT,
                theta_zero_indexes=botzero,
                implementation=self.implementation))
        #m2w * dua/dt component
        self.E_Igamv_the_BC += (
            speccon1d.dim1sin_E_Igamv_the_BC_aDfDt_linear(
                self.drn, self.m_block, self.eigs, self.tvals,
                self.Igamv, self.m2w, self.atop_vs_time, abot_vs_time,
                self.atop_omega_phase, self.abot_omega_phase, self.dT,
                theta_zero_indexes=botzero,
                implementation=self.implementation))
#        #(m1kw * dua/dt - m2w * dua/dt) component
#        self.E_Igamv_the_BC -= (
#            speccon1d.dim1sin_E_Igamv_the_BC_aDfDt_linear(
#                self.drn, self.m_block, self.eigs, self.tvals,
#                self.Igamv, self.m1kw-self.m2w,
#                self.atop_vs_time, abot_vs_time,
#                self.atop_omega_phase, self.abot_omega_phase,
#                self.dT,theta_zero_indexes=botzero,
#                implementation=self.implementation))
        #dTw * d/dZ(kw * duw/dZ) component
        if self.dTw!=0:
            self.E_Igamv_the_BC -= (self.dTw *
                speccon1d.dim1sin_E_Igamv_the_BC_D_aDf_linear(self.drn,
                    self.m_block, self.eigs, self.tvals, self.Igamv, self.kw,
                    self.wtop_vs_time, wbot_vs_time,
                    self.wtop_omega_phase, self.wbot_omega_phase, self.dT,
                    theta_zero_indexes=botzero,
                    implementation=self.implementation))

        # bottom row of block
        #m2a * duw/dt component
        self.E_Igamv_the_BC -= (
            speccon1d.dim1sin_E_Igamv_the_BC_aDfDt_linear(
                self.drn, self.m_block, self.eigs, self.tvals,
                self.Igamv, self.m2a, self.wtop_vs_time, wbot_vs_time,
                self.wtop_omega_phase, self.wbot_omega_phase, self.dT,
                theta_zero_indexes=topzero,
                implementation=self.implementation))
        #m1ka * dua/dt component
        self.E_Igamv_the_BC -= (
            speccon1d.dim1sin_E_Igamv_the_BC_aDfDt_linear(
                self.drn, self.m_block, self.eigs, self.tvals,
                self.Igamv, self.m1ka, self.atop_vs_time, abot_vs_time,
                self.atop_omega_phase, self.abot_omega_phase, self.dT,
                theta_zero_indexes=topzero,
                implementation=self.implementation))
        #m2a * dua/dt component
        self.E_Igamv_the_BC += (
            speccon1d.dim1sin_E_Igamv_the_BC_aDfDt_linear(
                self.drn, self.m_block, self.eigs, self.tvals,
                self.Igamv, self.m2a, self.atop_vs_time, abot_vs_time,
                self.atop_omega_phase, self.abot_omega_phase, self.dT,
                theta_zero_indexes=topzero,
                implementation=self.implementation))
        #n * dua/dt / mvref/ ua_ component
        self.E_Igamv_the_BC += (
            speccon1d.dim1sin_E_Igamv_the_BC_aDfDt_linear(
                self.drn, self.m_block, self.eigs, self.tvals,
                self.Igamv, self.n, self.atop_vs_time, abot_vs_time,
                self.atop_omega_phase, self.abot_omega_phase, self.dT,
                theta_zero_indexes=topzero,
                implementation=self.implementation))/ (self.mvref * self.ua_)
#       #(m1ka * dua/dt - m2a * dua/dt - n * dua/dt / mvref/ ua_) component
#        self.E_Igamv_the_BC -= (
#            speccon1d.dim1sin_E_Igamv_the_BC_aDfDt_linear(
#                self.drn, self.m_block, self.eigs, self.tvals,
#                self.Igamv, self.m1ka - self.m2a - self.n/self.mvref/self.ua_,
#                self.atop_vs_time, abot_vs_time,
#                self.atop_omega_phase, self.abot_omega_phase,
#                self.dT, theta_zero_indexes=topzero,
#                implementation=self.implementation))
        #S*n * dua/dt component
        self.E_Igamv_the_BC -= (
            speccon1d.dim1sin_E_Igamv_the_BC_abDfDt_linear(
                self.drn, self.m_block, self.eigs, self.tvals,
                self.Igamv, self.S, self.n, self.atop_vs_time, abot_vs_time,
                self.atop_omega_phase, self.abot_omega_phase, self.dT,
                theta_zero_indexes=topzero,
                implementation=self.implementation))/ (self.mvref * self.ua_)
        #dTa * d/dZ(Da * du/dZ) component
        if self.dTw!=0:
            self.E_Igamv_the_BC -= (self.dTa *
                speccon1d.dim1sin_E_Igamv_the_BC_D_aDf_linear(self.drn,
                    self.m_block, self.eigs, self.tvals, self.Igamv, self.Da,
                    self.atop_vs_time, abot_vs_time,
                    self.atop_omega_phase, self.abot_omega_phase, self.dT,
                    theta_zero_indexes=topzero,
                implementation=self.implementation))

        return



    def _make_por(self):
        """make the pore pressure output, ua and uw

        makes `self.por`, the average pore pressure at depths corresponding to
        self.ppress_z and times corresponding to self.tvals.  `self.por`  has size
        (len(ppress_z), len(tvals)).

        Notes
        -----
        Solution to consolidation equation with spectral method for pore pressure at depth is :

        .. math:: u\\left(Z,t\\right)=\\mathbf{\\Phi v E}\\left(\\mathbf{\\Gamma v}\\right)^{-1}\\mathbf{\\theta}+u_{top}\\left({t}\\right)\\left({1-Z}\\right)+u_{bot}\\left({t}\\right)\\left({Z}\\right)

        For pore pressure :math:`\\Phi` is simply :math:`sin\\left({mZ}\\right)` for each value of m


        """

        wbot_vs_time, abot_vs_time = self._normalised_bot_vs_time()
        tvals = self.tvals[self.ppress_z_tval_indexes]

        #water pore pressure at depth
        self.porw = speccon1d.dim1sin_f(self.m, self.ppress_z,
            tvals,
            self.v_E_Igamv_the[:self.neig, self.ppress_z_tval_indexes],
            self.drn, self.wtop_vs_time, wbot_vs_time,
            self.wtop_omega_phase, self.wbot_omega_phase)

        #air pore pressure at depth
        self.pora = speccon1d.dim1sin_f(self.m, self.ppress_z,
            tvals,
            self.v_E_Igamv_the[self.neig:, self.ppress_z_tval_indexes],
            self.drn, self.atop_vs_time, abot_vs_time,
            self.atop_omega_phase, self.abot_omega_phase)

        return




    def _make_avp(self):
        """calculate average pore pressure, for us uc and u

        makes `self.avp`, the average pore pressure at depths corresponding to
        self.avg_ppress_z_pairs and times corresponding to self.tvals.  `self.avp`  has size
        (len(ppress_z), len(tvals)).


        Notes
        -----
        The average pore pressure between Z1 and Z2 is given by:

        .. math:: \\overline{u}\\left(\\left({Z_1,Z_2}\\right),t\\right)=\\int_{Z_1}^{Z_2}{\\mathbf{\\Phi v E}\\left(\\mathbf{\\Gamma v}\\right)^{-1}\\mathbf{\\theta}+u_{top}\\left({t}\\right)\\left({1-Z}\\right)+u_{bot}\\left({t}\\right)\\left({Z}\\right)\,dZ}/\\left({Z_2-Z_1}\\right)

        """

        wbot_vs_time, abot_vs_time = self._normalised_bot_vs_time()
        tvals = self.tvals[self.avg_ppress_z_pairs_tval_indexes]

        #water pore pressure at depth
        self.avpw = speccon1d.dim1sin_avgf(self.m, self.avg_ppress_z_pairs,
            tvals,
            self.v_E_Igamv_the[:self.neig, self.avg_ppress_z_pairs_tval_indexes],
            self.drn, self.wtop_vs_time, wbot_vs_time,
            self.wtop_omega_phase, self.wbot_omega_phase)

        #air pore pressure at depth
        self.avpa = speccon1d.dim1sin_avgf(self.m, self.avg_ppress_z_pairs,
            tvals,
            self.v_E_Igamv_the[self.neig:, self.avg_ppress_z_pairs_tval_indexes],
            self.drn, self.atop_vs_time, abot_vs_time,
            self.atop_omega_phase, self.abot_omega_phase)

        return

    def _make_set(self):
        """calculate settlement

        makes `self.set`, the average pore pressure at depths corresponding to
        self.settlement_z_pairs and times corresponding to self.tvals.  `self.set`  has size
        (len(ppress_z), len(tvals)).


        Notes
        -----
        The average settlement between Z1 and Z2 is given by:

        .. math:: \\overline{\\rho}\\left(\\left({Z_1,Z_2}\\right),t\\right)=\\int_{Z_1}^{Z_2}{m_v\\left({Z}\\right)\\left({\\sigma\\left({Z,t}\\right)-u\\left({Z,t}\\right)}\\right)\\,dZ}


        .. math:: \\overline{\\rho}\\left(\\left({Z_1,Z_2}\\right),t\\right)=\\int_{Z_1}^{Z_2}{m_v\\left({Z}\\right)\\sigma\\left({Z,t}\\right)\\,dZ}+\\int_{Z_1}^{Z_2}{m_v\\left({Z}\\right)\\left({\\mathbf{\\Phi v E}\\left(\\mathbf{\\Gamma v}\\right)^{-1}\\mathbf{\\theta}+u_{top}\\left({t}\\right)\\left({1-Z}\\right)+u_{bot}\\left({t}\\right)\\left({Z}\\right)}\\right)\\,dZ}

        """

        wbot_vs_time, abot_vs_time = self._normalised_bot_vs_time()
        z1 = np.asarray(self.settlement_z_pairs)[:,0]
        z2 = np.asarray(self.settlement_z_pairs)[:,1]

        # setw ua part
        self.setw = speccon1d.dim1sin_integrate_af(self.m,
                     self.settlement_z_pairs,
                     self.tvals[self.settlement_z_pairs_tval_indexes],
                     self.v_E_Igamv_the[self.neig: ,self.settlement_z_pairs_tval_indexes],
                     self.drn, self.m2w - self.m1kw,
                     self.atop_vs_time, abot_vs_time,
                     self.atop_omega_phase, self.abot_omega_phase)
        # setw uw part
        self.setw -= speccon1d.dim1sin_integrate_af(self.m,
                     self.settlement_z_pairs,
                     self.tvals[self.settlement_z_pairs_tval_indexes],
                     self.v_E_Igamv_the[:self.neig ,self.settlement_z_pairs_tval_indexes],
                     self.drn, self.m2w,
                     self.wtop_vs_time, wbot_vs_time,
                     self.wtop_omega_phase, self.wbot_omega_phase)

        # seta ua part
        self.seta = speccon1d.dim1sin_integrate_af(self.m,
                     self.settlement_z_pairs,
                     self.tvals[self.settlement_z_pairs_tval_indexes],
                     self.v_E_Igamv_the[self.neig: ,self.settlement_z_pairs_tval_indexes],
                     self.drn, self.m2a - self.m1ka,
                     self.atop_vs_time, abot_vs_time,
                     self.atop_omega_phase, self.abot_omega_phase)
        # seta uw part
        self.setw -= speccon1d.dim1sin_integrate_af(self.m,
                     self.settlement_z_pairs,
                     self.tvals[self.settlement_z_pairs_tval_indexes],
                     self.v_E_Igamv_the[:self.neig ,self.settlement_z_pairs_tval_indexes],
                     self.drn, self.m2a,
                     self.wtop_vs_time, wbot_vs_time,
                     self.wtop_omega_phase, self.wbot_omega_phase)



        if not self.surcharge_vs_time is None:
            #setw surcharge part
            self.setw += (
                pwise.pxa_ya_cos_multiply_integrate_x1b_x2b_y1b_y2b_multiply_x1c_x2c_y1c_y2c_between_super(
                    self.surcharge_vs_time, self.surcharge_vs_depth,
                    self.m1kw,
                    self.tvals[self.settlement_z_pairs_tval_indexes], z1, z2,
                    omega_phase = self.surcharge_omega_phase,
                    achoose_max=True))
            #seta surcharge part
            self.seta += (
                pwise.pxa_ya_cos_multiply_integrate_x1b_x2b_y1b_y2b_multiply_x1c_x2c_y1c_y2c_between_super(
                    self.surcharge_vs_time, self.surcharge_vs_depth,
                    self.m1ka,
                    self.tvals[self.settlement_z_pairs_tval_indexes], z1, z2,
                    omega_phase = self.surcharge_omega_phase,
                    achoose_max=True))

        self.setw *= self.H * self.mvref
        self.seta *= self.H * self.mvref
        self.set = self.seta + self.setw

        return


    def _plot_porw(self):
        """plot depth vs pore water pressure for various times

        """
        t = self.tvals[self.ppress_z_tval_indexes]
        line_labels = ['{:.3g}'.format(v) for v in t]
        porw_prop = self.plot_properties.pop('porw', dict())
        if not 'xlabel' in porw_prop:
            porw_prop['xlabel'] = 'Pore water pressure'

        #to do
        fig_porw = geotecha.plotting.one_d.plot_vs_depth(self.porw,
                                                        self.ppress_z,
                                      line_labels=line_labels, H = self.H,
                                      RLzero=self.RLzero,
                                      prop_dict=porw_prop)
        return fig_porw
    def _plot_pora(self):
        """plot depth vs pore air pressure for various times

        """
        t = self.tvals[self.ppress_z_tval_indexes]
        line_labels = ['{:.3g}'.format(v) for v in t]
        pora_prop = self.plot_properties.pop('pora', dict())
        if not 'xlabel' in pora_prop:
            pora_prop['xlabel'] = 'Pore air pressure'

        #to do
        fig_pora = geotecha.plotting.one_d.plot_vs_depth(self.pora,
                                                         self.ppress_z,
                                      line_labels=line_labels, H = self.H,
                                      RLzero=self.RLzero,
                                      prop_dict=pora_prop)
        return fig_pora


    def _plot_avpw(self):
        """plot average pore water pressure vs time for various depth intervals

        """

        t = self.tvals[self.avg_ppress_z_pairs_tval_indexes]
        z_pairs = transformations.depth_to_reduced_level(
            np.asarray(self.avg_ppress_z_pairs), self.H, self.RLzero)
        line_labels = ['{:.3g} to {:.3g}'.format(z1, z2) for z1, z2 in z_pairs]

        avpw_prop = self.plot_properties.pop('avpw', dict())
        if not 'ylabel' in avpw_prop:
            avpw_prop['ylabel'] = 'Average pore water pressure'
        fig_avpw = geotecha.plotting.one_d.plot_vs_time(t, self.avpw.T,
                           line_labels=line_labels,
                           prop_dict=avpw_prop)
        fig_avpw.gca().set_xscale('log')
        return fig_avpw

    def _plot_avpa(self):
        """plot average pore air pressure vs time for various depth intervals

        """

        t = self.tvals[self.avg_ppress_z_pairs_tval_indexes]
        z_pairs = transformations.depth_to_reduced_level(
            np.asarray(self.avg_ppress_z_pairs), self.H, self.RLzero)
        line_labels = ['{:.3g} to {:.3g}'.format(z1, z2) for z1, z2 in z_pairs]

        avpa_prop = self.plot_properties.pop('avpa', dict())
        if not 'ylabel' in avpa_prop:
            avpa_prop['ylabel'] = 'Average pore air pressure'
        fig_avpa = geotecha.plotting.one_d.plot_vs_time(t, self.avpa.T,
                           line_labels=line_labels,
                           prop_dict=avpa_prop)
        fig_avpa.gca().set_xscale('log')
        return fig_avpa

    def _plot_set(self):
        """plot settlement vs time for various depth intervals


        """
        t = self.tvals[self.settlement_z_pairs_tval_indexes]
        z_pairs = transformations.depth_to_reduced_level(
            np.asarray(self.settlement_z_pairs), self.H, self.RLzero)
        line_labels = ['{:.3g} to {:.3g}'.format(z1, z2) for z1, z2 in z_pairs]

        set_prop = self.plot_properties.pop('set', dict())
        if not 'ylabel' in set_prop:
            set_prop['ylabel'] = 'Settlement'
        fig_set = geotecha.plotting.one_d.plot_vs_time(t, self.set.T,
                           line_labels=line_labels,
                           prop_dict=set_prop)
#        fig_set.gca().invert_yaxis()
        fig_set.gca().set_xscale('log')
        return fig_set

    def _plot_setw(self):
        """plot water settlement vs time for various depth intervals


        """
        t = self.tvals[self.settlement_z_pairs_tval_indexes]
        z_pairs = transformations.depth_to_reduced_level(
            np.asarray(self.settlement_z_pairs), self.H, self.RLzero)
        line_labels = ['{:.3g} to {:.3g}'.format(z1, z2) for z1, z2 in z_pairs]

        set_prop = self.plot_properties.pop('setw', dict())
        if not 'ylabel' in set_prop:
            set_prop['ylabel'] = 'Water settlement'
        fig_set = geotecha.plotting.one_d.plot_vs_time(t, self.setw.T,
                           line_labels=line_labels,
                           prop_dict=set_prop)
#        fig_set.gca().invert_yaxis()
        fig_set.gca().set_xscale('log')
        return fig_set

    def _plot_seta(self):
        """plot air settlement vs time for various depth intervals


        """
        t = self.tvals[self.settlement_z_pairs_tval_indexes]
        z_pairs = transformations.depth_to_reduced_level(
            np.asarray(self.settlement_z_pairs), self.H, self.RLzero)
        line_labels = ['{:.3g} to {:.3g}'.format(z1, z2) for z1, z2 in z_pairs]

        set_prop = self.plot_properties.pop('seta', dict())
        if not 'ylabel' in set_prop:
            set_prop['ylabel'] = 'Air settlement'
        fig_set = geotecha.plotting.one_d.plot_vs_time(t, self.seta.T,
                           line_labels=line_labels,
                           prop_dict=set_prop)
#        fig_set.gca().invert_yaxis()
        fig_set.gca().set_xscale('log')
        return fig_set

    def produce_plots(self):
        """produce plots of analysis"""

        geotecha.plotting.one_d.pleasing_defaults()

#        matplotlib.rcParams['figure.dpi'] = 80
#        matplotlib.rcParams['savefig.dpi'] = 80

        matplotlib.rcParams.update({'font.size': 11})
        matplotlib.rcParams.update({'font.family': 'serif'})

        self._figures=[]
        #por and porwell
        if not self.ppress_z is None:
            f=self._plot_porw()
            title = 'fig_porw'
            f.set_label(title)
            f.canvas.manager.set_window_title(title)
            self._figures.append(f)

            f=self._plot_pora()
            title = 'fig_pora'
            f.set_label(title)
            f.canvas.manager.set_window_title(title)
            self._figures.append(f)

        if not self.avg_ppress_z_pairs is None:

            f=self._plot_avpw()
            title = 'fig_avpw'
            f.set_label(title)
            f.canvas.manager.set_window_title(title)
            self._figures.append(f)

            f=self._plot_avpa()
            title = 'fig_avpa'
            f.set_label(title)
            f.canvas.manager.set_window_title(title)
            self._figures.append(f)

        #settle
        if not self.settlement_z_pairs is None:
            f=self._plot_set()
            title = 'fig_set'
            f.set_label(title)
            f.canvas.manager.set_window_title(title)
            self._figures.append(f)

            f=self._plot_setw()
            title = 'fig_setw'
            f.set_label(title)
            f.canvas.manager.set_window_title(title)
            self._figures.append(f)

            f=self._plot_seta()
            title = 'fig_seta'
            f.set_label(title)
            f.canvas.manager.set_window_title(title)
            self._figures.append(f)

        #loads
        f=self._plot_loads()
        title = 'fig_loads'
        f.set_label(title)
        f.canvas.manager.set_window_title(title)
        self._figures.append(f)

        #materials
        f=self._plot_materials()
        self._figures.append(f)
        title = 'fig_materials'
        f.set_label(title)
        f.canvas.manager.set_window_title(title)

    def _plot_materials(self):

        material_prop = self.plot_properties.pop('material', dict())

        z_x=[]
        xlabels=[]


        z_x.append(self.m1kw)
        xlabels.append('$m_{{1k}}^w/\\overline{{m}}_v$, $\\left'
            '(\\overline{{m}}_v={:g}\\right)$'.format(self.mvref))
        z_x.append(self.m2w)
        xlabels.append('$m_{{2}}^w/\\overline{{m}}_v$, $\\left'
            '(\\overline{{m}}_v={:g}\\right)$'.format(self.mvref))
        z_x.append(self.m1ka)
        xlabels.append('$m_{{1k}}^a/\\overline{{m}}_v$, $\\left'
            '(\\overline{{m}}_v={:g}\\right)$'.format(self.mvref))
        z_x.append(self.m2a)
        xlabels.append('$m_{{2}}^a/\\overline{{m}}_v$, $\\left'
            '(\\overline{{m}}_v={:g}\\right)$'.format(self.mvref))
        z_x.append(self.kw)
        xlabels.append('$k_w/\\overline{{k}}_w$, $\\left'
            '(\\overline{{k}}_w={:g}\\right)$'.format(self.kwref))
        z_x.append(self.Da)
        xlabels.append('$D_a^\\ast/\\overline{{D}}_a^\\ast$, $\\left'
            '(\\overline{{k}}_w={:g}\\right)$'.format(self.Daref))
        z_x.append(self.S)
        xlabels.append('Saturation, $S_r$')
        z_x.append(self.n)
        xlabels.append('Porosity, $n$')

        return (geotecha.plotting.one_d.plot_single_material_vs_depth(z_x,
                            xlabels, H = self.H,
                            RLzero = self.RLzero,prop_dict = material_prop))
    def _plot_loads(self):
        """plot loads

        """

        load_prop = self.plot_properties.pop('load', dict())
        load_triples=[]
        load_names = []
        ylabels=[]
        #surcharge
        if not self.surcharge_vs_time is None:
            load_names.append('surch')
            ylabels.append('Surcharge')
            load_triples.append(
                [(vs_time, vs_depth, omega_phase) for
                    vs_time, vs_depth, omega_phase  in
                    zip(self.surcharge_vs_time, self.surcharge_vs_depth,
                    self.surcharge_omega_phase)])


        if not self.wtop_vs_time is None:
            load_names.append('wtop')
            ylabels.append('Top water boundary')
            load_triples.append(
                [(vs_time, ([0],[1]), omega_phase) for
                    vs_time, omega_phase  in
                    zip(self.wtop_vs_time, self.wtop_omega_phase)])

        if not self.wbot_vs_time is None:
            #TODO: maybe if drn = 1, multiply bot_vs_time by H to give actual
            # gradient rather than normalised.
            load_names.append('wbot')
            ylabels.append('Bot water boundary')
            load_triples.append(
                [(vs_time, ([1],[1]), omega_phase) for
                    vs_time, omega_phase  in
                    zip(self.wbot_vs_time, self.wbot_omega_phase)])

        if not self.atop_vs_time is None:
            load_names.append('atop')
            ylabels.append('Top air boundary')
            load_triples.append(
                [(vs_time, ([0],[1]), omega_phase) for
                    vs_time, omega_phase  in
                    zip(self.atop_vs_time, self.atop_omega_phase)])

        if not self.abot_vs_time is None:
            #TODO: maybe if drn = 1, multiply bot_vs_time by H to give actual
            # gradient rather than normalised.
            load_names.append('abot')
            ylabels.append('Bot air boundary')
            load_triples.append(
                [(vs_time, ([1],[1]), omega_phase) for
                    vs_time, omega_phase  in
                    zip(self.abot_vs_time, self.abot_omega_phase)])

        return (geotecha.plotting.one_d.plot_generic_loads(load_triples, load_names,
                    ylabels=ylabels, H = self.H, RLzero=self.RLzero,
                    prop_dict=load_prop))


def main():
    """Run speccon1d_unsat as scipt"""
    a = GenericInputFileArgParser(obj=Speccon1dUnsat,
                                  methods=[('make_all', [], {})],
                                 pass_open_file=True)

    a.main()

if __name__ == '__main__':
    import nose
    nose.runmodule(argv=['nose', '--verbosity=3', '--with-doctest'])
#    nose.runmodule(argv=['nose', '--verbosity=3'])
    main()



