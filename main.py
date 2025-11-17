import argparse
import os
import sys
from common import *

# Suppress warnings
import warnings
warnings.filterwarnings("ignore")

# Define argument format
arg_format = "<--log> <book_path> <messages_path>"

# Argument parsing
parser = argparse.ArgumentParser(description="Main script", add_help=False)
parser.add_argument("--log", action="store_true", help="Enable logging")
parser.add_argument("book_path", type=str, help="Path to the book file")
parser.add_argument("messages_path", type=str, help="Path to the messages file")

# Parse arguments
args = parser.parse_args()
nargs = len(sys.argv) - 1

if nargs < 2 or nargs > 3:  # Check that there are 2 or 3 arguments
    raise ValueError(f"main.py has 2 required arguments and 1 optional flag: {arg_format}")

if nargs == 3 and not args.log:  # If 3, check that --log is the first
    raise ValueError(f"Bad arguments format, expected: {arg_format}")

book_path = args.book_path
messages_path = args.messages_path

# Check if all files exist
if not all(os.path.exists(path) for path in [book_path, messages_path]):
    raise FileNotFoundError("File does not exist at path provided.")

# Main code
book = load(book_path)
book = reconstruct(load_data(messages_path), init=book, log=args.log)
summarise(book)
