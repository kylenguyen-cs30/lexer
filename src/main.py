# Name : Hoang Nguyen
# Email: Hnguyen1193@csu.fullerton.edu
# Project: Lexical Analyzer
import sys


class Lexer:
    def __init__(self):
        # define state transition table
        self.transition_table = [
            # state 1 (starting state)
            [2, 4, 6, 19, 8, 19, 19, 12, 19, 14, 17, 1, 19],
            # state 2 (In identifier)
            [2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
            # state 3 (end of identifier)
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            # state 4 (In Number)
            [5, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
            # state 5 (end of Number)
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            # state 6 (In {} comment)
            [6, 6, 6, 7, 6, 6, 6, 6, 6, 6, 6, 6, 6],
            # state 7 (end of {} comment)
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            # state 8(Found ( )
            [20, 20, 20, 20, 9, 20, 20, 20, 20, 20, 20, 20, 20],
            # state 9 (In (**) comment)
            [9, 9, 9, 9, 9, 10, 9, 9, 9, 9, 9, 9, 9],
            # state 10 (Found * in (**))
            [9, 9, 9, 9, 9, 9, 11, 9, 9, 9, 9, 9, 9],
            # state 11 (End of (**))
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            # state 12 (Found : )
            [20, 20, 20, 20, 20, 20, 20, 20, 13, 20, 20, 20, 20],
            # state 13 (Token :=)
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            # state 14 (Found <)
            [20, 20, 20, 20, 20, 20, 20, 20, 15, 20, 16, 20, 20],
            # state 15 (Token <=)
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            # state 16 (Token <>)
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            # state 17 (Found >)
            [20, 20, 20, 20, 20, 20, 20, 20, 18, 20, 20, 20, 20],
            # state 18 (Token >=)
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            # state 19 (General Punctuation)
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            # state 20 (General Punctuation)
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ]

        # define which states need backup
        self.backup_states = [3, 5, 7, 11, 20]

        # Define token types based on final states
        self.token_types = {
            3: "IDENTIFIER",
            5: "INTEGER",
            7: "COMMENT",
            11: "COMMENT",
            13: "ASSIGN_OP",
            15: "LESS_EQUAL_OP",
            16: "NOT_EQUAL_OP",
            18: "GREATER_EQUAL_OP",
            19: "SEPARATOR",
            20: "SEPARATOR",
        }

        self.token_types_mapping = {
            "IDENTIFIER": "IDENTIFIER",
            "INTEGER": "INTEGER",
            "ASSIGN_OP": "OPERATOR",
            "LESS_EQUAL_OP": "OPERATOR",
            "NOT_EQUAL_OP": "OPERATOR",
            "GREATER_EQUAL_OP": "OPERATOR",
            "SEPARATOR": "SEPARATOR",
        }

        # list of keywords
        self.keywords = ["if", "return"]

        self.position = 0

        # input starting
        self.input_string = ""

    def get_col_index(self, char):
        if char.isalpha():
            return 0
        elif char.isdigit():
            return 1
        elif char == "{":
            return 12
        elif char == "}":
            return 12
        elif char == "(":
            return 4
        elif char == "*":
            return 5
        elif char == ")":
            return 6
        elif char == ":":
            return 7
        elif char == "=":
            return 8
        elif char == "<":
            return 9
        elif char == ">":
            return 10
        elif char.isspace():
            return 11
        else:
            return 12  # Other characters

    def scanner(self, input_string):
        self.input_string = input_string
        self.position = 0
        tokens = []

        # add special handling for  // comments
        self.input_string = self.handle_line_comments(self.input_string)
        while self.position < len(self.input_string):
            token = self.get_next_token()
            if token and token["type"] != "UNKNOWN":
                tokens.append(token)

        return tokens

    def handle_line_comments(self, text):
        lines = []
        for line in text.split("\n"):
            if "//" in line:
                comment_pos = line.find("//")
                comment_text = line[comment_pos:]
                line = line[:comment_pos] + "{" + comment_text[2:] + "}"
            lines.append(line)
        return "\n".join(lines)

    def get_next_token(self):
        if self.position >= len(self.input_string):
            return None

        # skip whitespace at beginning
        while (
            self.position < len(self.input_string)
            and self.input_string[self.position].isspace()
        ):
            self.position += 1
        if self.position >= len(self.input_string):
            return None

        # start with state 1
        current_state = 1
        lexeme_start = self.position
        lexeme_end = self.position
        backup_occurred = False

        # process characres until we reach accepting state
        while self.position < len(self.input_string):
            current_char = self.input_string[self.position]
            col_idx = self.get_col_index(current_char)

            # debug before state transition
            print(
                f"Position: {self.position}, Character: '{current_char}', Col index: {col_idx}, Current State: {current_state}"
            )

            # get next state from transition_table
            next_state = self.transition_table[current_state - 1][col_idx]

            # debug after determining next state
            print(f"  -> Next State: {next_state}")

            # check if we're in a backup state
            if next_state in self.backup_states:
                lexeme_end = self.position
                backup_occurred = True
                print(f"  -> Backup state reached,setting lexeme_end to {lexeme_end}")

            # move to next state
            current_state = next_state

            # move to next characters
            self.position += 1

            # if we are back to state 1, we have found a token
            if current_state == 1:
                print(f" -> Back to state 1, token found")
                break

        # if we didn't backup and reached the end of input, set lexeme_end
        if not backup_occurred and self.position > lexeme_start:
            lexeme_end = self.position

        # get the lexeme
        lexeme = self.input_string[lexeme_start:lexeme_end].strip()
        print(f"Extracted lexeme: '{lexeme}', Current State: {current_state}")

        if not lexeme:
            # skip empty lexeme
            print(" -> Empty lexeme, skipping")
            return None

        # determine token type
        token_type = "UNKNOWN"

        # Identify token type
        if lexeme.isalpha():
            if lexeme in self.keywords:
                token_type = "KEYWORD"
                print(f" -> Identified as KEYWORD")
            else:
                token_type = "IDENTIFIER"
                print(f" -> Identified as IDENTIFIER")
        elif lexeme.isdigit():
            token_type = "INTEGER"
            print(f" -> Identified as INTEGER")
        elif lexeme in ["(", ")", "{", "}", ";"]:
            token_type = "SEPARATOR"
            print(f" -> Identified as SEPARATOR")
        elif lexeme in [">", "=", ">=", "<", "<=", "<>"]:
            token_type = "OPERATOR"
            print(f" -> Identified as OPERATOR")
        elif lexeme.startswith("{") and lexeme.endswith("}"):
            token_type = "COMMENT"
            print(f" -> Identified as COMMENT")

        print(
            f"Returning token: Type: {token_type}, Lexeme: '{lexeme}', Position: {lexeme_start}"
        )
        return {"type": token_type, "lexeme": lexeme, "position": lexeme_start}


def main():
    # Read input file
    path = "src/sample1.txt"
    try:
        with open(path, "r") as file_open:
            input_text = file_open.read()
    except FileNotFoundError:
        print(f"Error: File {path} not found")
        return 1
    except Exception as e:
        print(f"Error reading file: {e}")
        return 1

    print("Input text:")
    print(input_text)
    print("-" * 50)

    lexer = Lexer()
    tokens = lexer.scanner(input_text)

    # Print tokens
    print("Tokens:")
    for token in tokens:
        print(
            f"Type: {token['type']}, Lexeme: '{token['lexeme']}', Position: {token['position']}"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
