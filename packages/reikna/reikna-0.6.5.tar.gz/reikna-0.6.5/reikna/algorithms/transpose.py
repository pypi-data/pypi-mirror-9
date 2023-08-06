import numpy

import reikna.helpers as helpers
from reikna.core import Computation, Parameter, Annotation, Type

TEMPLATE = helpers.template_for(__file__)


def transpose_shape(shape, axes):
    return tuple(shape[i] for i in axes)

def transpose_axes(axes, b_start, c_start):
    return axes[:b_start] + axes[c_start:] + axes[b_start:c_start]

def possible_transposes(shape_len):
    for b_start in range(shape_len - 1):
        for c_start in range(b_start + 1, shape_len):
            yield b_start, c_start

def get_operations(source, target):
    visited = set([source])
    actions = list(possible_transposes(len(source)))

    def traverse(node, breadcrumbs, current_best):
        if current_best is not None and len(breadcrumbs) >= len(current_best):
            return current_best

        for b_start, c_start in actions:
            result = transpose_axes(node, b_start, c_start)
            if result in visited and result != target:
                continue
            visited.add(result)

            new_breadcrumbs = breadcrumbs + ((b_start, c_start),)

            if result == target:
                if current_best is None or len(current_best) > len(new_breadcrumbs):
                    return new_breadcrumbs

            current_best = traverse(result, new_breadcrumbs, current_best)
        return current_best

    return traverse(source, tuple(), None)

def get_transposes(shape, axes=None):

    source = tuple(range(len(axes)))
    if axes is None:
        axes = tuple(reversed(axes))
    else:
        assert set(source) == set(axes)

    for i in range(len(source) - 1, 0, -1):
        if source[:i] == axes[:i]:
            result = get_operations(source[i:], axes[i:])
            prefix = source[:i]
            break
    else:
        result = get_operations(source, axes)
        prefix = tuple()

    operations = [(b + len(prefix), c + len(prefix)) for b, c in result]

    transposes = []
    for b_start, c_start in operations:
        transposes.append((shape[:b_start], shape[b_start:c_start], shape[c_start:]))
        shape = transpose_axes(shape, b_start, c_start)
    return transposes


class Transpose(Computation):
    """
    Bases: :py:class:`~reikna.core.Computation`

    Changes the order of axes in a multidimensional array.
    Works analogous to ``numpy.transpose``.

    :param arr_t: an array-like defining the initial array.
    :param axes: tuple with the new axes order.
        If ``None``, then axes will be reversed.

    .. py:function:: compiled_signature(output:o, input:i)

        :param output: an array with all the attributes of ``arr_t``,
            with the shape permuted according to ``axes``.
        :param input: an array with all the attributes of ``arr_t``.
    """

    def __init__(self, arr_t, axes=None, block_width_override=None):

        self._block_width_override = block_width_override

        all_axes = range(len(arr_t.shape))
        if axes is None:
            axes = tuple(reversed(all_axes))
        else:
            assert set(axes) == set(all_axes)

        self._axes = tuple(axes)

        output_shape = transpose_shape(arr_t.shape, self._axes)
        output_arr = Type(arr_t.dtype, output_shape)

        Computation.__init__(self, [
            Parameter('output', Annotation(output_arr, 'o')),
            Parameter('input', Annotation(arr_t, 'i'))])

    def _add_transpose(self, plan, device_params,
            mem_out, mem_in, batch_shape, height_shape, width_shape):

        bso = self._block_width_override
        block_width = device_params.local_mem_banks if bso is None else bso

        if block_width ** 2 > device_params.max_work_group_size:
            # If it is not CPU, current solution may affect performance
            block_width = int(numpy.sqrt(device_params.max_work_group_size))

        input_height = helpers.product(height_shape)
        input_width = helpers.product(width_shape)
        batch = helpers.product(batch_shape)

        blocks_per_matrix = helpers.min_blocks(input_height, block_width)
        grid_width = helpers.min_blocks(input_width, block_width)

        render_kwds = dict(
            input_width=input_width, input_height=input_height, batch=batch,
            block_width=block_width,
            grid_width=grid_width,
            blocks_per_matrix=blocks_per_matrix,
            input_slices=[len(batch_shape), len(height_shape), len(width_shape)],
            output_slices=[len(batch_shape), len(width_shape), len(height_shape)])

        plan.kernel_call(
            TEMPLATE.get_def('transpose'), [mem_out, mem_in],
            global_size=(batch, blocks_per_matrix * block_width, grid_width * block_width),
            local_size=(1, block_width, block_width),
            render_kwds=render_kwds)

    def _build_plan(self, plan_factory, device_params, output, input_):
        plan = plan_factory()
        transposes = get_transposes(input_.shape, self._axes)

        mem_out = None
        for i, transpose in enumerate(transposes):

            batch_shape, height_shape, width_shape = transpose

            mem_in = input_ if i == 0 else mem_out
            if i == len(transposes) - 1:
                mem_out = output
            else:
                mem_out = plan.temp_array(
                    batch_shape + width_shape + height_shape, output.dtype)

            self._add_transpose(plan, device_params,
                mem_out, mem_in, batch_shape, height_shape, width_shape)

        return plan
