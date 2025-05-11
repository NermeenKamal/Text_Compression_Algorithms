import tkinter as tk
from tkinter import ttk, messagebox
from collections import Counter
import heapq

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
    return ' '.join([codes[ch] for ch in text])

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
    return ' '.join([huff_codes[ch] for ch in text])

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

# GUI
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
            "Shannon-Fano Compress",
            "Huffman Compress",
            "LZW Compress",
            "Arithmetic Coding"
        )
        self.lab_menu.current(0)
        self.lab_menu.pack(pady=10)

        tk.Label(root, text="Enter Input:", bg=BG_COLOR, fg=FG_COLOR).pack()
        self.input_text = tk.Text(root, height=4, width=50)
        self.input_text.pack(pady=5)

        tk.Button(root, text="Run", command=self.run_selected_lab, bg=FG_COLOR, fg=BG_COLOR).pack(pady=5)

        tk.Label(root, text="Output:", bg=BG_COLOR, fg=FG_COLOR).pack()
        self.output_text = tk.Text(root, height=6, width=50, state='disabled')
        self.output_text.pack(pady=5)

    def run_selected_lab(self):
        selected_lab = self.lab_var.get()
        input_data = self.input_text.get("1.0", tk.END).strip()
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
                result = shannon_fano_compress(input_data)
            elif selected_lab == "Huffman Compress":
                result = huffman_compress(input_data)
            elif selected_lab == "LZW Compress":
                result = lzw_compress(input_data)
            elif selected_lab == "Arithmetic Coding":
                result = arithmetic_encode(input_data)
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

# Lab 6: Huffman Compress
# Input: ABBC
# Output: 0 10 10 11

# Lab 7: LZW Compress
# Input: ABABABABAB
# Output: 65 66 256 258 260

# Lab 7: Arithmetic Coding
# Input: ABBC
# Output: 0.2265625
