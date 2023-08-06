***************
Release history
***************


0.6.5 (31 Mar 2015)
===================

* CHANGED: the correspondence for ``numpy.uintp`` is not registered by default anymore --- this type is not really useful in CPU-GPU interaction.

* FIXED: (reported by J. Vacher) dtype/ctype correspondences for 64-bit integer types are registered even if the Python interpreter is 32-bit.

* ADDED: :py:class:`~reikna.core.computation.ComputationCallable` objects expose the attribute ``thread``.

* ADDED: :py:class:`~reikna.fft.FFTShift` computation.

* ADDED: an example of an element-reshuffling transformation.


0.6.4 (29 Sep 2014)
===================

* CHANGED: renamed ``power_dtype`` parameter to ``exponent_dtype`` (a more correct term) in :py:func:`~reikna.cluda.functions.pow`.

* FIXED: (PR by @ringw) exception caused by printing CUDA program object.

* FIXED: :py:func:`~reikna.cluda.functions.pow` (0, 0) now returns 1 as it should.

* ADDED: an example of :py:class:`~reikna.fft.FFT` with a custom transformation.

* ADDED: a type check in the :py:class:`~reikna.fft.FFT` constructor.

* ADDED: an explicit ``output_dtype`` parameter for :py:func:`~reikna.cluda.functions.pow`.

* ADDED: :py:class:`~reikna.cluda.api.Array` objects for each backend expose the attribute ``thread``.


0.6.3 (18 Jun 2014)
===================

* FIXED: (@schreon) a bug preventing the usage of :py:class:`~reikna.linalg.EntrywiseNorm` with custom ``axes``.

* FIXED: (PR by @SyamGadde) removed syntax constructions incompatible with Python 2.6.

* FIXED: added Python 3.4 to the list of classifiers.


0.6.2 (20 Feb 2014)
===================

* ADDED: :py:func:`~reikna.cluda.functions.pow` function module in CLUDA.

* ADDED: a function :py:func:`~reikna.cluda.any_api` that returns some supported GPGPU API module.

* ADDED: an example of :py:class:`~reikna.algorithms.Reduce` with a custom data type.

* FIXED: a Py3 compatibility issue in :py:class:`~reikna.algorithms.Reduce` introduced in ``0.6.1``.

* FIXED: a bug due to the interaction between the implementation of :py:meth:`~reikna.algorithms.PureParallel.from_trf` and the logic of processing nested computations.

* FIXED: a bug in :py:class:`~reikna.fft.FFT` leading to undefined behavior on some OpenCL platforms.


0.6.1 (4 Feb 2014)
==================

* FIXED: :py:class:`~reikna.algorithms.Reduce` can now pick a decreased work group size if the attached transformations are too demanding.


0.6.0 (27 Dec 2013)
===================

* CHANGED: some computations were moved to sub-packages: :py:class:`~reikna.algorithms.PureParallel`, :py:class:`~reikna.algorithms.Transpose` and :py:class:`~reikna.algorithms.Reduce` to :py:mod:`reikna.algorithms`, :py:class:`~reikna.linalg.MatrixMul` and :py:class:`~reikna.linalg.EntrywiseNorm` to :py:mod:`reikna.linalg`.

* CHANGED: ``scale_const`` and ``scale_param`` were renamed to :py:func:`~reikna.transformations.mul_const` and :py:func:`~reikna.transformations.mul_param`, and the scalar parameter name of the latter was renamed from ``coeff`` to ``param``.

* ADDED: two transformations for norm of an arbitrary order: :py:func:`~reikna.transformations.norm_const` and :py:func:`~reikna.transformations.norm_param`.

* ADDED: stub transformation :py:func:`~reikna.transformations.ignore`.

* ADDED: broadcasting transformations :py:func:`~reikna.transformations.broadcast_const` and :py:func:`~reikna.transformations.broadcast_param`.

* ADDED: addition transformations :py:func:`~reikna.transformations.add_const` and :py:func:`~reikna.transformations.add_param`.

* ADDED: :py:class:`~reikna.linalg.EntrywiseNorm` computation.

* ADDED: support for multi-dimensional sub-arrays in :py:func:`~reikna.cluda.dtypes.c_constant` and :py:func:`~reikna.cluda.dtypes.flatten_dtype`.

* ADDED: helper functions :py:func:`~reikna.cluda.dtypes.extract_field` and :py:func:`~reikna.cluda.dtypes.c_path` to work in conjunction with :py:func:`~reikna.cluda.dtypes.flatten_dtype`.

* ADDED: a function module :py:func:`~reikna.cluda.functions.add`.

* FIXED: casting a coefficient in the :py:func:`~reikna.cbrng.samplers.normal_bm` template to a correct dtype.

* FIXED: :py:func:`~reikna.cluda.dtypes.cast` avoids casting if the value already has the target dtype (since ``numpy.cast`` does not work with struct dtypes, see issue #4148).

* FIXED: a error in transformation module rendering for scalar parameters with struct dtypes.

* FIXED: normalizing dtypes in several functions from :py:mod:`~reikna.cluda.dtypes` to avoid errors with ``numpy`` dtype shortcuts.


0.5.2 (17 Dec 2013)
===================

* ADDED: :py:func:`~reikna.cbrng.samplers.normal_bm` now supports complex dtypes.

* FIXED: a nested :py:class:`~reikna.algorithms.PureParallel` can now take several identical argument objects as arguments.

* FIXED: a nested computation can now take a single input/output argument (e.g. a temporary array) as separate input and output arguments.

* FIXED: a critical bug in :py:class:`~reikna.cbrng.CBRNG` that could lead to the counter array not being updated.

* FIXED: convenience constructors of :py:class:`~reikna.cbrng.CBRNG` can now properly handle ``None`` as ``samplers_kwds``.


0.5.1 (30 Nov 2013)
===================

* FIXED: a possible infinite loop in :py:meth:`~reikna.cluda.api.Thread.compile_static` local size finding algorithm.


0.5.0 (25 Nov 2013)
===================

* CHANGED: :py:class:`~reikna.core.transformation.KernelParameter` is not derived from :py:class:`~reikna.core.Type` anymore (although it still retains the corresponding attributes).

* CHANGED: :py:class:`~reikna.algorithms.Predicate` now takes a dtype'd value as ``empty``, not a string.

* CHANGED: The logic of processing struct dtypes was reworked, and ``adjust_alignment`` was removed.
  Instead, one should use :py:func:`~reikna.cluda.dtypes.align` (which does not take a ``Thread`` parameter) to get a dtype with the offsets and itemsize equal to those a compiler would set.
  On the other hand, :py:func:`~reikna.cluda.dtypes.ctype_module` attempts to set the alignments such that the field offsets are the same as in the given numpy dtype
  (unless ``ignore_alignments`` flag is set).

* ADDED: struct dtypes support in :py:func:`~reikna.cluda.dtypes.c_constant`.

* ADDED: :py:func:`~reikna.cluda.dtypes.flatten_dtype` helper function.

* ADDED: added ``transposed_a`` and ``transposed_b`` keyword parameters to :py:class:`~reikna.linalg.MatrixMul`.

* ADDED: algorithm cascading to :py:class:`~reikna.algorithms.Reduce`, leading to 3-4 times increase in performance.

* ADDED: :py:func:`~reikna.cluda.functions.polar_unit` function module in CLUDA.

* ADDED: support for arrays with 0-dimensional shape as computation and transformation arguments.

* FIXED: a bug in :py:class:`~reikna.algorithms.Reduce`, which lead to incorrect results in cases when the reduction power is exactly equal to the maximum one.

* FIXED: :py:class:`~reikna.algorithms.Transpose` now works correctly for struct dtypes.

* FIXED: :py:class:`~reikna.helpers.bounding_power_of_2` now correctly returns ``1`` instead of ``2`` being given ``1`` as an argument.

* FIXED: :py:meth:`~reikna.cluda.api.Thread.compile_static` local size finding algorithm is much less prone to failure now.


0.4.0 (10 Nov 2013)
===================

* CHANGED: ``supports_dtype()`` method moved from :py:class:`~reikna.cluda.api.Thread` to :py:class:`~reikna.cluda.api.DeviceParameters`.

* CHANGED: ``fast_math`` keyword parameter moved from :py:class:`~reikna.cluda.api.Thread` constructor to :py:meth:`~reikna.cluda.api.Thread.compile` and :py:meth:`~reikna.cluda.api.Thread.compile_static`.
  It is also ``False`` by default, instead of ``True``.
  Correspondingly, ``THREAD_FAST_MATH`` macro was renamed to :c:macro:`COMPILE_FAST_MATH`.

* CHANGED: CBRNG modules are using the dtype-to-ctype support.
  Correspondingly, the C types for keys and counters can be obtained by calling :py:func:`~reikna.cluda.dtypes.ctype_module` on :py:attr:`~reikna.cbrng.bijections.Bijection.key_dtype` and :py:attr:`~reikna.cbrng.bijections.Bijection.counter_dtype` attributes.
  The module wrappers still define their types, but their names are using a different naming convention now.

* ADDED: module generator for nested dtypes (:py:func:`~reikna.cluda.dtypes.ctype_module`) and a function to get natural field offsets for a given API/device (``adjust_alignment``).

* ADDED: ``fast_math`` keyword parameter in :py:meth:`~reikna.core.Computation.compile`.
  In other words, now ``fast_math`` can be set per computation.

* ADDED: :c:macro:`ALIGN` macro is available in CLUDA kernels.

* ADDED: support for struct types as ``Computation`` arguments (for them, the ``ctypes`` attributes contain the corresponding module obtained with :py:func:`~reikna.cluda.dtypes.ctype_module`).

* ADDED: support for non-sequential axes in :py:class:`~reikna.algorithms.Reduce`.

* FIXED: bug in the interactive ``Thread`` creation (reported by James Bergstra).

* FIXED: Py3-incompatibility in the interactive ``Thread`` creation.

* FIXED: some code paths in virtual size finding algorithm could result in a type error.

* FIXED: improved the speed of test collection by reusing ``Thread`` objects.


0.3.6 (9 Aug 2013)
==================

* ADDED: the first argument to the ``Transformation`` or ``PureParallel`` snippet is now a ``reikna.core.Indices`` object instead of a list.

* ADDED: classmethod ``PureParallel.from_trf()``, which allows one to create a pure parallel computation out of a transformation.

* FIXED: improved ``Computation.compile()`` performance for complicated computations by precreating transformation templates.


0.3.5 (6 Aug 2013)
==================

* FIXED: bug with virtual size algorithms returning floating point global and local sizes in Py2.


0.3.4 (3 Aug 2013)
==================

* CHANGED: virtual sizes algorithms were rewritten and are now more maintainable.
  In addition, virtual sizes can now handle any number of dimensions of local and global size,
  providing the device can support the corresponding total number of work items and groups.

* CHANGED: id- and size- getting kernel functions now have return types corresponding to their equivalents.
  Virtual size functions have their own independent return type.

* CHANGED: ``Thread.compile_static()`` and ``ComputationPlan.kernel_call()`` take global and local sizes in the row-major order, to correspond to the matrix indexing in load/store macros.

* FIXED: requirements for PyCUDA extras (a currently non-existent version was specified).

* FIXED: an error in gamma distribution sampler, which lead to slightly wrong shape of the resulting distribution.


0.3.3 (29 Jul 2013)
===================

* FIXED: package metadata.


0.3.2 (29 Jul 2013)
===================

* ADDED: same module object, when being called without arguments from other modules/snippets, is rendered only once and returns the same prefix each time.
  This allows one to create structure declarations that can be used by functions in several modules.

* ADDED: reworked :py:mod:`~reikna.cbrng` module and exposed kernel interface of bijections and samplers.

* CHANGED: slightly changed the algorithm that determines the order of computation parameters after a transformation is connected to it.
  Now the ordering inside a list of initial computation parameters or a list of a single transformation parameters is preserved.

* CHANGED: kernel declaration string is now passed explicitly to a kernel template as the first parameter.

* FIXED: typo in FFT performance test.

* FIXED: bug in FFT that could result in changing the contents of the input array to one of the intermediate results.

* FIXED: missing data type normalization in :py:func:`~reikna.cluda.dtypes.c_constant`.

* FIXED: Py3 incompatibility in ``cluda.cuda``.

* FIXED: updated some obsolete computation docstrings.


0.3.1 (25 Jul 2013)
===================

* FIXED: too strict array type check for nested computations that caused some tests to fail.

* FIXED: default values of scalar parameters are now processed correctly.

* FIXED: Mako threw name-not-found exceptions on some list comprehensions in FFT template.

* FIXED: some earlier-introduced errors in tests.

* INTERNAL: ``pylint`` was ran and many stylistic errors fixed.


0.3.0 (23 Jul 2013)
===================

Major core API change:

* Computations have function-like signatures with the standard ``Signature`` interface; no more separation of inputs/outputs/scalars.

* Generic transformations were ditched; all the transformations have static types now.

* Transformations can now change array shapes, and load/store from/to external arrays in output/input transformations.

* No flat array access in kernels; all access goes through indices.
  This opens the road for correct and automatic stride support (not fully implemented yet).

* Computations and accompanying classes are stateless, and their creation is more straightforward.

Other stuff:

* Bumped Python requirements to >=2.6 or >=3.2, and added a dependency on ``funcsig``.

* ADDED: more tests for cluda.functions.

* ADDED: module/snippet attributes discovery protocol for custom objects.

* ADDED: strides support to array allocation functions in CLUDA.

* ADDED: modules can now take positional arguments on instantiation, same as snippets.

* CHANGED: ``Elementwise`` becomes :py:class:`~reikna.algorithms.PureParallel` (as it is not always elementwise).

* FIXED: incorrect behavior of functions.norm() for non-complex arguments.

* FIXED: undefined variable in functions.exp() template (reported by Thibault North).

* FIXED: inconsistent block/grid shapes in static kernels


0.2.4 (11 May 2013)
===================

* ADDED: ability to introduce new scalar arguments for nested computations
  (the API is quite ugly at the moment).

* FIXED: handling prefixes properly when connecting transformations to nested computations.

* FIXED: bug in dependency inference algorithm which caused it to ignore allocations in nested computations.


0.2.3 (25 Apr 2013)
===================

* ADDED: explicit :py:meth:`~reikna.cluda.api.Thread.release` (primarily for certain rare CUDA use cases).

* CHANGED: CLUDA API discovery interface (see the documentation).

* CHANGED: The part of CLUDA API that is supposed to be used by other layers was moved to the ``__init__.py``.

* CHANGED: CLUDA ``Context`` was renamed to ``Thread``, to avoid confusion with ``PyCUDA``/``PyOpenCL`` contexts.

* CHANGED: signature of :py:meth:`~reikna.cluda.api.Thread.create`; it can filter devices now, and supports interactive mode.

* CHANGED: :py:class:`~reikna.cluda.Module` with ``snippet=True`` is now :py:class:`~reikna.cluda.Snippet`

* FIXED: added ``transformation.mako`` and ``cbrng_ref.py`` to the distribution package.

* FIXED: incorrect parameter generation in ``test/cluda/cluda_vsizes/ids``.

* FIXED: skipping testcases with incompatible parameters in ``test/cluda/cluda_vsizes/ids`` and ``sizes``.

* FIXED: setting the correct length of :py:attr:`~reikna.cluda.api.DeviceParameters.max_num_groups` in case of CUDA and a device with CC < 2.

* FIXED: typo in ``cluda.api_discovery``.


0.2.2 (20 Apr 2013)
===================

* ADDED: ability to use custom argument names in transformations.

* ADDED: multi-argument :py:func:`~reikna.cluda.functions.mul`.

* ADDED: counter-based random number generator :py:class:`~reikna.cbrng.CBRNG`.

* ADDED: ``reikna.elementwise.Elementwise`` now supports argument dependencies.

* ADDED: Module support in CLUDA; see :ref:`tutorial-modules` for details.

* ADDED: :py:func:`~reikna.helpers.template_def`.

* CHANGED: ``reikna.cluda.kernel.render_template_source`` is the main renderer now.

* CHANGED: ``FuncCollector`` class was removed; functions are now used as common modules.

* CHANGED: all templates created with :py:func:`~reikna.helpers.template_for` are now rendered with ``from __future__ import division``.

* CHANGED: signature of ``OperationRecorder.add_kernel`` takes a renderable instead of a full template.

* CHANGED: :py:meth:`~reikna.cluda.api.Thread.compile_static` now takes a template instead of a source.

* CHANGED: ``reikna.elementwise.Elementwise`` now uses modules.

* FIXED: potential problem with local size finidng in static kernels (first approximation for the maximum workgroup size was not that good)

* FIXED: some OpenCL compilation warnings caused by an incorrect version querying macro.

* FIXED: bug with incorrect processing of scalar global size in static kernels.

* FIXED: bug in variance estimates in CBRNG tests.

* FIXED: error in the temporary varaiable type in :py:func:`reikna.cluda.functions.polar` and :py:func:`reikna.cluda.functions.exp`.


0.2.1 (8 Mar 2013)
==================

* FIXED: function names for kernel ``polar()``, ``exp()`` and ``conj()``.

* FIXED: added forgotten kernel ``norm()`` handler.

* FIXED: bug in ``Py.Test`` testcase execution hook which caused every test to run twice.

* FIXED: bug in nested computation processing for computation with more than one kernel.

* FIXED: added dependencies between :py:class:`~reikna.linalg.MatrixMul` kernel arguments.

* FIXED: taking into account dependencies between input and output arrays as well as the ones
  between internal allocations --- necessary for nested computations.

* ADDED: discrete harmonic transform :py:class:`~reikna.dht.DHT`
  (calculated using Gauss-Hermite quadrature).


0.2.0 (3 Mar 2013)
==================

* Added FFT computation (slightly optimized PyFFT version + Bluestein's algorithm for non-power-of-2 FFT sizes)

* Added Python 3 compatibility

* Added Thread-global automatic memory packing

* Added polar(), conj() and exp() functions to kernel toolbox

* Changed name because of the clash with `another Tigger <http://www.astron.nl/meqwiki/Tigger>`_.


0.1.0 (12 Sep 2012)
===================

* Lots of changes in the API

* Added elementwise, reduction and transposition computations

* Extended API reference and added topical guides


0.0.1 (22 Jul 2012)
===================

* Created basic core for computations and transformations

* Added matrix multiplication computation

* Created basic documentation
