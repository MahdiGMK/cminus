import csv

import Scanner

first = [x for x in csv.reader(open('first.csv', 'r'), delimiter='\t')]
follow = [x for x in csv.reader(open('follow.csv', 'r'), delimiter='\t')]
predict = [x for x in csv.reader(open('predict.csv', 'r'), delimiter='\t')]
grammar = [x.split() for x in open('grammar', 'r')]
first[0][-1] = follow[0][-1] = predict[0][-1] = ""
ts = follow[0][1:]
tmap = {}
for t in ts:
    tmap[t] = len(tmap) + 1
tmap[None] = tmap['']

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
assert len(first) == 48
assert len(follow) == 48
assert len(nts) == 47
assert len(predict) == 86
assert len(grammar) == 85
assert predict[0] == follow[0]
assert first[0] == follow[0]
#


class ParseTreeNode:
    def __init__(self, label):
        self.label = label
        self.children = []
        self.unexpected_eof = False
    def add_child(self, child):
        self.children.append(child)

class ParserToken:
    def __init__(self, line, index, str, ty) -> None:
        self.line = line
        self.index = index
        self.str = str
        self.ty = ty

def evaluateExpansion(id):
    return grammar[id-1][1:]

input_lines = open("input.txt", "r", encoding="utf-8", errors="ignore").readlines()
current_idx = 0
current_line_no = 0
line_tokens_dict = {}

def getToken():
    global current_idx
    global current_line_no
    token, next_idx, next_line_no, token_type = Scanner.get_next_token(input_lines, current_idx, current_line_no)
    tok = ParserToken(current_line_no,current_idx,token, token_type)
    current_idx = next_idx
    current_line_no = next_line_no
    return tok


with open('syntax_error.txt', 'w'): pass
def synError(msg: str):
    with open('syntax_error.txt', 'a') as f:
        f.write(msg)


def parse():
    root_node = ParseTreeNode('Program')
    stack = [root_node]
    node_stack = [root_node]
    token = getToken()
    while True:
        if not stack:
            while token.ty != None:
                synError(f"#{current_line_no + 1} : syntax error, illegal {token.ty}\n")
                token = getToken()
            break
        tktmap = tmap[token.ty]
        r = 0
        if (token.ty == None):
            # Check if all nonterminals in stack can go to epsilon
            all_epsilon = True
            temp_stack = stack.copy()
            for s in temp_stack:
                label = s.label if isinstance(s, ParseTreeNode) else s
                if label in ntmap:
                    nt_idx = ntmap[label]
                    can_epsilon = False
                    for rid in ntrows[nt_idx]:
                        prod = grammar[rid][1:]
                        if (len(prod) == 1 and prod[0] == 'epsilon') or len(prod) == 0:
                            can_epsilon = True
                            break
                    if not can_epsilon:
                        all_epsilon = False
                        break
                else:
                    # If it's a terminal, can't go to epsilon
                    all_epsilon = False
                    break
            if all_epsilon:
                # Only change all nonterminals to epsilons if all can be changed
                while stack:
                    label = stack[-1].label if isinstance(stack[-1], ParseTreeNode) else stack[-1]
                    if label in ntmap:
                        parent = stack.pop()
                        parent_node = node_stack.pop()
                        epsilon_node = ParseTreeNode('epsilon')
                        parent_node.add_child(epsilon_node)
                    else:
                        break
            else:
                # Do not change any nonterminals
                synError(f"#{current_line_no + 1} : syntax error, Unexpected EOF\n")
                root_node.unexpected_eof = True
            break

        top = stack[-1].label if isinstance(stack[-1], ParseTreeNode) else stack[-1]
        if (top in ntmap):
            top_idx = ntmap[top]
            for r in ntrows[top_idx]:
                if predict[r + 1][tktmap] == '+':
                    break
            if predict[r + 1][tktmap] == '+':
                replacement = grammar[r][1:]
                parent = stack.pop()
                parent_node = node_stack.pop()
                # If the production is epsilon (either ['epsilon'] or []), add an 'epsilon' node
                if (len(replacement) == 1 and replacement[0] == 'epsilon') or len(replacement) == 0:
                    epsilon_node = ParseTreeNode('epsilon')
                    parent_node.add_child(epsilon_node)
                else:
                    # Add children nodes for this expansion
                    children_nodes = [ParseTreeNode(sym) for sym in replacement]
                    for child in children_nodes:
                        parent_node.add_child(child)
                    for child in reversed(children_nodes):
                        stack.append(child)
                        node_stack.append(child)
            else:
                if follow[top_idx+1][tktmap] == '+':
                    synError(f"#{current_line_no + 1} : syntax error, missing {follow[top_idx+1][0]}\n")
                    # Remove: do not add missing node to the tree
                    parent = stack.pop()
                    parent_node = node_stack.pop()
                else:
                    if token.ty == None:
                        synError(f"#{current_line_no + 1} : syntax error, Unexpected EOF\n")
                        # Insert an error node and break
                        parent = stack.pop()
                        parent_node = node_stack.pop()
                        error_node = ParseTreeNode("Unexpected EOF")
                        root_node.unexpected_eof = True
                        parent_node.add_child(error_node)
                        # Any remaining nonterminals go to epsilon
                        while len(stack) > 0:
                            parent = stack.pop()
                            parent_node = node_stack.pop()
                            epsilon_node = ParseTreeNode('epsilon')
                            parent_node.add_child(epsilon_node)
                        break
                    synError(f"#{current_line_no + 1} : syntax error, illegal {token.ty}\n")
                    # Do not add illegal node to the parse tree, just skip the token
                    token = getToken()
        else:
            if top == token.ty:
                # Output terminal
                parent = stack.pop()
                parent_node = node_stack.pop()
                if Scanner.is_Keyword(token.str):
                    parent_node.label = f'(KEYWORD, {token.str})'
                elif Scanner.is_Symbol(token.str):
                    parent_node.label = f'(SYMBOL, {token.str})'
                else:
                    parent_node.label = f'({token.ty}, {token.str})'
                token = getToken()
            else:
                synError(f"#{current_line_no + 1} : syntax error, missing {top}\n")
                # Remove: do not add missing node to the tree
                parent = stack.pop()
                parent_node = node_stack.pop()
    # If no errors write no errors in the file
    if open('syntax_error.txt', 'r').read() == '':
        with open('syntax_error.txt', 'w') as f:
            f.write("No syntax errors found.\n")
    return root_node


def is_nonterminal(label):
    return label in ntmap
# Recursively print the tree with ASCII art to a list of lines
def print_parse_tree(node, prefix="", is_last=True, ancestors_last=None, output_lines=None):
    if output_lines is None:
        output_lines = []
    if ancestors_last is None:
        ancestors_last = []
    # First, recursively process children and collect their lines
    # Recursively process children and collect their lines
    child_lines = []
    for child in node.children:
        lines = print_parse_tree(child, prefix, True, ancestors_last, [])
        if lines:
            child_lines.append((child, lines))

    # Remove children who have no child (unless token/epsilon/$)
    filtered_children = []
    for child, lines in child_lines:
        if len(child.children) == 0 and not (child.label.startswith('(') or child.label in ['epsilon', '$']):
            continue
        filtered_children.append((child, lines))

    if len(filtered_children) == 0 and not (node.label.startswith('(') or node.label in ['epsilon', '$']):
        return output_lines

    # Build this node's line
    line = ""
    for is_ancestor_last in ancestors_last[:-1]:
        line += "│   " if not is_ancestor_last else "    "
    if ancestors_last:
        line += "└── " if ancestors_last[-1] else "├── "
    line += node.label
    output_lines.append(line)

    n = len(filtered_children)
    for i, (child, lines) in enumerate(filtered_children):
        is_last_child = (i == n - 1)
        for j, cline in enumerate(lines):
            child_prefix = ""
            for is_ancestor_last in ancestors_last:
                child_prefix += "│   " if not is_ancestor_last else "    "
            if j == 0:
                child_prefix += "└── " if is_last_child else "├── "
            else:
                child_prefix += "│   " if not is_last_child else "    "
            output_lines.append(child_prefix + cline)
    return output_lines

def save_parse_tree():
    root = parse()
    if not root.unexpected_eof:
        root.add_child(ParseTreeNode('$'))
    if root:
        lines = print_parse_tree(root, prefix="", is_last=True)
        # Remove the first connector for the root
        if lines:
            lines[0] = lines[0].replace("└── ", "", 1)
        with open('parse_tree.txt', 'w', encoding='utf-8') as f:
            for line in lines:
                f.write(line + '\n')

save_parse_tree()
