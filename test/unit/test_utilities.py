from unittest.mock import Mock

import numpy as np
import xarray

from PyMods.utilities import (create_coordinates_key, get_variable_values,
                              get_coordinate_variable,
                              get_variable_numeric_fill_value,
                              get_variable_group_and_name)
from test.test_utils import TestBase


class TestUtilities(TestBase):

    def test_create_coordinates_key(self):
        """ When given a string, ensure a list is returned that is split based
            on spaces, commas and space, commas.

        """
        test_args = [['spaces', 'lon lat'],
                     ['multiple spaces', 'lon    lat'],
                     ['comma', 'lon,lat'],
                     ['comma-space', 'lon, lat'],
                     ['comma-multiple-space', 'lon,    lat']]

        expected_output = ('lon', 'lat')

        for description, coordinates in test_args:
            with self.subTest(description):
                self.assertEqual(create_coordinates_key(coordinates),
                                 expected_output)

    def test_get_variable_values(self):
        """ Ensure values for a variable are retrieved, respecting the absence
            or presence of a time variable in the dataset.

        """

        with self.subTest('3-D dataset, with time'):
            dataset_with_time = xarray.open_dataset('test/data/africa.nc',
                                                    decode_cf=False)
            red_var = dataset_with_time.variables.get('red_var')
            self.assertEqual(len(red_var.shape), 3)

            red_var_values = get_variable_values(dataset_with_time, red_var)
            self.assertTrue(isinstance(red_var_values, np.ndarray))
            self.assertEqual(len(red_var_values.shape), 2)
            self.assertEqual(red_var_values.shape, red_var.shape[-2:])

            dataset_with_time.close()

    def test_get_coordinate_variables(self):
        """ Ensure the longitude or latitude coordinate variable, is retrieved
            when requested.

        """
        dataset = xarray.open_dataset('test/data/africa.nc', decode_cf=False)
        coordinates_tuple = ['lat', 'lon']

        for coordinate in coordinates_tuple:
            with self.subTest(coordinate):
                coordinates = get_coordinate_variable(dataset,
                                                      coordinates_tuple,
                                                      coordinate)

                self.assertTrue(isinstance(coordinates,
                                           xarray.core.variable.Variable))

        with self.subTest('Non existent coordinate variable returns None'):
            absent_coordinates_tuple = ['latitude']
            coordinates = get_coordinate_variable(dataset,
                                                  absent_coordinates_tuple,
                                                  absent_coordinates_tuple[0])

    def test_get_variable_group_and_name(self):
        """ Ensure a full variable name, containing the group is correctly
            split into the group and the name.

        """
        test_args = [['no_group', '', 'no_group'],
                     ['group_name/variable', 'group_name', 'variable'],
                     ['/nested/group/other_variable', '/nested/group', 'other_variable']]

        for variable_string, expected_group, expected_name in test_args:
            with self.subTest(variable_string):
                group, name = get_variable_group_and_name(variable_string)
                self.assertEqual(expected_group, group)
                self.assertEqual(expected_name, name)

    def test_get_variable_numeric_fill_value(self):
        """ Ensure a fill value is retrieved from a variable that has a vaild
            numeric value, and is cast as either an integer or a float. If no
            fill value is present on the variable, or the fill value is non-
            numeric, the function should return None. This is because
            pyresample explicitly checks for float or int fill values in
            get_sample_from_neighbour_info.

        """
        variable = Mock(spec=xarray.core.variable.Variable)

        test_args = [['np.float', np.float, 4.0, 4.0],
                     ['np.float128', np.float128, 4.0, 4.0],
                     ['np.float16', np.float16, 4.0, 4.0],
                     ['np.float32', np.float32, 4.0, 4.0],
                     ['np.float64', np.float64, 4.0, 4.0],
                     ['np.float_', np.float_, 4.0, 4.0],
                     ['np.int', np.int, 5, 5],
                     ['np.int0', np.int, 5, 5],
                     ['np.int16', np.int, 5, 5],
                     ['np.int32', np.int, 5, 5],
                     ['np.int64', np.int, 5, 5],
                     ['np.int8', np.int, 5, 5],
                     ['np.uint', np.uint, 5, 5],
                     ['np.uint0', np.uint0, 5, 5],
                     ['np.uint16', np.uint16, 5, 5],
                     ['np.uint32', np.uint32, 5, 5],
                     ['np.uint64', np.uint64, 5, 5],
                     ['np.uint8', np.uint8, 5, 5],
                     ['np.uintc', np.uintc, 5, 5],
                     ['np.uintp', np.uintp, 5, 5],
                     ['np.long', np.long, 5, 5],
                     ['float', float, 4.0, 4.0],
                     ['int', int, 5, 5],
                     ['str', str, '1235', None]]

        for description, caster, fill_value, expected_output in test_args:
            with self.subTest(description):
                variable.attrs.get.return_value = caster(fill_value)
                self.assertEqual(get_variable_numeric_fill_value(variable),
                                 expected_output)

        with self.subTest('Missing fill value attribute'):
            variable.attrs.get.return_value = None
            self.assertEqual(get_variable_numeric_fill_value(variable),
                             expected_output)