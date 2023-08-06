from functools import wraps


def validate(schema):
	def decorator(fn):
		@wraps(fn)
		def wrapper(*args, **kwargs):
			options = schema.validate(kwargs)
			return fn(options)
		return wrapper
	return decorator