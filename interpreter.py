
Scope = {}


class SyntacticClass:
    def __init__(self, value, childrens):
        self.childrens = childrens
        self.value = value

    def start_with(self, exp):
        keys = list(self.childrens.keys())
        return keys and keys[0] == exp


class Syn_S(SyntacticClass):
    def interpret(self):
        return self.childrens['code'].interpret()


class Syn_code(SyntacticClass):
    def interpret(self):
        if self.childrens.get('statement', False):
            self.childrens['statement'].interpret()
            self.childrens['code_p'].interpret()


class Syn_code_p(SyntacticClass):
    def interpret(self):
        if self.childrens.get('statement', False):
            self.childrens['statement'].interpret()
            self.childrens['code_p'].interpret()


class Syn_statement(SyntacticClass):
    def interpret(self):
        if self.childrens.get('bucle', False):
            self.childrens['bucle'].interpret()
        elif self.childrens.get('conditional', False):
            self.childrens['conditional'].interpret()
        elif self.childrens.get('declaration', False):
            self.childrens['declaration'].interpret()
        elif self.childrens.get('assigment', False):
            self.childrens['assigment'].interpret()
        elif self.childrens.get('other_statement', False):
            self.childrens['other_statement'].interpret()


class Syn_bucle(SyntacticClass):
    def interpret(self):
        while bool(self.childrens['expression'].interpret()):
            self.childrens['code'].interpret()


class Syn_conditional(SyntacticClass):
    def interpret(self):
        if bool(self.childrens['expression'].interpret()):
            self.childrens['code'].interpret()
        elif self.childrens.get('conditional_p', False):
            self.childrens['conditional_p'].interpret()


class Syn_conditional_p(SyntacticClass):
    def interpret(self):
        if self.childrens.get('else'):
            self.childrens['code'].interpret()


class Syn_declaration(SyntacticClass):
    def interpret(self):
        if self.start_with('d_number'):
            if Scope.get(self.childrens['variable'].value) is None:
                Scope[self.childrens['variable'].value] = 0
            else:
                raise Exception('The variable was previously defined')
        elif self.start_with('d_string'):
            if Scope.get(self.childrens['variable'].value) is None:
                Scope[self.childrens['variable'].value] = ''
            else:
                raise Exception('The variable was previously defined')
        elif self.start_with('d_video'):
            if Scope.get(self.childrens['variable'].value) is None:
                Scope[self.childrens['variable'].value] = ''  # put video empty instance
            else:
                raise Exception('The variable was previously defined')
        if self.childrens.get('declaration_p', False):
            Scope[self.childrens['variable'].value] = self.childrens['declaration_p'].interpret()
        return Scope[self.childrens['variable'].value]


class Syn_declaration_p(SyntacticClass):
    def interpret(self):
        if self.childrens.get('expression'):
            return self.childrens['expression'].interpret()
        return None


class Syn_assigment(SyntacticClass):
    def interpret(self):
        Scope[self.childrens['variable'].value] = self.childrens['expression'].interpret()
        return Scope[self.childrens['variable'].value]


class Syn_other_statement(SyntacticClass):
    def interpret(self):
        if self.childrens.get('Print', False):
            print(self.childrens['expression'].interpret())


class Syn_expression(SyntacticClass):
    def interpret(self):
        if self.start_with('('):
            if self.childrens.get('expression_p', False):
                return self.childrens['expression_p'].interpret(
                    self.childrens['expression'].interpret()
                )
            return self.childrens['expression'].interpret()
        elif self.start_with('variable'):
            return self.childrens['expression_p'].interpret(
                self.childrens['expression_variable'].interpret(
                    self.childrens['variable'].interpret()
                )
            )
        elif self.start_with('number'):
            return self.childrens['expression_p'].interpret(
                self.childrens['number'].interpret()
            )
        elif self.start_with('string'):
            return self.childrens['expression_p'].interpret(
                self.childrens['string'].interpret()
            )
        elif self.start_with('VideoFileClip'):
            # this needs video implementation
            print('Processing video')
        elif self.start_with('ImageClip'):
            # this needs video implementation
            print('Processing video')


class Syn_expression_variable(SyntacticClass):
    def interpret(self, val=None):
        if self.childrens.get('expression_variable_p'):
            return self.childrens['expression_variable_p'].interpret(
                val
            )
        return val


class Syn_expression_variable_p(SyntacticClass):
    def interpret(self, val=None):
        if self.childrens.get('subclip', False):
            return val.subclip()
        return val


class Syn_expression_p(SyntacticClass):
    def interpret(self, val=None):
        if self.childrens.get('expression'):
            return self.childrens['operator'].interpret(
                val, self.childrens['expression'].interpret()
            )
        return val


class Syn_operator(SyntacticClass):
    def interpret(self, term1, term2):
        if self.childrens.get('+', False):
            return term1 + term2
        elif self.childrens.get('-', False):
            return term1 - term2
        elif self.childrens.get('*', False):
            return term1 * term2
        elif self.childrens.get('/', False):
            return term1 / term2


class Node:
    def __init__(self, label, value, hijos):
        self.childrens = {}
        self.value = value
        self.label = label
        for i in range(0, len(hijos)):
            self.childrens[hijos[i]] = Node(hijos[i],'e',[])

    def __getitem__(self, child):
        return self.childrens[child]

    def setitem(self, hijos):
        for i in range(0, len(hijos)):
            self.childrens[hijos[i]] = Node(hijos[i],'e', [])

    def set_value(self, value):
        self.value = value

    def set_label(self, label):
        self.label = label

    def __repr__(self, level=0):
        ret = "\t" * level + repr(self.label) + "\n"
        for child in self.childrens:
            ret += self.childrens[child].__repr__(level + 1)
        return ret

    def interpret(self, prev=None, prev2=None):
        # print(self.label)
        if not self.childrens:
            if self.label == 'number':
                return int(self.value)
            elif self.label == 'string':
                return str(self.value)
            elif self.label == 'variable':
                return Scope.get(self.value)
        elif self.label == 'S':
            return Syn_S(self.value, self.childrens).interpret()
        elif self.label == 'code':
            return Syn_code(self.value, self.childrens).interpret()
        elif self.label == 'code_p':
            return Syn_code_p(self.value, self.childrens).interpret()
        elif self.label == 'statement':
            return Syn_statement(self.value, self.childrens).interpret()
        elif self.label == 'bucle':
            return Syn_bucle(self.value, self.childrens).interpret()
        elif self.label == 'conditional':
            return Syn_conditional(self.value, self.childrens).interpret()
        elif self.label == 'conditional_p':
            return Syn_conditional_p(self.value, self.childrens).interpret()
        elif self.label == 'declaration':
            return Syn_declaration(self.value, self.childrens).interpret()
        elif self.label == 'declaration_p':
            return Syn_declaration_p(self.value, self.childrens).interpret()
        elif self.label == 'assigment':
            return Syn_assigment(self.value, self.childrens).interpret()
        elif self.label == 'expression':
            return Syn_expression(self.value, self.childrens).interpret()
        elif self.label == 'expression_p':
            return Syn_expression_p(self.value, self.childrens).interpret(prev)
        elif self.label == 'expression_variable':
            return Syn_expression_variable(self.value, self.childrens).interpret(prev)
        elif self.label == 'expression_variable_p':
            return Syn_expression_variable_p(self.value, self.childrens).interpret(prev)
        elif self.label == 'operator':
            return Syn_operator(self.value, self.childrens).interpret(prev, prev2)
        elif self.label == 'other_statement':
            return Syn_other_statement(self.value, self.childrens).interpret()
        return None
