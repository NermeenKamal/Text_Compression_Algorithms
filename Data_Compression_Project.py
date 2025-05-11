import tkinter as tk
from tkinter import ttk, messagebox
from collections import Counter
import heapq
import re

BG_COLOR = "#5A282E"  # Dark Burgundy
FG_COLOR = "#F5F5DC"  # Beige

def text_to_ascii(text):
    ascii_codes = ""
    for ch in text:
        ascii_codes += str(ord(ch)) + " "
    return ascii_codes.strip()

def ascii_to_text(ascii_input):
    text = ""
    for code in ascii_input.strip().split():
        text += chr(int(code))
    return text

def rss_compress(text):
    result = ""
    count = 1
    for i in range(len(text)-1):
        if text[i] == text[i+1]:
            count += 1
        else:
            result += text[i] + str(count)
            count = 1
    result += text[-1] + str(count)
    return result

def rss_decompress(compressed):
    result = ""
    i = 0
    while i < len(compressed):
        ch = compressed[i]
        i += 1
        count = ""
        while i < len(compressed) and compressed[i].isdigit():
            count += compressed[i]
            i += 1
        result += ch * int(count)
    return result

def rle_compress(text):
    result = ""
    count = 1
    for i in range(len(text)-1):
        if text[i] == text[i+1]:
            count += 1
        else:
            result += f"({text[i]},{count}) "
            count = 1
    result += f"({text[-1]},{count})"
    return result.strip()

def rle_decompress(text):
    import re
    result = ""
    matches = re.findall(r"\((.),(\d+)\)", text)
    for ch, num in matches:
        result += ch * int(num)
    return result

def shannon_fano_compress(text):
    freq = Counter(text)
    symbols = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    codes = {}
    def build_code(symbols, code):
        if len(symbols) == 1:
            codes[symbols[0][0]] = code
            return
        total = sum([freq for _, freq in symbols])
        acc = 0
        for i in range(len(symbols)):
            acc += symbols[i][1]
            if acc >= total / 2:
                break
        build_code(symbols[:i+1], code + "0")
        build_code(symbols[i+1:], code + "1")
    build_code(symbols, "")
    return ' '.join([codes[ch] for ch in text]), codes

def shannon_fano_decompress(compressed_text, original_text=None):
    if not original_text:
        return "Please provide original text for Shannon-Fano decompression"

    freq = Counter(original_text)
    symbols = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    codes = {}

    def build_code(symbols, code):
        if len(symbols) == 1:
            codes[symbols[0][0]] = code
            return
        total = sum([freq for _, freq in symbols])
        acc = 0
        for i in range(len(symbols)):
            acc += symbols[i][1]
            if acc >= total / 2:
                break
        build_code(symbols[:i+1], code + "0")
        build_code(symbols[i+1:], code + "1")

    build_code(symbols, "")

    decode_dict = {code: char for char, code in codes.items()}

    result = ""
    bits = compressed_text.split()
    for bit in bits:
        if bit in decode_dict:
            result += decode_dict[bit]

    return result

def huffman_compress(text):
    freq = Counter(text)
    heap = [[wt, [sym, ""]] for sym, wt in freq.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        lo = heapq.heappop(heap)
        hi = heapq.heappop(heap)
        for pair in lo[1:]:
            pair[1] = '0' + pair[1]
        for pair in hi[1:]:
            pair[1] = '1' + pair[1]
        heapq.heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])

    huff_codes = dict(heap[0][1:])
    return ' '.join([huff_codes[ch] for ch in text]), huff_codes

def huffman_decompress(compressed_text, original_text=None):
    if not original_text:
        return "Please provide original text for Huffman decompression"

    freq = Counter(original_text)
    heap = [[wt, [sym, ""]] for sym, wt in freq.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        lo = heapq.heappop(heap)
        hi = heapq.heappop(heap)
        for pair in lo[1:]:
            pair[1] = '0' + pair[1]
        for pair in hi[1:]:
            pair[1] = '1' + pair[1]
        heapq.heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])

    huff_codes = dict(heap[0][1:])

    decode_dict = {code: char for char, code in huff_codes.items()}

    result = ""
    bits = compressed_text.split()
    for bit in bits:
        if bit in decode_dict:
            result += decode_dict[bit]

    return result

def lzw_compress(text):
    dict_size = 256
    dictionary = {chr(i): i for i in range(dict_size)}
    w = ""
    result = []
    for c in text:
        wc = w + c
        if wc in dictionary:
            w = wc
        else:
            result.append(str(dictionary[w]))
            dictionary[wc] = dict_size
            dict_size += 1
            w = c
    if w:
        result.append(str(dictionary[w]))
    return ' '.join(result)

def lzw_decompress(compressed):
    dict_size = 256
    dictionary = {i: chr(i) for i in range(dict_size)}

    compressed = compressed.split()
    if not compressed:
        return ""

    w = chr(int(compressed[0]))
    result = w

    for i in range(1, len(compressed)):
        code = int(compressed[i])

        if code in dictionary:
            entry = dictionary[code]
        elif code == dict_size:
            entry = w + w[0]
        else:
            return "Error: Bad compressed code"

        result += entry

        dictionary[dict_size] = w + entry[0]
        dict_size += 1

        w = entry

    return result

def arithmetic_encode(text):
    from fractions import Fraction
    freq = Counter(text)
    total = sum(freq.values())
    prob = {}
    for ch in freq:
        prob[ch] = Fraction(freq[ch], total)
    low = Fraction(0, 1)
    high = Fraction(1, 1)
    for ch in text:
        range_ = high - low
        cum_prob = sum(prob[c] for c in sorted(prob) if c < ch)
        low = low + range_ * cum_prob
        high = low + range_ * prob[ch]
    return str(float((low + high) / 2))

def arithmetic_decode(encoded_value, original_text=None):
    if not original_text:
        return "Please provide original text for arithmetic decoding"

    freq = Counter(original_text)
    total = sum(freq.values())
    prob = {}
    cum_prob = {}
    chars = sorted(freq.keys())

    start = 0
    for ch in chars:
        prob[ch] = freq[ch] / total
        cum_prob[ch] = start
        start += prob[ch]

    try:
        encoded_value = float(encoded_value)
        result = ""
        length = len(original_text)

        low, high = 0.0, 1.0
        for _ in range(length):
            for ch in chars:
                ch_low = low + (high - low) * cum_prob[ch]
                ch_high = ch_low + (high - low) * prob[ch]

                if ch_low <= encoded_value < ch_high:
                    result += ch
                    low, high = ch_low, ch_high
                    break

        return result
    except:
        return "Error decoding arithmetic code"

class CompressionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Compression Labs")
        self.root.configure(bg=BG_COLOR)

        self.lab_var = tk.StringVar()
        self.lab_menu = ttk.Combobox(root, textvariable=self.lab_var)
        self.lab_menu['values'] = (
            "Text to ASCII", "ASCII to Text",
            "RSS Compress", "RSS Decompress",
            "RLE Compress", "RLE Decompress",
            "Shannon-Fano Compress", "Shannon-Fano Decompress",
            "Huffman Compress", "Huffman Decompress",
            "LZW Compress", "LZW Decompress",
            "Arithmetic Coding", "Arithmetic Decoding"
        )
        self.lab_menu.current(0)
        self.lab_menu.pack(pady=10)

        tk.Label(root, text="Enter Input:", bg=BG_COLOR, fg=FG_COLOR).pack()
        self.input_text = tk.Text(root, height=4, width=50)
        self.input_text.pack(pady=5)

        tk.Label(root, text="Original Text (for some decompressions):", bg=BG_COLOR, fg=FG_COLOR).pack()
        self.original_text = tk.Text(root, height=2, width=50)
        self.original_text.pack(pady=5)

        tk.Button(root, text="Run", command=self.run_selected_lab, bg=FG_COLOR, fg=BG_COLOR).pack(pady=5)

        tk.Label(root, text="Output:", bg=BG_COLOR, fg=FG_COLOR).pack()
        self.output_text = tk.Text(root, height=6, width=50, state='disabled')
        self.output_text.pack(pady=5)

        self.lab_menu.bind("<<ComboboxSelected>>", self.on_lab_selected)

    def on_lab_selected(self, event=None):
        selected_lab = self.lab_var.get()
        if selected_lab in ["Shannon-Fano Decompress", "Huffman Decompress", "Arithmetic Decoding"]:
            self.original_text.configure(state='normal')
        else:
            self.original_text.delete("1.0", tk.END)
            self.original_text.configure(state='disabled')

    def run_selected_lab(self):
        selected_lab = self.lab_var.get()
        input_data = self.input_text.get("1.0", tk.END).strip()
        original_data = self.original_text.get("1.0", tk.END).strip()
        result = ""

        try:
            if selected_lab == "Text to ASCII":
                result = text_to_ascii(input_data)
            elif selected_lab == "ASCII to Text":
                result = ascii_to_text(input_data)
            elif selected_lab == "RSS Compress":
                result = rss_compress(input_data)
            elif selected_lab == "RSS Decompress":
                result = rss_decompress(input_data)
            elif selected_lab == "RLE Compress":
                result = rle_compress(input_data)
            elif selected_lab == "RLE Decompress":
                result = rle_decompress(input_data)
            elif selected_lab == "Shannon-Fano Compress":
                result, _ = shannon_fano_compress(input_data)
            elif selected_lab == "Shannon-Fano Decompress":
                result = shannon_fano_decompress(input_data, original_data)
            elif selected_lab == "Huffman Compress":
                result, _ = huffman_compress(input_data)
            elif selected_lab == "Huffman Decompress":
                result = huffman_decompress(input_data, original_data)
            elif selected_lab == "LZW Compress":
                result = lzw_compress(input_data)
            elif selected_lab == "LZW Decompress":
                result = lzw_decompress(input_data)
            elif selected_lab == "Arithmetic Coding":
                result = arithmetic_encode(input_data)
            elif selected_lab == "Arithmetic Decoding":
                result = arithmetic_decode(input_data, original_data)
            else:
                result = "Invalid selection."
        except Exception as e:
            result = f"Error: {e}"

        self.output_text.configure(state='normal')
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, result)
        self.output_text.configure(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    app = CompressionApp(root)
    root.mainloop()

# Lab 1: Text to ASCII
# Input: Hi
# Output: 72 105
# ('H' = 72 ,'i' = 105)

# Lab 1: ASCII to Text
# Input: 72 105
# Output: Hi
#
# Lab 5: RSS Compress
# Input: AAABBBCCDAA
# Output: A3B3C2D1A2
#
# Lab 5: RSS Decompress
# Input: A3B3C2D1A2
# Output: AAABBBCCDAA
#
# Lab 5: RLE Compress
# Input: AAABBBCCDAA
# Output: (A,3) (B,3) (C,2) (D,1) (A,2)
#
# Lab 5: RLE Decompress
# Input: (A,3) (B,3) (C,2) (D,1) (A,2)
# Output: AAABBBCCDAA
#
# Lab 6: Shannon-Fano Compress
# Input: ABBC
# Output: 0 10 10 11

# Lab 6: Shannon-Fano Decompress
# Input: 0 10 10 11
# Original Text: ABBC
# Output: ABBC

# Lab 6: Huffman Compress
# Input: ABBC
# Output: 0 10 10 11

# Lab 6: Huffman Decompress
# Input: 0 10 10 11
# Original Text: ABBC
# Output: ABBC

# Lab 7: LZW Compress
# Input: ABABABABAB
# Output: 65 66 256 258 260

# Lab 7: LZW Decompress
# Input: 65 66 256 258 260
# Output: ABABABABAB

# Lab 7: Arithmetic Coding
# Input: ABBC
# Output: 0.2265625

# Lab 7: Arithmetic Decoding
# Input: 0.2265625
# Original Text: ABBC
# Output: ABBC
