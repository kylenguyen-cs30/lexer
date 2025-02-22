# Name : Hoang Nguyen
# Email: Hnguyen1193@csu.fullerton.edu
# Project: Lexical Analyzer

import sys


class Lexer:
    def __init__(self):
        pass

    def scanner(self):
        pass


def main():
    # read input file
    path = "~/Developer/projects/lexer/sample1.txt"
    file_open = open(path, "r")

    # put them into a long array
    str_arr = file_open.read()
    print(str_arr)

    # use lexer to tokenizing the inputs
    return 0


if __name__ == "__main__":
    sys.exit(main())
