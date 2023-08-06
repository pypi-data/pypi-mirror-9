import unittest
import re
from mock import Mock
from valipede import *
from valipede.jsonschema import to_jsonschema


try:
  basestring
except NameError:
  basestring = str
  

class TestSchemaSerializer(unittest.TestCase):
	
	maxDiff = None
	
		
	def test_base_properties(self):
		schema = to_jsonschema(Schema(), title="foo")
		self.assertEquals(schema.get('properties'), {})
		self.assertEquals(schema.get('title'), 'foo')
		
		
	def test_required(self):
		schema = to_jsonschema(Schema(
			stuff = Integer(required=True),
			things = ListOf(Text(), required=True),
			metasyntacticvariable = Float()
		))
		self.assertEquals(set(schema['required']), {'things', 'stuff'})
		
		
	def test_label(self):
		schema = to_jsonschema(Schema(
			stuff = Integer(label="Blah blah blah")
		))
		self.assertEquals(schema['properties']['stuff']['title'], 'Blah blah blah')
		
		
	def test_description(self):
		schema = to_jsonschema(Schema(
			stuff = Integer(description="Blah blah blah")
		))
		self.assertEquals(schema['properties']['stuff']['description'], 'Blah blah blah')
		
		
	def test_default(self):
		schema = to_jsonschema(Schema(
			stuff = Integer(default="whale")
		))
		self.assertEquals(schema['properties']['stuff']['default'], 'whale')
		
		
	def test_fallback(self):
		class Thingy(Text):
			pass
			
		schema = to_jsonschema(Schema(
			stuff = Thingy()
		))
		self.assertEquals(
			schema['properties']['stuff'], 
			{
				'default': None,
				'format': 'Thingy',
				'type': 'string'
			}
		)
		
		
	def test_fallback_fail(self):
		class Thingy(Field):
			pass
		
		with self.assertRaises(Exception):
			to_jsonschema(Schema(
				stuff = Thingy()
			))
			
			
	def test_Compound(self):
		schema = to_jsonschema(Schema(
			stuff = Compound(foo=Text(), bar=Text(required=True))
		))
		self.assertEquals(
			schema['properties']['stuff'],
			{
				'default': None,
				'format': 'Compound',
				'type': 'object',
				'required': ['bar'],
				'properties': {
					'foo': {
						'default': None,
						'format': 'Text',
						'type': 'string'
					},
					'bar': {
						'default': None,
						'format': 'Text',
						'type': 'string'
					}
				}
			}
		)
	
	
	def test_Text(self):
		schema = to_jsonschema(Schema(
			stuff = Text(),
			things = Text(minlength=100, maxlength=5000, regex=re.compile('^b'))
		))
		self.assertEquals(
			schema['properties']['stuff'], 
			{
				'default': None, 
				'format': 'Text', 
				'type': 'string'
			}
		)
		self.assertEquals(
			schema['properties']['things'], 
			{
				'default': None, 
				'format': 'Text', 
				'type': 'string',
				'minLength': 100,
				'maxLength': 5000,
				'pattern': '^b'
			}
		)
		
		
	def test_HTML(self):
		schema = to_jsonschema(Schema(
			stuff = HTML()
		))
		self.assertEquals(
			schema['properties']['stuff'], 
			{
				'default': None, 
				'format': 'HTML', 
				'type': 'string'
			}
		)
		
		
	def test_Email(self):
		schema = to_jsonschema(Schema(
			stuff = Email()
		))
		self.assertEquals(
			schema['properties']['stuff'], 
			{
				'default': None, 
				'format': 'email', 
				'type': 'string'
			}
		)
		
	def test_DateTime(self):
		schema = to_jsonschema(Schema(
			stuff = DateTime()
		))
		self.assertEquals(
			schema['properties']['stuff'], 
			{
				'default': None, 
				'format': 'date-time', 
				'type': 'string'
			}
		)
		
		
	def test_Boolean(self):
		schema = to_jsonschema(Schema(
			stuff = Boolean()
		))
		self.assertEquals(
			schema['properties']['stuff'], 
			{
				'default': None, 
				'format': 'Boolean', 
				'type': 'boolean'
			}
		)
		
		
	def test_Float(self):
		schema = to_jsonschema(Schema(
			stuff = Float(),
			things = Float(min=5.331, max=7.2)
		))
		self.assertEquals(
			schema['properties']['stuff'], 
			{
				'default': None, 
				'format': 'Float', 
				'type': 'number'
			}
		)
		self.assertEquals(
			schema['properties']['things'], 
			{
				'default': None, 
				'format': 'Float', 
				'type': 'number',
				'maximum': 7.2,
				'minimum': 5.331
			}
		)
		
		
	def test_Integer(self):
		schema = to_jsonschema(Schema(
			stuff = Integer(),
			things = Integer(min=5, max=7)
		))
		self.assertEquals(
			schema['properties']['stuff'], 
			{
				'default': None, 
				'format': 'Integer', 
				'type': 'integer'
			}
		)
		self.assertEquals(
			schema['properties']['things'], 
			{
				'default': None, 
				'format': 'Integer', 
				'type': 'integer',
				'maximum': 7,
				'minimum': 5
			}
		)
		
		
	def test_BoundingBox(self):
		schema = to_jsonschema(Schema(
			stuff = BoundingBox()
		))
		self.assertEquals(
			schema['properties']['stuff'], 
			{
				'default': None, 
				'format': 'BoundingBox', 
				'type': 'array',
				'items': {
					'maxItems': 4,
					'minItems': 4,
					'minimum': -180.0,
					'maximum': 180.0,
					'type': 'float'
				}
			}
		)
		
		
	def test_LatLng(self):
		schema = to_jsonschema(Schema(
			stuff = LatLng()
		))
		self.assertEquals(
			schema['properties']['stuff'], 
			{
				'default': None, 
				'format': 'LatLng', 
				'type': 'array',
				'items': {
					'maxItems': 2,
					'minItems': 2,
					'minimum': -180.0,
					'maximum': 180.0,
					'type': 'float'
				}
			}
		)
		
		
	def test_Enum(self):
		schema = to_jsonschema(Schema(
			stuff = Enum('a', 'b', 'c')
		))
		self.assertEquals(
			schema['properties']['stuff'], 
			{
				'default': None, 
				'format': 'Enum', 
				'enum': ('a', 'b', 'c')
			}
		)
		
		
	def test_URL(self):
		schema = to_jsonschema(Schema(
			stuff = URL()
		))
		self.assertEquals(
			schema['properties']['stuff'], 
			{
				'default': None, 
				'format': 'uri', 
				'type': 'string'
			}
		)
		
		
	def test_OneOf(self):
		schema = to_jsonschema(Schema(
			stuff = OneOf(Integer(), Float())
		))
		self.assertEquals(
			schema['properties']['stuff'], 
			{
				'default': None, 
				'format': 'OneOf', 
				'anyOf': [
					{
						'default': None,
						'format': 'Integer',
						'type': 'integer'
					},
					{
						'default': None,
						'format': 'Float',
						'type': 'number'
					}
				]
			}
		)
		
		
	def test_ListOf(self):
		schema = to_jsonschema(Schema(
			stuff = ListOf(Text())
		))
		self.assertEquals(
			schema['properties']['stuff'], 
			{
				'default': [], 
				'format': 'ListOf', 
				'type': 'array',
				'items': {
					'default': None,
					'format': 'Text',
					'type': 'string'
				}
			}
		)
		
		
	def test_TypeOf(self):
		schema = to_jsonschema(Schema(
			foo = TypeOf(dict),
			bar = TypeOf(list),
			baz = TypeOf(int),
			qux = TypeOf(float),
			fred = TypeOf(basestring),
			wibble = TypeOf(int, float),
			wobble = TypeOf(TypeOf)
		))
		self.assertEquals(
			schema['properties'], 
			{
				'foo': {
					'default': None,
					'format': 'TypeOf',
					'type': 'object'
				},
				'bar': {
					'default': None,
					'format': 'TypeOf',
					'type': 'array'
				},
				'baz': {
					'default': None,
					'format': 'TypeOf',
					'type': 'integer'
				},
				'qux': {
					'default': None,
					'format': 'TypeOf',
					'type': 'float'
				},
				'fred': {
					'default': None,
					'format': 'TypeOf',
					'type': 'string'
				},
				'wibble': {
					'default': None,
					'format': 'TypeOf',
					'type': 'number'
				},
				'wobble': {
					'default': None,
					'format': 'TypeOf'
				}
			}
		)
		
	def test_Anything(self):
		schema = to_jsonschema(Schema(
			stuff = Anything()
		))
		self.assertEquals(
			schema['properties']['stuff'], 
			{
				'default': None,
				'format': 'Anything',
				'anyOf': [
					{'type':'array'},
					{'type':'boolean'},
					{'type':'null'},
					{'type':'object'},
					{'type':'string'},
					{'type':'number'}
				]
			}
		)
		