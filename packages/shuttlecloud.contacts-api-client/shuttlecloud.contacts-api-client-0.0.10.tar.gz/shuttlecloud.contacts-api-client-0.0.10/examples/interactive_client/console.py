import sys
import getpass


def exit_on_eof(function):
    """
    Terminates executing process when EOFError is raised.
    Decorates the specified function with such logic.
    """
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except EOFError:
            sys.exit(0)
    return wrapper


class PasswordMismatchError(Exception):
    pass


class Console(object):

    def __init__(self):
        self._input_history = dict()

    @exit_on_eof
    def explicit_input(self, prompt, history=False):
        """
        Reads input from stdin with the specified prompt.
        If indicated, saves an input corresponding to the prompt,
        so next time it can be accepted as the default one.
        """
        default = self._input_history.get(prompt, "") if history else ""
        formatted_default = " [{}]".format(default) if default else ""
        formatted_prompt = "{}{} > ".format(prompt, formatted_default).lstrip()
        value = raw_input(formatted_prompt).strip() or default
        if history:
            self._input_history[prompt] = value
        return value

    @exit_on_eof
    def hidden_input(self, prompt):
        """
        Reads input from stdin with the specified prompt.
        Hides all of the typed input characters.
        """
        formatted_prompt = "{} > ".format(prompt)
        value = getpass.getpass(formatted_prompt).strip()
        return value

    def password_input(self, prompt, repeat=False):
        """
        Reads input from stdin with the specified prompt.
        Hides all of the typed input characters.
        If indicated, reading is repeated and inputs compared.
        """
        value = self.hidden_input(prompt)
        if repeat:
            prompt = "repeat {}".format(prompt)
            repeated_value = self.hidden_input(prompt)
            if value != repeated_value:
                raise PasswordMismatchError("Passwords do not match")
        return value

    def clear_history(self):
        self._input_history.clear()

    def pop_history(self, key):
        return self._input_history.pop(key, None)
