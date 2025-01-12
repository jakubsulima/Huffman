class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq


def heapify(arr, n, i):
    smallest = i
    left = 2 * i + 1
    right = 2 * i + 2

    if left < n and arr[left].freq < arr[smallest].freq:
        smallest = left

    if right < n and arr[right].freq < arr[smallest].freq:
        smallest = right

    if smallest != i:
        arr[i], arr[smallest] = arr[smallest], arr[i]
        heapify(arr, n, smallest)


def build_min_heap(arr):
    n = len(arr)
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)


def pop_min(arr):
    last = arr.pop()
    if not arr:
        return last
    root = arr[0]
    arr[0] = last
    heapify(arr, len(arr), 0)
    return root


def push_node(arr, node):
    arr.append(node)
    i = len(arr) - 1
    while i > 0 and arr[(i - 1) // 2].freq > arr[i].freq:
        arr[i], arr[(i - 1) // 2] = arr[(i - 1) // 2], arr[i]
        i = (i - 1) // 2


def read_and_count(filename):
    with open(filename, "r", encoding="utf-8") as file:
        text = file.read()
    frequencies = {}
    for char in text:
        if char in frequencies:
            frequencies[char] += 1
        else:
            frequencies[char] = 1
    return text, frequencies


def build_huffman_tree(frequencies):
    nodes = [Node(char, freq) for char, freq in frequencies.items()]
    build_min_heap(nodes)

    while len(nodes) > 1:
        left = pop_min(nodes)
        right = pop_min(nodes)
        merged = Node(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        push_node(nodes, merged)

    return nodes[0]


def generate_codes(root, current_code="", codes=None):
    if codes is None:
        codes = {}
    if root is None:
        return codes
    if root.char is not None:
        codes[root.char] = current_code
        return codes
    generate_codes(root.left, current_code + "0", codes)
    generate_codes(root.right, current_code + "1", codes)
    return codes


def encode_text(text, codes):
    return "".join(codes[char] for char in text)


def save_encoded_file(encoded_filename, codes_filename, encoded_text, codes):
    padding_length = (8 - len(encoded_text) % 8) % 8
    encoded_text += "0" * padding_length

    byte_array = bytearray(
        int(encoded_text[i : i + 8], 2) for i in range(0, len(encoded_text), 8)
    )

    with open(encoded_filename, "wb") as encoded_file:
        encoded_file.write(bytes([padding_length]))
        encoded_file.write(byte_array)

    with open(codes_filename, "wb") as codes_file:
        codes_binary = b""
        for char, code in codes.items():
            char_binary = char.encode("utf-8")
            code_length = len(code)
            codes_binary += bytes([len(char_binary)]) + char_binary
            codes_binary += bytes([code_length]) + code.encode("utf-8")
        codes_file.write(codes_binary)


def load_encoded_file(encoded_filename, codes_filename):
    with open(encoded_filename, "rb") as encoded_file:
        padding_length = int(encoded_file.read(1)[0])
        encoded_bytes = encoded_file.read()

    encoded_text = "".join(f"{byte:08b}" for byte in encoded_bytes)
    encoded_text = encoded_text[:-padding_length]

    codes = {}
    with open(codes_filename, "rb") as codes_file:
        while True:
            char_length = codes_file.read(1)
            if not char_length:
                break
            char_length = int(char_length[0])
            char = codes_file.read(char_length).decode("utf-8")
            code_length = int(codes_file.read(1)[0])
            code = codes_file.read(code_length).decode("utf-8")
            codes[code] = char

    return encoded_text, codes


def decode_text(encoded_text, codes):
    reverse_codes = {v: k for k, v in codes.items()}
    decoded_text = ""
    buffer = ""
    for bit in encoded_text:
        buffer += bit
        if buffer in reverse_codes:
            decoded_text += reverse_codes[buffer]
            buffer = ""
    return decoded_text


def main():
    input_file = "plik.txt"
    encoded_file = "zaszyfrowany_plik.bin"
    codes_file = "kody_plik.bin"
    decoded_file = "odszyfrowany_plik.txt"

    text, frequencies = read_and_count(input_file)
    root = build_huffman_tree(frequencies)
    codes = generate_codes(root)
    encoded_text = encode_text(text, codes)
    save_encoded_file(encoded_file, codes_file, encoded_text, codes)

    loaded_text, loaded_codes = load_encoded_file(encoded_file, codes_file)
    decoded_text = decode_text(loaded_text, loaded_codes)

    with open(decoded_file, "w", encoding="utf-8") as out:
        out.write(decoded_text)

    assert text == decoded_text, "Decoded text does not match original!"
    print("Huffman encoding/decoding successful.")


if __name__ == "__main__":
    main()
