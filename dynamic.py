"""
For dynamic completion.
"""
import copy

import parsing
import evaluate

# This is something like the sys.path, but only for searching params. It means
# that this is the order in which Jedi searches params.
search_param_modules = ['.']


class ParamListener(object):
    """
    This listener is used to get the params for a function.
    """
    def __init__(self):
        self.param_possibilities = []

    def execute(self, params):
        self.param_possibilities.append(params)


def search_params(param):
    """
    This is a dynamic search for params. If you try to complete a type:
    >>> def func(foo):
    >>>     # here is the completion
    >>>     foo
    >>> func(1)
    >>> func("")

    It is not known what the type is, because it cannot be guessed with
    recursive madness. Therefore one has to analyse the statements that are
    calling the function, as well as analyzing the incoming params.
    """
    def get_params_for_module(module):
        """
        Returns the values of a param, or an empty array.
        """
        try:
            possible_stmts = current_module.used_names[func_name]
        except KeyError:
            return []

        for stmt in possible_stmts:
            evaluate.follow_statement(stmt)

        result = []
        for params in listener.param_possibilities:
            for p in params:
                if str(p) == param_name:
                    result += evaluate.follow_statement(p.parent)
        #print listener.param_possibilities, param, result

        return result

    func = param.get_parent_until(parsing.Function)
    current_module = param.get_parent_until()
    func_name = str(func.name)
    if func_name == '__init__' and isinstance(func.parent, parsing.Class):
        func_name = str(func.parent.name)

    # get the param name
    if param.assignment_details:
        arr = param.assignment_details[0][1]
    else:
        arr = param.get_assignment_calls()
    offset = 1 if arr[0][0] in ['*', '**'] else 0
    param_name = str(arr[0][offset].name)

    # add the listener
    listener = ParamListener()
    func.listeners.add(listener)

    result = get_params_for_module(current_module)

    # TODO check other modules
    # cleanup: remove the listener
    func.listeners.remove(listener)

    return result


@evaluate.memoize_default([])
def check_array_additions(array, is_list=True):
    """
    Checks if a `parsing.Array` has "add" statements:
    >>> a = [""]
    >>> a.append(1)
    """
    def scan_array(arr, search_name):
        """ Returns the function Calls that match func_name """
        result = []
        for sub in arr:
            for s in sub:
                if isinstance(s, parsing.Array):
                    result += scan_array(s, search_name)
                elif isinstance(s, parsing.Call):
                    n = s.name
                    if isinstance(n, parsing.Name) and search_name in n.names:
                        result.append(s)
        return result

    def check_calls(calls, add_name):
        result = []
        for c in calls:
            call_path = list(c.generate_call_path())
            separate_index = call_path.index(add_name)
            if not len(call_path) > separate_index + 1:
                # this means that there is no execution -> [].append
                continue
            backtrack_path = iter(call_path[:separate_index])

            position = c.parent_stmt.start_pos
            scope = c.parent_stmt.parent
            print 'd', call_path
            e = evaluate.follow_call_path(backtrack_path, scope, position)
            print 'e', e
            if not array in e:
                # the `append`, etc. belong to other arrays
                continue

            if add_name in ['append', 'add']:
                result += evaluate.follow_call_list(call_path[separate_index + 1])
            elif add_name in ['extend', 'update']:
                result += evaluate.follow_call_list(call_path[separate_index + 1])
        return result

    stmt = array._array.parent_stmt
    current_module = stmt.get_parent_until()
    search_names = ['append', 'extend', 'insert'] if is_list else \
                                                            ['add', 'update']
    possible_stmts = []
    result = []
    for n in search_names:
        try:
            possible_stmts += current_module.used_names[n]
        except KeyError:
            continue
        for stmt in possible_stmts:
            result += check_calls(scan_array(stmt.get_assignment_calls(), n), n)

    return result
