from typing import List, Set
import argparse
import logging
import re

from netCDF4 import Dataset


# walk the group tree.
def walktree(top):
    values = top.groups.values()
    yield values
    for value in top.groups.values():
        for children in walktree(value):
            yield children

class NCInfo:
    def __init__(self, ncfile: str):
        self.rootgroup = Dataset(ncfile)
        self.vars_with_coords = set()
        self.vars_meta = set()
        self.dims = set()
        self.coords = set()
        self.ancillary_data = set()  # TODO: include ancillary_data check

        for children in walktree(self.rootgroup):
            if self.rootgroup.variables:
                for nvar, var in self.rootgroup.variables.items(): # pylint: disable=E1101
                    if 'coordinates' in var.ncattrs():
                        self.vars_with_coords.add(nvar)
                        split_coords = self._extract_coordinates(var.coordinates)
                        self.coords.update(split_coords)
                    elif 'grid_mapping' in var.ncattrs():
                        self.vars_with_coords.add(nvar)
                        self.ancillary_data.add(var.grid_mapping)
                    else:
                        self.vars_meta.add(nvar)

                for dim in self.rootgroup.dimensions: # pylint: disable=E1133
                    self.dims.add(dim)

            for child in children:
                if child.variables:
                    for varn, var in child.variables.items():
                        if 'coordinates' in var.ncattrs():
                            self.vars_with_coords.add(f'{child.path}/{varn}')
                            split_coords = self._extract_coordinates(var.coordinates)
                            self.coords.update(split_coords)
                        elif 'grid_mapping' in var.ncattrs():
                            self.vars_with_coords.add(varn)
                            self.ancillary_data.add(var.grid_mapping)
                        else:
                            self.vars_meta.add(f'{child.path}/{varn}')

                    for dim in child.dimensions:
                        self.dims.add(f'{child.path}/{dim}')

    def get_science_variables(self) -> Set[str]:
        return self.vars_with_coords - self.dims - self.coords - self.ancillary_data

    def get_metadata_variables(self) -> Set[str]:
        return self.vars_meta - self.dims - self.coords - self.ancillary_data

    def _extract_coordinates(self, coordinates: str) -> List[str]:
        """ Take a string of potentially coordinate datasets and return a list
        of separate coordinate dataset names.

        """
        return re.split(r'\s+|,\s*', coordinates)


# Main program start for testing with any input file
#
if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(prog='scan', description='Run NetCDF scaning tool')
    PARSER.add_argument('--file',
                        help='The input file for scanning variables.')
    ARGS = PARSER.parse_args()

    logger = logging.getLogger("SwotRepr")
    syslog = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s")
    #       "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] [%(user)s] %(message)s")
    syslog.setFormatter(formatter)
    logger.addHandler(syslog)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    input_file = ARGS.file

    # ----------------------------------------
    info4 = NCInfo(input_file)
    print(info4.rootgroup.data_model)
    sciVars = info4.get_science_variables()
    print("--------- science_variables ----------")
    print(*(sorted(sciVars)), sep="\n")
    metaVars = info4.get_metadata_variables()
    print("--------- metadata ----------")
    print(*(sorted(metaVars)), sep="\n")