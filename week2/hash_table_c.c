#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <math.h>
#include <time.h>
#include <assert.h> // for assert

// Pythonのtime.time()とrandom.randint()の代替
#ifdef _WIN32
#include <windows.h>
#else
#include <sys/time.h>
#endif

// time.time()の代替
double get_current_time() {
#ifdef _WIN32
    FILETIME ft;
    GetSystemTimeAsFileTime(&ft);
    unsigned long long ull = (unsigned long long)ft.dwHighDateTime << 32 | ft.dwLowDateTime;
    return ull / 10000000.0;
#else
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return (double)tv.tv_sec + (double)tv.tv_usec / 1000000.0;
#endif
}

// random.randint(a, b) の代替
int custom_rand_int(int min, int max) {
    return min + rand() % (max - min + 1);
}

// Item構造体
typedef struct Item {
    char* key;
    char* value; // Pythonの任意の値をC言語ではchar* (文字列) として扱う
    struct Item* next;
} Item;

// HashTable構造体
typedef struct HashTable {
    int bucket_size;
    Item** buckets;
    int item_count;
} HashTable;

// グローバルな素数リスト
int prime_list[] = {
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97
};
int prime_list_len = sizeof(prime_list) / sizeof(prime_list[0]);

// ハッシュ関数
unsigned long calculate_hash(const char* key) {
    assert(key != NULL);
    unsigned long hash = 0;
    for (int i = 0; key[i] != '\0'; ++i) {
        // Pythonの ** はC言語では pow 関数だが、ここでは100の累乗なのでループで計算
        unsigned long term = (unsigned long)key[i];
        for (int j = 0; j < i; ++j) {
            term *= 100;
        }
        hash += term;
    }
    return hash;
}

// 素数判定関数
bool is_prime(int num) {
    if (num <= 1) return false;
    for (int i = 0; i < prime_list_len && prime_list[i] * prime_list[i] <= num; ++i) {
        if (num % prime_list[i] == 0) {
            return false;
        }
    }
    // prime_list_len 以上の素数で割り切れるか確認
    for (int i = prime_list[prime_list_len -1] + 1; i * i <= num; i+=2) { // 奇数のみチェック
        if (num % i == 0) {
            return false;
        }
    }
    return true;
}


// find_near_prime関数
int find_near_prime(int num) {
    for (int i = 0; i < prime_list_len; ++i) {
        if (prime_list[i] >= num) {
            return prime_list[i];
        }
    }

    // prime_listの最後に新しい素数を追加する必要がある場合（今回はprime_list_lenが固定なので直接参照）
    // 実際には動的な配列にすべきだが、ここではPythonの動作に合わせる
    for (int integer = prime_list[prime_list_len - 1]; integer <= num * 2; integer += 2) {
        if (is_prime(integer)) {
            // Pythonのprime_list.append()の挙動を完全に再現するには動的配列が必要
            // ここでは既に定義済みのprime_listを使用しているため、直接追加はしない
            // が、結果として見つかった素数を返す
            if (integer >= num) {
                return integer;
            }
        }
    }
    return prime_list[prime_list_len - 1]; // 見つからなかった場合、リストの最後の素数を返す（Pythonの挙動に合わせる）
}

// HashTableの初期化
HashTable* create_hash_table(int bucket_size) {
    HashTable* ht = (HashTable*)malloc(sizeof(HashTable));
    assert(ht != NULL);
    ht->bucket_size = bucket_size;
    ht->buckets = (Item**)calloc(bucket_size, sizeof(Item*)); // NULLで初期化
    assert(ht->buckets != NULL);
    ht->item_count = 0;
    return ht;
}

// HashTableの解放
void free_hash_table(HashTable* ht) {
    for (int i = 0; i < ht->bucket_size; ++i) {
        Item* item = ht->buckets[i];
        while (item) {
            Item* temp = item;
            item = item->next;
            free(temp->key);
            free(temp->value);
            free(temp);
        }
    }
    free(ht->buckets);
    free(ht);
}

// HashTableのサイズチェック (Pythonのcheck_size関数)
void hash_table_check_size(HashTable* ht) {
    assert(ht->bucket_size < 100 || ht->item_count >= ht->bucket_size * 0.3);
}

// rehash関数
void hash_table_rehash(HashTable* ht, int new_bucket_size) {
    Item** new_buckets = (Item**)calloc(new_bucket_size, sizeof(Item*));
    assert(new_buckets != NULL);

    for (int i = 0; i < ht->bucket_size; ++i) {
        Item* item = ht->buckets[i];
        while (item) {
            Item* next_item = item->next;

            unsigned long new_bucket_index = calculate_hash(item->key) % new_bucket_size;

            item->next = new_buckets[new_bucket_index];
            new_buckets[new_bucket_index] = item;

            item = next_item;
        }
    }

    free(ht->buckets);
    ht->buckets = new_buckets;
    ht->bucket_size = new_bucket_size;
}

// put関数
bool hash_table_put(HashTable* ht, const char* key, const char* value) {
    assert(key != NULL);
    hash_table_check_size(ht);

    unsigned long bucket_index = calculate_hash(key) % ht->bucket_size;
    Item* item = ht->buckets[bucket_index];

    while (item) {
        if (strcmp(item->key, key) == 0) {
            free(item->value); // 古い値を解放
            item->value = strdup(value); // 新しい値をコピー
            return false;
        }
        item = item->next;
    }

    Item* new_item = (Item*)malloc(sizeof(Item));
    assert(new_item != NULL);
    new_item->key = strdup(key); // キーをコピー
    new_item->value = strdup(value); // 値をコピー
    new_item->next = ht->buckets[bucket_index];
    ht->buckets[bucket_index] = new_item;
    ht->item_count++;

    if (ht->item_count > ht->bucket_size * 0.7) {
        int new_bucket_size = find_near_prime(ht->bucket_size * 2);
        hash_table_rehash(ht, new_bucket_size);
    }

    return true;
}

// get関数
// Pythonの (value, True/False) タプルを模倣
typedef struct GetResult {
    char* value;
    bool found;
} GetResult;

GetResult hash_table_get(HashTable* ht, const char* key) {
    assert(key != NULL);
    hash_table_check_size(ht);

    unsigned long bucket_index = calculate_hash(key) % ht->bucket_size;
    Item* item = ht->buckets[bucket_index];

    while (item) {
        if (strcmp(item->key, key) == 0) {
            return (GetResult){.value = item->value, .found = true};
        }
        item = item->next;
    }
    return (GetResult){.value = NULL, .found = false};
}

// delete関数
bool hash_table_delete(HashTable* ht, const char* key) {
    assert(key != NULL);
    hash_table_check_size(ht);

    unsigned long bucket_index = calculate_hash(key) % ht->bucket_size;
    Item* item = ht->buckets[bucket_index];
    Item* prev_item = NULL;

    while (item) {
        if (strcmp(item->key, key) == 0) {
            if (prev_item) {
                prev_item->next = item->next;
            } else {
                ht->buckets[bucket_index] = item->next;
            }

            free(item->key);
            free(item->value);
            free(item);
            ht->item_count--;

            if (ht->item_count < ht->bucket_size * 0.3 && ht->bucket_size > 97) {
                int new_bucket_size = find_near_prime(ht->bucket_size / 2);
                hash_table_rehash(ht, new_bucket_size);
            }
            return true;
        }
        prev_item = item;
        item = item->next;
    }
    return false;
}

// size関数
int hash_table_size(HashTable* ht) {
    return ht->item_count;
}

// --- テストコード ---

void functional_test() {
    HashTable* hash_table = create_hash_table(97);

    assert(hash_table_put(hash_table, "aaa", "1") == true);
    GetResult res = hash_table_get(hash_table, "aaa");
    assert(res.found == true && strcmp(res.value, "1") == 0);
    assert(hash_table_size(hash_table) == 1);

    assert(hash_table_put(hash_table, "bbb", "2") == true);
    assert(hash_table_put(hash_table, "ccc", "3") == true);
    assert(hash_table_put(hash_table, "ddd", "4") == true);
    res = hash_table_get(hash_table, "aaa"); assert(res.found == true && strcmp(res.value, "1") == 0);
    res = hash_table_get(hash_table, "bbb"); assert(res.found == true && strcmp(res.value, "2") == 0);
    res = hash_table_get(hash_table, "ccc"); assert(res.found == true && strcmp(res.value, "3") == 0);
    res = hash_table_get(hash_table, "ddd"); assert(res.found == true && strcmp(res.value, "4") == 0);
    res = hash_table_get(hash_table, "a"); assert(res.found == false);
    res = hash_table_get(hash_table, "aa"); assert(res.found == false);
    res = hash_table_get(hash_table, "aaaa"); assert(res.found == false);
    assert(hash_table_size(hash_table) == 4);

    assert(hash_table_put(hash_table, "aaa", "11") == false);
    res = hash_table_get(hash_table, "aaa"); assert(res.found == true && strcmp(res.value, "11") == 0);
    assert(hash_table_size(hash_table) == 4);

    assert(hash_table_delete(hash_table, "aaa") == true);
    res = hash_table_get(hash_table, "aaa"); assert(res.found == false);
    assert(hash_table_size(hash_table) == 3);

    assert(hash_table_delete(hash_table, "a") == false);
    assert(hash_table_delete(hash_table, "aa") == false);
    assert(hash_table_delete(hash_table, "aaa") == false);
    assert(hash_table_delete(hash_table, "aaaa") == false);

    assert(hash_table_delete(hash_table, "ddd") == true);
    assert(hash_table_delete(hash_table, "ccc") == true);
    assert(hash_table_delete(hash_table, "bbb") == true);
    res = hash_table_get(hash_table, "aaa"); assert(res.found == false);
    res = hash_table_get(hash_table, "bbb"); assert(res.found == false);
    res = hash_table_get(hash_table, "ccc"); assert(res.found == false);
    res = hash_table_get(hash_table, "ddd"); assert(res.found == false);
    assert(hash_table_size(hash_table) == 0);

    assert(hash_table_put(hash_table, "abc", "1") == true);
    assert(hash_table_put(hash_table, "acb", "2") == true);
    assert(hash_table_put(hash_table, "bac", "3") == true);
    assert(hash_table_put(hash_table, "bca", "4") == true);
    assert(hash_table_put(hash_table, "cab", "5") == true);
    assert(hash_table_put(hash_table, "cba", "6") == true);
    res = hash_table_get(hash_table, "abc"); assert(res.found == true && strcmp(res.value, "1") == 0);
    res = hash_table_get(hash_table, "acb"); assert(res.found == true && strcmp(res.value, "2") == 0);
    res = hash_table_get(hash_table, "bac"); assert(res.found == true && strcmp(res.value, "3") == 0);
    res = hash_table_get(hash_table, "bca"); assert(res.found == true && strcmp(res.value, "4") == 0);
    res = hash_table_get(hash_table, "cab"); assert(res.found == true && strcmp(res.value, "5") == 0);
    res = hash_table_get(hash_table, "cba"); assert(res.found == true && strcmp(res.value, "6") == 0);
    assert(hash_table_size(hash_table) == 6);

    assert(hash_table_delete(hash_table, "abc") == true);
    assert(hash_table_delete(hash_table, "cba") == true);
    assert(hash_table_delete(hash_table, "bac") == true);
    assert(hash_table_delete(hash_table, "bca") == true);
    assert(hash_table_delete(hash_table, "acb") == true);
    assert(hash_table_delete(hash_table, "cab") == true);
    assert(hash_table_size(hash_table) == 0);
    printf("Functional tests passed!\n");

    free_hash_table(hash_table);
}

void performance_test() {
    HashTable* hash_table = create_hash_table(97);
    double performance_test_begin = get_current_time();

    for (int iteration = 0; iteration < 100; ++iteration) {
        double begin = get_current_time();
        srand(iteration); // Pythonのrandom.seed(iteration)

        for (int i = 0; i < 10000; ++i) {
            int rand_num = custom_rand_int(0, 100000000);
            char key[20]; // 十分なサイズを確保
            sprintf(key, "%d", rand_num);
            hash_table_put(hash_table, key, key);
        }
        srand(iteration); // 再度シードを設定
        for (int i = 0; i < 10000; ++i) {
            int rand_num = custom_rand_int(0, 100000000);
            char key[20];
            sprintf(key, "%d", rand_num);
            hash_table_get(hash_table, key);
        }
        double end = get_current_time();
        printf("%d %.6f\n", iteration, end - begin);
    }

    for (int iteration = 0; iteration < 100; ++iteration) {
        srand(iteration);
        for (int i = 0; i < 10000; ++i) {
            int rand_num = custom_rand_int(0, 100000000);
            char key[20];
            sprintf(key, "%d", rand_num);
            hash_table_delete(hash_table, key);
        }
    }

    assert(hash_table_size(hash_table) == 0);
    double performance_test_end = get_current_time();
    double total_time = performance_test_end - performance_test_begin;
    printf("total_time %.6f\n", total_time);
    printf("Performance tests passed!\n");

    free_hash_table(hash_table);
}

int main() {
    functional_test();
    performance_test();
    return 0;
}