# Name : Hoang Nguyen
# Email: Hnguyen1193@csu.fullerton.edu
# Project: Lexical Analyzer


class Lexer:
    def __init__(self):
        pass

    def scanner(self):
        pass


def main():
    # read input file
    lines = []

    with open("sample1.txt", "r") as file:
        for line in file:
            lines.append(line.strip())

    print(lines)
    # put them into a long array
    # use lexer to tokenizing the inputs
    return 0


if __name__ == "__main__":
    main()
