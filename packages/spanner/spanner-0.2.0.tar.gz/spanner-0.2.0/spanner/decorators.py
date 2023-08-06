import functools
import inspect


def validate_args(*expected_types):
    def decorator_switcheroo(function_to_validate):
        @functools.wraps(function_to_validate)
        def wrapped_function(*args, **kwargs):
            arg_names = inspect.getargspec(function_to_validate).args

            if len(arg_names) != len(expected_types):
                msg = 'Please provide expected types for all arguments for function {function}()' \
                      .format(function=function_to_validate.func_name)
                raise RuntimeError(msg)

            # default values (if any)
            arg_to_default = dict()
            defaults = inspect.getargspec(function_to_validate).defaults
            if defaults is not None:
                num_defaults = len(defaults)
                for arg, default in zip(arg_names[-num_defaults:], defaults):
                    arg_to_default[arg] = default

            # non-keyword args - can count on the ordering of these arguments
            arg_values = list(args)

            # keyword args / defaults - these might be in mixed order, i.e., some kwargs specified, some defaulted,
            # so need to process them at the same time to get the order to match arg_names and expected_types
            num_kwargs_or_defaults = len(arg_names) - len(args)
            if num_kwargs_or_defaults > 0:
                for arg_name in arg_names[-num_kwargs_or_defaults:]:
                    if arg_name in kwargs:
                        arg_values.append(kwargs[arg_name])
                    elif arg_name in arg_to_default:
                        default = arg_to_default[arg_name]
                        arg_values.append(default)
                    else:
                        msg = 'No value provided for argument "{arg}" in function {function}()' \
                              .format(arg=arg_name, function=function_to_validate.func_name)
                        raise RuntimeError(msg)

            for arg_name, value, expected_type in zip(arg_names, arg_values, expected_types):
                # Allow defaulted None values regardless of expected type
                if value is None and arg_name in arg_to_default and arg_to_default[arg_name] is None:
                    continue

                if not isinstance(value, expected_type):
                    msg = 'Expected {expected_type} for argument "{arg}" in call to {function}(); '\
                          'received {actual_type} ({val})' \
                          .format(expected_type=expected_type, arg=arg_name, function=function_to_validate.func_name,
                                  val=value, actual_type=type(value))
                    raise RuntimeError(msg)

            return function_to_validate(*args, **kwargs)
        return wrapped_function
    return decorator_switcheroo
