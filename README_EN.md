# Beamer Cleaner

A tool for cleaning Beamer slide PDFs by extracting the last page of each logical label to generate a concise handout version.

[中文版 (Chinese Version)](README_CN.md)

## Features

- Extracts the last page of each logical label in a PDF
- Supports processing a single PDF file or batch processing an entire directory
- Maintains the original directory structure
- Supports complex PDF label parsing, including Unicode-encoded labels

## Installation

1. Ensure Python 3.6 or higher is installed
2. Clone this repository or download the source code
3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Process a Single PDF File

```bash
python beamer_cleaner.py -s input.pdf output.pdf
```

### Batch Process All PDF Files in a Directory

```bash
python beamer_cleaner.py -r input_directory output_directory
```

## Parameters

- `-s`, `--single`: Process a single PDF file
- `-r`, `--recursive`: Recursively process PDF files in a directory
- `input`: Path to the input PDF file or directory
- `output`: Path to the output PDF file or directory

## How It Works

1. Reads the PDF file and identifies the logical label of each page
2. Parses and sorts the labels
3. Extracts the last page corresponding to each logical label
4. Merges these pages into a new PDF file in the sorted order

## License

[//]: # ([MIT]&#40;LICENSE&#41;)
