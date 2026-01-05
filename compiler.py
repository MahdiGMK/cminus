# Mahdi Bahramian
# 401171593
# Radin Jarireh
# 402111142


def is_WhiteSpace(ch: str) -> bool:
    return len(ch) == 1 and ch in " \t\n\r\v\f"


def is_Symbol(ch: str) -> bool:
    return (len(ch) == 1 and ch in ";:,[](){}+-*/=<") or ch == "=="

def is_Keyword(s: str) -> bool:
    keywords = ["if", "else", "void", "int", "for", "break", "return"]
    return s in keywords

def token_Start_Checker(ch: str, look_ahead="") -> str:
    if ch.isalpha() or ch == '_':
        return "ID"
    if ch.isdigit():
        return "NUM"
    if is_Symbol(ch):
        return "SYMBOL"
    if is_WhiteSpace(ch):
        return "WHITESPACE"
    if ch == "/" and look_ahead == "/":
        return "LINE_COMMENT"
    if ch == "/" and look_ahead == "*":
        return "MULTI_LINE_COMMENT"
    return "UNKNOWN"

class Scanner:
    @staticmethod
    def get_next_token(input: list, start_idx: int, start_line_no: int):
        line_no = start_line_no
        multiple_line_comment_open = None
        multiple_line_comment_string = ""

        symbol_table = ["if", "else", "void", "int", "for", "break", "return"]

        idx = 0
        while (line_no < len(input)):
            line = input[line_no]

            idx = start_idx - 1 if line_no == start_line_no else -1
            current_token_start = idx + 1
            current_token_possible_ID = False
            current_token_possible_NUM = False
            current_active_error = None

            while idx < len(line):
                idx += 1
                # If idx moved past end, stop this line loop to avoid indexing errors
                if idx >= len(line):
                    break

                if idx + 1 < len(line):
                    look_ahead = line[idx + 1]
                else:
                    look_ahead = '\n'
                # Comment handling
                if multiple_line_comment_open != None:
                    if (line[idx] != '*' or look_ahead != '/'):
                        multiple_line_comment_string += line[idx]
                        continue
                    multiple_line_comment_open = None
                    multiple_line_comment_string = ""
                    idx += 1
                    current_token_start = idx + 2
                    continue

                if idx == current_token_start:
                    if token_Start_Checker(line[idx], look_ahead) == "UNKNOWN":
                        if current_active_error is None:
                            current_active_error = {
                                "line": line_no,
                                "start_idx": idx,
                                "type": "Illegal character"
                            }
                        current_token_start += 1
                        continue

                    if line[idx] == '*' and look_ahead == '/':
                        # with open("lexical_errors.txt", "a", encoding="utf-8", errors="ignore") as error_file:
                        #     error_file.write(f"{line_no}.\t(*/, Stray closing comment)\n")

                        current_token_start += 2
                        idx += 1
                        continue

                    if current_active_error is not None:
                        current_active_error["string"] = line[current_active_error["start_idx"]:idx]
                        # with open("lexical_errors.txt", "a", encoding="utf-8", errors="ignore") as error_file:
                        #     error_file.write(f"{current_active_error['line']}.\t({current_active_error['string']}, {current_active_error['type']})\n")
                        current_active_error = None

                    if line[idx] == '/' and look_ahead == '/':
                        break
                    if line[idx] == '/' and look_ahead == '*':
                        multiple_line_comment_open = line_no
                        current_token_start = idx + 2
                        idx += 1
                        continue

                    if is_WhiteSpace(line[idx]):
                        current_token_start += 1
                        continue

                    if idx + 1 < len(line) and is_Symbol(line[idx:idx + 2]):
                        return line[idx:idx + 2], idx + 2, line_no, line[idx:idx + 2]
                    1
                    if is_Symbol(line[idx]):
                        return line[idx], idx + 1, line_no, line[idx]

                    if line[idx].isalpha() or line[idx] == '_':
                        current_token_possible_ID = True
                        continue
                    if line[idx].isdigit():
                        current_token_possible_NUM = True
                        continue
                else:
                    if current_token_possible_ID:
                        if line[idx].isalnum() or line[idx] == '_':
                            continue
                        else:
                            if token_Start_Checker(line[idx]) == "UNKNOWN":
                                while idx < len(line) and (token_Start_Checker(line[idx]) == "UNKNOWN" or token_Start_Checker(line[idx]) == "ID"):
                                    idx += 1
                                # with open("lexical_errors.txt", "a", encoding="utf-8", errors="ignore") as error_file:
                                #     error_file.write(f"{line_no}.\t({line[current_token_start:idx]}, Illegal character)\n")
                                current_token_start = idx
                                current_token_possible_ID = False
                                idx -= 1
                                continue

                            token = line[current_token_start:idx]
                            if is_Keyword(token):
                                return token, idx, line_no, token
                            else:
                                if token not in symbol_table:
                                    symbol_table.append(token)
                                return token, idx, line_no, "ID"

                    if current_token_possible_NUM:
                        if line[idx].isdigit():
                            continue
                        else:
                            if token_Start_Checker(line[idx]) == "UNKNOWN" or token_Start_Checker(line[idx]) == "ID":
                                while idx < len(line) and (token_Start_Checker(line[idx]) == "UNKNOWN" or token_Start_Checker(line[idx]) == "ID" or token_Start_Checker(line[idx]) == "NUM"):
                                    idx += 1
                                # with open("lexical_errors.txt", "a", encoding="utf-8", errors="ignore") as error_file:
                                #     error_file.write(f"{line_no}.\t({line[current_token_start:idx]}, Malformed number)\n")
                                current_token_start = idx
                                current_token_possible_NUM = False
                                idx -= 1
                                continue
                            if line[current_token_start] == '0' and idx - current_token_start > 1:
                                # with open("lexical_errors.txt", "a", encoding="utf-8", errors="ignore") as error_file:
                                #     error_file.write(f"{line_no}.\t({line[current_token_start:idx]}, Malformed number)\n")
                                current_token_start = idx
                                current_token_possible_NUM = False
                                idx -= 1
                                continue
                            token = line[current_token_start:idx]
                            return token, idx, line_no, "NUM"

            if current_token_possible_ID:
                token = line[current_token_start:len(line)]
                if is_Keyword(token):
                    return token, 0, line_no + 1, token
                else:
                    if token not in symbol_table:
                        symbol_table.append(token)
                    return token, 0, line_no + 1, "ID"
            elif current_token_possible_NUM:
                token = line[current_token_start:len(line)]
                return token, 0, line_no + 1, "NUM"

            if multiple_line_comment_open != None:
                multiple_line_comment_string += "\n"
            line_no += 1
            start_idx = 0

        if multiple_line_comment_open != None:
            error = {
                "line": multiple_line_comment_open,
                "start_idx": None,
                "string": "/*" + multiple_line_comment_string,
                "type": "Open comment at EOF"
            }
            if len(multiple_line_comment_string) > 8:
                error["string"] = "/*" + multiple_line_comment_string[:7] + "..."
            # with open("lexical_errors.txt", "a", encoding="utf-8", errors="ignore") as error_file:
            #     error_file.write(f"{error['line']}.\t({error['string']}, {error['type']})\n")
        return None, idx, line_no, None


#

import csv

FIRST_FILE = """
	ID	[	NUM	]	;	(	)	int	void	,	{	}	break	if	else	for	return	=	==	<	+	-	*	/	ε
Program	−	−	−	−	−	−	−	+	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+
Declaration-list	−	−	−	−	−	−	−	+	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+
Declaration	−	−	−	−	−	−	−	+	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
Declaration-initial	−	−	−	−	−	−	−	+	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
Declaration-prime	−	+	−	−	+	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
Var-declaration-prime	−	+	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
Fun-declaration-prime	−	−	−	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
Type-specifier	−	−	−	−	−	−	−	+	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
Params	−	−	−	−	−	−	−	+	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
Param-list	−	−	−	−	−	−	−	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+
Param	−	−	−	−	−	−	−	+	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
Param-prime	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+
Compound-stmt	−	−	−	−	−	−	−	−	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−
Statement-list	+	−	+	−	+	+	−	−	−	−	+	−	+	+	−	+	+	−	−	−	+	+	−	−	+
Statement	+	−	+	−	+	+	−	−	−	−	+	−	+	+	−	+	+	−	−	−	+	+	−	−	−
Expression-stmt	+	−	+	−	+	+	−	−	−	−	−	−	+	−	−	−	−	−	−	−	+	+	−	−	−
Selection-stmt	−	−	−	−	−	−	−	−	−	−	−	−	−	+	−	−	−	−	−	−	−	−	−	−	−
Else-stmt	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	−	−	−	−	−	−	−	−	−	+
Iteration-stmt	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	−	−	−	−	−	−	−	−	−
Return-stmt	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	−	−	−	−	−	−	−	−
Return-stmt-prime	+	−	+	−	+	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	+	−	−	−
Expression	+	−	+	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	+	−	−	−
B	−	+	−	−	−	+	−	−	−	−	−	−	−	−	−	−	−	+	+	+	+	+	+	+	+
H	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	+	+	+	+	+	+	+
Simple-expression-zegond	−	−	+	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	+	−	−	−
Simple-expression-prime	−	−	−	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	+	+	+	+	+	+	+
C	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	+	−	−	−	−	+
Relop	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	+	−	−	−	−	−
Additive-expression	+	−	+	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	+	−	−	−
Additive-expression-prime	−	−	−	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	+	+	+	+
Additive-expression-zegond	−	−	+	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	+	−	−	−
D	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	+	−	−	+
Addop	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	+	−	−	−
Term	+	−	+	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	+	−	−	−
Term-prime	−	−	−	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	+	+
Term-zegond	−	−	+	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	+	−	−	−
G	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	+	+
Signed-factor	+	−	+	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	+	−	−	−
Signed-factor-zegond	−	−	+	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	+	−	−	−
Factor	+	−	+	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
Var-call-prime	−	+	−	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+
Var-prime	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+
Factor-prime	−	−	−	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+
Factor-zegond	−	−	+	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
Args	+	−	+	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	+	−	−	+
Arg-list	+	−	+	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	+	−	−	−
Arg-list-prime	−	−	−	−	−	−	−	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+"""
FOLLOW_FILE = """
	ID	[	NUM	]	;	(	)	int	void	,	{	}	break	if	else	for	return	=	==	<	+	-	*	/	┤
Program	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+
Declaration-list	+	−	+	−	+	+	−	−	−	−	+	+	+	+	−	+	+	−	−	−	+	+	−	−	+
Declaration	+	−	+	−	+	+	−	+	+	−	+	+	+	+	−	+	+	−	−	−	+	+	−	−	+
Declaration-initial	−	+	−	−	+	+	+	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
Declaration-prime	+	−	+	−	+	+	−	+	+	−	+	+	+	+	−	+	+	−	−	−	+	+	−	−	+
Var-declaration-prime	+	−	+	−	+	+	−	+	+	−	+	+	+	+	−	+	+	−	−	−	+	+	−	−	+
Fun-declaration-prime	+	−	+	−	+	+	−	+	+	−	+	+	+	+	−	+	+	−	−	−	+	+	−	−	+
Type-specifier	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
Params	−	−	−	−	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
Param-list	−	−	−	−	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
Param	−	−	−	−	−	−	+	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
Param-prime	−	−	−	−	−	−	+	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
Compound-stmt	+	−	+	−	+	+	−	+	+	−	+	+	+	+	+	+	+	−	−	−	+	+	−	−	+
Statement-list	−	−	−	−	−	−	−	−	−	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−
Statement	+	−	+	−	+	+	−	−	−	−	+	+	+	+	+	+	+	−	−	−	+	+	−	−	−
Expression-stmt	+	−	+	−	+	+	−	−	−	−	+	+	+	+	+	+	+	−	−	−	+	+	−	−	−
Selection-stmt	+	−	+	−	+	+	−	−	−	−	+	+	+	+	+	+	+	−	−	−	+	+	−	−	−
Else-stmt	+	−	+	−	+	+	−	−	−	−	+	+	+	+	+	+	+	−	−	−	+	+	−	−	−
Iteration-stmt	+	−	+	−	+	+	−	−	−	−	+	+	+	+	+	+	+	−	−	−	+	+	−	−	−
Return-stmt	+	−	+	−	+	+	−	−	−	−	+	+	+	+	+	+	+	−	−	−	+	+	−	−	−
Return-stmt-prime	+	−	+	−	+	+	−	−	−	−	+	+	+	+	+	+	+	−	−	−	+	+	−	−	−
Expression	−	−	−	+	+	−	+	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
B	−	−	−	+	+	−	+	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
H	−	−	−	+	+	−	+	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
Simple-expression-zegond	−	−	−	+	+	−	+	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
Simple-expression-prime	−	−	−	+	+	−	+	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
C	−	−	−	+	+	−	+	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
Relop	+	−	+	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	+	−	−	−
Additive-expression	−	−	−	+	+	−	+	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
Additive-expression-prime	−	−	−	+	+	−	+	−	−	+	−	−	−	−	−	−	−	−	+	+	−	−	−	−	−
Additive-expression-zegond	−	−	−	+	+	−	+	−	−	+	−	−	−	−	−	−	−	−	+	+	−	−	−	−	−
D	−	−	−	+	+	−	+	−	−	+	−	−	−	−	−	−	−	−	+	+	−	−	−	−	−
Addop	+	−	+	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	+	−	−	−
Term	−	−	−	+	+	−	+	−	−	+	−	−	−	−	−	−	−	−	+	+	+	+	−	−	−
Term-prime	−	−	−	+	+	−	+	−	−	+	−	−	−	−	−	−	−	−	+	+	+	+	−	−	−
Term-zegond	−	−	−	+	+	−	+	−	−	+	−	−	−	−	−	−	−	−	+	+	+	+	−	−	−
G	−	−	−	+	+	−	+	−	−	+	−	−	−	−	−	−	−	−	+	+	+	+	−	−	−
Signed-factor	−	−	−	+	+	−	+	−	−	+	−	−	−	−	−	−	−	−	+	+	+	+	+	+	−
Signed-factor-zegond	−	−	−	+	+	−	+	−	−	+	−	−	−	−	−	−	−	−	+	+	+	+	+	+	−
Factor	−	−	−	+	+	−	+	−	−	+	−	−	−	−	−	−	−	−	+	+	+	+	+	+	−
Var-call-prime	−	−	−	+	+	−	+	−	−	+	−	−	−	−	−	−	−	−	+	+	+	+	+	+	−
Var-prime	−	−	−	+	+	−	+	−	−	+	−	−	−	−	−	−	−	−	+	+	+	+	+	+	−
Factor-prime	−	−	−	+	+	−	+	−	−	+	−	−	−	−	−	−	−	−	+	+	+	+	+	+	−
Factor-zegond	−	−	−	+	+	−	+	−	−	+	−	−	−	−	−	−	−	−	+	+	+	+	+	+	−
Args	−	−	−	−	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
Arg-list	−	−	−	−	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
Arg-list-prime	−	−	−	−	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−"""
PREDICT_FILE = """
	ID	[	NUM	]	;	(	)	int	void	,	{	}	break	if	else	for	return	=	==	<	+	-	*	/	┤
1	−	−	−	−	−	−	−	+	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+
2	−	−	−	−	−	−	−	+	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
3	+	−	+	−	+	+	−	−	−	−	+	+	+	+	−	+	+	−	−	−	+	+	−	−	+
4	−	−	−	−	−	−	−	+	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
5	−	−	−	−	−	−	−	+	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
6	−	−	−	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
7	−	+	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
8	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
9	−	−	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
10	−	−	−	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
11	−	−	−	−	−	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
12	−	−	−	−	−	−	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
13	−	−	−	−	−	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
14	−	−	−	−	−	−	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
15	−	−	−	−	−	−	−	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
16	−	−	−	−	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
17	−	−	−	−	−	−	−	+	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
18	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
19	−	−	−	−	−	−	+	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
20	−	−	−	−	−	−	−	−	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−
21	+	−	+	−	+	+	−	−	−	−	+	−	+	+	−	+	+	−	−	−	+	+	−	−	−
22	−	−	−	−	−	−	−	−	−	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−
23	+	−	+	−	+	+	−	−	−	−	−	−	+	−	−	−	−	−	−	−	+	+	−	−	−
24	−	−	−	−	−	−	−	−	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−
25	−	−	−	−	−	−	−	−	−	−	−	−	−	+	−	−	−	−	−	−	−	−	−	−	−
26	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	−	−	−	−	−	−	−	−	−
27	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	−	−	−	−	−	−	−	−
28	+	−	+	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	+	−	−	−
29	−	−	−	−	−	−	−	−	−	−	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−
30	−	−	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
31	−	−	−	−	−	−	−	−	−	−	−	−	−	+	−	−	−	−	−	−	−	−	−	−	−
32	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	−	−	−	−	−	−	−	−	−	−
33	+	−	+	−	+	+	−	−	−	−	+	+	+	+	+	+	+	−	−	−	+	+	−	−	−
34	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	−	−	−	−	−	−	−	−	−
35	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	−	−	−	−	−	−	−	−
36	+	−	+	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	+	−	−	−
37	−	−	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
38	−	−	+	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	+	−	−	−
39	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
40	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	−	−	−	−	−	−	−
41	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
42	−	−	−	+	+	+	+	−	−	+	−	−	−	−	−	−	−	−	+	+	+	+	+	+	−
43	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	−	−	−	−	−	−	−
44	−	−	−	+	+	−	+	−	−	+	−	−	−	−	−	−	−	−	+	+	+	+	+	+	−
45	−	−	+	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	+	−	−	−
46	−	−	−	+	+	+	+	−	−	+	−	−	−	−	−	−	−	−	+	+	+	+	+	+	−
47	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	+	−	−	−	−	−
48	−	−	−	+	+	−	+	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
49	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	−	−	−	−	−	−
50	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	−	−	−	−	−
51	+	−	+	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	+	−	−	−
52	−	−	−	+	+	+	+	−	−	+	−	−	−	−	−	−	−	−	+	+	+	+	+	+	−
53	−	−	+	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	+	−	−	−
54	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	+	−	−	−
55	−	−	−	+	+	−	+	−	−	+	−	−	−	−	−	−	−	−	+	+	−	−	−	−	−
56	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	−	−	−	−
57	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	−	−	−
58	+	−	+	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	+	−	−	−
59	−	−	−	+	+	+	+	−	−	+	−	−	−	−	−	−	−	−	+	+	+	+	+	+	−
60	−	−	+	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	+	−	−	−
61	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	−	−
62	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	−
63	−	−	−	+	+	−	+	−	−	+	−	−	−	−	−	−	−	−	+	+	+	+	−	−	−
64	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	−	−	−	−
65	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	−	−	−
66	+	−	+	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
67	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	−	−	−	−
68	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	−	−	−
69	−	−	+	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
70	−	−	−	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
71	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
72	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
73	−	−	−	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
74	−	+	−	+	+	−	+	−	−	+	−	−	−	−	−	−	−	−	+	+	+	+	+	+	−
75	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
76	−	−	−	+	+	−	+	−	−	+	−	−	−	−	−	−	−	−	+	+	+	+	+	+	−
77	−	−	−	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
78	−	−	−	+	+	−	+	−	−	+	−	−	−	−	−	−	−	−	+	+	+	+	+	+	−
79	−	−	−	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
80	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
81	+	−	+	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	+	−	−	−
82	−	−	−	−	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
83	+	−	+	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	+	+	−	−	−
84	−	−	−	−	−	−	−	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−
85	−	−	−	−	−	−	+	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−	−"""
GRAMMAR_FILE = """
Program   Declaration-list
Declaration-list   Declaration Declaration-list
Declaration-list
Declaration   Declaration-initial Declaration-prime
Declaration-initial   Type-specifier ID
Declaration-prime   Fun-declaration-prime
Declaration-prime   Var-declaration-prime
Var-declaration-prime   [ NUM ] ;
Var-declaration-prime   ;
Fun-declaration-prime   ( Params ) Compound-stmt
Type-specifier   int
Type-specifier   void
Params   int ID Param-prime Param-list
Params   void
Param-list   , Param Param-list
Param-list
Param   Declaration-initial Param-prime
Param-prime   [  ]
Param-prime
Compound-stmt   { Declaration-list Statement-list }
Statement-list   Statement Statement-list
Statement-list
Statement   Expression-stmt
Statement   Compound-stmt
Statement   Selection-stmt
Statement   Iteration-stmt
Statement   Return-stmt
Expression-stmt   Expression ;
Expression-stmt   break ;
Expression-stmt   ;
Selection-stmt   if ( Expression ) Statement Else-stmt
Else-stmt   else Statement
Else-stmt
Iteration-stmt   for ( Expression ;  Expression ;  Expression ) Compound-stmt
Return-stmt   return Return-stmt-prime
Return-stmt-prime   Expression ;
Return-stmt-prime   ;
Expression   Simple-expression-zegond
Expression   ID B
B   = Expression
B   [ Expression ] H
B   Simple-expression-prime
H   = Expression
H   G D C
Simple-expression-zegond   Additive-expression-zegond C
Simple-expression-prime   Additive-expression-prime C
C   Relop Additive-expression
C
Relop   ==
Relop   <
Additive-expression   Term D
Additive-expression-prime   Term-prime D
Additive-expression-zegond   Term-zegond D
D   Addop Term D
D
Addop   +
Addop   -
Term   Signed-factor G
Term-prime   Factor-prime G
Term-zegond   Signed-factor-zegond G
G   * Signed-factor G
G   / Signed-factor G
G
Signed-factor   + Factor
Signed-factor   - Factor
Signed-factor   Factor
Signed-factor-zegond   + Factor
Signed-factor-zegond   - Factor
Signed-factor-zegond   Factor-zegond
Factor   ( Expression )
Factor   ID Var-call-prime
Factor   NUM
Var-call-prime   ( Args )
Var-call-prime   Var-prime
Var-prime   [ Expression ]
Var-prime
Factor-prime   ( Args )
Factor-prime
Factor-zegond   ( Expression )
Factor-zegond   NUM
Args   Arg-list
Args
Arg-list   Expression Arg-list-prime
Arg-list-prime   , Expression Arg-list-prime
Arg-list-prime"""



first = [x for x in csv.reader(FIRST_FILE.split(sep='\n')[1:], delimiter='\t')]
follow = [x for x in csv.reader(FOLLOW_FILE.split(sep='\n')[1:], delimiter='\t')]
predict = [x for x in csv.reader(PREDICT_FILE.split(sep='\n')[1:], delimiter='\t')]
grammar = [x.split() for x in GRAMMAR_FILE.split(sep='\n')[1:]]
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


with open('syntax_errors.txt', 'w'): pass
errctr = 0
def synError(msg: str):
    global errctr
    with open('syntax_errors.txt', 'a') as f:
        if errctr == 0:
            f.write(msg)
        else:
            f.write('\n' + msg)
    errctr += 1


def parse():
    root_node = ParseTreeNode('Program')
    stack = [root_node]
    node_stack = [root_node]
    token = getToken()
    while True:
        if not stack:
            while token.ty != None:
                synError(f"#{current_line_no + 1} : syntax error, illegal {token.ty}")
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
                synError(f"#{current_line_no + 1} : syntax error, Unexpected EOF")
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
                    synError(f"#{current_line_no + 1} : syntax error, missing {follow[top_idx+1][0]}")
                    # Remove: do not add missing node to the tree
                    parent = stack.pop()
                    parent_node = node_stack.pop()
                else:
                    if token.ty == None:
                        synError(f"#{current_line_no + 1} : syntax error, Unexpected EOF")
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
                    synError(f"#{current_line_no + 1} : syntax error, illegal {token.ty}")
                    # Do not add illegal node to the parse tree, just skip the token
                    token = getToken()
        else:
            if top == token.ty:
                # Output terminal
                parent = stack.pop()
                parent_node = node_stack.pop()
                if is_Keyword(token.str):
                    parent_node.label = f'(KEYWORD, {token.str})'
                elif is_Symbol(token.str):
                    parent_node.label = f'(SYMBOL, {token.str})'
                else:
                    parent_node.label = f'({token.ty}, {token.str})'
                token = getToken()
            else:
                synError(f"#{current_line_no + 1} : syntax error, missing {top}")
                # Remove: do not add missing node to the tree
                parent = stack.pop()
                parent_node = node_stack.pop()
    # If no errors write no errors in the file
    if open('syntax_errors.txt', 'r').read() == '':
        with open('syntax_errors.txt', 'w') as f:
            f.write("No syntax errors found.")
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
            for i in range(len(lines)):
                line = lines[i]
                if i == 0:
                    f.write(line)
                else:
                    f.write('\n' + line)

save_parse_tree()
