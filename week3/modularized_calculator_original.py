#! /usr/bin/python3

def read_number(line, index):
    number = 0
    while index < len(line) and line[index].isdigit():
        number = number * 10 + int(line[index])
        # print('line[index]', line[index])
        index += 1
    if index < len(line):
        if line[index] == '.':
            index += 1
            multiplier_number = 1
            while index < len(line) and line[index].isdigit():
                number =  int(line[index]) * (0.1 ** multiplier_number) + number
                multiplier_number += 1
                index += 1
    # print("number", number)
    token = {'type': 'NUMBER', 'number': number}
    return token, index

def read_plus(line, index):
    token = {'type': 'PLUS'}
    return token, index + 1

def read_minus(line, index):
    token = {'type': 'MINUS'}
    return token, index + 1

def read_times(line, index):
    token = {'type': 'TIMES'}
    return token, index + 1

def read_devided(line, index):
    token = {'type': 'DEVIDED'}
    return token, index + 1

def read_left_bracket(line, index):
    token = {'type': 'LEFT_BRACKET'}
    return token, index + 1

def read_right_bracket(line, index):
    token = {'type': 'RIGHT_BRACKET'}
    return token, index + 1

def read_abs(line, index):
    token = {'type': 'ABS'}
    return token, index + 4

def read_int(line, index):
    token = {'type': 'INT'}
    return token, index + 4

def read_round(line, index):
    token = {'type': 'ROUND'}
    return token, index + 6

def tokenize(line):
    """
    Tokenize the input line and return a list of tokens
    """
    tokens = []
    index = 0
    while index < len(line):
        if line[index].isdigit():
            (token, index) = read_number(line, index)
        elif line[index] == '+':
            (token, index) = read_plus(line, index)
        elif line[index] == '-':
            (token, index) = read_minus(line, index)
        elif line[index] == '*':
            (token, index) = read_times(line, index)
        elif line[index] == '/':
            (token, index) = read_devided(line, index)
        elif line[index] == '(':
            (token, index) = read_left_bracket(line, index)
        elif line[index] == ')':
            (token, index) = read_right_bracket(line, index)
        elif line[index] == 'a':
            (token, index) = read_abs(line, index)
        elif line[index] == 'i':
            (token, index) = read_int(line, index)
        elif line[index] == 'r':
            (token, index) = read_round(line, index)
        else:
            print('Invalid character found: ' + line[index])
            exit(1)
        tokens.append(token)
    return tokens

def evaluate(tokens):
    """
    Evaluate the list of tokens and return a calculated result
    """
    tokens.insert(0, {'type': 'PLUS'}) # Insert a dummy '+' token
    index = 1
    
    # 掛け算割り算を計算
    while index < len(tokens):
        if tokens[index]['type'] == 'NUMBER':
            if index + 1 < len(tokens):
                if tokens[index + 1]['type'] == 'TIMES':
                    tmp_res = tokens[index]['number'] * tokens[index + 2]['number']
                    del tokens[index: index + 3]
                    tokens.insert(index, {'type': 'NUMBER', 'number': tmp_res})
                elif tokens[index + 1]['type'] == 'DEVIDED':
                    tmp_res = tokens[index]['number'] / tokens[index + 2]['number']
                    del tokens[index: index + 3]
                    tokens.insert(index, {'type': 'NUMBER', 'number': tmp_res})
        
        index += 1
    
    # 足し算・引き算を計算
    answer = 0
    index = 1
    while index < len(tokens):
        if tokens[index]['type'] == 'NUMBER':
            if tokens[index - 1]['type'] == 'PLUS':
                answer += tokens[index]['number']
            elif tokens[index - 1]['type'] == 'MINUS':
                answer -= tokens[index]['number']
            else:
                print('Invalid syntax')
        index += 1
    return answer

def evaluate_parentheses(tokens):
    """
    Calculate the contents of the parentheses and return the tokens without the parentheses
    """
    index = 0
    right_bracket_index = 0
    tmp_res = 0
    while index < len(tokens):
        if tokens[index]['type'] == 'RIGHT_BRACKET':
            
            right_bracket_index = index
            while not (tokens[index]['type'] == 'LEFT_BRACKET'
            or tokens[index]['type'] == 'ABS'
            or tokens[index]['type'] == 'INT'
            or tokens[index]['type'] == 'ROUND'):
                index -= 1
            
            if tokens[index]['type'] == 'LEFT_BRACKET':
                tmp_res = evaluate(tokens[index+1: right_bracket_index])
            elif tokens[index]['type'] == 'ABS':
                tmp_res = abs(int(evaluate(tokens[index+1: right_bracket_index])))
            elif tokens[index]['type'] == 'INT':
                tmp_res = int(evaluate(tokens[index+1: right_bracket_index]))
            elif tokens[index]['type'] == 'ROUND':
                tmp_res = round(evaluate(tokens[index+1: right_bracket_index]))
            del tokens[index: right_bracket_index + 1]
            tokens.insert(index, {'type': 'NUMBER', 'number': tmp_res})
        index += 1
    return tokens

def test(line):
    tokens = tokenize(line)
    simplified_tokens = evaluate_parentheses(tokens)
    print(simplified_tokens)
    actual_answer = evaluate(simplified_tokens)
    expected_answer = eval(line)
    if abs(actual_answer - expected_answer) < 1e-8:
        print("PASS! (%s = %f)" % (line, expected_answer))
    else:
        print("FAIL! (%s should be %f but was %f)" % (line, expected_answer, actual_answer))

# Add more tests to this function :)
def run_test():
    print("==== Test started! ====")
    test("1+2")
    test("1.0+2.1-3")
    test("1.0*2.0")
    test("2.0/2.0")
    test("3.0+4*2-1/5")
    test("(3.0+4*(2-1))/5")
    test("12+abs(int(round(-1.55)+abs(int(-2.3+4))))")
    
    print("==== Test finished! ====\n")

run_test()

# while True:
#     print('> ', end="")
#     line = input()
#     tokens = tokenize(line)
#     answer = evaluate(tokens)
#     print("answer = %f\n" % answer)
