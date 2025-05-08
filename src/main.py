# Name : Hoang Nguyen
# Email: Hnguyen1193@csu.fullerton.edu
# Project: Lexical Analyzer
import sys


class Lexer:
    def __init__(self):
        # define state transition table

        self.transition_table = [
            # State 1 (Initial) - index 0
            [
                2,  # [0] Letters -> State 2 (Identifier/Keyword)
                4,  # [1] Digits -> State 4 (Number)
                19,  # [2] Brackets
                12,  # [3] Colon
                19,  # [4] Equal
                14,  # [5] Less Than
                17,  # [6] Greater Than
                8,  # [7] Asterisk
                1,  # [8] Whitespace
                19,  # [9] Others],
            ],
            # State 2 (Identifier) - index 1
            [2, 2, 3, 3, 3, 3, 3, 3, 3, 3],
            # State 3 (End Identifier) - index 2
            [1] * 10,
            # State 4 (Number) - index 3
            [5, 4, 5, 5, 5, 5, 5, 5, 5, 5],
            # State 5 (End Number) - index 4
            [1] * 10,
            # State 6 (Placeholder) - index 5 ⚠️ THÊM MỚI
            [20] * 10,
            # State 7 (Placeholder) - index 6 ⚠️ THÊM MỚI
            [20] * 10,
            # State 8 (Comment Start) - index 7
            [20, 20, 20, 20, 20, 20, 20, 9, 20, 20],
            # State 9 (In Comment) - index 8
            [9, 9, 9, 9, 9, 10, 9, 9, 9, 9],
            # State 10 (Comment End) - index 9
            [9, 9, 9, 9, 9, 9, 11, 9, 9, 9],
            # State 11 (Placeholder) - index 10 ⚠️ THÊM MỚI
            [20] * 10,
            # State 12 (Assignment) - index 11
            [20, 20, 20, 20, 13, 20, 20, 20, 20, 20],
            # State 13 (Placeholder) - index 12 ⚠️ THÊM MỚI
            [20] * 10,
            # State 14 (Less Than) - index 13
            [20, 20, 20, 20, 15, 20, 16, 20, 20, 20],
            # State 15 (Placeholder) - index 14 ⚠️ THÊM MỚI
            [20] * 10,
            # State 16 (Placeholder) - index 15 ⚠️ THÊM MỚI
            [20] * 10,
            # State 17 (Greater Than) - index 16
            [20, 20, 20, 20, 18, 20, 20, 20, 20, 20],
            # State 18 (Placeholder) - index 17 ⚠️ THÊM MỚI
            [20] * 10,
            # State 19 (Separators) - index 18
            [1] * 10,
            # State 20 (Backup) - index 19
            [1] * 10,
        ]

        self.state_index_map = {
            1: 0,
            2: 1,
            3: 2,
            4: 3,
            5: 4,
            6: 5,
            7: 6,
            8: 7,
            9: 8,
            10: 9,
            11: 10,
            12: 11,
            13: 12,
            14: 13,
            15: 14,
            16: 15,
            17: 16,
            18: 17,
            19: 18,
            20: 19,
        }

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
            "KEYWORD": "KEYWORD",
        }

        # list of keywords
        self.keywords = ["if", "return"]

        self.position = 0

        # input starting
        self.input_string = ""

    def get_col_index(self, char):
        if char.isalpha():
            return 0  # Letters
        elif char.isdigit():
            return 1  # Digits
        elif char in {"{", "}", "(", ")", ";"}:
            return 2  # Brackets/Parentheses
        elif char == ":":
            return 3  # Colon
        elif char == "=":
            return 4  # Equal
        elif char == "<":
            return 5  # Less Than
        elif char == ">":
            return 6  # Greater Than
        elif char == "*":
            return 7  # Asterisk
        elif char.isspace():
            return 8  # Whitespace
        else:
            return 9  # Others

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
        # the position of the current index is at the end
        # of the file.
        if self.position >= len(self.input_string):
            return None

        # skip whitespace at beginning
        # NOTE: bỏ qua phần trắng và kết thúc file
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

            try:
                state_index = self.state_index_map[current_state]
            except KeyError:
                raise RuntimeError(f"Invalid state: {current_state}")

            # debug before state transition
            print(
                f"Position: {self.position}, Character: '{current_char}', Col index: {col_idx}, Current State: {current_state}"
            )

            # get next state from transition_table
            next_state = self.transition_table[state_index][col_idx]

            # debug after determining next state
            print(f"  -> Next State: {next_state}")

            # THAY ĐỔI QUAN TRỌNG: xử lí đặc biệt cho các ký tự phân cách
            # nếu đang ở trạng thái 1 (ban đầu) và next_state là 19 SEPARATOR
            # thì chỉ xử lí ký tự hiện tại và kết thúc
            if current_state == 1 and next_state == 19:
                self.position += 1
                lexeme_end = self.position
                current_state = next_state
                break

            # check if we're in a backup state
            if next_state in self.backup_states:
                lexeme_end = self.position
                backup_occurred = True
                print(
                    f"  -> Backup state reached,setting lexeme_end to {lexeme_end}"
                )
                break

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
            print(" -> Empty lexeme, skipping")
            return None

        # xác định trạng trái cuối
        final_state = current_state

        # xử lý các trường hợ đặc biệt nếu trạng thái hiện tại không nằm trong token_types.
        if final_state not in self.token_types:
            if lexeme in self.keywords:
                token_type = "KEYWORD"
            else:
                # dựa vào nội dung lexeme để xác định loại token
                if lexeme.isalpha():
                    final_state = 3
                elif lexeme.isdigit():
                    final_state = 5
                elif lexeme in ["(", ")", "{", "}", ";"]:
                    # xác định chính xác trạng thái dựa trên toán tử
                    final_state = self.get_operator_state(lexeme)

        # lấy loại token từ final_state
        token_type = self.token_types.get(final_state, "UNKNOWN")

        # xử lí loại trường hợp đặc biệt cho từ khoá
        if lexeme in self.keywords:
            token_type = "KEYWORD"
        elif token_type in self.token_types_mapping:
            # áp dụng mapping từ loại token cụ thể sang loại chung
            token_type = self.token_types_mapping.get(token_type, token_type)

        # xử lí các trường hợp đặc biệt bằng state machine
        if token_type == "UNKNOWN":
            token_type = self.handle_spacial_cases(lexeme, final_state)

        # chuyển đổi token_type cụ thể sang loại chung nếu cần
        # general_token_type = self.token_types_mapping.get(
        #     token_type, token_type
        # )

        print(
            f"Return token: Type: {token_type}, Lexeme: '{lexeme}' , Position: {lexeme_start}"
        )

        return {"type": token_type, "lexeme": lexeme, "position": lexeme_start}

    def get_operator_state(self, operator):
        operator_states = {
            ">=": 18,  # GREATER_EQUAL_OP
            "<=": 15,  # LESS_EQUAL_OP
            "<>": 16,  # NOT_EQUAL_OP
            ":=": 13,  # ASSIGN_OP
            ">": 19,  # SEPARATOR (hoặc cần trạng thái riêng)
            "<": 19,  # SEPARATOR (hoặc cần trạng thái riêng)
            "=": 19,  # SEPARATOR (hoặc cần trạng thái riêng)
        }
        return operator_states.get(operator, 19)  # mặc định là là SEPARATOR

    def handle_spacial_cases(self, lexeme, state):
        # tận dụng state machine cho các trường hợp đặc biệt
        if state == 19:
            return "SEPARATOR"
        if lexeme in [">=", "<=", "<>", ":="]:
            return self.token_types.get(
                self.get_operator_state(lexeme), "OPERATOR"
            )
        return "UNKNOWN"


def main():
    # Read input file
    path = "sample1.txt"
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
