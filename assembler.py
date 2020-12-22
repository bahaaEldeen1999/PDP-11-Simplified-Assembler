import os
import json

instructions_path = "rules/instructions.json"
instructions_file = open(instructions_path)

instructions = json.load(instructions_file)

ONE_OP = instructions['one_op']
TWO_OP = instructions['two_op']
BRANCH = instructions['branch']
NO_OP = instructions['no_op']
JUMP = instructions['jump']


filepath = "test.txt"

file = open(filepath)

for line in file:
    try:
        # preprocessing
        i = 0
        while i < len(line):
            if line[i] == ',':
                line = line[:i] + " "+line[i] + " "+line[i+1:]
                i += 3
            i += 1

        line = line.split()
        print("line")
        print(line)
        i = 0
        while i < len(line):
            word = line[i]
            word = word.strip().lower()
            if word[0] == ';':
                # comment line
                break
            if word in ONE_OP:
                # check to see next word is valid
                pass
            elif word in TWO_OP:
                pass
            elif word in BRANCH:
                pass
            elif word in NO_OP:
                pass
            elif word in JUMP:
                pass
            elif i == 0 and word[-1] == ':':
                # label
                pass
            else:
                print(word)
                raise Exception("unknown word")
            i += 1
    except:
        print("Error in Assembling")
