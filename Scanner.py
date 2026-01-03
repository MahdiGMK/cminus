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

def get_next_token(input: list, start_idx: int, start_line_no: int):
    line_no = start_line_no
    multiple_line_comment_open = None
    multiple_line_comment_string = ""

    symbol_table = ["if", "else", "void", "int", "for", "break", "return"]

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
                    with open("lexical_errors.txt", "a", encoding="utf-8", errors="ignore") as error_file:
                        error_file.write(f"{line_no}.\t(*/, Stray closing comment)\n")

                    current_token_start += 2
                    idx += 1
                    continue

                if current_active_error is not None:
                    current_active_error["string"] = line[current_active_error["start_idx"]:idx]
                    with open("lexical_errors.txt", "a", encoding="utf-8", errors="ignore") as error_file:
                        error_file.write(f"{current_active_error['line']}.\t({current_active_error['string']}, {current_active_error['type']})\n")
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
                            with open("lexical_errors.txt", "a", encoding="utf-8", errors="ignore") as error_file:
                                error_file.write(f"{line_no}.\t({line[current_token_start:idx]}, Illegal character)\n")
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
                            with open("lexical_errors.txt", "a", encoding="utf-8", errors="ignore") as error_file:
                                error_file.write(f"{line_no}.\t({line[current_token_start:idx]}, Malformed number)\n")
                            current_token_start = idx
                            current_token_possible_NUM = False
                            idx -= 1
                            continue
                        if line[current_token_start] == '0' and idx - current_token_start > 1:
                            with open("lexical_errors.txt", "a", encoding="utf-8", errors="ignore") as error_file:
                                error_file.write(f"{line_no}.\t({line[current_token_start:idx]}, Malformed number)\n")
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
        with open("lexical_errors.txt", "a", encoding="utf-8", errors="ignore") as error_file:
            error_file.write(f"{error['line']}.\t({error['string']}, {error['type']})\n")
    return None, idx, line_no, None

if __name__ == "__main__":
    tokens = []
    symbol_table = ["if", "else", "void", "int", "for", "break", "return"]
    error_count = 0

    # Clear the lexical_errors.txt file
    with open("lexical_errors.txt", "w", encoding="utf-8", errors="ignore") as error_file:
        pass

    # Read all input lines
    with open("input.txt", "r", encoding="utf-8", errors="ignore") as f:
        input_lines = f.readlines()

    # Tokenize using get_next_token
    current_idx = 0
    current_line_no = 0
    line_tokens_dict = {}

    while True:
        token, next_idx, next_line_no, token_type = get_next_token(input_lines, current_idx, current_line_no)
                
        if token is None:
            break
        
        # Store token grouped by line number
        if next_line_no not in line_tokens_dict:
            line_tokens_dict[next_line_no] = []
        line_tokens_dict[next_line_no].append({token: token_type})
        
        current_idx = next_idx
        current_line_no = next_line_no

    # Convert to tokens list format
    for line_no in sorted(line_tokens_dict.keys()):
        tokens.append((line_no + 1, line_tokens_dict[line_no]))

    # Check if any errors were written
    with open("lexical_errors.txt", "r", encoding="utf-8", errors="ignore") as f:
        error_content = f.read()
    
    if not error_content.strip():
        with open("lexical_errors.txt", "w", encoding="utf-8", errors="ignore") as f:
            f.write("No lexical errors found.\n")

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
