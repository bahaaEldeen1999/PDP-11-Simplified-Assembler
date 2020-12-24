import os
import json

instructions_path = "rules/instructions.json"
registers_path = "rules/registers.json"
modes_path = "rules/address.json"

instructions_file = open(instructions_path)
registers_file = open(registers_path)
modes_file = open(modes_path)

instructions = json.load(instructions_file)
registers = json.load(registers_file)
modes = json.load(modes_file)
ONE_OP = instructions['one_op']
TWO_OP = instructions['two_op']
BRANCH = instructions['branch']
NO_OP = instructions['no_op']
JUMP = instructions['jump']
REGISTERS = registers
MODES = modes["mode"]


filepath = "test.txt"

file = open(filepath)

output_file = open("output.txt", "w")
'''
0 => direct
1 => auto +
2 => auto -
3 => indexed
4 => immediate
5 => relative
6 => indirect
7 => auto + indirect
8 => auto - indirect
9 => index indirect
10 => absolute
11 => relative indirect
'''
SYMBOL_TABLE = {}
LABEL_TABLE = {}


def checkAddressingMode(word, isDe):
    global SYMBOL_TABLE
    try:
        if word in REGISTERS:
            return (0 + isDe*6)
        if word[0] == '(' and word[-2] == ')' and word[-1] == '+':
            return (1+isDe*6)
        if word[0] == '-' and word[1] == '(' and word[-1] == ')':
            return (2+isDe*6)
        if word[-4] == '(' and word[-1] == ')' and word[2:4] in REGISTERS:
            return (3+isDe*6)
        if word[0] == "#":
            return (4+isDe*6)
        if word in SYMBOL_TABLE:
            return (5+isDe*6)
        if word[0] == '@':
            newWord = word[1:]
            return checkAddressingMode(newWord, 1)
        return -1
    except:
        return -1


def buildInstruction(i, line, mode):
    global MODES, REGISTERS, SYMBOL_TABLE
    try:

        instruction = MODES[mode]
        if mode == 0:
            instruction += REGISTERS[line[i+1]]
        elif mode == 1:
            instruction += REGISTERS[line[i+1][1:3]]
        elif mode == 2:
            instruction += REGISTERS[line[i+1][2:4]]
        elif mode == 3:
            instruction += REGISTERS[line[i+1][-3:-1]]
        elif mode == 6:
            instruction += REGISTERS[line[i+1][1:]]
        elif mode == 7:
            instruction += REGISTERS[line[i+1][2:4]]
        elif mode == 8:
            instruction += REGISTERS[line[i+1][3:5]]
        elif mode == 9:
            instruction += REGISTERS[line[i+1][-3:-1]]
        elif mode == 4 or mode == 5:
            instruction += "111"
        return instruction

    except:
        return "-1"


def AddExtraInstruction(i, line, mode):
    global MODES, REGISTERS, SYMBOL_TABLE
    instruction = ""
    if mode == 3:
        instruction += line[i+1][0:-4]
    elif mode == 9:
        instruction += line[i+1][1:-4]
    elif mode == 4:
        instruction += line[i+1][1:]
    elif mode == 10:
        instruction += line[i+1][2:]
    elif mode == 5:
        instruction += SYMBOL_TABLE[line[i+1]]
    elif mode == 11:
        instruction += SYMBOL_TABLE[line[i+1][1:]]
    return instruction


# pass 1
FileArr = []
for line in file:
    # print(line)
    line = line.lower()
    try:
        i = 0
        fileLine = ""
        while i < len(line):
            if line[i] == ',':
                line = line[:i] + " "+line[i] + " "+line[i+1:]
                i += 3
            i += 1

        line = line.split()
        i = 0
        while i < len(line):

            word = line[i]
            word = word.strip().lower()

            if word == "define":
                SYMBOL_TABLE[line[i+1]] = line[i+2]
                break
            if word[-1] == ":":
                print(word[:-1])
                LABEL_TABLE[word[:-1]] = word[:-1]
                break
            i += 1
    except:
        print("Error in Assembling")
file.seek(0)
# print(SYMBOL_TABLE)
noOfWordsArr = []
# pass 2
for line in file:
    # print(line)
    try:
        # preprocessing
        i = 0
        line = line.lower()
        while i < len(line):
            if line[i] == ',':
                line = line[:i] + " "+line[i] + " "+line[i+1:]
                i += 3
            i += 1

        line = line.split()
        i = 0
        while i < len(line):
            word = line[i]
            word = word.strip().lower()
            # print(word)
            if word[0] == ';':
                # comment line
                break
            if word in ONE_OP:
                # print("line "+line[i+1])
                mode = checkAddressingMode(line[i+1], 0)
                # print("mode "+str(mode))
                if mode == -1:
                    raise Exception("not valid")
                instruction = ONE_OP[word].replace(" ", "")
                instruction += buildInstruction(i, line, mode)
                instruction2 = AddExtraInstruction(i, line, mode)
                FileArr.append(instruction)
                if (instruction2 != ""):
                    noOfWordsArr.append(2)
                    FileArr.append("\n")
                    FileArr.append(instruction2)
                else:
                    noOfWordsArr.append(1)
                FileArr.append("\n")
                break
            elif word in TWO_OP:
                if line[i+2] == ',':
                    noOfWords = 1
                    mode1 = checkAddressingMode(line[i+1], 0)
                    mode2 = checkAddressingMode(line[i+3], 0)
                    # print("mode2 "+str(mode2), line[i+3])
                    if mode1 == -1 or mode2 == -1:
                        raise Exception("not valid")
                    instruction = TWO_OP[word].replace(" ", "")
                    instruction += buildInstruction(i, line, mode1)
                    instruction += buildInstruction(i+2, line, mode2)
                    instruction1 = AddExtraInstruction(i, line, mode1)
                    instruction2 = AddExtraInstruction(i+2, line, mode2)

                    FileArr.append(instruction)
                    if (instruction1 != ""):
                        noOfWords += 1
                        FileArr.append("\n")
                        FileArr.append(instruction1)
                    if (instruction2 != ""):
                        noOfWords += 1
                        FileArr.append("\n")
                        FileArr.append(instruction2)
                    noOfWordsArr.append(noOfWords)
                    FileArr.append("\n")
                    break

            elif word in BRANCH:
                instruction = BRANCH[word].replace(" ", "")
                instruction += LABEL_TABLE[line[i+1]]
                FileArr.append(instruction+"\n")
                noOfWordsArr.append(1)
                break
            elif word in NO_OP:
                pass
            elif word in JUMP:
                pass
            elif i == 0 and word[-1] == ':':
                # label
                pass
            elif word == "define":
                FileArr.append(SYMBOL_TABLE[line[1]]+"\n")
                noOfWordsArr.append(1)
                break
            else:
                print(word)
                raise Exception("unknown word")
            i += 1
    except:
        print("Error in Assembling Pass 2")


file.seek(0)
currAddress = 0
j = 0
# pass 3
for line in file:
    try:
        line = line.lower()
        line = line.split()
        # print(line)
        if line[0][-1] == ":":
            LABEL_TABLE[line[0][0:-1]] = str(currAddress)
            if len(line) == 1:
                continue
        elif line[0] == "define":
            SYMBOL_TABLE[line[1]] = str(currAddress)

        currAddress += noOfWordsArr[j]
        j += 1

    except:
        print("Error in pass 3 assembline")
# print(LABEL_TABLE, SYMBOL_TABLE, FileArr)
print(LABEL_TABLE)
for i in range(len(FileArr)):
    x = FileArr[i][8:].replace("\n", "")
    if x in LABEL_TABLE:
        base = int(LABEL_TABLE[x], 10)
        #print(base, i)
        address = base-(i//2)
        address = f'{address:08b}'
        #print("address ", address)
        FileArr[i] = FileArr[i][:8] + str(address)+"\n"
    elif FileArr[i] in SYMBOL_TABLE:
        FileArr[i] = SYMBOL_TABLE[FileArr[i]]
output_file.writelines(FileArr)
