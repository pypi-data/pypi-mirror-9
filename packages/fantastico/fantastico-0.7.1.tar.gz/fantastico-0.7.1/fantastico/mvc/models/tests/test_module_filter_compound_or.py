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
.. py:module:fantastico.mvc.models.tests.test_model_filter_compound
'''
from fantastico.exceptions import FantasticoNotSupportedError, FantasticoError
from fantastico.mvc.models.model_filter import ModelFilter
from fantastico.mvc.models.model_filter_compound import ModelFilterAnd, \
    ModelFilterOr
from fantastico.tests.base_case import FantasticoUnitTestsCase
from mock import Mock
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer

class ModelFilterOrTests(FantasticoUnitTestsCase):
    '''This class provides test suite for compound *and* model filter.'''
    
    def init(self):
        self._model = Mock()
        self._model.id = Column("id", Integer)
    
    def test_modelfilteror_noargs(self):
        '''This test case ensures compound **or** filter can not be built without arguments.'''
        
        with self.assertRaises(FantasticoNotSupportedError):
            ModelFilterOr()
            
    def test_modelfilteror_notenoughargs(self):
        '''This test case ensures compound **or** filter can not be built with a single argument.'''
        
        with self.assertRaises(FantasticoNotSupportedError):
            ModelFilterOr(ModelFilter(self._model.id, 1, ModelFilter.EQ))

    def test_modelfilteror_wrongargtype(self):
        '''This test case ensures compound **or** filter works only with ModelFilter arguments.'''
        
        with self.assertRaises(FantasticoNotSupportedError):
            ModelFilterAnd(Mock(), Mock())

    def test_modelfilteror_ok(self):
        '''This test case ensures compound **or** filter correctly transform the filter into sql alchemy and_ statement.'''
        
        self._or_invoked = False
        
        model_filter = ModelFilterOr(ModelFilter(self._model.id, 1, ModelFilter.EQ),
                                      ModelFilter(self._model.id, 1, ModelFilter.EQ),
                                      ModelFilter(self._model.id, 1, ModelFilter.EQ))
        
        query = Mock()
        
        def filter_fn(expr):
            self._or_invoked = True
            
            return Mock()
            
        self._model.id.table = Mock()
        query._primary_entity = query
        query.selectable = self._model.id.table
        
        query.filter = filter_fn
        
        query_new = model_filter.build(query)
        
        self.assertTrue(self._or_invoked)
        self.assertIsInstance(query_new, Mock)

    def test_modelfiteror_unhandled_exception(self):
        '''This test case ensures unhandled exceptions raised from ModelFilter are gracefully handled by ModelFilterOr build.'''
        
        model_filter = ModelFilter(self._model.id, 1, ModelFilter.EQ)
        model_filter.get_expression = Mock(side_effect=Exception("Unhandled exception"))
        
        model_filter_or = ModelFilterOr(model_filter, model_filter, model_filter)
        
        with self.assertRaises(FantasticoError):
            model_filter_or.build(Mock())