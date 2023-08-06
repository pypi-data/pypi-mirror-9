import unittest
from mock import Mock
import simpleobserver
from valipede import *



class TestSchema(unittest.TestCase):

    def test_has_fields(self):
        field = Text()
        foo = Schema(bar=field)
        self.assertEquals(foo.fields, { 'bar': field })
        
        
    def test_has_mixins(self):
        foo = Schema(bar=Text())
        baz = Schema(foo)
        self.assertEquals(baz.fields, foo.fields)
        self.assertEquals(baz.mixins, (foo,))


    def test_validate_is_called(self):
        foo = Schema()
        foo.validator.validate = Mock(return_value="validated fields")
        result = foo.validate({'things':'stuff'})
        foo.validator.validate.assert_called_once_with({'things':'stuff'})
        self.assertEquals(result, "validated fields")


    def test_has_subjects(self):
        foo = Schema()
        self.assertIsInstance(foo.before, simpleobserver.Subject)
        self.assertIsInstance(foo.after, simpleobserver.Subject)


    def test_observers_called(self):
        foo = Schema()
        foo.validator.validate = Mock(return_value="validated fields")
        before = Mock()
        after = Mock()
        foo.before('validate', before)
        foo.after('validate', after)
        
        foo.validate({})
        
        before.assert_called_once_with({})
        after.assert_called_once_with("validated fields")
        
        
        
if __name__ == "__main__":
    unittest.main()
