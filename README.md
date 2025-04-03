# Assignment 4 - Hestia // Lauri Karvonen

Generating a command line utility program, which feeds the input of one or multiple sources to LLM.

# Markitdown Utility

A command-line utility for processing various document types with LLMs (Large Language Models) to generate summaries or answer custom queries.

## Overview

Markitdown is a versatile tool that can extract text from multiple input formats, including text files, web pages, PDFs, Word documents, and CSV files. It sends this content to an LLM (using OpenAI's API) to generate summaries or respond to custom queries about the content.

## Features

- **Multiple Input Support**: Process text files, URLs, PDFs, Word documents, CSV files, and more
- **Combined Processing**: Handle multiple inputs of different types simultaneously
- **Custom Queries**: Ask specific questions about the content or use the default summarization
- **Automatic Text Chunking**: Handles large documents by intelligently splitting them into manageable pieces
- **Flexible Output**: Print results to console or save to a file

## Installation

1. Clone the repository or download the script
2. Install the required dependencies:

```bash
pip install requests beautifulsoup4 python-docx PyPDF2 langchain openai python-dotenv
```
3. Create a .env file in the same directory as the script with your OpenAI API key:

```plaintext
OPENAI_API_KEY=your_actual_api_key_here
```
## Usage
Basic syntax:
```bash
python markitdown_utility.py input1 [input2 input3...] [options]
```

## Command-line Options
- inputs: One or more input sources (files or URLs)
- -q, --query: Custom query prompt (default: summarize the content)
- -o, --output: Save output to a file instead of printing to console
- -v, --verbose: Show detailed processing information
## Supported Input Types
- Text files (.txt, .md)
- URLs (web pages)
- CSV files (.csv)
- Word documents (.docx)
- PDF files (.pdf)
- HTML files (.html, .htm)
- JSON files (.json)

## Examples
### Summarize a text file
```bash
python markitdown_utility.py story.txt
```
### Process a webpage with a custom query
```bash
python markitdown_utility.py https://example.com -q "Extract the main arguments"
```
### Process multiple documents and save output to a file
```bash
python markitdown_utility.py document.pdf data.csv -o analysis.txt
```
### Process multiple different sources with verbose output
```bash
python markitdown_utility.py report.docx https://example.com statistics.csv -v
```

## How It Works
1. **Input Processing:** The tool extracts text from each input source based on its type
2. **Content Combination:** All extracted content is combined with separators
3. **Chunking (if needed):** Large content is split into manageable chunks
4. **LLM Processing:** Content is sent to the OpenAI API with your query or a default summarization prompt
5. **Result Generation:** Results are combined (for chunked content) and presented to the user
## Troubleshooting
- API Key Issues: Ensure your .env file is in the same directory as the script and contains the correct API key
- Dependency Errors: Make sure all required packages are installed
- File Access Errors: Check file paths and permissions
- Content Size Limits: Very large documents are automatically chunked, but may take longer to process

## License
This project is open source and available under the MIT License.

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
