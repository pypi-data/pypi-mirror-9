******
Mockie
******

Helper classes for easier mocking and patching tests.

-----

|pypi| |unix_build|

-----

======
Sample
======

.. code-block:: python

   from mockie import TestCase
   from my import module

   class MyTest(TestCase):

       def setUp(self):
           self.mock_shutil = self.patch("my.module.shutil")

       def test_my_function_with_side_effects(self):
           module.function()
           self.mock_shutil.rmtree.assert_called_once_with("my_file.txt")


===
API
===

--------
TestCase
--------

+ ``self.Mock``
+ ``self.MagicMock``
+ ``self.patch``
+ ``self.patch_object``
+ ``self.patch_multiple``
+ ``self.patch_dict``
+ ``self.mock_open``
+ ``self.assertCalled``
+ ``self.assertCalledOnceWith``
+ ``self.assertAnyCall``
+ ``self.assertIsMocked``
+ ``self.assertIsMock``
+ ``self.assertIsMagicMock``


=============
License (MIT)
=============

The MIT License (MIT)

Copyright (c) 2015 `marcwebbie <https://github.com/marcwebbie>`_.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


.. |pypi| image:: https://img.shields.io/pypi/v/mockie.svg?style=flat-square&label=latest%20version
    :target: https://pypi.python.org/pypi/mockie
    :alt: Latest version released on PyPi

.. |coverage| image:: https://img.shields.io/coveralls/marcwebbie/mockie/master.svg?style=flat-square
    :target: https://coveralls.io/r/marcwebbie/mockie?branch=master
    :alt: Test coverage

.. |unix_build| image:: https://img.shields.io/travis/marcwebbie/mockie/master.svg?style=flat-square&label=unix%20build
    :target: http://travis-ci.org/marcwebbie/mockie
    :alt: Build status of the master branch on Mac/Linux

.. role:: python(code)
   :language: python
