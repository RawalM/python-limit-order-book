from common import *
# Change template.py to solution.py before running this line.
from solution import *

"""
Load book.
"""

book_path = "./input/book_1.csv"
# book_path = "./input/book_2.csv"
# book_path = "./input/book_3.csv"

# book_path = "./input/test.extra.case1.csv"

"""
Load message.
"""
# messages_path = "./input/empty.txt"
# messages_path = "./input/message_ex_reduce.txt"
# messages_path = "./input/message_ex_add.txt"
# messages_path = "./input/message_ex_cross.txt"
# messages_path = "./input/message_ex_same_price.txt"

messages_path = "./input/message_a.txt"
# messages_path = "./input/message_ar.txt"
# messages_path = "./input/message_arc.txt"

"""
Load book.
"""
book = load(book_path)
book = sort(book)

book = reconstruct(load_data(messages_path), init=book, log=False)
summarise(book)

# result = extra4(book,k=0.1)
# result = extra3(book)
# print(result)

