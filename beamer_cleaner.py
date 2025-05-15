import os
import re
import fitz  # PyMuPDF
import argparse
from pypdf import PdfWriter, PdfReader

class PdfCleaner:
    @staticmethod
    def decode_label(label: str) -> str:
        """
        尝试解析形如 <FEFF0031> 的标签。
        例如: <FEFF0031> => 0031 (十六进制) => Unicode码点0x0031 => '1'
        如果解析失败，则返回原始字符串。
        """
        pattern = r"^<FEFF([0-9A-Fa-f]+)>$"
        match = re.match(pattern, label)
        if match:
            hex_digits = match.group(1)
            code_points = [hex_digits[i:i+4] for i in range(0, len(hex_digits), 4)]
            decoded = []
            for cp in code_points:
                try:
                    val = int(cp, 16)
                    decoded.append(chr(val))
                except ValueError:
                    return label
            return "".join(decoded)
        return label

    @staticmethod
    def label_sort_key(label: str):
        """
        将标签转换为排序所用的Key。
        - 若能解析为整数，则返回(0, 该整数)，确保数字优先比较
        - 若不能解析为整数，则返回(1, label)，确保字符串排在数字之后
        """
        try:
            return (0, int(label))
        except ValueError:
            return (1, label)

    def clean_pdf(self, input_pdf: str, output_pdf: str) -> bool:
        """
        处理单个PDF文件，提取每个逻辑标签的最后一页。

        Args:
            input_pdf: 输入PDF文件的路径
            output_pdf: 输出PDF文件的路径

        Returns:
            bool: 处理成功返回True，失败返回False
        """
        try:
            doc = fitz.open(input_pdf)
            writer = PdfWriter()
            label_to_page = {}

            # 收集每个逻辑标签对应的最后一页
            for page_num in range(len(doc)):
                raw_label = doc[page_num].get_label() or str(page_num + 1)
                decoded = self.decode_label(raw_label)
                label_to_page[decoded] = page_num

            # 按逻辑标签排序并提取页面
            sorted_labels = sorted(label_to_page.keys(), key=self.label_sort_key)

            temp_path = "temp_page.pdf"
            for label in sorted_labels:
                page_num = label_to_page[label]
                temp_doc = fitz.open()
                temp_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
                temp_doc.save(temp_path)

                pdf_page = PdfReader(temp_path).pages[0]
                writer.add_page(pdf_page)

            # 保存结果
            with open(output_pdf, "wb") as out_file:
                writer.write(out_file)

            # 清理临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)

            return True

        except Exception as e:
            print(f"处理PDF时出错: {str(e)}")
            return False
        finally:
            if 'doc' in locals():
                doc.close()

def batch_process(input_dir: str, output_dir: str):
    """
    批量处理目录中的PDF文件。

    Args:
        input_dir: 输入目录路径
        output_dir: 输出目录路径
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    cleaner = PdfCleaner()
    # 遍历目录树
    for root, dirs, files in os.walk(input_dir):
        # 计算相对路径，用于在输出目录中创建相同的目录结构
        rel_path = os.path.relpath(root, input_dir)
        current_output_dir = os.path.join(output_dir, rel_path)

        # 确保输出目录存在
        if not os.path.exists(current_output_dir):
            os.makedirs(current_output_dir)

        # 处理当前目录中的PDF文件
        for filename in files:
            in_path = os.path.join(root, filename)
            # 确保是文件而不是目录，并且是PDF文件
            if os.path.isfile(in_path) and filename.lower().endswith(".pdf"):
                out_path = os.path.join(current_output_dir, filename)
                if cleaner.clean_pdf(in_path, out_path):
                    print(f"已成功处理: {in_path}")
                else:
                    print(f"处理失败: {in_path}")


def parse_args():
    """
    解析命令行参数
    """
    parser = argparse.ArgumentParser(description='PDF幻灯片清理工具')

    # 创建互斥参数组
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-r', '--recursive', action='store_true',
                       help='递归处理整个目录中的PDF文件')
    group.add_argument('-s', '--single', action='store_true',
                       help='处理单个PDF文件')

    # 添加位置参数
    parser.add_argument('input', help='输入PDF文件或目录的路径')
    parser.add_argument('output', help='输出PDF文件或目录的路径')

    return parser.parse_args()

def main():
    args = parse_args()
    cleaner = PdfCleaner()

    if args.recursive:
        # 批量处理目录
        if not os.path.isdir(args.input):
            print(f"错误: 输入路径 '{args.input}' 不是一个目录")
            return
        batch_process(args.input, args.output)
    else:
        # 处理单个文件
        if not os.path.isfile(args.input):
            print(f"错误: 输入文件 '{args.input}' 不存在")
            return
        if cleaner.clean_pdf(args.input, args.output):
            print(f"已成功处理: {args.input}")
        else:
            print(f"处理失败: {args.input}")

if __name__ == '__main__':
    main()