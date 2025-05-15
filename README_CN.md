# Beamer Cleaner

一个用于清理 Beamer 幻灯片 PDF 的工具，提取每个逻辑标签的最后一页，生成简洁的讲义版本。

[English Version (英文版)](README_EN.md)

## 功能特点

- 提取 PDF 中每个逻辑标签的最后一页
- 支持处理单个 PDF 文件或批量处理整个目录
- 保持原始目录结构
- 支持复杂的 PDF 标签解析，包括 Unicode 编码标签

## 安装

1. 确保已安装 Python 3.6 或更高版本
2. 克隆此仓库或下载源代码
3. 安装依赖项：

```bash
pip install -r requirements.txt
```

## 使用方法

### 处理单个 PDF 文件

```bash
python beamer_cleaner.py -s input.pdf output.pdf
```

### 批量处理目录中的所有 PDF 文件

```bash
python beamer_cleaner.py -r input_directory output_directory
```

## 参数说明

- `-s`, `--single`: 处理单个 PDF 文件
- `-r`, `--recursive`: 递归处理整个目录中的 PDF 文件
- `input`: 输入 PDF 文件或目录的路径
- `output`: 输出 PDF 文件或目录的路径

## 工作原理

1. 读取 PDF 文件并识别每个页面的逻辑标签
2. 对标签进行解析和排序
3. 提取每个逻辑标签对应的最后一页
4. 按照排序后的顺序将这些页面合并到新的 PDF 文件中

## 许可证

[//]: # ([MIT]&#40;LICENSE&#41;)
