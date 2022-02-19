from statistics import mean, median
import collections
import string

text = input("Enter text: ")
#text = "Some Some Some Some text text text"
#text = "Hello my friend, it's very interesting message,,,,, and I hope you read this.. Maybe... But.. ... I Like unicorns!"
# remove punctuation
text = text.translate(str.maketrans('', '', string.punctuation))

words = text.split()
words.sort()

words_count = dict()

# count of each word in the text
while len(words) > 0:
    curr_word = words[0]
    curr_word_count = words.count(curr_word)
    words_count[curr_word] = curr_word_count
    del words[:curr_word_count]

print(words_count)

# average count
average_count = mean(list(words_count.values()))
print(f"Average count: {round(average_count, 3)}")

# mediana
print(f"Median: {median(list(words_count.values()))}")

# remove spaces
text = text.replace(" ", "")
# calculate ngrams
grams = dict()
def ngrams (text, n = 2):
    if n <= 0:
        return

    for global_i in range(len(text) - n + 1):
        curr_gram = ""
        for i in range(global_i, global_i + n):
            curr_gram += text[i]

        if curr_gram in grams.keys():
            grams[curr_gram] += 1
        else:
            grams[curr_gram] = 1
    return grams

n = int(input("Enter \'n\' param for ngrams: "))
print(f"Ngrams: {ngrams(text, n)}")

#top 10
def print_top_by_value (k = 10):
    global grams

    if k <= 0:
        return

    print(f"Top {k} grams:")
    grams = sorted(grams.items(), key=lambda item: item[1], reverse=True)   
    grams = collections.OrderedDict(grams)
    for i in grams.keys():
        if not k:
            break
        k -= 1
        print(f"\t{i} has {grams[i]} repeats")

k = int(input("Enter top count: "))
print_top_by_value(k)
