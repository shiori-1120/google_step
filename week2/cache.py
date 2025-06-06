import sys, math

# Implement a data structure that stores the most recently accessed N pages.
# See the below test cases to see how it should work.
#
# Note: Please do not use a library like collections.OrderedDict). The goal is
#       to implement the data structure yourself!

def calculate_hash(key):
    assert type(key) == str
    hash = 0
    for i, x in enumerate(key):
        hash += ord(x) * 100 ** i
    return hash

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

class Item:
    def __init__(self, key, value, cache_next, cache_prev, item_next):
        assert type(key) == str
        self.key = key
        self.value = value
        self.cache_next = cache_next
        self.cache_prev = cache_prev
        self.item_next = item_next

class Cache:
    # Initialize the cache.
    # |n|: The size of the cache.
    def __init__(self, n):
        self.bucket_size = 2*n
        self.buckets = [None] * self.bucket_size
        self.item_count = 0
        self.head = None
        self.tail = None
        

    # Access a page and update the cache so that it stores the most recently
    # accessed N pages. This needs to be done with mostly O(1).
    # |url|: The accessed URL
    # |contents|: The contents of the URL
    # 2回目のアクセス処理がうまくいってない
    def access_page(self, url, contents):
        # print(url, contents)
        assert type(url) == str
        bucket_index = calculate_hash(url) % self.bucket_size
        item = self.buckets[bucket_index]
        while item:
            if item.key == url:
                item.cache_prev = item.cache_next
                tmp_head = self.head
                self.head = item
                item.cache_next = tmp_head
                return
            
            item = item.next
        new_item = Item(url, contents, self.head, None, self.buckets[bucket_index])
        # print("new item", url, contents, self.head, None, self.buckets[bucket_index])
        self.buckets[bucket_index] = new_item
        

        if self.head:
            tmp_head = self.head
            tmp_tail = self.tail
            
            tmp_head.prev = new_item
            
            self.head = new_item
            if self.item_count > 1:
                self.tail = tmp_tail.cache_prev

            new_item.cache_next = tmp_head

        else:
            self.head = new_item
            self.tail = new_item
        return
        

    # Return the URLs stored in the cache. The URLs are ordered in the order
    # in which the URLs are mostly recently accessed.
    def get_pages(self):
        print(self.head)
        item = self.head
        url_list = []
        while item:
            print("item", item)
            url_list.append(item.key)
            item = item.cache_next
            print("url_list", url_list)
        return url_list


def cache_test():
    # Set the size of the cache to 4.
    cache = Cache(4)

    # Initially, no page is cached.
    assert cache.get_pages() == []

    # Access "a.com".
    cache.access_page("a.com", "AAA")
    # "a.com" is cached.
    assert cache.get_pages() == ["a.com"]

    # Access "b.com".
    cache.access_page("b.com", "BBB")
    # The cache is updated to:
    #   (most recently accessed)<-- "b.com", "a.com" -->(least recently accessed)
    assert cache.get_pages() == ["b.com", "a.com"]

    # Access "c.com".
    cache.access_page("c.com", "CCC")
    # The cache is updated to:
    #   (most recently accessed)<-- "c.com", "b.com", "a.com" -->(least recently accessed)
    assert cache.get_pages() == ["c.com", "b.com", "a.com"]

    # Access "d.com".
    cache.access_page("d.com", "DDD")
    # The cache is updated to:
    #   (most recently accessed)<-- "d.com", "c.com", "b.com", "a.com" -->(least recently accessed)
    assert cache.get_pages() == ["d.com", "c.com", "b.com", "a.com"]

    # Access "d.com" again.
    cache.access_page("d.com", "DDD")
    # The cache is updated to:
    #   (most recently accessed)<-- "d.com", "c.com", "b.com", "a.com" -->(least recently accessed)
    assert cache.get_pages() == ["d.com", "c.com", "b.com", "a.com"]

    # Access "a.com" again.
    cache.access_page("a.com", "AAA")
    # The cache is updated to:
    #   (most recently accessed)<-- "a.com", "d.com", "c.com", "b.com" -->(least recently accessed)
    assert cache.get_pages() == ["a.com", "d.com", "c.com", "b.com"]

    cache.access_page("c.com", "CCC")
    assert cache.get_pages() == ["c.com", "a.com", "d.com", "b.com"]
    cache.access_page("a.com", "AAA")
    assert cache.get_pages() == ["a.com", "c.com", "d.com", "b.com"]
    cache.access_page("a.com", "AAA")
    assert cache.get_pages() == ["a.com", "c.com", "d.com", "b.com"]

    # Access "e.com".
    cache.access_page("e.com", "EEE")
    # The cache is full, so we need to remove the least recently accessed page "b.com".
    # The cache is updated to:
    #   (most recently accessed)<-- "e.com", "a.com", "c.com", "d.com" -->(least recently accessed)
    assert cache.get_pages() == ["e.com", "a.com", "c.com", "d.com"]

    # Access "f.com".
    cache.access_page("f.com", "FFF")
    # The cache is full, so we need to remove the least recently accessed page "c.com".
    # The cache is updated to:
    #   (most recently accessed)<-- "f.com", "e.com", "a.com", "c.com" -->(least recently accessed)
    assert cache.get_pages() == ["f.com", "e.com", "a.com", "c.com"]

    # Access "e.com".
    cache.access_page("e.com", "EEE")
    # The cache is updated to:
    #   (most recently accessed)<-- "e.com", "f.com", "a.com", "c.com" -->(least recently accessed)
    assert cache.get_pages() == ["e.com", "f.com", "a.com", "c.com"]

    # Access "a.com".
    cache.access_page("a.com", "AAA")
    # The cache is updated to:
    #   (most recently accessed)<-- "a.com", "e.com", "f.com", "c.com" -->(least recently accessed)
    assert cache.get_pages() == ["a.com", "e.com", "f.com", "c.com"]

    print("Tests passed!")


if __name__ == "__main__":
    cache_test()
