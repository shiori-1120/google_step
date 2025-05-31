def upgrade_search_anagram(random_word, new_dictionary):
    ramdom_word_hashmap_list = [] 
    for word_item in random_word:
        ramdom_word_hashmap_list.append(make_alphabet_hashmap(word_item))

    final_anagram_lists = []

    for hash_table in ramdom_word_hashmap_list:
        max_score = 0
        max_score_list = []
        
        for dictionary_hash_table in new_dictionary:
            for char_needed, count_needed in dictionary_hash_table[0].items():
                if hash_table.get(char_needed, 0) < count_needed:
                    break
            else: 
                current_word_score = get_word_score(dictionary_hash_table[0])
                
                if current_word_score > max_score:
                    max_score = current_word_score
                    max_score_list = [dictionary_hash_table[1]]
                # elif current_word_score == max_score:
                #     max_score_list.append(dictionary_hash_table[1])
        
        final_anagram_lists += max_score_list

    return final_anagram_lists

def get_word_score(word_hash_table):
    scores_list = [1, 3, 2, 2, 1, 3, 3, 1, 1, 4, 4, 2, 2, 1, 1, 3, 4, 1, 1, 1, 2, 3, 3, 4, 3, 4]
    
    score = 0
    for char, count in word_hash_table.items():
        char_index = ord(char) - ord('a')     
        score += count * scores_list[char_index]
    return score

def make_alphabet_hashmap(word):
    hash_table = {}
    for char in word:
        if char in  hash_table:
            hash_table[char] += 1
        else:
            hash_table[char] = 1
    return hash_table

with open('words.txt', 'r', encoding='utf-8') as f:
    dictionary = [line.strip() for line in f if line.strip()]
    
new_dictionary = []
for word in dictionary:
    new_dictionary.append([make_alphabet_hashmap(word), word])

with open('large.txt', 'r', encoding='utf-8') as f:
    word = [line.strip() for line in f if line.strip()]

anagram_lists = upgrade_search_anagram(word, new_dictionary)
print(anagram_lists)

str_ = '\n'.join(anagram_lists)
with open("large_answer_test.txt", 'wt') as f:
    f.write(str_)