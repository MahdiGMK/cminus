from io import BufferedReader, TextIOWrapper
from warnings import simplefilter

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

if __name__ == "__main__":
    tokens = []
    symbol_table = ["if", "else", "void", "int", "for", "break", "return"]
    lexical_errors = []

    with open("input.txt", "r", encoding="utf-8", errors="ignore") as f:
        lineno = 0
        multiple_line_comment_open = None
        multiple_line_comment_string = ""
        for line in f:
            line_tokens = []
            lineno += 1
            current_token_start = 0
            line_length = len(line)
            current_line_comment_open = False
            current_token_possible_ID = False
            current_token_possible_NUM = False
            current_active_error = None
            idx = -1
            while idx + 1 < line_length:
                idx = idx + 1

                if idx + 1 < line_length:
                    look_ahead = line[idx + 1]
                else:
                    look_ahead = '\n'

                #comment handling
                if multiple_line_comment_open != None:
                    if (line[idx] != '*' or line[idx + 1] != '/'):
                        multiple_line_comment_string += line[idx]
                        continue
                    multiple_line_comment_open = None
                    current_token_start = idx + 2
                    idx += 1
                    continue

                if idx == current_token_start:
                    if token_Start_Checker(line[idx], look_ahead) == "UNKNOWN":
                        if current_active_error is None:
                            current_active_error = {
                                "line": lineno,
                                "start_idx": idx,
                                "type": "Illegal character"
                            }
                        current_token_start += 1
                        continue

                    if line[idx] == '*' and look_ahead == '/':
                        lexical_errors.append({
                            "line": lineno,
                            "start_idx": idx,
                            "string": "*/",
                            "type": "Stray closing comment"
                        })
                        current_token_start += 2
                        idx += 1
                        continue

                    if current_active_error is not None:
                        current_active_error["string"] = line[current_active_error["start_idx"]:idx]
                        lexical_errors.append(current_active_error)
                        current_active_error = None
    
                    if line[idx] == '/' and look_ahead == '/':
                        current_line_comment_open = True
                        break
                    if line[idx] == '/' and look_ahead == '*':
                        multiple_line_comment_open = lineno
                        current_token_start = idx + 2
                        idx += 1
                        continue

                    if is_WhiteSpace(line[idx]):
                        current_token_start += 1
                        continue

                    if idx + 1 < line_length and is_Symbol(line[idx:idx + 2]):
                        line_tokens.append({line[idx:idx + 2]: "SYMBOL"})
                        current_token_start = idx + 2
                        idx += 1
                        continue
                    if is_Symbol(line[idx]):
                        line_tokens.append({line[idx]: "SYMBOL"})
                        current_token_start = idx + 1
                        continue

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
                                while idx < line_length and (token_Start_Checker(line[idx]) == "UNKNOWN" or token_Start_Checker(line[idx]) == "ID"):
                                    idx += 1
                                lexical_errors.append({
                                    "line": lineno,
                                    "start_idx": current_token_start,
                                    "type": "Illegal character",
                                    "string": line[current_token_start:idx]
                                })
                                current_token_start = idx
                                current_token_possible_ID = False
                                idx -= 1
                                continue
                                    
                            token = line[current_token_start:idx]
                            if is_Keyword(token):
                                line_tokens.append({token: "KEYWORD"})
                            else:
                                line_tokens.append({token: "ID"})
                                if token not in symbol_table:
                                    symbol_table.append(token)
                            current_token_start = idx
                            current_token_possible_ID = False
                            idx -= 1
                            continue

                    if current_token_possible_NUM:
                        if line[idx].isdigit():
                            continue
                        else:
                            if token_Start_Checker(line[idx]) == "UNKNOWN" or token_Start_Checker(line[idx]) == "ID":
                                while idx < line_length and (token_Start_Checker(line[idx]) == "UNKNOWN" or token_Start_Checker(line[idx]) == "ID" or token_Start_Checker(line[idx]) == "NUM"):
                                    idx += 1
                                lexical_errors.append({
                                    "line": lineno,
                                    "start_idx": current_token_start,
                                    "type": "Malformed number",
                                    "string": line[current_token_start:idx]
                                })
                                current_token_start = idx
                                current_token_possible_NUM = False
                                idx -= 1
                                continue
                            if line[current_token_start] == '0' and idx - current_token_start > 1:
                                lexical_errors.append({
                                    "line": lineno,
                                    "start_idx": current_token_start,
                                    "type": "Malformed number",
                                    "string": line[current_token_start:idx]
                                })
                                current_token_start = idx
                                current_token_possible_NUM = False
                                idx -= 1
                                continue
                            token = line[current_token_start:idx]
                            line_tokens.append({token: "NUM"})
                            current_token_start = idx
                            current_token_possible_NUM = False
                            idx -= 1
                            continue

            if current_token_possible_ID:
                token = line[current_token_start:line_length]
                if is_Keyword(token):
                    line_tokens.append({token: "KEYWORD"})
                else:
                    line_tokens.append({token: "ID"})
                    if token not in symbol_table:
                        symbol_table.append(token)

            elif current_token_possible_NUM:
                token = line[current_token_start:line_length]
                line_tokens.append({token: "NUM"})            
            tokens.append((lineno, line_tokens))

            if multiple_line_comment_open != None:
                multiple_line_comment_string += "\n"

if multiple_line_comment_open != None:
    lexical_errors.append({
        "line": multiple_line_comment_open,
        "start_idx": None,
        "string": "/*" + multiple_line_comment_string,
        "type": "Open comment at EOF"
    })
    if len(multiple_line_comment_string) > 8:
        lexical_errors[-1]["string"] = "/*" + multiple_line_comment_string[:4] + "..." 


with open("tokens.txt", "w", encoding="utf-8", errors="ignore") as f:
    for lineno, line_tokens in tokens:
        if len(line_tokens) == 0:
            continue
        f.write(f"{lineno}.\t")
        for token in line_tokens:
            for k, v in token.items():
                f.write(f"({v}, {k}) ")
        f.write("\n")

with open("symbol_table.txt", "w", encoding="utf-8", errors="ignore") as f:
    id_number = 0
    for symbol in symbol_table:
        id_number += 1
        f.write(f"{id_number}.\t{symbol}\n")

with open("lexical_errors.txt", "w", encoding="utf-8", errors="ignore") as f:
    if len(lexical_errors) == 0:
        f.write("No lexical errors found.\n")
    else:
        for error in lexical_errors:
            f.write(f"{error['line']}.\t({error['string']}, {error['type']})\n")
        
        
