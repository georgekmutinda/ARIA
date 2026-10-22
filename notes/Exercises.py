"""def reverse_words(sentence : str) -> str:
    words = sentence.split()
    reversed_words = words[::-1]
    return ' '.join(reversed_words)

print(reverse_words("hello world"))


def count_char_frequency(text: str) -> dict:
    frequency = {}
    for char in text:
        if char in frequency:
            frequency[char] += 1
        else:
            frequency[char] = 1 
    return frequency

print(count_char_frequency("hello world"))

def flatten(nested: list) -> list:
    flat_list = []
    for sublist in nested:
        flat_list.extend(sublist)
    return flat_list

print(flatten([[1, 2], [3, 4], [5, 6]]))
"""
"""
def group_by_length(words: list) -> dict:
    grouped_dict={}
    for word in words:
        length = len(word)
        if length in grouped_dict: 
            grouped_dict[length].append(word)
        else: 
            grouped_dict[length] = [word]
    return grouped_dict

print(group_by_length(["hi", "go", "hello", "world", "python"]))

the key idea is knowing that a dictionary has a key and a value. First we need to identify the key which is the Dictionary_Name[key]. 
In this case the key is the length.
we start with an empty dictionary, iterarte over the words, calculating the length.
Check if the length exists in the dictionary, at start it is a no, else, we add the word to  that length, ie the key. mutation
Dictionary_name["key"] = "value" 
if the key exists we just have to add the word to that key using the append function. 
Also think which is the unique value, since we can have multiple words of the same length, thus that cant be the key, but the length is unique.
"""

def running_average(value: list) -> list:
    averages =[]
    for i  in range(len(value)):
        current = value[i]
        if i == 0:
            avg  = current
            
        avg = current + value[i-1] /2
        averages.append(avg)
    return averages
print(running_average([1, 2, 3, 4]))
        