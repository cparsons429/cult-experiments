from PIL import Image

imFile = "functioning_white_shirt_mask.png"
im = Image.open(imFile, 'r')
print im.mode == 'RGBA'

rgbaData = im.tobytes("raw", "RGBA")
hexData = map(hex, map(ord, rgbaData))

f = open("functioning_white_shirt_rgba.txt", "w+")

for i in range(len(hexData)):
    f.write(str(int(hexData[i], 16)) + ",")

f.close()
