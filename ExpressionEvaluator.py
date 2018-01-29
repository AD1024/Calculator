import Reader


class Operator:
    __slots__ = ['lchild', 'op', 'rchild']

    def __init__(self, lopnd, opat, ropnd):
        self.lchild = lopnd
        self.rchild = ropnd
        self.op = opat

    def __repr__(self):
        return '{}{}{}'.format(self.lchild, self.op, self.rchild)


class Const:
    def __init__(self, v):
        self.value = v

    def __str__(self):
        return '{}'.format(self.value)

    def __repr__(self):
        return '{}'.format(self.value)


class Evaluator:
    def __init__(self, rt):
        self.root = rt

    def exec(self, node):
        func = getattr(self, 'eval_{}'.format(type(node).__name__))
        return func(node)

    def eval_Operator(self, node):
        return {
            '+': lambda: self.exec(node.lchild) + self.exec(node.rchild),
            '-': lambda: self.exec(node.lchild) - self.exec(node.rchild),
            '*': lambda: self.exec(node.lchild) * self.exec(node.rchild),
            '/': lambda: self.exec(node.lchild) / self.exec(node.rchild),
            '%': lambda: self.exec(node.lchild) % self.exec(node.rchild),
            '^': lambda: self.exec(node.lchild) ** self.exec(node.rchild),
            '|': lambda: int(self.exec(node.lchild)) | int(self.exec(node.rchild)),
            '&': lambda: int(self.exec(node.lchild)) & int(self.exec(node.rchild)),
            '$': lambda: int(self.exec(node.lchild)) ^ int(self.exec(node.rchild)),
        }[node.op]()

    def eval_Const(self, node):
        return node.value

    def eval(self):
        return self.exec(self.root)


class ExprTreeConstructor:
    def __init__(self, exp):
        self.expr = list(exp)
        self.num = []
        self.op = []

    def add_node(self):
        se = self.num.pop()
        fi = Const(0)
        if self.num:
            fi = self.num.pop()
        {
            '+': lambda: self.num.append(Operator(fi, '+', se)),
            '-': lambda: self.num.append(Operator(fi, '-', se)),
            '*': lambda: self.num.append(Operator(fi, '*', se)),
            '/': lambda: self.num.append(Operator(fi, '/', se)),
            '%': lambda: self.num.append(Operator(fi, '%', se)),
            '^': lambda: self.num.append(Operator(fi, '^', se)),
            '|': lambda: self.num.append(Operator(fi, '|', se)),
            '&': lambda: self.num.append(Operator(fi, '&', se)),
            '$': lambda: self.num.append(Operator(fi, '$', se)),
        }[self.op[-1]]()
        self.op.pop()

    def build(self):
        reader = Reader.new_instance(self.expr)
        while reader.has_next():
            i = reader.next()
            if i.isdigit():
                const_value = i
                while reader.has_next() and reader.get_cursor_data().isdigit():
                    const_value += reader.next()
                if reader.get_cursor_data() == '.':
                    const_value += reader.next()
                    while reader.has_next() and reader.get_cursor_data().isdigit():
                        const_value += reader.next()
                self.num.append(Const(float(const_value)))
            elif i == 'i' or i == 'n':
                while reader.has_next() and reader.get_cursor_data().isalpha():
                    i += reader.next()
                self.num.append(Const(float(i)))
            elif i == '(':
                self.op.append(i)
            elif i == ')':
                while self.op[-1] != '(':
                    self.add_node()
                self.op.pop()
            elif i in ('*', '/'):
                while self.op and (self.op[-1] in ('*', '/')):
                    self.add_node()
                self.op.append(i)
            elif i in ('+', '-'):
                if i == '-' and (reader.get_prev_data(2) is None or (not reader.get_prev_data(2).isdigit())):
                    while reader.has_next() and reader.get_cursor_data().isdigit():
                        i += reader.next()
                    if reader.get_cursor_data() == '.':
                        i += reader.next()
                        while reader.has_next() and reader.get_cursor_data().isdigit():
                            i += reader.next()
                    self.num.append(Const(float(i)))
                else:
                    while self.op and self.op[-1] != '(' and self.op[-1] not in ('|', '$', '&'):
                        self.add_node()
                    self.op.append(i)
            elif i == '%':
                while self.op and self.op[-1] == '%':
                    self.add_node()
                self.op.append(i)
            elif i == '^':
                while self.op and self.op[-1] == '^':
                    self.add_node()
                self.op.append(i)
            elif i in ('|', '&', '$'):
                while self.op and self.op[-1] != '(':
                    self.add_node()
                self.op.append(i)

        while self.op:
            self.add_node()
        if not self.num:
            self.num.append(Const(None))
        return self.num[-1]
