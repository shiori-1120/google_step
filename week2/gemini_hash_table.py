import random, sys, time

###########################################################################
#                                                                         #
# Implement a hash table from scratch! (⑅•ᴗ•⑅)                         #
#                                                                         #
# Please do not use Python's dictionary or Python's collections library.  #
# The goal is to implement the data structure yourself.                   #
#                                                                         #
###########################################################################

# Hash function.
#
# |key|: string
# Return value: a hash value
def calculate_hash(key):
    assert type(key) == str
    # 改善点1: より衝突の少ないハッシュ関数に変更
    # Pythonのhash()関数に近い考え方で、乗算とXORを組み合わせる
    # 31は一般的に良いとされる乗数
    hash_val = 0
    for char in key:
        hash_val = (hash_val * 31 + ord(char)) & 0xFFFFFFFF  # 32ビットに収める
    return hash_val


# generate_prime 関数の改善のための補助関数
# あらかじめ素数リストを保持し、高速化する
_primes = [
    97, 197, 397, 797, 1597, 3203, 6421, 12853, 25717, 51437, 102877, 205759,
    411527, 823109, 1646243, 3292489, 6584983, 13169977, 26339969, 52679969,
    105359939, 210719881, 421439783, 842879579, 1685759167, 3371518343,
    6743036987, 13486073983, 26972147983, 53944295981, 107888591971, # 前回まで
    215777183951, 431554367917, 863108735849, 1726217471719, 3452434943471,
    6904869886979, 13809739773999, 27619479548003, 55238959096009, 110477918192021,
    # 220955836384043, 441911672768107, 883823345536219, 1767646691072461, 3535293382144941,
    # 7070586764289899, 14141173528579801, 28282347057159607, 56564694114319223, 113129388228638457,
    # 226258776457276917, 452517552914553833, 905035105829107677, 1810070211658215353, 3620140423316430737,
    # 7240280846632861483, 14480561693265722967, 28961123386531445941, 57922246773062891893, 115844493546125783817
]

def generate_prime(min_num):
    # 改善点2: 事前計算された素数リストから、min_num以上の最小の素数を返す
    # 再ハッシュ時の素数生成を劇的に高速化する
    for p in _primes:
        if p >= min_num:
            return p
    # もしリストの範囲を超えたら、非常に大きな素数を生成する必要があるが、
    # このテストケースの範囲では上記リストで十分なはず。
    # 必要に応じてさらに素数を追加するか、一般的な素数生成アルゴリズムを使う。
    # しかし、今回の要件（テストケース変更なしでの高速化）では、この範囲で十分。
    
    # リストでカバーできない場合（念のため）
    # より効率的な素数判定アルゴリズム (ミラー・ラビン素数判定法など) を
    # 導入することも可能だが、複雑になるため今回はシンプルな試行除算を改善した
    # 上記のリストでカバーできない場合は、元の generate_prime と同等の
    # 試行除算だが、リスト上限により発生しない想定
    
    # 非常に大きな素数が必要になった場合、元の実装の計算コストが高いので、
    # より高度な素数生成方法を検討する必要がある。
    # 現実的なハッシュテーブルでは、多くの場合、固定の素数リストを使用するか、
    # 特定のアルゴリズム (例: Fermat's Little Theoremと試行除算の組み合わせ)
    # で動的に生成する。
    
    # デフォルトの動作（万が一リストを超える場合のため）
    num = min_num
    while True:
        if num <= 1:
            num = 2
        is_prime = True
        # 効率化: √num までで十分
        # しかし、このコードは主に _primes リストが使われることを想定
        for i in range(2, int(num**0.5) + 1):
            if num % i == 0:
                is_prime = False
                break
        if is_prime:
            return num
        num += 1
        if num % 2 == 0: # 偶数は素数ではないためスキップ
            num += 1


def return_new_hash_table(new_bucket_size):
    return HashTable(bucket_size = new_bucket_size)

# An item object that represents one key - value pair in the hash table.
class Item:
    # |key|: The key of the item. The key must be a string.
    # |value|: The value of the item.
    # |next|: The next item in the linked list. If this is the last item in the
    #         linked list, |next| is None.
    def __init__(self, key, value, next):
        assert type(key) == str
        self.key = key
        self.value = value
        self.next = next


# The main data structure of the hash table that stores key - value pairs.
# The key must be a string. The value can be any type.
#
# |self.bucket_size|: The bucket size.
# |self.buckets|: An array of the buckets. self.buckets[hash % self.bucket_size]
#                 stores a linked list of items whose hash value is |hash|.
# |self.item_count|: The total number of items in the hash table.
class HashTable:

    # Initialize the hash table.
    def __init__(self, bucket_size = 97):
        # Set the initial bucket size to 97. A prime number is chosen to reduce
        # hash conflicts.
        self.bucket_size = bucket_size
        self.buckets = [None] * self.bucket_size
        self.item_count = 0
        self._rehashing = False


    # Put an item to the hash table. If the key already exists, the
    # corresponding value is updated to a new value.
    #
    # |key|: The key of the item.
    # |value|: The value of the item.
    # Return value: True if a new item is added. False if the key already exists
    #              and the value is updated.
    def put(self, key, value):
        assert type(key) == str

        bucket_index = calculate_hash(key) % self.bucket_size
        item = self.buckets[bucket_index]

        # 既存のキーの更新を効率化するため、Itemのnextを辿る前に現在のアイテムを確認
        # 無駄なループを避ける
        if item and item.key == key: # 最初のエントリが一致する場合
            item.value = value
            return False

        current = item
        while current and current.next: # 最後の要素まで探索
            if current.next.key == key: # 次の要素が一致する場合
                current.next.value = value
                return False
            current = current.next

        # 新しいアイテムを追加
        new_item = Item(key, value, self.buckets[bucket_index])
        self.buckets[bucket_index] = new_item
        self.item_count += 1

        # 負荷率が0.7を超えたら再ハッシュ
        if self.item_count > self.bucket_size * 0.7:
            self._rehash(self.bucket_size * 2)
        return True

    def get(self, key):
        assert type(key) == str

        bucket_index = calculate_hash(key) % self.bucket_size
        item = self.buckets[bucket_index]
        while item:
            if item.key == key:
                return (item.value, True)
            item = item.next
        return (None, False)

    def delete(self, key):
        assert type(key) == str

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

                # 負荷率が0.1を下回り、かつ最小サイズより大きい場合に再ハッシュ
                if self.item_count < self.bucket_size * 0.3 and self.bucket_size > 97:
                    self._rehash(self.bucket_size // 2)
                return True
            prev_item = item
            item = item.next
        return False

    def _rehash(self, new_bucket_size_hint):  # 再ハッシュ処理を共通化
        if self._rehashing:
            return  # 多重再ハッシュを防ぐ

        self._rehashing = True
        # generate_prime を呼び出し、適切な素数を取得
        new_bucket_size = generate_prime(new_bucket_size_hint)
        new_hash_table = HashTable(bucket_size=new_bucket_size)

        for bucket in self.buckets:
            item = bucket
            while item:
                # new_hash_table.put は Item の生成とリンクの更新を行うため、
                # ここで新しい Item を生成し、そのまま new_hash_table に渡すことで効率化。
                # ただし、今回はテストケース変更不可のため、既存のputを使用。
                # putメソッド内でのハッシュ計算とリンクリスト操作により、実質的に正しい。
                new_hash_table.put(item.key, item.value)
                item = item.next

        self.bucket_size = new_hash_table.bucket_size
        self.buckets = new_hash_table.buckets
        self.item_count = new_hash_table.item_count
        self._rehashing = False

    # Return the total number of items in the hash table.
    def size(self):
        return self.item_count

    # Check that the hash table has a "reasonable" bucket size.
    # The bucket size is judged "reasonable" if it is smaller than 100 or
    # the buckets are 30% or more used.
    #
    # Note: Don't change this function.
    def check_size(self):
        assert (self.bucket_size < 100 or
                self.item_count >= self.bucket_size * 0.3)


# Test the functional behavior of the hash table.
def functional_test():
    hash_table = HashTable()

    assert hash_table.put("aaa", 1) == True
    assert hash_table.get("aaa") == (1, True)
    assert hash_table.size() == 1

    assert hash_table.put("bbb", 2) == True
    assert hash_table.put("ccc", 3) == True
    assert hash_table.put("ddd", 4) == True
    assert hash_table.get("aaa") == (1, True)
    assert hash_table.get("bbb") == (2, True)
    assert hash_table.get("ccc") == (3, True)
    assert hash_table.get("ddd") == (4, True)
    assert hash_table.get("a") == (None, False)
    assert hash_table.get("aa") == (None, False)
    assert hash_table.get("aaaa") == (None, False)
    assert hash_table.size() == 4

    assert hash_table.put("aaa", 11) == False
    assert hash_table.get("aaa") == (11, True)
    assert hash_table.size() == 4

    assert hash_table.delete("aaa") == True
    assert hash_table.get("aaa") == (None, False)
    assert hash_table.size() == 3

    assert hash_table.delete("a") == False
    assert hash_table.delete("aa") == False
    assert hash_table.delete("aaa") == False
    assert hash_table.delete("aaaa") == False

    assert hash_table.delete("ddd") == True
    assert hash_table.delete("ccc") == True
    assert hash_table.delete("bbb") == True
    assert hash_table.get("aaa") == (None, False)
    assert hash_table.get("bbb") == (None, False)
    assert hash_table.get("ccc") == (None, False)
    assert hash_table.get("ddd") == (None, False)
    assert hash_table.size() == 0

    assert hash_table.put("abc", 1) == True
    assert hash_table.put("acb", 2) == True
    assert hash_table.put("bac", 3) == True
    assert hash_table.put("bca", 4) == True
    assert hash_table.put("cab", 5) == True
    assert hash_table.put("cba", 6) == True
    assert hash_table.get("abc") == (1, True)
    assert hash_table.get("acb") == (2, True)
    assert hash_table.get("bac") == (3, True)
    assert hash_table.get("bca") == (4, True)
    assert hash_table.get("cab") == (5, True)
    assert hash_table.get("cba") == (6, True)
    assert hash_table.size() == 6

    assert hash_table.delete("abc") == True
    assert hash_table.delete("cba") == True
    assert hash_table.delete("bac") == True
    assert hash_table.delete("bca") == True
    assert hash_table.delete("acb") == True
    assert hash_table.delete("cab") == True
    assert hash_table.size() == 0
    print("Functional tests passed!")


# Test the performance of the hash table.
#
# Your goal is to make the hash table work with mostly O(1).
# If the hash table works with mostly O(1), the execution time of each iteration
# should not depend on the number of items in the hash table. To achieve the
# goal, you will need to 1) implement rehashing (Hint: expand / shrink the hash
# table when the number of items in the hash table hits some threshold) and
# 2) tweak the hash function (Hint: think about ways to reduce hash conflicts).
def performance_test():
    hash_table = HashTable()

    for iteration in range(100):
        begin = time.time()
        random.seed(iteration)
        for i in range(10000):
            rand = random.randint(0, 100000000)
            hash_table.put(str(rand), str(rand))
        random.seed(iteration)
        for i in range(10000):
            rand = random.randint(0, 100000000)
            hash_table.get(str(rand))
        end = time.time()
        print("%d %.6f" % (iteration, end - begin))

    print("here")
    for iteration in range(100):
        print("here1", iteration)
        random.seed(iteration)
        for i in range(10000):
            print("here2", iteration, i)
            rand = random.randint(0, 100000000)
            hash_table.delete(str(rand))
    print("here3")

    assert hash_table.size() == 0
    print("Performance tests passed!")


if __name__ == "__main__":
    # functional_test()
    performance_test()