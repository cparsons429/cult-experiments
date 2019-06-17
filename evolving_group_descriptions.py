def find_dist_squared(embedding0, embedding1):
    dist_squared = 0

    for i in range(len(embedding0)):
        dist_squared += (embedding0[i] - embedding1[i]) ** 2

    return dist_squared


print "opening embeddings file"

dictionary = []
embeddings_f = open("embeddings.txt", "r")

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

print "finding market"

market_embedding = []

for encoding in dictionary:
    if encoding["word"] == "market":
        market_embedding = encoding["embedding"]
        break

print "finding ten closest to market"

ten_closest_to_market = []

for i in range(10):
    encoding = {
        "word": "",
        "distance": float("inf")
    }

    ten_closest_to_market.append(encoding)

for encoding in dictionary:
    dist = find_dist_squared(market_embedding, encoding["embedding"])

    if dist < ten_closest_to_market[9]["distance"]:
        # naive search to find where to insert our new word in the list, efficiency is not super important here
        # if only python had linked lists... sigh

        for i in range(10):
            if dist < ten_closest_to_market[i]["distance"]:
                # slide all encodings with greater distance over by one
                for j in range(9, i, -1):
                    ten_closest_to_market[j] = ten_closest_to_market[j - 1]

                # insert this encoding
                ten_closest_to_market[i] = {
                    "word": encoding["word"],
                    "distance": dist
                }

                break

print "closest words to \"market\": distance squared"

for encoding in ten_closest_to_market:
    print encoding["word"] + ": " + str(encoding["distance"])
