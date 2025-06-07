# week 3

## 宿題 1: 演算子の拡張（`*`, `/`）

---

既存のモジュール化されたプログラムを修正し、乗算（`*`）と除算（`/`）に対応させてください。

**前提:**
不正な入力はないものと仮定して構いません。
細かい仕様は自由に定義してください。

**全体の前提**
* 数式として成り立たない入力はない
(e.g.) ~~1/0~~
* かっこの数はそろっている
(e.g.) ~~(1+((3+4+5)~~
* `+`, `-`, `*`, `/`, `abs()`, `int()`, `round()`以外の演算子等は入力されない
* かっこの中の処理がない式は入力されない
* 数字だけの入力はない
* 不要なかっこが存在しない
(e.g.) ~~((1+2))~~, ~~(1)~~
* 入力に空白な詩

---

### 実装

`*`と`/`のトークンを返す処理を追加
```
def read_times(line, index):
    token = {'type': 'TIMES'}
    return token, index + 1

def read_devided(line, index):
    token = {'type': 'DEVIDED'}
    return token, index + 1
```

tokenize(line)関数内において以下の処理を追加
`line[index]`が`*`または`/`の時に適切なトークンを返す関数を呼び出している
```
        elif line[index] == '*':
            (token, index) = read_times(line, index)
        elif line[index] == '/':
            (token, index) = read_devided(line, index)
```
evaluate(tokens)関数内に以下の処理を追加
足し算・引き算を計算する前に掛け算・割り算を計算
(e.g.) `1+1*4+1`を`1+4+1`する（実際にはtokenの配列を操作して行っている）
```

```
    tmp_res = 0
    # 掛け算・割り算を計算
    while index < len(tokens):
        if tokens[index]['type'] == 'NUMBER':
            if index + 1 < len(tokens):
                # かけ算
                if tokens[index + 1]['type'] == 'TIMES':
                    # かける数の正負による分岐
                    if tokens[index + 2]['type'] == 'NUMBER':
                        tmp_res = tokens[index]['number'] * tokens[index + 2]['number']
                        del tokens[index: index + 3]
                    elif tokens[index + 2]['type'] == 'MINUS':
                        tmp_res = tokens[index]['number'] * (-tokens[index + 3]['number'])
                        del tokens[index: index + 4]
                        
                    tokens.insert(index, {'type': 'NUMBER', 'number': tmp_res})
                    index -= 1
                # わり算
                elif tokens[index + 1]['type'] == 'DEVIDED':
                    # かける数の正負による分岐
                    if tokens[index + 2]['type'] == 'NUMBER':
                        tmp_res = tokens[index]['number'] / tokens[index + 2]['number']
                        del tokens[index: index + 3]
                    elif tokens[index + 2]['type'] == 'MINUS':
                        tmp_res = tokens[index]['number'] / (-tokens[index + 3]['number'])
                        del tokens[index: index + 4]
                        
                    tokens.insert(index, {'type': 'NUMBER', 'number': tmp_res})
                    index -= 1
        index += 1

    index = 1 # 足し算・引き算のためにindexを初期化
---

## 宿題 2: テストケースの追加

---

作成したプログラムが正しく動作することを確認するため、**テストケース**を追加してください。できるだけ網羅的にテストケースを作成しましょう。

### テストケース
* 1*1 # 簡単なテストケース
* 1*0 # ゼロがあるときの演算
* 0*0 # 両方ゼロの時
* 0.00000000*0.00000000 # たくさんのゼロの時
* 99999999999999999999999999*99999999999999999999999 # 大きい数の時
* 12345*67890 # 0~9をすべて使ってみる
* 1.23*4.56 # 小数のかけ算
* 0.01*0.03 # 一桁目が0の小数同士のかけ算
* 1/6 # わり算
* 1/3 # 割り切れないわり算
* 0.1/0.4 # 小数同士の割り算
* 1*3*4*5*2 # *を繰り返す
* 1*2/3*4/5 # /と*を繰り返す
* 1/2/3 # /を繰り返す
* 1*-2

# TODO: テストケースの追加

---

## 宿題 3: 括弧への対応

---

プログラムを拡張し、**括弧**に対応させてください。

### 実装

かっこの中身を計算してかっこの無いtokenの配列を返すevaluate_parentheses(tokens)の処理を追加
```
tokens = tokenize(line) 
simplified_tokens = evaluate_parentheses(tokens) 
actual_answer = evaluate(simplified_tokens)
expected_answer = eval(line)
```
#### evaluate_parentheses(tokens)

この関数は以下のような処理を行っている

```
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
            while not tokens[index]['type'] == 'LEFT_BRACKET':
                index -= 1
            
            if tokens[index]['type'] == 'LEFT_BRACKET':
                tmp_res = evaluate(tokens[index+1: right_bracket_index])
            del tokens[index: right_bracket_index + 1]
            tokens.insert(index, {'type': 'NUMBER', 'number': tmp_res})

        index += 1
    return tokens
```
1. `index`を増やしてかっこの右側を探す
2. `index`を減らしてかっこの左側を探す
3. かっこの中身を`evaluate(tokens)`で計算
4. `tokens`からかっこの中身の部分を消して`evaluate(tokens)`で計算した数字のtokenを入れる
5. `tokens`の最後の`index`まで上記の操作を繰り返す


`(`, `)`を読んでトークンを返す処理も追加
```
def read_left_bracket(line, index):
    token = {'type': 'LEFT_BRACKET'}
    return token, index + 1

def read_right_bracket(line, index):
    token = {'type': 'RIGHT_BRACKET'}
    return token, index + 1
```

tokenize(line)関数内
```
        elif line[index] == '(':
            (token, index) = read_left_bracket(line, index)
        elif line[index] == ')':
            (token, index) = read_right_bracket(line, index)
```


### テストケース

* (1+1) # もっとも簡単なテストケース
* (3*4)+(1-2) # かっこの計算をつなげたもの
* (((1+1)+1)+1)+1 # かっこの中にかっこがあるもの
* (1/1)/1 # かっこの計算にわり算
* (1+1)-1 # かっこの計算に引き算
* (1+1)*4 # かっこの計算にかけ算

---

## 宿題 4: 関数への対応

---


`abs()`, `int()`, `round()` の組み込み関数に対応できるようにプログラムを拡張してください。

* `abs(-2.2)` => `2.2` （絶対値）
* `int(1.55)` => `1` （小数を切り捨てる）
* `round(1.55)` => `2` （四捨五入）

### 実装

`evaluate_parentheses(tokens)`に次の処理を追加する
* 左のかっこ`(`と同様に`abs(`, `int(`, `round(`を扱う
* かっこの中を計算するときに`(`, `abs(`, `int(`, `round(`に応じた処理を行うようにする


```
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
                tmp_res = abs(evaluate(tokens[index+1: right_bracket_index]))
            elif tokens[index]['type'] == 'INT':
                tmp_res = int(evaluate(tokens[index+1: right_bracket_index]))
            elif tokens[index]['type'] == 'ROUND':
                tmp_res = round(evaluate(tokens[index+1: right_bracket_index]))
            del tokens[index: right_bracket_index + 1]
            tokens.insert(index, {'type': 'NUMBER', 'number': tmp_res})
        index += 1
    return tokens
```
`abs(`, `int(`, `round(`を読んでトークンを返す処理を追加

* 返すindexに注意
```
def read_abs(line, index):
    token = {'type': 'ABS'}
    return token, index + 4 # abs(の分だけindexを進める

def read_int(line, index):
    token = {'type': 'INT'}
    return token, index + 4

def read_round(line, index):
    token = {'type': 'ROUND'}
    return token, index + 6
```

`tokenize(line)`関数内に処理を追加
```
        elif line[index] == 'a':
            (token, index) = read_abs(line, index)
        elif line[index] == 'i':
            (token, index) = read_int(line, index)
        elif line[index] == 'r':
            (token, index) = read_round(line, index)
```

### テストケース

* abs(-6.78) 
* int(0)
* int(1.11111111111111)
* round(5.678)
* round(0)
* round(3)
* round(1*4/3+2-9)
* abs(int(round(-9)))
