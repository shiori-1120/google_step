# Week 2

## Homework 1: ほぼ O(1) で動くハッシュテーブルの実装

**目標:** `delete(key)` を実装し、`functional_test()` が合格するようなハッシュテーブルを実装してください。

#### 実装状況

https://github.com/shiori-1120/google_step/blob/main/week2/hash_table.py

`delete(key)` の実装が完了し、`functional_test()` に合格した。

`delete(key)` の動作

* キーが一致する項目を見つけた場合、その項目の前の要素のポインタを次の要素に向ける。
* 前の要素がない場合は、次の要素をバケットの先頭にする。
* 削除が成功したら `True` を返す。
* キーが一致する項目が見つからなければ `False` を返す。

```python
    def delete(self, key):
        assert type(key) == str
        self.check_size() # Note: Don't remove this code.
        bucket_index = calculate_hash(key) % self.bucket_size
        item = self.buckets[bucket_index]
        prev_item = None
        while item:
            if item.key == key:
                if prev_item:
                    prev_item.next = item.next
                else:
                    self.buckets[bucket_index] = item.next
                    
                self.item_count -= 1
                
                return True
            prev_item = item
            item = item.next
            
        return False
```

### ヒント 2: 再ハッシュの実装

データを追加してもほぼ O(1) で動くように、再ハッシュを実装しましょう。

* **作り方の例:**
    * 要素数がテーブルサイズの 70% を上回ったら、テーブルサイズを 2 倍に拡張します。

---

#### 実装状況

要素数がテーブルサイズの 70% を超えた場合の拡張処理。
また、テーブルサイズは元のサイズの2倍に近い素数を用いた。

```python
        if  self.item_count > self.bucket_size * 0.7:
            new_bucket_size = find_near_prime(self.bucket_size*2)
            self.rehash(new_bucket_size)
```

---

* 要素数がテーブルサイズの 30% を下回ったら、テーブルサイズを半分に縮小します。

---

#### 実装状況

要素数がテーブルサイズの 30% を下回った場合の縮小処理。
拡張処理と同様に、テーブルサイズは元のサイズの2倍に近い素数を用いた。

```python
                if self.item_count < self.bucket_size * 0.3 and self.bucket_size >97:
                    new_bucket_size = find_near_prime(self.bucket_size//2)
                    self.rehash(new_bucket_size)
```

---

#### 実装状況

テーブルサイズを奇数素数に調整

`find_near_prime` 関数のロジック
1.  既存の素数リストから、指定された数値以上の最も近い素数を探す。
2.  リストにない場合は、指定された数値の2倍までの範囲で素数を探索し、リストに追加する。
3.  素数判定には、`sqrt(k)` 以下の素数で割り算する方法を用いる。
4.  引数より大きい素数が見つかったらそれを返す。
5.  見つからなければ引数の2倍までの数の内の素数で一番大きいものを返す

```python
prime_list = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]

def find_near_prime(num):
    for p in prime_list:
        if p >= num:
            return p

    for integer in range(prime_list[-1], int(num*2), 2):
        is_prime = True
        for prime in prime_list:
            if prime >= math.sqrt(integer):
                break
            elif integer % prime == 0:
                is_prime = False
                break
        if is_prime:
            prime_list.append(integer)
            if integer >= num:
                return integer
    return prime_list[-1]
```

### ヒント 3: ハッシュ関数の見直し

サンプルコードのハッシュ関数はあまり望ましいとは言えません。ハッシュの衝突を減らすにはハッシュ関数をどう工夫すればいいでしょう？

* **現状の問題点:**
    * "alice" と "elica" が同じハッシュ値になって衝突します。
    * これは、ASCIIコードの値を単純に足しているためです。

---

#### 改善点

文字ごとに一桁ずらして足すようにハッシュ関数を変更した。これにより、アナグラム同士のハッシュ値が衝突しなくなる。

```python
def calculate_hash(key):
    assert type(key) == str
    # Note: This is not a good hash function. Do you see why?
    hash = 0
    for i, x in enumerate(key):
        hash += ord(x) * 10 ** i
    return hash
```

---

* **実行時間について (参考):**
    * パソコンの状態で実行時間が大きく変わった( ﾟДﾟ)
    * **Python:**
        * 電源接続時: 19.79 s
        * 省電力モード: 57.38 s
    * **C:**
        * 電源接続時: 0.6672 s
        * 省電力モード: 1.940 s

## Homework 2: 大規模データベースにおける木構造の採用理由

木構造を使えば O(log N)、ハッシュテーブルを使えばほぼ O(1) で検索・追加・削除を実現することができ、これだけ見ればハッシュテーブルのほうが優れているように見える。ところが現実の大規模なデータベースでは、ハッシュテーブルではなく木構造が使われることが多い。その理由を考えよ。

---

#### 回答
* 木構造は階層構造を作りやすい。
* ハッシュテーブルはハッシュ値の衝突の確率を 0% にすることはできない。
* 大規模なデータベースでは、再ハッシュのコストが非常に大きくなる。
* 再ハッシュ中はデータへのアクセスができなくなってしまう。
* 木構造のほうがデータ同士の関連性を保持しやすい。
* ハッシュテーブルでは範囲検索などが難しい。
  
**??**

-  jsonってハッシュテーブルと似た構造？？
-  firebaseのDBとかはcollection内のdocumentは(document IDをもとに)木構造で管理して、その中のfieldをハッシュテーブル的な感じで管理している？？


## Extra 1: 常に O(1) での操作が可能なデータ構造

常に O(1) で検索・追加・削除できるデータ構造は存在するでしょうか？

---

#### 回答

ハッシュマップで常にキーが重複しないデータを作れれば可能ではないかと考える。
しかし、ハッシュが検索できるのは、そのサイズが有限だからかもしれない。

## Homework 3: ほぼ O(1) で実現するキャッシュデータ構造

次の操作をほぼ O(1) で実現するデータ構造を考えましょう。

* 与えられた `<URL, Web ページ>` があるかないかを検索する。
* もしない場合、キャッシュ内で一番古い `<URL, Web ページ>` を捨てて、代わりに与えられた `<URL, Web ページ>` を追加する。
* あった場合、そのデータを連結リストの先頭に持ってきます。

### ヒント

* ハッシュテーブルだけだと順序を管理できないので、別のデータ構造を組み合わせて、X 個の `<URL, Web ページ>` をアクセスされた順に取り出せるようにしましょう。

---

#### 回答

提案するデータ構造　

* ハッシュテーブルに保存されているデータを双方向連結リストとして管理する。
* 双方向連結リストにすると、`head` と `tail` があり、先頭と末尾のデータにすぐにアクセスできる。（一番古いデータをすぐに捨てて、新しいデータを格納できる。）
* キャッシュ内にデータがあるときは `head` に追加し、見つかったデータの前の要素と次の要素をつなげて既存のデータを削除する。

---

## Homework 4: 宿題 3 のキャッシュ作成

* 宿題 3 のキャッシュを作成してみましょう（余裕があれば）。

---

#### 進捗

作成中。
https://github.com/shiori-1120/google_step/blob/main/week2/cache.py
