#!/usr/bin/env python

import numpy as np

from landlab import Component


# A landlab component should inherit from the Component class.
class ExampleComponent(Component):
    # The name of your component
    _name = 'Example'

    # Listing of variable names that can be set by another component.
    _input_var_names = (
        'lithosphere__overlying_pressure',
        'lithosphere__elevation',
        'planet_surface_sediment__deposition_increment',
    )
    
    # Listing of variable names that the component can provide another.
    _output_var_names = (
        'lithosphere__elevation_increment',
        'lithosphere__elevation',
    )

    # Units for each of the input and output varaibles.
    _var_units = {
        'lithosphere__overlying_pressure': 'Pa',
        'lithosphere__elevation': 'm',
        'lithosphere__elevation_increment': 'm',
        'planet_surface_sediment__deposition_increment': 'm',
    }

    # The grid element where values are defined on the grid. A variable grid
    # element must be one of the following: 'node', 'cell', 'link', 'face'.
    _var_mapping = {
        'lithosphere__overlying_pressure': 'node',
        'lithosphere__elevation': 'node',
        'lithosphere__elevation_increment': 'node',
        'planet_surface_sediment__deposition_increment': 'node',
    }
    
    # A short description for each variable.
    _var_defs = {
        'lithosphere__overlying_pressure':
            'The pressure at the base of the lithosphere',
        'lithosphere__elevation':
            'The elevation of the top of the lithosphere, i.e., the land '
            'surface',
        'lithosphere__elevation_increment':
            'The change in elevation of the top of the lithosphere (the land '
            'surface) in one timestep',
        'planet_surface_sediment__deposition_increment':
            'The amount of sediment deposited at the land surface in one '
            'timestep',
    }
    
    ### ---> 2. Make sure that self._grid is an alias for the grid after
    # initialization, below
    ################################

    def __init__(self, grid, **kwds):
        self._eet = kwds.pop('eet', 65000.)
        self._youngs = kwds.pop('youngs', 7e10)
        self._method = kwds.pop('method', 'airy')
        self._grid = grid

        assert_method_is_valid(self._method)

        super(ExampleComponent, self).__init__(grid, **kwds)

        for name in self._input_var_names:
            if name not in self.grid.at_node:
                self.grid.add_zeros('node', name, units=self._var_units[name])

        for name in self._output_var_names:
            if name not in self.grid.at_node:
                self.grid.add_zeros('node', name, units=self._var_units[name])

        self._last_load = self.grid.field_values('node', 'lithosphere__overlying_pressure').copy()

        self._nodal_values = self.grid['node']

        self._r = self._set_kei_func_grid()

    def _set_kei_func_grid(self):
        from scipy.special import kei

        alpha = get_flexure_parameter(self._eet, self._youngs, 2)
        dx, dy = np.meshgrid(
            np.arange(self._grid.number_of_node_columns) * self._grid.dx,
            np.arange(self._grid.number_of_node_rows) * self._grid.dx)

        return kei(np.sqrt(dx ** 2 + dy ** 2) / alpha)

    def update(self, n_procs=1):
        elevation = self._nodal_values['lithosphere__elevation']
        load = self._nodal_values['lithosphere__overlying_pressure']
        deflection = self._nodal_values['lithosphere__elevation_increment']
        deposition = self._nodal_values['planet_surface_sediment__deposition_increment']

        new_load = ((load - self._last_load) +
                    (deposition * 2650. * 9.81).flat)

        self._last_load = load.copy()

        deflection.fill(0.)

        if self._method == 'airy':
            deflection[:] = new_load / (3300. * 9.81)
        else:
            self.subside_loads(new_load, deflection=deflection,
                               n_procs=n_procs)
        np.subtract(elevation, deflection, out=elevation)

    def subside_loads(self, loads, deflection=None, n_procs=1):
        if deflection is None:
            deflection = np.empty(self.shape, dtype=np.float)

        from .cfuncs import subside_grid_in_parallel

        w = deflection.reshape(self._grid.shape)
        load = loads.reshape(self._grid.shape)
        alpha = get_flexure_parameter(self._eet, self._youngs, 2)

        subside_grid_in_parallel(w, load, self._r, alpha, n_procs)

        return deflection


if __name__ == "__main__":
    import doctest
    doctest.testmod()
