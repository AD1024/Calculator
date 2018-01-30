from math import *
import math
from ExpressionEvaluator import *
from enum import Enum
from _functools import reduce
import time

dynamic_env = {}  # Variables
static_env = {}
lambda_scope = {}  # Local variable for lambdas
local_bindings = []

OPERATOR_LIST = ('+', '-', '*', '/', '%', '^', '|', '$', '&')
ESCAPE_SPACE_SYMBOL = ('\n', '\r', '\t', ' ', '')
MATH_FUNC = tuple(filter(lambda x: not x.startswith('_') and 'function' in type(getattr(math, x)).__name__, dir(math)))
MATH_CONST = tuple(filter(lambda x: not x.startswith('_') and type(getattr(math, x)).__name__ == 'float', dir(math)))
BUILT_IN = ('sum', 'min', 'max', 'any', 'all')
KWLIST = tuple(__import__('keyword').kwlist)


class ErronoToken(Enum):
    name_error = 'name'
    syntax_error = 'syntax'
    value_error = 'value'


class DataType(Enum):
    Int = 'int'
    Float = 'float'
    Fun = 'func'
    AFun = 'lambda'
    Bool = 'bool'


class LambdaFunc:
    __slots__ = ['func_body', 'param_list', '_id', 'name', 'param', 'func_context']

    def __init__(self, param, body, _id, name='', actual_param=None):
        self.func_body = body
        self.param_list = param
        self._id = _id
        self.name = name
        self.param = actual_param
        self.func_context = None

    def run(self, param):
        if len(param) != len(self.param_list):
            print('TypeError: missing argument(s); expected {} <> actual {}'.format(len(self.param_list), len(param)))
            return None
        __id = int(self._id, base=16)
        for k, v in zip(self.param_list, param):
            if __id not in lambda_scope.keys():
                lambda_scope[__id] = {k: v}
            else:
                lambda_scope[__id].update({k: v})
        if self.func_context is not None:
            __id = self.func_context.get_id()
            for k, v in zip(self.func_context.param_list, self.func_context.param):
                if __id not in lambda_scope.keys():
                    lambda_scope[__id] = {k: v}
                else:
                    lambda_scope[__id].update({k: v})
        process_body = process_calculation(self.func_body, lambda_call=__id)
        ret = eval_calculation(process_body)
        self.param = param
        if type(ret).__name__ == 'LambdaFunc':
            ret.func_context = self.__copy__()
        return ret

    def get_id(self):
        return self._id

    def __copy__(self):
        return LambdaFunc(self.param_list, self.func_body, self._id, self.name, self.param)

    def __repr__(self):
        return '<defined-function @ {}: {} -> {}>'.format(self._id,
                                                          reduce(lambda x, y: '{}, {}'.format(x, y), self.param_list),
                                                          self.func_body)


def assign_id():
    return hex(int(time.time()))


def new_lambda(param, body, name=''):
    return LambdaFunc(param, body, assign_id(), name)


def check_parenthesis_matching(exp):
    s = []
    for i in exp:
        if i == '(':
            s.append(i)
        elif i == ')':
            if not s:
                print('Parenthesis does not match, stop calculating')
                return False
            else:
                s.pop()
    return True if not s else False


def check_arg_name(name, lambda_call=-1):
    if name in dynamic_env.keys():
        if static_env[name] == DataType.Fun:
            return False
        return True
    if name in MATH_FUNC + MATH_CONST + BUILT_IN:
        return False
    if lambda_call != -1:
        return None if lambda_scope[lambda_call].get(name, None) is None else True
    return print('NameError: {} is not defined'.format(name))


def is_real(s):
    if '.' in s and s.count('.') == 1:
        return len(list(filter(lambda x: x.isdigit(), s.split('.'))))
    else:
        return s.isdigit()


def parse_lambda(lmda):
    p = lmda.find('->')
    if p == -1:
        return ErronoToken('syntax')
    param = lmda[:p]
    body = lmda[p + 2:]
    reader = Reader.new_instance(param)
    parsed_param = ''
    while reader.has_next():
        cur = reader.next()
        if cur not in ESCAPE_SPACE_SYMBOL and cur not in '{,}'.split(','):
            parsed_param += cur
    parsed_param = parsed_param.split(',')
    reader = Reader.new_instance(body)
    parsed_body = reader.next()
    stk = 2 if parsed_body == '{' else None
    if stk is None:
        while reader.has_next() and reader.get_cursor_data() != '}':
            cur = reader.next()
            if cur not in ESCAPE_SPACE_SYMBOL:
                parsed_body += cur
    else:
        while reader.has_next() and stk:
            cur = reader.next()
            if cur not in ESCAPE_SPACE_SYMBOL:
                if cur == '{':
                    stk += 1
                elif cur == '}':
                    stk -= 1
                parsed_body += cur
    return parsed_param, parsed_body


def push_anonymous_fun(exp):
    param_list, func_body = parse_lambda(exp)
    func = new_lambda(param_list, func_body, '{}'.format(hex(int(time.time()))))
    local_bindings.append(func)
    static_env.update({func.name: DataType.AFun})


def parse_value_assignment(exp):
    if exp.count('=') > 1:
        print('Syntax Error: duplicated \'=\'')
        return None, None
    eq_pos = exp.find('=')
    l_expr, r_expr = exp[:eq_pos], exp[eq_pos + 1:]
    l_arg = []
    r_arg = []
    reader = Reader.new_instance(l_expr)
    while reader.has_next():
        cur = reader.next()
        if cur in ESCAPE_SPACE_SYMBOL:
            continue
        if cur.isalpha():
            while reader.has_next() and reader.get_cursor_data().isalpha():
                cur += reader.next()
            if cur in MATH_FUNC:
                print('NameError: {} is a math function'.format(cur))
                return None, None
            if cur in BUILT_IN:
                print('NameError: {} is a built-in function'.format(cur))
                return None, None
            if cur in KWLIST:
                print('NameError: {} is a keyword'.format(cur))
                return None, None
            l_arg.append(cur)
        elif cur in OPERATOR_LIST:
            print('calculation found in left expr, stop data assignment')
            return None, None
        elif cur == ',':
            continue
        elif cur not in ESCAPE_SPACE_SYMBOL:
            print('Invalid symbol found in l_expr @ {}'.format(reader.get_cursor() - 1))
    reader = Reader.new_instance(r_expr)
    while reader.has_next():
        cur = reader.next()
        if cur in ESCAPE_SPACE_SYMBOL:
            continue
        if cur.isalpha() or cur.isdigit():
            while reader.has_next() and reader.get_cursor_data() not in (',', '(', '{'):
                cur += reader.next()
            if reader.has_next() and reader.get_cursor_data() == '(':
                stk = 1
                cur += reader.next()
                while reader.has_next() and stk:
                    ptr = reader.next()
                    if ptr in ESCAPE_SPACE_SYMBOL:
                        continue
                    if ptr == '(':
                        stk += 1
                    elif ptr == ')':
                        stk -= 1
                    cur += ptr
                r_arg.append(cur)
            else:
                r_arg.append(cur)
        # elif cur == ',':
        #     inner_exp = ''
        #     while reader.has_next() and reader.get_cursor_data() != ',':
        #         inner_exp += reader.next()
        #     reader.next()
        #     if inner_exp:
        #         r_arg.append(inner_exp)
        #     else:
        #         r_arg.append(None)
        elif cur == '{':
            while reader.has_next() and reader.get_cursor_data() != '}':
                cur += reader.next()
            cur += reader.next()
            parse_data = parse_lambda(cur)
            r_arg.append(new_lambda(parse_data[0], parse_data[1]))
    if len(l_arg) != len(r_arg):
        print('Argument length dose not match, stop data assignment')
        return None, None
    else:
        return l_arg, r_arg


def process_calculation(exp, dep=-1, lambda_call=-1):
    reader = Reader.new_instance(exp)
    res = []
    _append = res.append
    while reader.has_next():
        cur = reader.next()
        if cur.isalpha():
            while reader.has_next() and reader.get_cursor_data() not in OPERATOR_LIST + ('(', ')', ' '):
                cur += reader.next()
            if cur in MATH_CONST:
                res += str(eval(cur))
                continue
            if cur in ('True', 'False'):
                res += cur
                continue
            chk_res = check_arg_name(cur, lambda_call)
            if chk_res is None:
                if lambda_call == -1:
                    return ErronoToken('name')
                else:
                    if lambda_scope[lambda_call].get(cur, None) is None:
                        return ErronoToken('name')
                    else:
                        res += str(lambda_scope[lambda_call].get(cur, None))
                        continue
            elif not chk_res or (
                    lambda_call != -1 and type(lambda_scope[lambda_call].get(cur)).__name__ == 'LambdaFunc'):
                arg_cur = reader.next()
                if arg_cur not in ('(', ' '):
                    if cur in MATH_FUNC:
                        # print('<math-function {}>'.format(cur))
                        return [eval(cur)]
                    elif cur in BUILT_IN:
                        # print('<built-in function {}>'.format(cur))
                        return [eval(cur)]
                    elif cur in dynamic_env.keys() and static_env[cur] == DataType.Fun:
                        print('{}'.format(repr(dynamic_env[cur])))
                        return [dynamic_env.get(cur)]
                else:
                    if arg_cur == ' ':
                        if cur in BUILT_IN:
                            break
                        call_param = ''
                        while reader.has_next() and reader.get_cursor_data() not in OPERATOR_LIST + ('(', ')', ' '):
                            call_param += reader.next()
                        if not is_real(call_param):
                            if check_arg_name(call_param) is None \
                                    and call_param[:call_param.find('(')] not in MATH_FUNC:
                                return ErronoToken('name')
                            call_param = eval_calculation(process_calculation(call_param, 1, lambda_call=lambda_call))
                        else:
                            call_param = float(call_param)
                        if cur in dynamic_env and static_env[cur] == DataType.Fun:
                            lambda_call = dynamic_env[cur]
                            _append(lambda_call.run((call_param,)))
                        else:
                            func_call = eval(cur)
                            _append(func_call(call_param))
                    else:
                        param_list = ''
                        stk_cnt = 0
                        while reader.has_next() and stk_cnt >= 0:
                            ptr = reader.next()
                            if ptr == '(':
                                stk_cnt += 1
                            elif ptr == ')':
                                stk_cnt -= 1
                            if ptr == ')' and stk_cnt < 0:
                                ptr = ''
                            param_list += ptr
                        if '{' in param_list or '(' in param_list:
                            t_reader = Reader.new_instance(param_list)
                            param_list = []
                            while t_reader.has_next():
                                t_cur = t_reader.next()
                                if t_cur in ('{', '('):
                                    ptr = t_cur
                                    while t_reader.has_next() and t_reader.get_cursor_data() not in ('}', ')'):
                                        t_cur = t_reader.next()
                                        ptr += t_cur
                                    ptr += t_reader.next()
                                    param_list.append(ptr)
                                elif t_cur == ',' or t_cur in ESCAPE_SPACE_SYMBOL:
                                    continue
                                elif t_cur.isalpha():
                                    ptr = t_cur
                                    while t_reader.has_next() and t_reader.get_cursor_data().isalpha():
                                        ptr += t_reader.next()
                                    if t_reader.has_next():
                                        t_cur = t_reader.next()
                                        if t_cur in ('{', '('):
                                            flag = 1
                                            ptr += t_cur
                                            stk = 1
                                            while t_reader.has_next() and (stk or flag):
                                                t_cur = t_reader.next()
                                                flag = 0
                                                if t_cur == '(':
                                                    stk += 1
                                                elif t_cur == ')':
                                                    stk -= 1
                                                if t_cur == ')' and stk < 0:
                                                    t_cur = ''
                                                ptr += t_cur
                                            param_list.append(ptr)
                                        else:
                                            t_reader.prev()
                                            param_list.append(ptr)
                                    else:
                                        param_list.append(ptr)
                                elif t_cur.isdigit():
                                    while t_reader.has_next() and (t_reader.get_cursor_data().isdigit()
                                                                 or t_reader.get_cursor_data() == '.'):
                                        t_cur += t_reader.next()
                                    param_list.append(t_cur)
                        else:
                            param_list = param_list.split(',')
                        # print(param_list)
                        for i in range(0, len(param_list)):
                            param_list[i] = process_calculation(param_list[i], dep=1, lambda_call=lambda_call)
                            if isinstance(param_list[i], ErronoToken):
                                return ErronoToken('name')
                        for i in range(0, len(param_list)):
                            param_list[i] = eval_calculation(param_list[i])
                        if cur in dynamic_env and static_env[cur] == DataType.Fun:
                            lambda_call = dynamic_env[cur]
                            _append(lambda_call.run(tuple(param_list)))
                            continue

                        def find_nearest_arg(func):
                            pass

                        if lambda_call != -1 and type(lambda_scope[lambda_call].get(cur)).__name__ == 'LambdaFunc':
                            lambda_call = lambda_scope[lambda_call].get(cur)
                            # print(lambda_call)
                            _append(lambda_call.run(tuple(param_list)))
                            continue
                        try:
                            if len(param_list) > 1:
                                _append(eval('{}({})'.format(cur,
                                                             reduce(lambda x, y: '{},{}'.format(x, y), param_list))))
                            else:
                                _append(eval('{}({})'.format(cur, str(param_list).replace('[', '').replace(']', ''))))
                        except TypeError:
                            if cur in ('gcd',):
                                param_list = list(map(lambda x: int(x), param_list))
                                _append(eval('{}({})'.format(cur,
                                                             reduce(lambda x, y: '{},{}'.format(x, y), param_list))))
                            elif cur in BUILT_IN:
                                _append(eval('{}([{}])'.format(cur,
                                                               reduce(lambda x, y: '{},{}'.format(x, y), param_list))))
            else:
                _append(dynamic_env.get(cur) if lambda_call == -1 else lambda_scope[lambda_call].get(cur))
        elif cur == '{':
            while reader.has_next() and reader.get_cursor_data() != '}':
                ptr = reader.next()
                if ptr not in ESCAPE_SPACE_SYMBOL:
                    cur += ptr
            cur += reader.next()
            push_anonymous_fun(cur)
            stk_cnt = 1
            if reader.has_next():
                nxt = reader.next()
                if nxt == '(':
                    param_list = ''
                    while reader.has_next() and stk_cnt:
                        ptr = reader.next()
                        if ptr in ESCAPE_SPACE_SYMBOL:
                            continue
                        if ptr == '(':
                            stk_cnt += 1
                        elif ptr == ')':
                            stk_cnt -= 1
                        param_list += ptr
                    param_list = param_list[:-1].split(',')
                    for i in range(0, len(param_list)):
                        param_list[i] = process_calculation(param_list[i], dep=1, lambda_call=lambda_call)
                        if isinstance(param_list[i], ErronoToken):
                            return ErronoToken('name')
                    for i in range(0, len(param_list)):
                        param_list[i] = eval_calculation(param_list[i])
                    lambda_call = local_bindings.pop()
                    _append(lambda_call.run(tuple(param_list)))
                else:
                    reader.prev()
            else:
                res.append(local_bindings.pop())
        else:
            if dep != -1:
                if cur == '(':
                    dep += 1
                elif cur == ')':
                    dep -= 1
                if dep == 0:
                    return res
            _append(cur)
    return res


def eval_calculation(exp):
    return Evaluator(ExprTreeConstructor(exp).build()).eval()


def print_result(result):
    print('Œ >-> {}'.format(result))


def main():
    print('Input calculation:')
    while 1:
        print('==>', end=' ')
        try:
            exp = input()
        except EOFError:
            print()
            exit(0)
        if exp == '\math_func':
            print(MATH_FUNC)
            continue
        elif exp == '\math_const':
            print(MATH_CONST)
            continue
        if exp in ('', '\n', '\t', '\a') or len(exp) == 0:
            continue
        if exp.startswith('rm'):
            splt = exp.split(' ')
            if len(splt) == 2 and splt[0] == 'rm':
                if check_arg_name(splt[1]):
                    dynamic_env.pop(splt[1])
                continue
        is_assgin = exp.find('=') != -1
        if is_assgin:
            arg_l, arg_r = parse_value_assignment(exp)
            if arg_r is None and arg_l is None:
                continue
            if not arg_r:
                for i in arg_l:
                    dynamic_env.update({i: None})
            else:
                status = 0
                for i in range(0, len(arg_r)):
                    if isinstance(arg_r[i], LambdaFunc):
                        arg_r[i] = [arg_r[i]]
                        continue
                    arg_r[i] = process_calculation(arg_r[i])
                    if isinstance(arg_r[i], ErronoToken):
                        status = 1
                        break
                if status:
                    continue
                for i in range(0, len(arg_r)):
                    dynamic_env.update({arg_l[i]: eval_calculation(arg_r[i])})
                    if type(dynamic_env[arg_l[i]]).__name__ == 'LambdaFunc':
                        static_env.update({arg_l[i]: DataType.Fun})
                    else:
                        static_env.update({arg_l[i]: {
                            int: lambda: DataType.Int,
                            bool: lambda: DataType.Bool,
                            float: lambda: DataType.Float,
                        }.get(type(dynamic_env[arg_l[i]]))()})
        else:
            if check_parenthesis_matching(exp):
                exp = process_calculation(exp)
                if isinstance(exp, ErronoToken):
                    continue
                print_result(eval_calculation(exp))


if __name__ == '__main__':
    main()
