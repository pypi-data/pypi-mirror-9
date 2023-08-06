import os, time

class Command:
    commandline_options = []
    help = "Add a new rule"

    def __init__(self):
        if (len(commandline_options!=2)):
            raise Exception("Internal error: each command must supply 2 command line options")

            	
    def __call__(self, option, opt_str, value, parser, *args, **kwargs):
        return True

        

    def help(self, indent = "  "):
        """
        Text documentation for the method.
        """

        (min_args, max_args, defaults) = self.args()

        text = "%s(%s) -> %s\n\n" % (self.name, ", ".join(max_args), xmlrpc_type(self.returns))

        text += "Description:\n\n"
        lines = [indent + line.strip() for line in self.__doc__.strip().split("\n")]
        text += "\n".join(lines) + "\n\n"

        def param_text(name, param, indent, step):
            """
            Format a method parameter.
            """

            text = indent

            # Print parameter name
            if name:
                param_offset = 32
                text += name.ljust(param_offset - len(indent))
            else:
                param_offset = len(indent)

            # Print parameter type
            param_type = python_type(param)
            text += xmlrpc_type(param_type) + "\n"

            # Print parameter documentation right below type
            if isinstance(param, Parameter):
                wrapper = textwrap.TextWrapper(width = 70,
                                               initial_indent = " " * param_offset,
                                               subsequent_indent = " " * param_offset)
                text += "\n".join(wrapper.wrap(param.doc)) + "\n"
                param = param.type

            text += "\n"

            # Indent struct fields and mixed types
            if isinstance(param, dict):
                for name, subparam in param.iteritems():
                    text += param_text(name, subparam, indent + step, step)
            elif isinstance(param, Mixed):
                for subparam in param:
                    text += param_text(name, subparam, indent + step, step)
            elif isinstance(param, (list, tuple, set)):
                for subparam in param:
                    text += param_text("", subparam, indent + step, step)

            return text

        text += "Parameters:\n\n"
        for name, param in zip(max_args, self.accepts):
            text += param_text(name, param, indent, indent)

        text += "Returns:\n\n"
        text += param_text("", self.returns, indent, indent)

        return text

    def args(self):
        """
        Returns a tuple:

        ((arg1_name, arg2_name, ...),
         (arg1_name, arg2_name, ..., optional1_name, optional2_name, ...),
         (None, None, ..., optional1_default, optional2_default, ...))

        That represents the minimum and maximum sets of arguments that
        this function accepts and the defaults for the optional arguments.
        """
        
        # Inspect call. Remove self from the argument list.
        max_args = self.call.func_code.co_varnames[1:self.call.func_code.co_argcount]
        defaults = self.call.func_defaults
        if defaults is None:
            defaults = ()

        min_args = max_args[0:len(max_args) - len(defaults)]
        defaults = tuple([None for arg in min_args]) + defaults
        
        return (min_args, max_args, defaults)

    def type_check(self, name, value, expected, args):
        """
        Checks the type of the named value against the expected type,
        which may be a Python type, a typed value, a Parameter, a
        Mixed type, or a list or dictionary of possibly mixed types,
        values, Parameters, or Mixed types.
        
        Extraneous members of lists must be of the same type as the
        last specified type. For example, if the expected argument
        type is [int, bool], then [1, False] and [14, True, False,
        True] are valid, but [1], [False, 1] and [14, True, 1] are
        not.

        Extraneous members of dictionaries are ignored.
        """

        # If any of a number of types is acceptable
        if isinstance(expected, Mixed):
            for item in expected:
                try:
                    self.type_check(name, value, item, args)
                    return
                except SfaInvalidArgument, fault:
                    pass
            raise fault

        # If an authentication structure is expected, save it and
        # authenticate after basic type checking is done.
        #if isinstance(expected, Auth):
        #    auth = expected
        #else:
        #    auth = None

        # Get actual expected type from within the Parameter structure
        if isinstance(expected, Parameter):
            min = expected.min
            max = expected.max
            nullok = expected.nullok
            expected = expected.type
        else:
            min = None
            max = None
            nullok = False

        expected_type = python_type(expected)

        # If value can be NULL
        if value is None and nullok:
            return

        # Strings are a special case. Accept either unicode or str
        # types if a string is expected.
        if expected_type in StringTypes and isinstance(value, StringTypes):
            pass

        # Integers and long integers are also special types. Accept
        # either int or long types if an int or long is expected.
        elif expected_type in (IntType, LongType) and isinstance(value, (IntType, LongType)):
            pass

        elif not isinstance(value, expected_type):
            raise SfaInvalidArgument("expected %s, got %s" % \
                                     (xmlrpc_type(expected_type),
                                      xmlrpc_type(type(value))),
                                     name)

        # If a minimum or maximum (length, value) has been specified
        if expected_type in StringTypes:
            if min is not None and \
               len(value.encode(self.api.encoding)) < min:
                raise SfaInvalidArgument, "%s must be at least %d bytes long" % (name, min)
            if max is not None and \
               len(value.encode(self.api.encoding)) > max:
                raise SfaInvalidArgument, "%s must be at most %d bytes long" % (name, max)
        elif expected_type in (list, tuple, set):
            if min is not None and len(value) < min:
                raise SfaInvalidArgument, "%s must contain at least %d items" % (name, min)
            if max is not None and len(value) > max:
                raise SfaInvalidArgument, "%s must contain at most %d items" % (name, max)
        else:
            if min is not None and value < min:
                raise SfaInvalidArgument, "%s must be > %s" % (name, str(min))
            if max is not None and value > max:
                raise SfaInvalidArgument, "%s must be < %s" % (name, str(max))

        # If a list with particular types of items is expected
        if isinstance(expected, (list, tuple, set)):
            for i in range(len(value)):
                if i >= len(expected):
                    j = len(expected) - 1
                else:
                    j = i
                self.type_check(name + "[]", value[i], expected[j], args)

        # If a struct with particular (or required) types of items is
        # expected.
        elif isinstance(expected, dict):
            for key in value.keys():
                if key in expected:
                    self.type_check(name + "['%s']" % key, value[key], expected[key], args)
            for key, subparam in expected.iteritems():
                if isinstance(subparam, Parameter) and \
                   subparam.optional is not None and \
                   not subparam.optional and key not in value.keys():
                    raise SfaInvalidArgument("'%s' not specified" % key, name)

        #if auth is not None:
        #    auth.check(self, *args)
