
import os
from os import path

DOLAR = '$'
EPSILON = 'lambda'
operation_assign = ['=', '+', '-', '*', '/']
parenthesis = ['(', ')', '[', ']', '{', '}']
comparison_op = ['!=', '==', '<', '>', '<=', '>=']
reserved_word = ['Frame', 'Video', 'Audio', 'int']
conditional_statement = ['for', 'while', 'if']
function_statement = ['cargar', 'append', 'front', 'getNumberFrames', 'printf', 'setNumberFrames', 'join']


class File:
    file = None

    def __init__(self, name_file, path_file=''):
        self.name_file = name_file
        self.path_file = os.path.join((str(os.getcwd()),path_file)[len(path_file)], self.name_file)
        print("From file:", self.path_file)
        self.init_file()

    def init_file(self):
        if not path.exists(self.path_file):
            self.file = open(self.path_file, 'x')
            self.file.close()

    def append_line(self, line):
        self.file = open(self.name_file, 'a')
        self.file.write(line)
        self.file.close()

    def get_all_lines(self):
        self.file = open(self.name_file, 'r')
        lines = self.file.readlines()
        self.file.close()
        return lines


class Production:
    def __init__(self):
        self.left = []
        self.right = []

    def print(self):
        for i in self.right:
            print(self.left + " -> " + ' '.join(i))

    def get_left(self):
        return self.left.strip()

    def get_production(self):
        return self.right

    def add_right(self, new):
        for elem in new:
            self.right.append(elem)


class Grammar:
    tas = dict({'': {}})
    firsts = {}
    nexts = {}
    initial_node = 'goal'
    production = []
    terminals = []
    non_terminals = []

    def set_init(self, initial):
        self.initial_node = initial

    def get_index(self, left):
        i = 0
        for nt in self.non_terminals:
            if nt == left:
                return i
            i += 1
        return -1

    def load(self, file, separator_union='|', separator='::='):
        lines = file.get_all_lines()
        simbols = []
        for line in lines:
            pdc = line.split(separator)
            if len(pdc) == 1:
                continue
            my_left = pdc[0]
            my_right = pdc[1]
            expand = my_right.split(separator_union)
            expand = self.treat(expand)

            if not (my_left.strip() in self.non_terminals):
                self.non_terminals.append(my_left.strip())
                new_production = Production()
                new_production.left = my_left
                new_production.right = expand
                self.production.append(new_production)
            else:
                idx = self.get_index(my_left.strip())
                self.production[idx].add_right(expand)

            for rights in expand:
                for sim in rights:
                    if not (sim in simbols):
                        simbols.append(sim)
        self.fill_t(simbols)
        self.terminals.append('$')

    def fill_t(self, simbols):
        for ter in simbols:
            if not(ter in self.non_terminals):
                self.terminals.append(ter)

    def print(self):
        for p in self.production:
            p.print()

    def get_production(self, left):
        return self.production[self.get_index(left)].get_production()

    def treat(self, my_right):
        production = []
        for right in my_right:
            right = right.replace("$","")
            right = right.strip()
            production.append(right.split(' '))
        return production

    def join(self, ps, pc):
        for p in ps:
            pc.append(p)
        return pc

    def concatenate(self, pc, rs):
        for ele in rs:
            pc.append(ele)

    def get_first(self, prim):
        productions = self.get_production(prim)
        firsts_simple = []
        firsts_complex = []
        for prod in productions:
            if prod[0] in self.non_terminals:
                self.concatenate(firsts_complex, self.get_first(prod[0]))
            else:
                firsts_simple.append(prod[0])
        firsts = self.join(firsts_simple, firsts_complex)
        return firsts

    def get_productions(self):
        return self.production

    def get_firsts(self):
        self.firsts = {}
        for nodo in self.non_terminals:
            self.firsts[nodo] = self.get_first(nodo)
        return self.firsts

    def get_non_terminal(self, miniprod, i):
        for idx in range(i, len(miniprod)):
            if miniprod[idx] in self.non_terminals:
                return idx
        return -1

    def add(self, obt, tmp):
        for i in tmp:
            if not (i in obt):
                obt.append(i)

    def get_next(self, nt, sgts):
        productions = self.production
        for prod in productions:
            for right in prod.right:
                for idx in range(0, len(right)):
                    if nt == right[idx]:
                        if idx == len(right)-1:
                            self.add(sgts[right[idx]], sgts[prod.get_left()])
                        else:
                            if right[idx+1] in self.terminals:
                                if not(right[idx+1] in sgts[right[idx]]):
                                    sgts[right[idx]].append(right[idx+1])
                            else:
                                temp = self.get_first(right[idx+1])
                                if EPSILON in temp:
                                    temp.remove(EPSILON)
                                    self.add(temp, sgts[prod.get_left()])
                                self.add(sgts[right[idx]], temp)

    def get_nexts(self):
        self.nexts = {}
        for i in self.non_terminals:
            self.nexts[i] = []
        self.nexts[self.initial_node].append(DOLAR)
        for nt in self.non_terminals:
            self.get_next(nt, self.nexts)
        return self.nexts

    def create_table(self):
        self.tas = dict({'': {}})
        for p in self.production:
            self.tas[p.get_left()] = {}
            if len(p.get_production()) == 1:
                for i in self.firsts[p.get_left()]:
                    self.tas[p.get_left()][i] = p.get_production()[0]
            else:
                for i in p.get_production():
                    if i[0] != EPSILON:
                        if i[0] in self.terminals:
                            self.tas[p.get_left()][i[0]] = i
                        else:
                            prim_temp = self.get_first(i[0])
                            for term in prim_temp:
                                if term != EPSILON:
                                    self.tas[p.get_left()][term] = i
                    else:
                        for f in self.nexts[p.get_left()]:
                            self.tas[p.get_left()][f] = i
        self.tas[self.initial_node][list(self.tas[self.initial_node].keys())[0]].append('$')
        return self.tas

    def print_tas(self):
        for fst_key, sub_dict in self.tas.items():
            for snd_key, production in sub_dict.items():
                print(fst_key, snd_key, production)


class Token:
    item = None
    type = None
    line = None
    column = None

    def __init__(self, it, ty, ln, col):
        self.item = it.strip()
        self.line = ln
        self.column = col
        if ty == 'OTHER':
            if self.item in operation_assign:
                self.type = it
            elif self.item in parenthesis:
                self.type = it
            elif self.item in comparison_op:
                self.type = it

        elif ty == 'STREAM':
            if self.item in reserved_word:
                self.type = 'type'
            elif self.item in conditional_statement:
                self.type = it
            elif self.item in function_statement:
                self.type = 'name'
            else:
                self.type = 'name'
        else:
            self.type = ty

    def __str__(self):
        return "<%s, %s, %d, %d>" % (self.item, self.type, self.line, self.column)

    def __repr__(self):
        return "<%s, %s, %d, %d>" % (self.item, self.type, self.line, self.column)


class synE:
    def __init__(self, value, childrens):
        self.childrens = childrens
        self.value = value

    def interpret(self):
        return self.childrens['Ep'].interpret(self.childrens['T'].interpret())


class synEp:
    def __init__(self, value, childrens):
        self.childrens = childrens
        self.value = value

    def interpret(self, prev):
        if self.childrens.get('T'):
            valueT = self.childrens.get('T').interpret()
            if self.childrens.get('+'):
                return self.childrens.get('Ep').interpret(prev + valueT)
            elif self.childrens.get('-'):
                return self.childrens.get('Ep').interpret(prev - valueT)
        return prev


class synT:
    def __init__(self, value, childrens):
        self.childrens = childrens
        self.value = value

    def interpret(self):
        return self.childrens['Tp'].interpret(self.childrens['F'].interpret())


class synTp:
    def __init__(self, value, childrens):
        self.childrens = childrens
        self.value = value

    def interpret(self, prev):
        if self.childrens.get('F'):
            valueF = self.childrens.get('F').interpret()
            if self.childrens.get('*'):
                return self.childrens.get('Tp').interpret(prev * valueF)
        return prev


class synF:
    def __init__(self, value, childrens):
        self.childrens = childrens
        self.value = value

    def interpret(self):
        if self.childrens.get('E'):
            return self.childrens['E'].interpret()
        return self.childrens['num'].interpret()


class Node:
    def __init__(self,label,value, hijos):
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

    def interpret(self, prev=None):
        if not self.childrens:
            return int(self.value)
        elif self.label == 'E':
            return synE(self.value, self.childrens).interpret()
        elif self.label == 'Ep':
            return synEp(self.value, self.childrens).interpret(prev)
        elif self.label == 'T':
            return synT(self.value, self.childrens).interpret()
        elif self.label == 'Tp':
            return synTp(self.value, self.childrens).interpret(prev)
        elif self.label == 'F':
            return synF(self.value, self.childrens).interpret()

def write(stack, input, izq, der):
    line = ' '.join(stack) + "\t"*4 + ' '.join([str(x) for x in input]) + "\t" * 4 + izq + " -> " + ' '.join(der) + '\n'
    f = open("ouput.txt", "a")
    f.write(line)
    f.close()


class Validator:
    terminal = {}
    table = {}
    epsilon = EPSILON
    error_message = 'There was a problem, failed'
    initial_state = 'S'

    def __init__(self, terminals, table, initial_state):
        for term in terminals:
            self.terminal[term] = True
        self.table = table
        self.initial_state = initial_state

    def _join(self, lista, prod):
        temp = prod.copy()
        temp.reverse()
        lista.extend(temp)

    def _validate(self, non_terminal, idx, tokens, lista, node, nivel):
        dict = self.table.get(non_terminal, None)
        if dict is None:
            return -1
        prod = dict.get(tokens[idx].type, None)

        #print("non_terminal",non_terminal,"production",prod,"tokens[idx].type",tokens[idx].type)  #//Imprime las variables locales

        lista.pop()
        if prod is None:
            return -1
        self._join(lista, prod)

        izq = non_terminal
        der = prod
        _input = tokens[idx:]
        stack = lista.copy()
        write(stack, _input, izq, der)

        node.setitem(prod)
        #print(prod)
        for term in prod:
            #print(prod)
            print('termino',term,non_terminal,tokens[idx].type,term==tokens[idx].type)  #//Ver que termino se trabaja.
            if term == '':
                lista.pop()
                continue
            if term == self.epsilon:
                lista.pop()
                continue
            is_terminal = self.terminal.get(term, False)
            #print(is_terminal)
            if not is_terminal:
                idx = self._validate(term, idx, tokens, lista, node.childrens[term], nivel+1)
                if idx == -1:
                    return -1
            else:
                if tokens[idx].type != term and term == '$':
                    continue
                if tokens[idx].type == term:
                    node.childrens[term].value = int(tokens[idx].item)\
                        if tokens[idx].type == 'num' else tokens[idx].item
                    idx += 1
                else:
                    return -1
                lista.pop()
                write(lista.copy(), _input, "", [term])
        return idx

    def validate(self, tokens):
        arbol = Node(self.initial_state,'e', [])
        lista = [self.initial_state]
        size = self._validate(self.initial_state, 0, tokens, lista, arbol, 0)
        #print("Lo logro")  //Imprime una correcta finalización.
        #print(size,len(tokens))
        return arbol, size == len(tokens)


class Tokenizer:
    tokens = []

    def __init__(self, path_text):
        file = open(path_text, 'r')
        num_line = 1
        for line in file:
            self.tokenizer_line(line, num_line)
            num_line += 1
        token = Token(DOLAR, DOLAR, -1, -1)
        self.tokens.append(token)

    def tokenizer_line(self, line, n_line):
        idx = 0
        while idx < len(line):
            if line[idx].isdigit():
                token,idx = self.check_number(line, n_line, idx)
                self.tokens.append(token)
            elif line[idx].isalpha():
                token,idx = self.check_variable(line, n_line, idx)
                self.tokens.append(token)
            elif line[idx] == ' ' or line[idx] == '\n':
                idx += 1
            else:
                if line[idx:idx+2] in comparison_op:
                    token = Token(line[idx:idx+2], line[idx:idx+2], n_line, idx)
                    self.tokens.append(token)
                    idx += 2
                else:
                    token = Token(line[idx:idx+1], "OTHER", n_line, idx)
                    self.tokens.append(token)
                    idx += 1

    def check_number(self, string, n_line, index):
        begin = index
        while (index < len(string)) and string[index].isdigit():
            index += 1
        temp = Token(string[begin:index], "num", n_line, begin)
        return temp, index

    def check_variable(self, string, n_line, index):
        begin = index
        while (index < len(string)) and string[index].isalpha():
            index += 1
        temp = Token(string[begin:index], "STREAM", n_line, begin)
        return temp, index


if __name__ == '__main__':
    tokens = Tokenizer('input.txt')
    print(tokens.tokens)
    file = File('rules.txt')
    grammar = Grammar()
    grammar.set_init('S')
    grammar.load(file, '@', '::=')
    grammar.get_firsts()
    grammar.get_nexts()
    grammar.create_table()
    #grammar.print_tas() #///Para verificar que se crea correctamente la tabla
    print("No terminales",grammar.non_terminals)
    print("Terminales",grammar.terminals)

    validator = Validator(grammar.terminals, grammar.tas, 'S')
    parse_tree, is_valid = validator.validate(tokens.tokens)
    if not is_valid:
        raise Exception("Input is not accepted by rules")
    print(parse_tree)
    print("Interpret value")
    print(parse_tree.interpret())
