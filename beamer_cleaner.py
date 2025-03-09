import os
import re
import fitz  # PyMuPDF
from pypdf import PdfWriter, PdfReader

def decode_label(label: str) -> str:
    """
    尝试解析形如 <FEFF0031> 的标签。
    例如: <FEFF0031> => 0031 (十六进制) => Unicode码点0x0031 => '1'
    如果解析失败，则返回原始字符串。
    """
    pattern = r"^<FEFF([0-9A-Fa-f]+)>$"
    match = re.match(pattern, label)
    if match:
        hex_digits = match.group(1)  # 比如 '0031'
        # 每4位视为一个Unicode码点
        code_points = [hex_digits[i:i+4] for i in range(0, len(hex_digits), 4)]
        decoded = []
        for cp in code_points:
            try:
                val = int(cp, 16)
                decoded.append(chr(val))
            except ValueError:
                return label  # 无法解析就返回原始
        return "".join(decoded)
    return label

def label_sort_key(label: str):
    """
    将标签转换为排序所用的Key。
    - 若能解析为整数，则返回(0, 该整数)，确保数字优先比较
    - 若不能解析为整数，则返回(1, label)，确保字符串排在数字之后
    """
    try:
        return (0, int(label))
    except ValueError:
        # 非纯数字或无法解析成数字
        return (1, label)

def extract_final_state_pages(input_pdf, output_pdf):
    doc = fitz.open(input_pdf)
    writer = PdfWriter()

    # 存储每个逻辑标签对应的“最后一页”
    label_to_page = {}

    for page_num in range(len(doc)):
        raw_label = doc[page_num].get_label()  # 可能返回 '1' 或 '<FEFF0031>' 等
        if not raw_label:
            # 有些PDF可能没有逻辑标签，默认用物理页号字符串
            raw_label = str(page_num + 1)

        decoded = decode_label(raw_label)  # 解析形如 <FEFF0031> => '1'

        # 记录或覆盖该逻辑标签的最新页数（物理页）
        label_to_page[decoded] = page_num

    # 将收集到的页号按逻辑标签排序
    # label_sort_key会让可解析成数字的标签按数字排，其他按字符串排
    sorted_labels = sorted(label_to_page.keys(), key=label_sort_key)

    for label in sorted_labels:
        page_num = label_to_page[label]
        # 将该页面插入临时PDF再读入pypdf
        temp_doc = fitz.open()
        temp_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
        temp_path = "temp_page.pdf"
        temp_doc.save(temp_path)

        pdf_page = PdfReader(temp_path).pages[0]
        writer.add_page(pdf_page)

    with open(output_pdf, "wb") as out_file:
        writer.write(out_file)

def batch_process(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".pdf"):
            in_path = os.path.join(input_dir, filename)
            out_path = os.path.join(output_dir, filename)
            extract_final_state_pages(in_path, out_path)
            print(f"已处理: {filename}")


# 示例使用
# 示例用法
if __name__ == '__main__':
    input_dir = r"C:\input\path"  # 输入目录
    output_dir = r"C:\output\path"  # 输出目录
    batch_process(input_dir, output_dir)
