import csv

first = [x for x in csv.reader(open('first.csv', 'r'), delimiter='\t')]
follow = [x for x in csv.reader(open('follow.csv', 'r'), delimiter='\t')]
predict = [x for x in csv.reader(open('predict.csv', 'r'), delimiter='\t')]
grammar = [x.split() for x in open('grammar', 'r')]
first[0][-1] = follow[0][-1] = predict[0][-1] = ""
ts = follow[0][1:]
tmap = {}
for t in ts:
    tmap[t] = len(tmap) + 1

nts = []
ntrows = []
ntmap = {}
rid = 0
for x in grammar:
    if (len(nts) == 0 or nts[-1] != x[0]):
        nts.append(x[0])
        ntmap[x[0]] = len(ntmap)
        ntrows.append([rid])
    else:
        ntrows[-1].append(rid)
    rid += 1


for x in first:
    assert len(x) == 26
for x in follow:
    assert len(x) == 26
for x in predict:
    assert len(x) == 26
assert len(first) == 47
assert len(follow) == 47
assert len(nts) == 46
assert len(predict) == 84
assert len(grammar) == 83
assert predict[0] == follow[0]
assert first[0] == follow[0]
#

class ParserToken:
    def __init__(self, line, index, str, ty) -> None:
        self.line = line
        self.index = index
        self.str = str
        self.ty = ty

def evaluateExpansion(id):
    return grammar[id-1][1:]
def getToken():
    return ParserToken(0,0,"void", "void")
def parse():
    stack = ['Program']
    token = getToken()
    while True:
        r = 0
        top = stack[-1]
        if (top in ntmap):
            top = ntmap[top]
            for r in ntrows[top]:
                if predict[r + 1][tmap[token.ty]] == '+':
                    break
            if predict[r + 1][tmap[token.ty]] == '+':
                print('happy')
                replacement = grammar[r][1:]
                stack.pop()
                for x in reversed(replacement):
                    stack.append(x)
            else:
                print('sad')
        else:
            if top == token.ty:
                print("happy")
                if top == '':
                    return
                token = getToken()
                stack.pop()
            else:
                print('sad')
parse()
