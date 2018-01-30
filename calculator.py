from ExpressionEvaluator import *
import Reader
from enum import Enum
from math import *
import math
from _functools import reduce

dynamic_env = {}

OPERATOR_LIST = ('+', '-', '*', '/', '%', '^')
ESCAPE_SPACE_SYMBOL = ('\n', '\r', '\t', ' ', '')
MATH_FUNC = tuple(filter(lambda x: not x.startswith('_') and 'function' in type(getattr(math, x)).__name__, dir(math)))
MATH_CONST = tuple(filter(lambda x: not x.startswith('_') and type(getattr(math, x)).__name__ == 'float', dir(math)))
BUILT_IN = ('sum', 'min', 'max', 'any', 'all')
KWLIST = tuple(__import__('keyword').kwlist)


class ErronoToken(Enum):
    name_error = 'name'
    syntax_error = 'syntax'
    value_error = 'value'


def print_result(result):
    print('Œ >-> {}'.format(result))


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


def check_arg_name(name):
    if name in dynamic_env.keys():
        return True
    if name in MATH_FUNC + MATH_CONST + BUILT_IN:
        return False
    return print('NameError: {} is not defined'.format(name))


def is_real(s):
    if '.' in s and s.count('.') == 1:
        return len(list(filter(lambda x: x.isdigit(), s.split('.'))))
    else:
        return s.isdigit()


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
        if cur.isalpha() or cur.isdigit():
            while reader.has_next() and reader.get_cursor_data() != ',':
                cur += reader.next()
            r_arg.append(cur)
        elif cur == ',':
            inner_exp = ''
            while reader.has_next() and reader.get_cursor_data() != ',':
                inner_exp += reader.next()
            reader.next()
            if inner_exp:
                r_arg.append(inner_exp)
            else:
                r_arg.append(None)
    if len(l_arg) != len(r_arg):
        print('Argument length dose not match, stop data assignment')
        return None, None
    else:
        return l_arg, r_arg


def process_calculation(exp, dep=-1):
    reader = Reader.new_instance(exp)
    res = ''
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
            chk_res = check_arg_name(cur)
            if chk_res is None:
                return ErronoToken('name')
            elif not chk_res:
                arg_cur = reader.next()
                if arg_cur not in ('(', ' '):
                    if cur in MATH_FUNC:
                        print('<math-function {}>'.format(cur))
                        return ErronoToken('name')
                    elif cur in BUILT_IN:
                        print('<built-in function {}>'.format(cur))
                        return ErronoToken('name')
                else:
                    func_call = eval(cur)
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
                            call_param = eval_calculation(process_calculation(call_param))
                        else:
                            call_param = float(call_param)
                        res = res + str(func_call(call_param))
                    else:
                        param_list = ''
                        stk_cnt = 1
                        while reader.has_next() and stk_cnt:
                            ptr = reader.next()
                            if ptr == '(':
                                stk_cnt += 1
                            elif ptr == ')':
                                stk_cnt -= 1
                            param_list += ptr
                        param_list = param_list[:-1].split(',')
                        # reader.next()
                        for i in range(0, len(param_list)):
                            param_list[i] = process_calculation(param_list[i], dep=1)
                            if isinstance(param_list[i], ErronoToken):
                                return ErronoToken('name')
                        for i in range(0, len(param_list)):
                            param_list[i] = eval_calculation(param_list[i])
                        try:
                            if len(param_list) > 1:
                                res += str(
                                    eval('{}({})'.format(cur,
                                                         reduce(lambda x, y: '{},{}'.format(x, y), param_list))))
                            else:
                                res += str(
                                    eval('{}({})'.format(cur, str(param_list).replace('[', '').replace(']', ''))))
                        except TypeError:
                            if cur in ('gcd',):
                                param_list = list(map(lambda x: int(x), param_list))
                                res += str(
                                    eval('{}({})'.format(cur,
                                                         reduce(lambda x, y: '{},{}'.format(x, y), param_list))))
                            elif cur in BUILT_IN:
                                res += str(
                                    eval('{}([{}])'.format(cur,
                                                           reduce(lambda x, y: '{},{}'.format(x, y), param_list))))
            else:
                res = res + str(dynamic_env.get(cur))
        else:
            if dep != -1:
                if cur == '(':
                    dep += 1
                elif cur == ')':
                    dep -= 1
                if dep == 0:
                    return res
            res += cur
    return res


def eval_calculation(exp):
    return Evaluator(ExprTreeConstructor(exp).build()).eval()


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
                    arg_r[i] = process_calculation(arg_r[i])
                    if isinstance(arg_r[i], ErronoToken):
                        status = 1
                        break
                if status:
                    continue
                for i in range(0, len(arg_r)):
                    dynamic_env.update({arg_l[i]: eval_calculation(arg_r[i])})
        else:
            if check_parenthesis_matching(exp):
                exp = process_calculation(exp)
                if isinstance(exp, ErronoToken):
                    continue
                print_result(eval_calculation(exp))


main()
