import ast
import tkinter as tk
from tkinter import ttk, messagebox
from collections import Counter
import heapq
import re  # regular expression : search in text

BG_COLOR = "#5A282E"  # Dark Burgundy
FG_COLOR = "#F5F5DC"  # Beige

# Lab 1: Text to ASCII
def text_to_ascii(text):
    ascii_codes = ""
    for ch in text:
        ascii_codes += str(ord(ch)) + " "  # ord -> ASCII_code_number
    return ascii_codes.strip() # remove spaces

# Lab 1: ASCII to Text
def ascii_to_text(ascii_input):
    text = ""
    for code in ascii_input.strip().split():  # remove spaces in start and end,
                                       # split to seperated numbers
        text += chr(int(code))
    return text

# Lab 5: RSS Compress
def rss_compress(text):
    result = ""
    count = 1 # count repeats
    for i in range(len(text)-1): # AAA BB -> A3 B2
        if text[i] == text[i+1]:
            count += 1
        else:
            result += text[i] + str(count) # A + string(3)
            count = 1 # to move for another character count
    result += text[-1] + str(count)  # add last char and its count لان العداد ينتهي قبل اضافة اخر حرف
    return result

# Lab 5: RSS Decompress
def rss_decompress(compressed):
    result = ""
    i = 0
    while i < len(compressed):
        ch = compressed[i]
        i += 1 # نروح على الرقم اللي بعد الحرف
        count = "" # variable to store number
        while i < len(compressed) and compressed[i].isdigit():
            count += compressed[i]  # بمشي على الارقام اللي بعد الحرف و بخزنهم
            i += 1
        result += ch * int(count) # a * 12 concatenation
    return result

# Lab 5: RLE Compress
def rle_compress(text):
    result = ""
    count = 1
    for i in range(len(text)-1):
        if text[i] == text[i+1]: # A A A B B C C C
            count += 1 # count repeat
        else:
            result += f"({text[i]},{count}) " # concatenation (,) pairs
            count = 1
    result += f"({text[-1]},{count})" # last char with last repeat (,)
    return result.strip() #remove_white_spaces

# Lab 5: RLE Decompress
def rle_decompress(text):
    result = ""                  # d+ -> عدد مكون من رقم او اكثر
    matches = re.findall(r"\((.),(\d+)\)", text) # (.) -> حرف واحد داخل القوس
    for ch, num in matches:  # matches -> بيفصل بين char, num
        result += ch * int(num) # A * 3 , concatenation +=
    return result

# Lab 6: Shannon-Fano Compress
def shannon_fano_compress(text):
    freq = Counter(text)  # Counter function from collections libray to count frequency
    # "ABBC" → {'A': 1, 'B': 2, 'C': 1}
    symbols = sorted(freq.items(), key=lambda x: x[1], reverse=True)  # [('B', 2), ('A', 1), ('C', 1)]
    codes = {}  # codebook

    def build_code(symbols, code):  # recursive
        if len(symbols) == 1:     # if one symbol -> send code to it
            codes[symbols[0][0]] = code
            return
        total = sum(freq for _, freq in symbols) # [(B,4), (A,2), (C,1)] → total = 4 + 2 + 1 = 7
        acc = 0  # to split list into two parts
        for i in range(len(symbols)):  # search for split point
            acc += symbols[i][1]  # i = 0 → acc = 0 + 4 = 4   -> 4 is for B(i=0)
            if acc >= total / 2:  # اكبر من 7.5
                break
        build_code(symbols[:i+1], code + '0') # first half left  # [('B', 4)]
        build_code(symbols[i+1:], code + '1') # second half right # [('A', 2), ('C', 1)]

    build_code(symbols, "")
    encoded_string = ''.join([codes[ch] for ch in text])

    # return encoded bits and the codebook (for decompression)
    return f"Encoded: {encoded_string}\nCodebook: {codes}", codes

# Lab 6: Shannon-Fano Decompress
def shannon_fano_decompress(encoded_string, codebook_str):
    import ast # ast.literal_eval  -> convert string to dictionary
    try:
        codebook = ast.literal_eval(codebook_str) # {'A': '0', 'B': '10'} → {'0': 'A', '10': 'B'}
        reverse_codebook = {v: k for k, v in codebook.items()} # to search by code not char
    except:
        return "Invalid codebook format"

    result = ""
    buffer = ""
    for bit in encoded_string:  # بنمشي على ال binary بال bits
        buffer += bit # يجمه الbits ورا بعضه
        if buffer in reverse_codebook: # اول ما الكود يكون كود موجود ف الcodebook
            result += reverse_codebook[buffer] # يجيب الحرف الموازي و يعمل concatenation
            buffer = ""  # نصفر الbuffer
    return result

# Lab 6: Huffman Compress
def huffman_compress(text):
    freq = Counter(text)
    heap = [[wt, [sym, ""]] for sym, wt in freq.items()] # الوزن (التكرار) , الرمز + كوده (فارغ حالياً)
    heapq.heapify(heap) # قائمة اولية Min Heap(tree)
    while len(heap) > 1: # بناء الشجرة
        lo = heapq.heappop(heap) # نسحب أصغر عنصرين (الأقل تكرارًا)
        hi = heapq.heappop(heap)
        for pair in lo[1:]:
            pair[1] = '0' + pair[1] # العناصر اليسار تأخذ 0
        for pair in hi[1:]:
            pair[1] = '1' + pair[1] # العناصر اليمين تأخذ 1
        heapq.heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:]) # نعيدهم للـ heap كnode جديدة: الوزن = مجموع التكرارات
    huff_codes = dict(heap[0][1:]) #نستخرج جدول الأكواد النهائية
    compressed = ' '.join(huff_codes[ch] for ch in text)
    return compressed, huff_codes

# Lab 6: Huffman Decompress
def huffman_decompress(compressed_text, codebook):
    decode_dict = {v: k for k, v in codebook.items()} #نسخة معكوسة من قاموس الترميز
    result = ""                           # {'A': '0', 'B': '10', 'C': '11'} BECOMES {'0': 'A', '10': 'B', '11': 'C'}
    for bit in compressed_text.split(): # يقسم النص المدخل عند المسافات البيضا "0 10 10 11" -> ["0", "10", "10", "11"]
        if bit in decode_dict:
            result += decode_dict[bit]
    return result

# Lab 7: LZW Compress
def lzw_compress(text):
    dict_size = 256 # عدد الرموز ف ال ASCII Code
    dictionary = {chr(i): i for i in range(dict_size)} # create  قاموس أولي -> key=char, value=code_num
    w = ""   # current اللي بيتم معالجته               # 'A': 65, 'B': 66, ...
    result = []  # قائمة تخزن رموز الضغط
    for c in text:
        wc = w + c # نمط مركب = نمط قديم + نمط حالي -> بيكون string concatenation
        if wc in dictionary: # نتحقق إذا كان هذا النمط المركب موجوداً بالفعل في القاموس
            w = wc # نحدث النمط الحالي ليصبح هو النمط المركب للبحث عن أنماط أطول
        else: # لو النمط مش موجود
            result.append(str(dictionary[w])) # نضيف رمز النمط الحالي w إلى result
            dictionary[wc] = dict_size  # نضيف النمط المركب الجديد wc إلى القاموس مع رمز جديد
            dict_size += 1
            w = c # نعيد تعيين w ليكون الحرف الحالي c فقط
    if w:
        result.append(str(dictionary[w]))  # لو انتهت الloop ولسه موجود w نضيفه
    return ' '.join(result)

# Lab 7: LZW Decompress
def lzw_decompress(compressed):  # single char -> 0-255 , code >= 256
    dict_size = 256 # dictionary
    dictionary = {i: chr(i) for i in range(dict_size)} # 65: A , 66: B
    compressed = compressed.split()  # split into list of symbols
    if not compressed:
        return ""
    w = chr(int(compressed[0]))  # start = تحويل اول رمز الى حرف
    result = w
    for i in range(1, len(compressed)):  # start from the second symbol
        code = int(compressed[i]) # تحويل الرمز من سلسلة نصية إلى رقم
        if code in dictionary:
            entry = dictionary[code] # نطلع الحرف المقابل للرمز
        elif code == dict_size: # special case when الرمز هو نفس الرمز التالي
            entry = w + w[0] # سلسة = current + first char
        else:
            return "Error: Bad compressed code"
        result += entry
        dictionary[dict_size] = w + entry[0]
        dict_size += 1
        w = entry
    return result

# Lab 7: Arithmetic Coding
def create_cumulative_ranges(probabilities):
    cum_ranges = {}
    start = 0.0
    for symbol, prob in probabilities.items():
        cum_ranges[symbol] = (start, start + prob)
        start += prob
    return cum_ranges

def improved_arithmetic_encode(text):
    freq = Counter(text)
    total = sum(freq.values())
    probabilities = {ch: freq[ch]/total for ch in freq}

    ranges = create_cumulative_ranges(probabilities)

    low, high = 0.0, 1.0

    for symbol in text:
        range_size = high - low

        symbol_low, symbol_high = ranges[symbol]

        new_high = low + range_size * symbol_high
        new_low = low + range_size * symbol_low

        low, high = new_low, new_high

    encoded_value = (low + high) / 2

    result = {
        "value": encoded_value,
        "probabilities": {k: v for k, v in probabilities.items()},
        "length": len(text)
    }

    return result

def improved_arithmetic_decode(encoded_data):
    value = encoded_data["value"]
    probabilities = encoded_data["probabilities"]
    length = encoded_data["length"]

    ranges = create_cumulative_ranges(probabilities)

    result = ""
    low, high = 0.0, 1.0

    for _ in range(length):
        found = False
        for symbol, (symbol_low, symbol_high) in ranges.items():
            range_size = high - low
            current_low = low + range_size * symbol_low
            current_high = low + range_size * symbol_high

            if current_low <= value < current_high:
                result += symbol

                low, high = current_low, current_high
                found = True
                break

        if not found:
            return "Error: Cannot decode value"

    return result




class CompressionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Compression Labs")
        self.root.configure(bg="#5A282E")  # Dark Burgundy

        # Store codebooks between operations
        self.huffman_codebook = None
        self.shannon_fano_codebook = None

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

        tk.Label(root, text="Enter Input:", bg="#5A282E", fg="#F5F5DC").pack()
        self.input_text = tk.Text(root, height=4, width=50)
        self.input_text.pack(pady=5)

        # Codebook section (for Huffman/Shannon-Fano)
        tk.Label(root, text="Codebook (for Huffman/Shannon-Fano):", bg="#5A282E", fg="#F5F5DC").pack()
        self.codebook_input = tk.Text(root, height=2, width=50)
        self.codebook_input.pack(pady=5)
        self.codebook_input.configure(state='disabled')

        # Original Text section (for some decompressions)
        tk.Label(root, text="Original Text (for Arithmetic Decoding):", bg="#5A282E", fg="#F5F5DC").pack()
        self.original_text = tk.Text(root, height=2, width=50)
        self.original_text.pack(pady=5)
        self.original_text.configure(state='disabled')

        tk.Button(root, text="Run", command=self.run_selected_lab, bg="#F5F5DC", fg="#5A282E").pack(pady=5)

        tk.Label(root, text="Output:", bg="#5A282E", fg="#F5F5DC").pack()
        self.output_text = tk.Text(root, height=6, width=50, state='disabled')
        self.output_text.pack(pady=5)

        self.lab_menu.bind("<<ComboboxSelected>>", self.on_lab_selected)

    def on_lab_selected(self, event=None):
        selected_lab = self.lab_var.get()

        # Enable/disable codebook input based on selection
        if selected_lab in ["Shannon-Fano Decompress", "Huffman Decompress"]:
            self.codebook_input.configure(state='normal')
        else:
            self.codebook_input.delete("1.0", tk.END)
            self.codebook_input.configure(state='disabled')

        # Enable/disable original text input based on selection
        if selected_lab == "Arithmetic Decoding":
            self.original_text.configure(state='normal')
        else:
            self.original_text.delete("1.0", tk.END)
            self.original_text.configure(state='disabled')

    def run_selected_lab(self):
        selected_lab = self.lab_var.get()
        input_data = self.input_text.get("1.0", tk.END).strip()
        original_data = self.original_text.get("1.0", tk.END).strip()
        codebook_data = self.codebook_input.get("1.0", tk.END).strip()

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
                result, self.shannon_fano_codebook = shannon_fano_compress(input_data)
            elif selected_lab == "Shannon-Fano Decompress":
                result = shannon_fano_decompress(input_data, codebook_data)
            elif selected_lab == "Huffman Compress":
                result, self.huffman_codebook = huffman_compress(input_data)
                result = f"Compressed: {result}\nCodebook: {self.huffman_codebook}"
            elif selected_lab == "Huffman Decompress":
                result = huffman_decompress(input_data, ast.literal_eval(codebook_data))
            elif selected_lab == "LZW Compress":
                result = lzw_compress(input_data)
            elif selected_lab == "LZW Decompress":
                result = lzw_decompress(input_data)
            elif selected_lab == "Arithmetic Coding":
                result = improved_arithmetic_encode(input_data)
            elif selected_lab == "Arithmetic Decoding":
                result = improved_arithmetic_decode(ast.literal_eval(input_data))

            self.show_output(result)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def show_output(self, result):
        self.output_text.configure(state='normal')
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", str(result))
        self.output_text.configure(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    app = CompressionApp(root)
    root.mainloop()


# Lab 1: Text to ASCII
# Input: Hi
# Output: 72 105
# ('H' = 72, 'i' = 105)

# Lab 1: ASCII to Text
# Input: 72 105
# Output: Hi

# Lab 5: RSS Compress
# Input: AAABBBCCDAA
# Output: A3B3C2D1A2

# Lab 5: RSS Decompress
# Input: A3B3C2D1A2
# Output: AAABBBCCDAA

# Lab 5: RLE Compress
# Input: AAABBBCCDAA
# Output: (A,3) (B,3) (C,2) (D,1) (A,2)

# Lab 5: RLE Decompress
# Input: (A,3) (B,3) (C,2) (D,1) (A,2)
# Output: AAABBBCCDAA

# Lab 6: Shannon-Fano Compress
# Input: ABBC
# Output:
# Encoded: 01010111
# Codebook: {'A': '0', 'B': '10', 'C': '11'}

# Lab 6: Shannon-Fano Decompress
# Input: 01010111
# Original Text: {'A': '0', 'B': '10', 'C': '11'}
# Output: ABBC

# Lab 6: Huffman Compress
# Input: ABBC
# Output: 0 10 10 11
# Codebook: {'A': '0', 'B': '10', 'C': '11'}

# Lab 6: Huffman Decompress
# Input: 0 10 10 11
# Codebook: {'A': '0', 'B': '10', 'C': '11'}
# Output: ABBC

# Lab 7: LZW Compress
# Input: ABABABABAB
# Output: 65 66 256 258 257 66

# Lab 7: LZW Decompress
# Input: 65 66 256 258 257 66
# Output: ABABABABAB

# Lab 7: Arithmetic Coding
# Input: ABBC
# Output:
# {'value': 0.48185947789004335,
# 'probabilities': {'a': 0.5714285714285714, 'b': 0.42857142857142855}, 'length': 7}

# Lab 7: Arithmetic Decoding
# Input: 0.2265625
# Original Text: ABBC
# Output: ABBC
