"""..
    Copyright (c) 2014-2015, Magni developers.
    All rights reserved.
    See LICENSE.rst for further information.

Module for wrapping the Magni IPython Notebook examples.

**This module is based on the "ipnbdoctest.py" script by Benjamin
Ragan-Kelley (MinRK)**, source: https://gist.github.com/minrk/2620735.

"""

from __future__ import division, print_function
import base64
import contextlib
import os
import shutil
import unittest
import types
try:
    from Queue import Empty  # Python 2
except ImportError:
    from queue import Empty  # Python 3
try:
    from StringIO import StringIO as BytesIO  # Python 2
except ImportError:
    from io import BytesIO  # Python 3

from IPython.kernel import KernelManager
from IPython.nbformat.current import reads, NotebookNode
import numpy as np
import scipy.misc

import magni


class _Meta(type):
    """
    Identification of IPython Notebook examples and construction of test class.

    """

    def __new__(class_, name, bases, attrs):
        path = magni.__path__[0].rsplit(os.sep, 1)[0]
        path = path + os.path.sep + 'examples' + os.path.sep

        for filename in os.listdir(path):
            if filename[-6:] == '.ipynb':
                name = 'test_' + filename[:-6].replace('-', '_')
                func = attrs['_run_example']
                func = types.FunctionType(func.__code__, func.__globals__,
                                          name, (path + filename,))
                func.__doc__ = func.__doc__.format(filename)
                attrs[name] = func

        return type.__new__(class_, name, bases, attrs)


# For python 2 and 3 compatibility
class _Hack(_Meta):
    def __new__(class_, name, bases, attrs):
        return _Meta(name, (unittest.TestCase,), attrs)


_TestCase = type.__new__(_Hack, 'temp', (), {})


class TestIPythonExamples(_TestCase):
    """
    Test of Ipython Notebook examples for equality of output to reference.

    """

    def setUp(self):
        """
        Identify IPython Notebook examples to run.

        """

        path = magni.__path__[0].rsplit(os.sep, 1)[0]
        path = path + os.path.sep + 'examples' + os.path.sep
        files_to_copy = ['example.mi', 'data.hdf5', 'display.py']

        for cfile in files_to_copy:
            shutil.copy(os.path.join(path, cfile), '.')

    def _run_example(self, ipynb):
        """
        Test of {} Magni IPython Notebook example.

        """

        with open(ipynb) as f_ipynb:
            notebook = reads(f_ipynb.read(), 'json')

        notebook_result = _check_ipynb(notebook)
        passed, successes, failures, errors, report = notebook_result

        self.assertTrue(passed, msg=report)
        error_msg = ('Magni IPython Notebook example status:\n' +
                     'Successes: {}, Failures: {}, Errors: {}').format(
                         successes, failures, errors)
        self.assertEqual(errors + failures, 0, msg=error_msg)


def _check_ipynb(notebook):
    """
    Check an IPython Notebook for matching input and output.

    Each cell input in the `notebook` is executed and the result is compared
    to the cell output saved in the `notebook`.

    Parameters
    ----------
    notebook : IPython.nbformat.current.NotebookNode
        The notebook to check for matching input and output.

    Returns
    -------
    passed : Bool
        The indicator of a successful check (or not).
    sucessess : int
        The number of cell outputs that matched.
    failures : int
        The number of cell outputs that failed to match.
    errors : int
        The number of cell executions that resulted in errors.
    report : str
        The report detailing possible failures and errors.

    """

    kernel_manager = KernelManager()
    kernel_manager.start_kernel()
    kernel_client = kernel_manager.client()
    kernel_client.start_channels()
    iopub = kernel_client.iopub_channel
    shell = kernel_client.shell_channel

    successes = 0
    failures = 0
    errors = 0

    report = ''
    for worksheet in notebook.worksheets:
        for cell in worksheet.cells:
            if cell.cell_type == 'code':
                try:
                    test_results = _execute_cell(cell, shell, iopub)
                except RuntimeError as e:
                    report += ('{!s} in cell number: {}'
                               .format(e, cell.prompt_number))
                    errors += 1
                    break

                identical_output = all(
                    [_compare_cell_output(test_result, reference)
                     for test_result, reference in
                     zip(test_results, cell.outputs)])

                if identical_output:
                    successes += 1
                else:
                    failures += 1

                    try:
                        str_test_results = [
                            '(for out {})\n'.format(k) + '\n'.join(
                                [' : '.join([str(key), str(val)])
                                 for key, val in t.items()
                                 if key not in ('metadata', 'png')]
                            ) for k, t in enumerate(test_results)]
                        str_cell_outputs = [
                            '(for out {})\n'.format(k) + '\n'.join(
                                [' : '.join([str(key), str(val)])
                                 for key, val in t.items()
                                 if key not in ('metadata', 'png')]
                            ) for k, t in enumerate(cell.outputs)]
                    except TypeError as e:
                        report += 'TypeError in ipynb_examples test\n\n'
                        for entry in cell.outputs:
                            if 'traceback' in entry.keys():
                                for item in entry['traceback']:
                                    report += str(item) + '\n'
                    else:
                        report += '\n' * 2 + '~' * 40
                        report += (
                            '\nFailure in {}:{}\nGot: {}\n\n\nExpected: {}'
                        ).format(notebook.metadata.name,
                                 cell.prompt_number,
                                 '\n'.join(str_test_results),
                                 '\n'.join(str_cell_outputs))

    kernel_client.stop_channels()
    kernel_manager.shutdown_kernel()

    passed = not (failures or errors)

    return passed, successes, failures, errors, report


def _compare_cell_output(test_result, reference):
    """
    Compare a cell test output to a reference output.

    Parameters
    ----------
    test_results : IPython.nbformat.current.NotebookNode
        The cell test result that must be compared to the reference.
    reference : IPython.nbformat.current.NotebookNode
        The reference cell output to compare to.

    Returns
    -------
    comparison_result : bool
        The indicator of equality between the test output and the reference.

    """

    skip_compare = ['traceback', 'latex', 'prompt_number']

    if test_result['output_type'] == 'display_data':
        # Prevent comparison of matplotlib figure instance memory addresses
        skip_compare.append('text')
        skip_compare.append('metadata')

    for key in reference:

        if key not in test_result:
            raise Exception(str(reference) + '!!!!!' + str(test_result))
            return False
        elif key not in skip_compare:
            if key == 'text':
                if test_result[key].strip() != reference[key].strip():
                    return False
            elif key == 'png':
                ref_png = base64.b64decode(reference[key])
                ref_ndarray = scipy.misc.imread(BytesIO(ref_png))
                cmp_png = base64.b64decode(test_result[key])
                cmp_ndarray = scipy.misc.imread(BytesIO(cmp_png))

                # check shape of images
                if cmp_ndarray.shape != ref_ndarray.shape:
                    return False

                # mask of channels in pixels with different values
                diff = cmp_ndarray != ref_ndarray
                # mask of pixels with different values
                diff = np.any(diff, axis=2)
                # mask of non-transparent pixels with different values
                diff = diff * np.bool_(ref_ndarray[:, :, 3])

                # check if all non-transparent pixels match
                if diff.sum() == 0:
                    continue

                # coordinates of non-transparent pixels with different values
                points = np.where(diff)
                points = np.int32(points + (np.zeros(points[0].shape),)).T

                # mask of black pixels
                mask = ((ref_ndarray[:, :, 0] == 0) *
                        (ref_ndarray[:, :, 1] == 0) *
                        (ref_ndarray[:, :, 2] == 0) *
                        (ref_ndarray[:, :, 3] == 255))

                # lookup table of the top most connected black pixel of the
                # looked up pixel
                C_N = np.zeros(mask.shape, dtype=np.int16)

                for i in range(0, mask.shape[0] - 1):
                    C_N[i + 1, :] = (np.logical_not(mask[i, :]) * i +
                                     mask[i, :] * C_N[i, :])

                # lookup table of the right most connected black pixel of the
                # looked up pixel
                C_E = np.zeros(mask.shape, dtype=np.int16)

                for i in range(mask.shape[1] - 1, 0, -1):
                    C_E[:, i - 1] = (np.logical_not(mask[:, i]) * i +
                                     mask[:, i] * C_E[:, i])

                # lookup table of the bottom most connected black pixel of the
                # looked up pixel
                C_S = np.zeros(mask.shape, dtype=np.int16)

                for i in range(mask.shape[0] - 1, 0, -1):
                    C_S[i - 1, :] = (np.logical_not(mask[i, :]) * i +
                                     mask[i, :] * C_S[i, :])

                # lookup table of the left most connected black pixel of the
                # looked up pixel
                C_W = np.zeros(mask.shape, dtype=np.int16)

                for i in range(0, mask.shape[1] - 1):
                    C_W[:, i + 1] = (np.logical_not(mask[:, i]) * i +
                                     mask[:, i] * C_W[:, i])

                # loop over non-transparent pixels with different values
                for i, point in enumerate(points):
                    y, x = point[:2]

                    # find other non-transparent pixels with different values
                    # ... with the same y-coordinate
                    matches_y = np.where(points[:, 0] == y)[0]
                    # ... with an x-coordinate at least 10 pixels away
                    matches_y = matches_y[
                        np.abs(points[matches_y, 1] - x) > 10
                    ]
                    # ... which is connected by black pixels
                    matches_y = matches_y[
                        (points[matches_y, 1] >= C_W[y, x]) *
                        (points[matches_y, 1] <= C_E[y, x])
                    ]

                    # find other non-transparent pixels with different values
                    # ... with the same x-coordinate
                    matches_x = np.where(points[:, 1] == x)[0]
                    # ... with a y-coordinate at least 10 pixels away
                    matches_x = matches_x[
                        np.abs(points[matches_x, 0] - y) > 10
                    ]
                    # ... which is connected by black pixels
                    matches_x = matches_x[
                        (points[matches_x, 0] >= C_N[y, x]) *
                        (points[matches_x, 0] <= C_S[y, x])
                    ]

                    if len(matches_y) + len(matches_x) == 0:
                        # this pixel cannot be the corner of a box
                        break

                    for j in matches_y:
                        for k in matches_x:
                            # loop over combinations of possible boxes
                            y_test = points[k, 0]
                            x_test = points[j, 1]

                            if not C_W[y_test, x] <= x_test <= C_E[y_test, x]:
                                # one horizontal line of the box isn't black
                                continue

                            if not C_N[y, x_test] <= y_test <= C_S[y, x_test]:
                                # one vertical line of the box isn't black
                                continue

                            # the box is a box and the corners are flagged
                            points[i, 2] = points[j, 2] = points[k, 2] = 1

                if not np.all(points[:, 2]):
                    return False
            else:
                if test_result[key] != reference[key]:
                    return False

    return True


def _execute_cell(cell, shell, iopub, timeout=300):
    """
    Execute an IPython Notebook Cell and return the cell output.

    Parameters
    ----------
    cell : IPython.nbformat.current.NotebookNode
        The IPython Notebook cell to execute.
    shell : IPython.kernel.blocking.channels.BlockingShellChannel
        The shell channel which the cell is submitted to for execution.
    iopub : IPython.kernel.blocking.channels.BlockingIOPubChannel
        The iopub channel used to retrieve the result of the execution.
    timeout : int
        The number of seconds to wait for the execution to finish before giving
        up.

    Returns
    -------
    cell_outputs : list
        The list of NotebookNodes holding the result of the execution.

    """

    # Execute input
    shell.execute(cell.input)
    exe_result = shell.get_msg(timeout=timeout)
    if exe_result['content']['status'] == 'error':
        raise RuntimeError('Failed to execute cell due to error: {!r}'.format(
            str(exe_result['content']['evalue'])))

    cell_outputs = list()

    # Poll for iopub messages until no more messages are available
    while True:
        try:
            msg = iopub.get_msg(timeout=0.5)
        except Empty:
            break

        msg_type = msg['msg_type']
        if msg_type in ('status', 'pyin'):
            continue

        content = msg['content']
        node = NotebookNode(output_type=msg_type)

        if msg_type == 'stream':
            node.stream = content['name']
            node.text = content['data']
        elif msg_type in ('display_data', 'pyout'):
            node['metadata'] = content['metadata']
            for mime, data in content['data'].items():
                attr = mime.split('/')[-1].lower()
                attr = attr.replace('+xml', '').replace('plain', 'text')
                setattr(node, attr, data)
            if msg_type == 'pyout':
                node.prompt_number = content['execution_count']
        elif msg_type == 'pyerr':
            node.ename = content['ename']
            node.evalue = content['evalue']
            node.traceback = content['traceback']
        else:
            raise RuntimeError('Unhandled iopub message of type: {}'.format(
                msg_type))

        cell_outputs.append(node)

    return cell_outputs
