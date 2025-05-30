def search_anagram(random_word, new_dictionary):
    sorted_ramdom_word = ''.join(sorted(random_word))
    
    anagram = binary_search(sorted_ramdom_word, new_dictionary)
    
    return anagram

def generate_new_dictionary(dictionary):
    new_dictionary = []
    for word in dictionary:
        new_dictionary.append((''.join(sorted(word)), word))
    sorted_new_dictionary = sorted(new_dictionary, key=lambda x: x[0])
    
    return sorted_new_dictionary
        
def binary_search(word, dictionary):
    left = 0
    right = len(dictionary) - 1
    
    while left <= right:
        mid = (left + right) // 2
        
        if dictionary[mid][0] < word:
            left = mid + 1
        elif dictionary[mid][0] > word:
            right = mid - 1
        elif dictionary[mid][0] == word:
            searched_word_list = []
            searched_word_list.append(dictionary[mid][1])
            i = 1
            j = 1
            while dictionary[mid + i][0] == word:
                searched_word_list.append(dictionary[mid + i][1])
                i += 1
            while dictionary[mid - j][0] == word:
                searched_word_list.append(dictionary[mid - j][1])
                j += 1
            return searched_word_list
        
    return

print("検索するアナグラムの個数を教えてください") 
N = input(int())

with open('anagram/words.txt', 'r', encoding='utf-8') as f:
    dictionary = [line.strip() for line in f if line.strip()]

new_dictionary = generate_new_dictionary(dictionary)

for i in range(N):
    word = input()

    if type(word) == str:
        anagram = search_anagram(word, new_dictionary)
        print(anagram)
        
    else: print("error")