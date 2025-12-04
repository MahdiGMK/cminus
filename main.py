from io import BufferedReader, TextIOWrapper
from warnings import simplefilter

def is_WhiteSpace(ch: str) -> bool:
    return len(ch) == 1 and ch in " \t\n\r\v\f"


def is_Symbol(ch: str) -> bool:
    return (len(ch) == 1 and ch in ";:,[](){}+-*/=<>") or ch == "=="

def is_Keyword(s: str) -> bool:
    keywords = ["if", "else", "void", "int", "for", "break", "return"]
    return s in keywords

if __name__ == "__main__":
    # Open file
    tokens = []
    symbol_table = ["if", "else", "void", "int", "for", "break", "return"]
    with open("input.txt", "r", encoding="utf-8", errors="ignore") as f:
        lineno = 0
        multiple_line_comment_open = False
        for line in f:
            line_tokens = []
            lineno += 1
            current_token_start = 0
            line_length = len(line)
            current_line_comment_open = False
            current_token_possible_ID = False
            current_token_possible_NUM = False
            idx = -1
            while idx + 1 < line_length:
                idx = idx + 1

                if idx + 1 < line_length:
                    look_ahead = line[idx + 1]
                else:
                    look_ahead = '\n'

                #comment handling
                if multiple_line_comment_open:
                    if (line[idx] != '*' or line[idx + 1] != '/'):
                        continue
                    multiple_line_comment_open = False
                    current_token_start = idx + 2
                    idx += 1
                    continue

                if idx == current_token_start:
                    if line[idx] == '/' and look_ahead == '/':
                        current_line_comment_open = True
                        break
                    if line[idx] == '/' and look_ahead == '*':
                        multiple_line_comment_open = True
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

        
