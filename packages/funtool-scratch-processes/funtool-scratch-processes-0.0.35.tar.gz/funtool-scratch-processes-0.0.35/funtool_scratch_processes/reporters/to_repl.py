import code
import inspect

def interact(reporter,state_collection,overriding_parameters=None,logging=None):
    drop_to_repl()    
    return state_collection


def drop_to_repl():
    """
    Python debug breakpoint.
    """

    caller = inspect.currentframe().f_back

    env = {}
    env.update(caller.f_globals)
    env.update(caller.f_locals)

    try:
        import readline # noqa
        import rlcompleter
        readline.set_completer(rlcompleter.Completer(env).complete)
        readline.parse_and_bind("tab: complete")
    except ImportError:
        pass

    shell = code.InteractiveConsole(env)
    shell.interact(
        '* Break: {} ::: Line {}\n'
        '* Continue with Ctrl+D...'.format(
            caller.f_code.co_filename, caller.f_lineno
        )
    )

