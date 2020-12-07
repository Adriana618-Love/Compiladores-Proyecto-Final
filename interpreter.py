
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
