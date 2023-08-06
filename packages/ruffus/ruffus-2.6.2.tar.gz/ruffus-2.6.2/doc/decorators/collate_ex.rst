.. include:: ../global.inc
.. _decorators.collate_ex:
.. index::
    pair: @collate (Advanced Usage); Syntax
    pair: @collate, inputs(...); Syntax
    pair: @collate, add_inputs(...); Syntax

.. role:: raw-html(raw)
   :format: html

:raw-html:`<style> .red {color:red} </style>`

.. role:: red


.. seealso::

    * :ref:`@collate <new_manual.collate>` in the **Ruffus** Manual
    * :ref:`Use of add_inputs(...) | inputs(...) <new_manual.inputs>` in the **Ruffus** Manual
    * :ref:`Decorators <decorators>` for more decorators

.. |input| replace:: `input`
.. _input: `decorators.collate_ex.input`_
.. |extras| replace:: `extras`
.. _extras: `decorators.collate_ex.extras`_
.. |output| replace:: `output`
.. _output: `decorators.collate_ex.output`_
.. |filter| replace:: `filter`
.. _filter: `decorators.collate_ex.filter`_
.. |matching_regex| replace:: `matching_regex`
.. _matching_regex: `decorators.collate_ex.matching_regex`_
.. |matching_formatter| replace:: `matching_formatter`
.. _matching_formatter: `decorators.collate_ex.matching_formatter`_
.. |replace_inputs| replace:: `replace_inputs`
.. _replace_inputs: `decorators.collate_ex.replace_inputs`_
.. |add_inputs| replace:: `add_inputs`
.. _add_inputs: `decorators.collate_ex.add_inputs`_


################################################################################################################################################
@collate( |input|_, |filter|_, |replace_inputs|_ | |add_inputs|_, |output|_, [|extras|_,...] )
################################################################################################################################################
    **Purpose:**
        Use |filter|_ to identify common sets of |input|_\s which are to be grouped or collated together:

        Each set of |input|_\ s which generate identical |output|_ and |extras|_ using the
        :ref:`formatter<decorators.formatter>` or :ref:`regex<decorators.regex>` (regular expression)
        filters are collated into one job.

        This variant of ``@collate`` allows additional inputs or dependencies to be added
        dynamically to the task, with optional string substitution.

        :ref:`add_inputs<decorators.add_inputs>` nests the the original input parameters in a list before adding additional dependencies.

        :ref:`inputs<decorators.inputs>` replaces the original input parameters wholescale.

        This is a **many to fewer** operation.

        Only out of date jobs (comparing input and output files) will be re-run.

    **Example of** :ref:`add_inputs<decorators.add_inputs>`

        ``regex(r".*(\..+)"), "\1.summary"`` creates a separate summary file for each suffix.
        But we also add date of birth data for each species::

            animal_files = "tuna.fish", "shark.fish", "dog.mammals", "cat.mammals"
            # summarise by file suffix:
            @collate(animal_files, regex(r".+\.(.+)$"),  add_inputs(r"\1.date_of_birth"), r'\1.summary')
            def summarize(infiles, summary_file):
                pass

        This results in the following equivalent function calls::

            summarize([ ["shark.fish",  "fish.date_of_birth"   ],
                        ["tuna.fish",   "fish.date_of_birth"   ] ], "fish.summary")
            summarize([ ["cat.mammals", "mammals.date_of_birth"],
                        ["dog.mammals", "mammals.date_of_birth"] ], "mammals.summary")

    **Example of** :ref:`add_inputs<decorators.inputs>`

        using ``inputs(...)`` will summarise only the dates of births for each species group::

            animal_files = "tuna.fish", "shark.fish", "dog.mammals", "cat.mammals"
            # summarise by file suffix:
            @collate(animal_files, regex(r".+\.(.+)$"),  inputs(r"\1.date_of_birth"), r'\1.summary')
            def summarize(infiles, summary_file):
                pass

        This results in the following equivalent function calls::

            summarize(["fish.date_of_birth"   ], "fish.summary")
            summarize(["mammals.date_of_birth"], "mammals.summary")

    **Parameters:**


.. _decorators.collate_ex.input:

    * **input** = *tasks_or_file_names*
       can be a:

       #.  Task / list of tasks.
            File names are taken from the output of the specified task(s)
       #.  (Nested) list of file name strings (as in the example above).
            File names containing ``*[]?`` will be expanded as a |glob|_.
             E.g.:``"a.*" => "a.1", "a.2"``


.. _decorators.collate_ex.filter:

.. _decorators.collate_ex.matching_regex:

    * **filter** = *matching_regex*
       is a python regular expression string, which must be wrapped in
       a :ref:`regex<decorators.regex>` indicator object
       See python `regular expression (re) <http://docs.python.org/library/re.html>`_
       documentation for details of regular expression syntax

.. _decorators.collate_ex.matching_formatter:

    * **filter** = *matching_formatter*
       a :ref:`formatter<decorators.formatter>` indicator object containing optionally
       a  python `regular expression (re) <http://docs.python.org/library/re.html>`_.

.. _decorators.collate_ex.add_inputs:

.. _decorators.collate_ex.replace_inputs:

    * **add_inputs** = *add_inputs*\ (...) or **replace_inputs** = *inputs*\ (...)
       Specifies the resulting |input|_\ (s) to each job.

       Positional parameters must be disambiguated by wrapping the values in :ref:`inputs(...)<decorators.inputs>` or an :ref:`add_inputs(...)<decorators.add_inputs>`.

       Named parameters can be passed the values directly.

       Takes:

       #.  Task / list of tasks.
            File names are taken from the output of the specified task(s)
       #.  (Nested) list of file name strings.
            Strings will be subject to substitution.
            File names containing ``*[]?`` will be expanded as a |glob|_.
            E.g. ``"a.*" => "a.1", "a.2"``

.. _decorators.collate_ex.output:

    * **output** = *output*
        Specifies the resulting output file name(s).

.. _decorators.collate_ex.extras:

    * **extras** = *extras*
        Any extra parameters are passed verbatim to the task function

        If you are using named parameters, these can be passed as a list, i.e. ``extras= [...]``


See :ref:`@collate <decorators.collate>` for more straightforward ways to use collate.
