.. Copyright 2013 Oliver Palmer
..
.. Licensed under the Apache License, Version 2.0 (the "License");
.. you may not use this file except in compliance with the License.
.. You may obtain a copy of the License at
..
..   http://www.apache.org/licenses/LICENSE-2.0
..
.. Unless required by applicable law or agreed to in writing, software
.. distributed under the License is distributed on an "AS IS" BASIS,
.. WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
.. See the License for the specific language governing permissions and
.. limitations under the License.

PyFarm Core
===========

This sub-library contains core modules, classes, and data types which are
used by other parts of the project.  Overall this library contains:
    * core exceptions and warnings
    * system information submodule
    * file operations wrappers and classes
    * base command line wrapper
    * other general utilities


Installation Note
-----------------
The installation of this module does not ensure all its dependencies are met.
As an example sqlalchemy is required for part of the ``core.config`` module
however that specific module is only required for the admin interface and
master.