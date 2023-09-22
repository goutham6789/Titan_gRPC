from decorators.Decorator import decorator


def precheck(**expected_kwargs):

	@decorator
	def wrapper(method, *args, **kwargs):

		if not expected_kwargs:
			raise TypeError('No arguments given to precheck!')

		checked_values = {}
		for i in range(0, len(args)):
			try:
				checked_values[method.func_code.co_varnames[i]] = args[i]
			except IndexError:
				pass

		for varname, value in expected_kwargs.iteritems():
			if varname not in checked_values.keys():
				raise NameError('Non-existent argument to precheck: %s' % varname)

			expected_types = []
			if isinstance(value, tuple) and 0 < len(value):
				for tuple_value in value:
					if tuple_value is not None:
						expected_types.append(tuple_value)
					else:
						expected_types.append(type(None))
			elif isinstance(value, list) and 0 < len(value):
				if checked_values[varname] not in value:
					raise ValueError("Prechecked argument '{}' should be in {}".format(varname, value))
			else:
				expected_types.append(value)

			if expected_types and not any(isinstance(checked_values[varname], expected_type) for expected_type in expected_types):
				raise TypeError("Prechecked argument '{}' should be {} but was {}".format(varname, expected_types, type(checked_values[varname])))

		return method(*args, **kwargs)
	return wrapper
