ORIGINAL_EMBEDDINGS_FILE = "embeddingsOriginal.txt"  # file with pre-trained word embeddings
TOP_WORDS_FILE = "google10000EnglishUsa.txt"  # list of Google's 10000 most frequent english (usa) words, in order
TRUNCATED_EMBEDDINGS_FILE = "embeddings.txt"  # updated file with only encodings for most frequently used words

# naive approach, we don't really care about efficiency here because this script is only going to be run once
# first, get all encodings from the original embeddings file

dictionary = []
orig_embeddings_f = open(ORIGINAL_EMBEDDINGS_FILE, "r")

print "encoding embeddings"

while True:
    # if only python had do while loops... sigh

    next_line = orig_embeddings_f.readline()
    vals = next_line.split()

    try:
        encoding = {
            "word": vals.pop(0),
            "embedding": []
        }
    except:
        # if that fails, we've reached EOF
        break

    for val in vals:
        encoding["embedding"].append(float(val))

    dictionary.append(encoding)

orig_embeddings_f.close()

# second, for each word in the top words file, find its corresponding embedding and save it to a truncated dict

trunc_dictionary = []
top_words_f = open(TOP_WORDS_FILE, "r")
next_line = "a"

print "truncating embeddings"
i = 0

while next_line != "":
    # if only python had do while loops... sigh

    next_line = top_words_f.readline()

    for j in range(len(dictionary)):
        if dictionary[j]["word"] == next_line.rstrip("\n"):
            trunc_dictionary.append(dictionary.pop(j))
            break

    if i % 100 == 0:
        print i

    i += 1

top_words_f.close()

# third, write our truncated dictionary to a truncated embeddings file

print "saving embeddings"

trunc_embeddings_f = open(TRUNCATED_EMBEDDINGS_FILE, "w")

for encoding in trunc_dictionary:
    save_str = encoding["word"]

    for index in encoding["embedding"]:
        save_str += " " + str(index)

    trunc_embeddings_f.write(save_str + "\n")

trunc_embeddings_f.close()

print "embeddings saved"
