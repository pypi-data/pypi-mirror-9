from . import fields

try:
  basestring
except NameError:
  basestring = str

class JSONSchemaSerializer(object):
	
	fallbacks = (
		fields.Text, fields.Integer, fields.Float, fields.DateTime,
		fields.Boolean, fields.Enum, fields.ListOf, fields.OneOf, 
		fields.Compound, fields.Anything
	)
		
	def serialize(self, schema, title=None):
		props = {}
		required_props = []
		for k,v in schema.fields.items():
			props[k] = self.get_property(v)
			if v.required:
				required_props.append(k)
		definition =  {
			'properties': props
		}
		if required_props:
			definition['required'] = required_props
		if title:
			definition['title'] = title
		return definition
			
			
	def get_property(self, field):
		prop = {}
		prop['default'] = field.default
		prop['format'] = field.__class__.__name__
		if field.label:
			prop['title'] = field.label
		if field.description:
			prop['description'] = field.description
		type_name = field.__class__.__name__
		method_name = 'handle_%s' % type_name
		if not hasattr(self, method_name):
			method_name = None
			for cls in self.fallbacks:
				if isinstance(field, cls):
					method_name = 'handle_%s' % cls.__name__
					break
			if not method_name:
				raise ValueError("No handler for %s" % type_name)
		getattr(self, method_name)(field, prop)
		return prop
		
		
	def handle_Text(self, field, prop):
		prop['type'] = 'string'
		if field.maxlength:
			prop['maxLength'] = field.maxlength
		if field.minlength:
			prop['minLength'] = field.minlength
		if field.regex:
			prop['pattern'] = field.regex.pattern
		
		
	def handle_Integer(self, field, prop):
		prop['type'] = 'integer'
		if field.min:
			prop['minimum'] = field.min
		if field.max:
			prop['maximum'] = field.max
		
		
	def handle_Float(self, field, prop):
		self.handle_Integer(field, prop)
		prop['type'] = 'number'
		
		
	def handle_DateTime(self, field, prop):
		prop['type'] = 'string'
		prop['format'] = 'date-time'
		
		
	def handle_Email(self, field, prop):
		self.handle_Text(field, prop)
		prop['format'] = 'email'
		del prop['pattern']
		
		
	def handle_URL(self, field, prop):
		self.handle_Text(field, prop)
		prop['format'] = 'uri'
		del prop['pattern']
		
		
	def handle_Boolean(self, field, prop):
		prop['type'] = 'boolean'
		
		
	def handle_Enum(self, field, prop):
		prop['enum'] = field.values
		
		
	def handle_ListOf(self, field, prop):
		prop['type'] = 'array'
		prop['items'] = self.get_property(field.field)
		
		
	def handle_OneOf(self, field, prop):
		prop['anyOf'] = list(map(self.get_property, field.fields))
		
		
	def handle_Link(self, field, prop):
		self.handle_Text(field, prop)
		prop['format'] = 'Link'
		prop['schema'] = '#/definitions/%s' % field.schema.__name__
		
		
	def handle_Compound(self, field, prop):
		prop['type'] = 'object'
		properties = {}
		required = []
		for k, v in field.fields.items():
			properties[k] = self.get_property(v)
			if v.required:
				required.append(k)
		prop['properties'] = properties
		if len(required) > 0:
			prop['required'] = required
			
			
	def handle_Anything(self, field, prop):
		prop['anyOf'] = [
			{'type':'array'},
			{'type':'boolean'},
			{'type':'null'},
			{'type':'object'},
			{'type':'string'},
			{'type':'number'}
		]
			
			
	def handle_BoundingBox(self, field, prop):
		prop['type'] = 'array'
		prop['items'] = {
			'type': 'float',
			'minimum': -180.0,
			'maximum': 180.0,
			'maxItems': 4,
			'minItems': 4
		}
		
		
	def handle_LatLng(self, field, prop):
		prop['type'] = 'array'
		prop['items'] = {
			'type': 'float',
			'minimum': -180.0,
			'maximum': 180.0,
			'maxItems': 2,
			'minItems': 2
		}
		
		
	def handle_TypeOf(self, field, prop):
		type = field.types[0]
		if type == dict:
			prop['type'] = 'object'
		elif type == list:
			prop['type'] = 'array'
		elif len(field.types) == 2 and int in field.types and float in field.types:
			prop['type'] = 'number'
		elif type == int:
			prop['type'] = 'integer'
		elif type == float:
			prop['type'] = 'float'
		elif type == basestring:
			prop['type'] = 'string'


def to_jsonschema(schema, title=None, serializer=JSONSchemaSerializer):
	return serializer().serialize(schema, title=title)
	
	
def from_jsonschema(jsonschema):
	pass
	