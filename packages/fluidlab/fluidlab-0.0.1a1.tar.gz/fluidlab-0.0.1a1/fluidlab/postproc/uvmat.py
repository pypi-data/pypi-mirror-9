"""Uvmat interface (:mod:`fluidlab.postproc.uvmat`)
===================================================

From matlab, something like::

  system(['python -m fluidlab.postproc.uvmat ' path_to_instructions_xml])

"""

import os
import sys

import numpy as np
import scipy

import logging
log_level = logging.INFO  # to get information messages
# log_level = logging.WARNING  # no information messages
logging.basicConfig(format='%(message)s',
                    level=log_level)

from fluiddyn.util.containerxml import ContainerXML, tidy_containerxml
from fluidlab.postproc.serieofarrays import SerieOfArraysFromFiles


class InstructionsUVMAT(ContainerXML):

    def __init__(self, **kargs):

        if 'tag' not in kargs:
            kargs['tag'] = 'instructions_uvmat'

        super(InstructionsUVMAT, self).__init__(**kargs)

        if kargs['tag'] == 'instructions_uvmat' and 'path_file' in kargs:
            self._init_root()

    def _init_root(self):

        # get nicer names and a simpler organization...
        tidy_containerxml(self)

        input_table = self.input_table.split(' & ')
        self.input_table = '|'.join(input_table)

        path_dir_root = input_table[0]
        path_dir_input = os.path.join(path_dir_root, input_table[1][1:])
        self.set_attrib('path_dir_input', path_dir_input)

        self.set_attrib(
            'path_dir_output',
            path_dir_input + self.output_dir_ext)

        ir = self.index_range
        slice0 = [ir.first_i, ir.last_i+1, ir.incr_i]
        try:
            slice1 = [ir.first_j-1, ir.last_j, ir.incr_j]
            self.set_attrib('index_slices', [slice0, slice1])
        except AttributeError:
            self.set_attrib('index_slices', [slice0])


class ActionBase(object):
    def __init__(self, instructions):
        self.instructions = instructions

        # create the serie of arrays
        logging.info('Create the serie of arrays')
        self.serie_arrays = SerieOfArraysFromFiles(
            path=instructions.path_dir_input,
            index_slices=instructions.index_slices)


class ActionAverage(ActionBase):
    """Compute the average and save as a png file."""
    def run(self):
        instructions = self.instructions
        sas = self.serie_arrays
        # compute the average
        logging.info('Compute the average')
        a = sas.get_array_from_indices(
            tuple(slice[0] for slice in instructions.index_slices))
        mean = np.zeros_like(a, dtype=np.float32)
        nb_fields = 0
        for indices in sas.iter_indices():
            mean += sas.get_array_from_indices(indices)
            nb_fields += 1
        mean /= nb_fields

        strindices_first_file = sas.compute_strindices_from_indices(
            [slice[0] for slice in instructions.index_slices])
        strindices_last_file = sas.compute_strindices_from_indices(
            [slice[1]-1 for slice in instructions.index_slices])

        name_file = (sas.base_name + sas.separator_base_index
                     + strindices_first_file + '-' + strindices_last_file
                     + '.' + sas.extension_file)

        path_save = os.path.join(instructions.path_dir_output, name_file)
        logging.info('Save in file:\n%s',  path_save)
        scipy.misc.imsave(path_save, mean)
        return mean


actions_classes = {'aver_stat': ActionAverage}


def main():
    if len(sys.argv) > 1:
        path_instructions_xml = sys.argv[1]
    else:  # a test
        path_instructions_xml = os.path.join(
            os.environ['HOME'],
            # 'useful/save',
            'Dev/Matlab/Demo/UVMAT_DEMO04_PIV_challenge_2005_CaseC',
            'Images.stat/0_XML',
            'c001ab.xml')

    logging.info('\nFrom Python, start with instructions in xml file:\n%s',
                 path_instructions_xml)

    instructions = InstructionsUVMAT(path_file=path_instructions_xml)

    action_name = instructions.action.action_name
    logging.info('Verify if the action "%s" is implemented by FluidDyn',
                 action_name)
    if action_name not in actions_classes.keys():
        raise NotImplementedError(
            'action "' + action_name + '" is not yet implemented.')

    Action = actions_classes[action_name]
    action = Action(instructions)
    return action.run()


if __name__ == '__main__':

    result = main()
