import console
import reflection


class InteractiveMethodCaller(object):

    def __init__(self, instance):
        self._instance = instance
        self._console = console.Console()

    def call_method_directly(self, method_name, *args, **kwargs):
        """
        Calls instance's method by its name and with specified arguments.
        Returns the result of that method.
        """
        method = getattr(self._instance, method_name)
        result = method(*args, **kwargs)
        return result

    def call_method_interactively(self):
        """
        Reads the method name and its argument values from stdin.
        Calls such defined method and returns its result.
        """
        input_method = self._console.explicit_input
        method_signatures = dict(reflection.get_method_signatures(self._instance))
        method_names = sorted(method_signatures)

        prompt = "Choose one of the methods:\n{}\nmethod".format(", ".join(method_names))
        method_name = input_method(prompt)

        if method_name not in method_signatures:
            self._console.pop_history(prompt)
            print "\nInvalid method name"
            return

        argument_names = method_signatures[method_name]
        arguments = map(input_method, argument_names)

        result = self.call_method_directly(method_name, *arguments)
        return result
