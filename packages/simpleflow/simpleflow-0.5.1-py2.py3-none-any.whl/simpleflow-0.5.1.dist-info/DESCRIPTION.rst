Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
Description: ===============================
        simpleflow
        ===============================
        
        .. image:: https://badge.fury.io/py/simpleflow.png
            :target: http://badge.fury.io/py/simpleflow
        
        .. image:: https://travis-ci.org/botify-labs/simpleflow.png?branch=master
                :target: https://travis-ci.org/botify-labs/simpleflow
        
        .. image:: https://pypip.in/d/simpleflow/badge.png
                :target: https://crate.io/packages/simpleflow?version=latest
        
        
        Simple Flow is a Python library that provides abstractions to write programs in
        the `distributed dataflow paradigm
        <https://en.wikipedia.org/wiki/Distributed_data_flow>`_. It relies on futures
        to describe the dependencies between tasks. It coordinates the execution of
        distributed tasks with Amazon `SWF <https://aws.amazon.com/swf/>`_.
        
        A ``Future`` object models the asynchronous execution of a computation that may
        end.
        
        It tries to mimics the interface of the Python `concurrent.futures
        <http://docs.python.org/3/library/concurrent.futures>`_ library.
        
        Features
        --------
        
        - Provides a ``Future`` abstraction to define dependencies between tasks.
        - Define asynchronous tasks from callables.
        - Handle workflows with Amazon SWF.
        - Implement replay behavior like the Amazon Flow framework.
        - Handle retry of tasks that failed.
        - Automatically register decorated tasks.
        - Handle the completion of a decision with more than 100 tasks.
        - Provides a local executor to check a workflow without Amazon SWF (see
          ``simpleflow --local`` command).
        
        Quickstart
        ----------
        
        Let's take a simple example that computes the result of ``(x + 1) * 2``.
        
        We need to declare the functions as activities to make them available:
        
        .. code::
        
            from simpleflow import activity
        
            @activity.with_attributes(task_list='quickstart')
            def increment(x):
                return x + 1
        
            @activity.with_attributes(task_list='quickstart')
            def double(x):
                return x * 2
        
        
        And then define the workflow itself in a ``example.py`` file:
        
        .. code::
        
            from simpleflow import Workflow
        
            class SimpleComputation(Workflow):
                def run(self, x):
                    y = self.submit(increment, x)
                    z = self.submit(double, y)
                    return z.result
        
        Now check that the workflow works locally: ::
        
            $ simpleflow --local -w example.SimpleComputation -i example/input.json
        
        The file ``example/input.json`` contains the input passed to the workflow. It
        should have the format:
        
        .. code::
        
            {"args": [1],
             "kwargs": {}
            }
        
        which is equivalent to:
        
        .. code::
        
            {"kwargs": {"x": 1}}
        
        Documentation
        -------------
        
        Full documentation is available at https://simpleflow.readthedocs.org/.
        
        Requirements
        ------------
        
        - Python >= 2.6 or >= 3.3
        
        License
        -------
        
        MIT licensed. See the bundled `LICENSE <https://github.com/botify-labs/simpleflow/blob/master/LICENSE>`_ file for more details.
        
        
        Changelog
        ---------
        
        0.1.0 (2014-02-19)
        ++++++++++++++++++
        
        * First release.
Keywords: simpleflow
Platform: UNKNOWN
Classifier: Development Status :: 2 - Pre-Alpha
Classifier: Intended Audience :: Developers
Classifier: License :: OSI Approved :: MIT License
Classifier: Natural Language :: English
Classifier: Programming Language :: Python :: 2
Classifier: Programming Language :: Python :: 2.6
Classifier: Programming Language :: Python :: 2.7
Classifier: Programming Language :: Python :: 3
Classifier: Programming Language :: Python :: 3.3
