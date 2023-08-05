'''
Copyright 2013 Cosnita Radu Viorel

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

.. codeauthor:: Radu Viorel Cosnita <radu.cosnita@gmail.com>
.. py:module:: fantastico.oauth2.models.tests.test_scopes
'''
from fantastico.oauth2.models.scopes import Scope
from fantastico.tests.base_case import FantasticoUnitTestsCase

class ScopeTests(FantasticoUnitTestsCase):
    '''This class provides the tests suite for Scope entity.'''

    def test_init_ok(self):
        '''This test case ensures scope entity can be instantiated.'''

        scope_name = "simple name"
        scope_desc = "simple description"

        scope = Scope(scope_name, scope_desc)

        self.assertIsNone(scope.scope_id)
        self.assertEqual(scope_name, scope.name)
        self.assertEqual(scope_desc, scope.description)

    def test_init_noargs(self):
        '''This test case ensures scope entity can be instantiated without arguments.'''

        scope = Scope()

        self.assertIsNone(scope.scope_id)
        self.assertIsNone(scope.name)
        self.assertIsNone(scope.description)
