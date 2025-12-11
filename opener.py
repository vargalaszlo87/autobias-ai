import lzma

with lzma.open("output/adatok.xz", "rt") as f:   # rt = read text
    for line in f:
        print(line.strip())