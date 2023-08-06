from functools import wraps


def validate(schema):
	def decorator(fn):
		@wraps(fn)
		def wrapper(*args, **kwargs):
			options = schema.validate(kwargs)
			args = list(args) + [options]
			return fn(*args)
		return wrapper
	return decorator