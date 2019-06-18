import numpy.random as rnd
import time


DESCRIPTION_LEN = 10  # number of words in a description
NUM_CLOSE_WORDS = 10  # number of "closest words" to find for each word in a description
POWER_LAW_CONST = 5  # used for calculating the new word to which a given word in a description will mutate
ZIPF_LAW_CONST = 1.01  # used to begin with initial words that are more frequently used, just needs to be close to 1
NUM_MUTANTS = 5  # number of mutated descriptions to be shown at each step of evolution
EMBEDDINGS_FILE = "embeddings.txt"  # file with pre-trained word embeddings
SAVED_DESCRIPTIONS_FILE = "savedDescriptions.txt"  # file with the descriptions that users have saved


def dist_sqr(embedding0, embedding1):
    # compute the square of the euclidean distance between one embedding and another
    dist_squared = 0

    for i in range(len(embedding0)):
        dist_squared += (embedding0[i] - embedding1[i]) ** 2

    return dist_squared


def binary_search(val, list, lowest_pos=0):
    # simple binary search for an ordered list
    mid = len(list) / 2

    if len(list) == 0:
        return lowest_pos
    elif val < list[mid]:
        return binary_search(val, list[0: mid], lowest_pos)
    else:
        return binary_search(val, list[mid + 1:], lowest_pos + mid + 1)


def generate_first_descriptions(dictionary):
    # randomly generate a set of first descriptions
    first_descriptions = []

    for i in range(NUM_MUTANTS):
        first_desc = []

        # randomly appending words from the dictionary
        for j in range(DESCRIPTION_LEN):
            zipf_val = rnd.zipf(ZIPF_LAW_CONST)

            while zipf_val > len(dictionary):
                # just in case our zipf value is absurdly big
                zipf_val = rnd.zipf(ZIPF_LAW_CONST)

            first_desc.append(dictionary[int(zipf_val) - 1])

        first_descriptions.append(first_desc)

    return first_descriptions


def get_first_descriptions(dictionary):
    # start with other users' saved descriptions
    saved_descriptions = []
    unencoded_descriptions = []
    first_descriptions = [[{"word": "", "embedding": []} for j in range(DESCRIPTION_LEN)] for i in range(NUM_MUTANTS)]

    next_line = "a"

    while next_line != "":
        # if only python had do while loops... sigh
        next_line = saved_descriptions_f.readline()
        next_desc = next_line.strip().split(",")[1]  # we only want to print the description, not its timestamp
        saved_descriptions.append(next_desc.split())  # each array in saved_descriptions contains a description's words

    # randomly choosing descriptions from this list of saved descriptions
    for i in range(NUM_MUTANTS):
        unencoded_descriptions.append(dictionary[int(rnd.uniform(0, len(saved_descriptions)))])

    # now we just need to encode these descriptions, then we have our first set of descriptions!
    for encoding in dictionary:
        for i in range(NUM_MUTANTS):
            for j in range(DESCRIPTION_LEN):
                # if this encoding matches one of our unencoded words, insert this encoded word into first_descriptions
                if encoding["word"] == unencoded_descriptions[i][j]:
                    first_descriptions[i][j] = encoding

    return first_descriptions


def mutate_description(dictionary, description):
    # create mutants of a given description
    # first, we generate a 2d array of the closest words to each of the words in the description
    closest_words = []
    for i in range(DESCRIPTION_LEN):
        # each array consists of the (NUM_CLOSE_WORDS)-closest encodings to the given word
        closest = []

        for j in range(NUM_CLOSE_WORDS):
            # each encoding contains the new word, its embedding, and its distance from the given word
            encoding = {
                "word": "",
                "embedding": [],
                "distance": float("inf")
            }

            closest.append(encoding)

        closest_words.append(closest)

    # second, we run through all the encodings in the dictionary, finding our closest words
    for encoding in dictionary:
        # find the distance from this encoding to each of our description words
        distances = [dist_sqr(encoding["embedding"], description[i]["embedding"]) for i in range(DESCRIPTION_LEN)]

        for i in range(DESCRIPTION_LEN):
            # if the distance from this encoding to any one of our description words makes it one of the
            # (NUM_CLOSEST_WORDS)-closest words to that description word, we'll update the list of closest words to
            # that description word
            if distances[i] < closest_words[i][NUM_CLOSE_WORDS - 1]["distance"]:
                # find the position where this new word belongs
                pos = binary_search(distances[i], [close_word["distance"] for close_word in closest_words[i]])

                # slide over all following "close words"
                for j in range(NUM_CLOSE_WORDS - 1, pos, -1):
                    closest_words[i][j] = closest_words[i][j - 1]

                # insert this "close word"
                closest_words[i][pos] = {
                    "word": encoding["word"],
                    "embedding": encoding["embedding"],
                    "distance": distances[i]
                }

    # third, we create mutated descriptions based on the "close words" to each word in the description
    mutated_descriptions = []

    for i in range(NUM_MUTANTS):
        # create the specified number of mutated descriptions
        mutated_desc = []

        for j in range(DESCRIPTION_LEN):
            # randomly select a word from the closest words, using a power law distribution
            # this gives greater probability of selection to closer words, especially to the same word itself
            selected_word_float = NUM_CLOSE_WORDS * (1 - rnd.power(POWER_LAW_CONST))
            selected_word = closest_words[j][int(selected_word_float)]

            # put this randomly selected word in the mutated description
            mutated_desc.append({
                "word": selected_word["word"],
                "embedding": selected_word["embedding"]
            })

        mutated_descriptions.append(mutated_desc)

    return mutated_descriptions

print "opening embeddings files"

dictionary = []
embeddings_f = open(EMBEDDINGS_FILE, "r")

print "encoding embeddings"

while True:
    # if only python had do while loops... sigh

    next_line = embeddings_f.readline()
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

embeddings_f.close()

print "beginning program\n"

print "welcome to \"evolving phrases\"!"
print "to play, a set of phrases will appear, with numbers next to them"
print "choose the most interesting phrase, type its number, and press enter\n"

print "then, a *new* set of phrases will evolve from the phrase you just chose"
print "repeat the same thing - pick the most interesting phrase, and keep on going!"
print "when you're bored and want to exit, just type \"x\", and press enter\n"

print "and one last thing!"
print "if you have a particularly interesting phrase appear, type a star before typing its number"
print "like \"*6\""
print "that phrase will then be saved for future players!\n"

print "let's begin..."

beginning_descs = raw_input("\ntype \"a\" and press enter if you want to start with randomly generated phrases, " +
                            "or type \"b\" and press enter if you want to start with other players' saved phrases: ")

# we only break out when we have a valid answer to the previous question
while True:
    beginning_descs.strip("\"")

    if beginning_descs == "a" or beginning_descs == "A":
        descriptions = generate_first_descriptions(dictionary)
        print
        break
    elif beginning_descs == "b" or beginning_descs == "B":
        print "\nloading saved phrases"

        saved_descriptions_f = open(SAVED_DESCRIPTIONS_FILE, "r")
        descriptions = get_first_descriptions(dictionary)  # this could take a little bit, so we warn user about delay
        saved_descriptions_f.close()

        print "ready to play!\n"

        break
    else:
        beginning_descs = raw_input("invalid input! please type \"a\" or \"b\": ")

still_playing = True
saved_descriptions_f = open(SAVED_DESCRIPTIONS_FILE, "w")

# we only break out when the user indicates they want to exit
while still_playing:
    save = False

    # printing out the descriptions
    for i in range(NUM_MUTANTS):
        description_str = str(i) + ": "

        for encoding in descriptions[i]:
            description_str += encoding["word"] + " "

        print description_str

    next_desc = raw_input("\nmost interesting phrase: ")

    # we only break out when we have a valid answer to the previous question
    while True:
        next_desc.strip("\"")

        if next_desc == "x" or next_desc == "X":
            still_playing = False
            break
        else:
            # we begin by noting whether the user wants to save this description
            # note that if they input something invalid, if
            # (a) the first element is a star, trimming it won't make the whole thing valid and
            # (b) if the first element isn't a star, trimming the first element will still keep the whole thing invalid
            if "*" in next_desc:
                next_desc = next_desc[1:]
                save = True

            # now to see if they input something valid
            try:
                chosen_desc = int(next_desc)

                # if input could be converted to an int, and the int is in the correct range, we're good to go
                if -1 < chosen_desc < NUM_MUTANTS:
                    print "\nevolving phrases"

                    # if the user wants us to save this description, write it with the following format:
                    # unix timestamp, description
                    if save:
                        save_str = str(time.time()) + ", "

                        for encoding in descriptions[chosen_desc]:
                            save_str += encoding["word"] + " "

                        save_str.rstrip()  # trim trailing space
                        saved_descriptions_f.write(save_str)

                    descriptions = mutate_description(dictionary, descriptions[chosen_desc])

                    print "phrases evolved\n"
                    break
                else:
                    next_desc = raw_input("invalid response - please write a number from 0 to " + str(NUM_MUTANTS - 1) +
                                          ", with a \"*\" before the number if you want to save that phrase: ")
            except:
                next_desc = raw_input("invalid response - please write a number from 0 to " + str(NUM_MUTANTS - 1) +
                                      ", with a \"*\" before the number if you want to save that phrase: ")

saved_descriptions_f.close()
print "\nthanks for playing :)"
