def search_anagram(random_word, dictionary):
    sorted_ramdom_word = sorted(random_word)
    
    new_dictionary = []
    for word in dictionary:
        new_dictionary.append((sorted(word), word))
    sorted_new_dictionary=sorted(new_dictionary, key=lambda x: x[1])
    anagram = binary_sort(sorted_ramdom_word, sorted_new_dictionary)
    
    return anagram
        
def binary_search(word, dictionary):
    
    