#!/usr/bin/env python3
import os
import sys
import argparse
import requests
from bs4 import BeautifulSoup
import csv
import docx
import PyPDF2
import json
from langchain.text_splitter import RecursiveCharacterTextSplitter
from openai import OpenAI
from dotenv import load_dotenv

# USER INSTRUCTIONS
"""
Markitdown Utility - Process multiple documents with an LLM

This command line utility extracts text from various document types and processes them
with an LLM (Language Learning Model) to generate summaries or answer custom queries.

Setup:
1. Install required dependencies:
   pip install requests beautifulsoup4 python-docx PyPDF2 langchain openai python-dotenv

2. Create a .env file in the same directory with your OpenAI API key:
   OPENAI_API_KEY=your_actual_api_key_here

Basic Usage:
   python markitdown_utility.py input1 [input2 input3...] [options]

Supported Input Types:
- Text files (.txt, .md)
- URLs (web pages)
- CSV files (.csv)
- Word documents (.docx)
- PDF files (.pdf)
- HTML files (.html, .htm)
- JSON files (.json)

Command-line Options:
  -q, --query     Custom query prompt (default: summarize the content)
  -o, --output    Save output to a file instead of printing to console
  -v, --verbose   Show detailed processing information

Examples:
1. Summarize a text file:
   python markitdown_utility.py story.txt

2. Process a webpage with a custom query:
   python markitdown_utility.py https://example.com -q "Extract the main arguments"

3. Process multiple documents and save output to a file:
   python markitdown_utility.py document.pdf data.csv -o analysis.txt

4. Process multiple different sources with verbose output:
   python markitdown_utility.py report.docx https://example.com statistics.csv -v
"""

# Load environment variables from .env file
load_dotenv()

# Get API key with error handling
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Error: OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
    print("Create a .env file in the same directory with: OPENAI_API_KEY=your_key_here")
    sys.exit(1)

# Initialize OpenAI client with the API key
client = OpenAI(api_key=api_key)

def extract_text_from_url(url):
    """
    Extract text content from a URL.
    
    Args:
        url (str): The URL to fetch and extract text from
        
    Returns:
        str or None: Extracted text content or None if extraction failed
    """
    try:
        # Fetch the URL content with a timeout
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        # Parse HTML using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements that contain non-content text
        for script in soup(["script", "style"]):
            script.extract()
            
        # Get text content with newline separators
        text = soup.get_text(separator='\n')
        
        # Clean up the text: remove extra whitespace and empty lines
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    except Exception as e:
        print(f"Error extracting text from URL {url}: {e}")
        return None

def extract_text_from_pdf(file_path):
    """
    Extract text content from a PDF file.
    
    Args:
        file_path (str): Path to the PDF file
        
    Returns:
        str or None: Extracted text content or None if extraction failed
    """
    try:
        text = ""
        # Open and read the PDF file in binary mode
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            # Extract text from each page
            for page_num in range(len(reader.pages)):
                text += reader.pages[page_num].extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error extracting text from PDF {file_path}: {e}")
        return None

def extract_text_from_docx(file_path):
    """
    Extract text content from a DOCX file.
    
    Args:
        file_path (str): Path to the DOCX file
        
    Returns:
        str or None: Extracted text content or None if extraction failed
    """
    try:
        # Open and parse the DOCX file
        doc = docx.Document(file_path)
        full_text = []
        # Extract text from each paragraph
        for para in doc.paragraphs:
            full_text.append(para.text)
        return '\n'.join(full_text)
    except Exception as e:
        print(f"Error extracting text from DOCX {file_path}: {e}")
        return None

def extract_text_from_csv(file_path):
    """
    Extract text content from a CSV file.
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        str or None: Extracted text content or None if extraction failed
    """
    try:
        text = []
        # Open and read the CSV file
        with open(file_path, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            # Convert each row to a comma-separated string
            for row in reader:
                text.append(', '.join(row))
        return '\n'.join(text)
    except Exception as e:
        print(f"Error extracting text from CSV {file_path}: {e}")
        return None

def extract_text_from_text_file(file_path):
    """
    Extract text content from a plain text file.
    
    Args:
        file_path (str): Path to the text file
        
    Returns:
        str or None: Extracted text content or None if extraction failed
    """
    try:
        # Try reading with UTF-8 encoding first
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        try:
            # Fall back to Latin-1 encoding if UTF-8 fails
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()
        except Exception as e:
            print(f"Error extracting text from file {file_path}: {e}")
            return None
    except Exception as e:
        print(f"Error extracting text from file {file_path}: {e}")
        return None

def process_input(input_source):
    """
    Process an input source and extract its text content.
    
    Args:
        input_source (str): Path to a file or URL
        
    Returns:
        str or None: Extracted text content or None if extraction failed
    """
    # Check if input is a URL
    if input_source.startswith(('http://', 'https://')):
        print(f"Processing URL: {input_source}")
        return extract_text_from_url(input_source)
    
    # Check if file exists
    if not os.path.exists(input_source):
        print(f"Error: File not found: {input_source}")
        return None
    
    # Get file extension to determine file type    
    file_extension = os.path.splitext(input_source)[1].lower()
    
    print(f"Processing file: {input_source}")
    # Process based on file extension
    if file_extension == '.pdf':
        return extract_text_from_pdf(input_source)
    elif file_extension == '.docx':
        return extract_text_from_docx(input_source)
    elif file_extension == '.csv':
        return extract_text_from_csv(input_source)
    elif file_extension in ['.txt', '.md', '.json', '.html', '.htm']:
        return extract_text_from_text_file(input_source)
    else:
        # Try as text file for unknown extensions
        print(f"Warning: Unrecognized file extension for {input_source}. Trying as text file.")
        return extract_text_from_text_file(input_source)

def split_text_into_chunks(text, chunk_size=2000, chunk_overlap=200):
    """
    Split text into manageable chunks for processing by LLM.
    
    Args:
        text (str): The text to split
        chunk_size (int): Maximum size of each chunk
        chunk_overlap (int): Overlap between chunks
        
    Returns:
        list: List of text chunks
    """
    # Use LangChain's text splitter for intelligent chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    return text_splitter.split_text(text)

def process_with_llm(content, query=None):
    """
    Process content with LLM using the provided query or default to summarization.
    
    Args:
        content (str): The content to process
        query (str, optional): Custom query prompt
        
    Returns:
        str: LLM-generated response
    """
    # Create prompt based on whether a custom query was provided
    if not query:
        prompt = f"Please summarize the following content concisely:\n\n{content}"
    else:
        prompt = f"{query}\n\nContent:\n{content}"
    
    try:
        # Call OpenAI API to process the content
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Using GPT-3.5 Turbo model
            messages=[
                {"role": "system", "content": "You are a helpful assistant that processes documents."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000  # Limit response length
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        sys.exit(1)

def main():
    """Main function to handle command line arguments and orchestrate processing."""
    # Set up argument parser with descriptive help text
    parser = argparse.ArgumentParser(
        description='Process various document types with an LLM for summarization or custom queries.',
        epilog='Example: python markitdown_utility.py file.txt https://example.com -q "Extract key points" -o output.txt'
    )
    
    # Add command-line arguments
    parser.add_argument('inputs', nargs='+', help='Input sources (files or URLs)')
    parser.add_argument('-q', '--query', help='Custom query prompt (default: summarize)')
    parser.add_argument('-o', '--output', help='Output file path (default: print to console)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    
    # Parse command-line arguments
    args = parser.parse_args()
    
    # Process all input sources
    all_content = []
    
    for input_source in args.inputs:
        # Extract content from each input source
        content = process_input(input_source)
        if content:
            if args.verbose:
                print(f"Extracted {len(content)} characters from {input_source}")
            all_content.append(content)
    
    # Check if any content was successfully extracted
    if not all_content:
        print("Error: No content could be extracted from the provided inputs.")
        sys.exit(1)
    
    # Combine all content with document separators
    combined_content = "\n\n" + "-" * 30 + " DOCUMENT SEPARATOR " + "-" * 30 + "\n\n".join(all_content)
    
    # Check if content is too large and needs chunking (OpenAI has token limits)
    if len(combined_content) > 4000:
        if args.verbose:
            print(f"Content size ({len(combined_content)} chars) exceeds processing limit. Chunking content...")
        
        # Split content into smaller chunks
        chunks = split_text_into_chunks(combined_content)
        if args.verbose:
            print(f"Split content into {len(chunks)} chunks")
        
        # Process each chunk with LLM and collect results
        results = []
        for i, chunk in enumerate(chunks):
            if args.verbose:
                print(f"Processing chunk {i+1}/{len(chunks)}")
            result = process_with_llm(chunk, args.query)
            results.append(result)
        
        # Create a coherent final result from multiple chunk results
        if len(results) > 1:
            if args.verbose:
                print("Combining results from multiple chunks...")
            combined_results = "\n\n".join(results)
            # Ask LLM to create a coherent summary from the individual chunk summaries
            final_result = process_with_llm(
                combined_results, 
                "Combine the following summaries into a coherent single summary, removing redundancies:"
            )
        else:
            final_result = results[0]
    else:
        # Content is small enough for direct processing
        final_result = process_with_llm(combined_content, args.query)
    
    # Output the final result to file or console
    if args.output:
        try:
            # Write result to output file
            with open(args.output, 'w', encoding='utf-8') as output_file:
                output_file.write(final_result)
            print(f"Output written to {args.output}")
        except Exception as e:
            print(f"Error writing to output file: {e}")
            print(final_result)  # Fallback to console output if file writing fails
    else:
        # Print result to console with formatting
        print("\n" + "=" * 80 + "\n")
        print(final_result)
        print("\n" + "=" * 80)

# Entry point of the program
if __name__ == "__main__":
    main()