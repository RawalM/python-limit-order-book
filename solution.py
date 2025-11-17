# COMP 226: Computer Based Trading in Financial Marketing
# Author: Maadhyam Rawal
# Date: 19-03-2025

# DO NOT CHANGE THESE SINCE YOU NEED THEM.
import pandas as pd
import numpy as np
import copy


def sort(book, sort_bid=True, sort_ask=True):
    """
    This function aims at sorting the limit order book.
    DO NOT CHANGE THIS FUNCTION.
    """
    if sort_ask and len(book['ask']) >= 1:
        book['ask'] = book['ask'].sort_values(by=['price', 'oid'],
                                              key=lambda col: col.map(
                                                  lambda x: (len(x), x)) if col.name == 'oid' else col,
                                              ascending=[True, True]).reset_index(drop=True)
        if len(book['ask']) > 0:
            book['ask'] = book['ask'].iloc[::-1]

    if sort_bid and len(book['bid']) >= 1:
        book['bid'] = book['bid'].sort_values(by=['price', 'oid'],
                                              key=lambda col: col.map(
                                                  lambda x: (len(x), x)) if col.name == 'oid' else col,
                                              ascending=[False, True]).reset_index(drop=True)

    return book


def total_volumes(book) -> dict:
    """
    Arguments:
        book - A dictionary containing "ask" and "bid", each of which are dataframes
               containing the collection of limit orders.
    Returns:
        A dictionary with "ask" and "bid", the values of which are the total volumes in
        the book. E.g., {'ask': XXX, 'bid': XXX}. 'ask' should be the first.
    """
    return{
        'ask':book['ask']['size'].sum() if not book ['ask'].empty else 0,
        'bid': book['bid']['size'].sum() if not book ['bid'].empty else 0
    }


def best_prices(book) -> dict:
    """
    Arguments:
        book - A dictionary containing "ask" and "bid", each of which are dataframes
               containing the collection of limit orders.
    Returns:
        A dictionary with "ask" and "bid", the values of which are the best prices in
        the book. E.g., {'ask': XXX, 'bid': XXX}. 'ask' should be the first.
    """
    return {
        'ask':book['ask']['price'].min() if not book ['ask'].empty else None,
        'bid': book['bid']['price'].max() if not book ['bid'].empty else None
    }


def midprice(book) -> float:
    """
    Arguments:
        book - A dictionary containing "ask" and "bid", each of which are dataframes
               containing the collection of limit orders.
    Returns:
        The midprice of the book (a number).
    """
    best = best_prices(book)
    if best['ask'] is None or best['bid'] is None:
        return None
    return(best['ask'] + best['bid']) /2


def spread(book) -> float:
    """
    Arguments:
        book - A dictionary containing "ask" and "bid", each of which are dataframes
               containing the collection of limit orders.
    Returns:
        The spread of the book (a number).
    """
    best = best_prices(book)
    if best['ask'] is None or best['bid'] is None:
        return None
    return best['ask'] - best['bid']


def add(book, message) -> dict:
    """
    Adds an order to the book and matches it if possible.
    
    Arguments:
        book - A dictionary containing "ask" and "bid", each of which are DataFrames.
        message - A dictionary containing "oid", "side", "price", and "size" entries.
    
    Returns:
        The updated and sorted book.
    """
    side = message['side']   # Order side: 'B' for buy, 'S' for sell
    oid = message['oid']     # Unique order ID
    price = float(message['price'])  # Order price
    size = int(message['size'])  # Order size

    # used Iloc in the following code because the code wasnt giving me the correct outputs at all with loc
    # Loc and Iloc reference: https://www.geeksforgeeks.org/difference-between-loc-and-iloc-in-pandas-dataframe/
    
    if side == 'B':  # Buy Order
        while size > 0 and not book['ask'].empty:  # Check if there's an order to match
            best_ask = book['ask'].iloc[-1]  # Get the lowest available sell order (best ask)
            best_ask_price = best_ask['price']

            if price >= best_ask_price:  # If buy order price is higher/equal, match
                trade_size = min(size, best_ask['size'])  # Amount of shares to trade
                size -= trade_size  # Reduce the remaining size of the incoming order
                new_size = best_ask['size'] - trade_size  # Remaining size in ask order

                # Remove matched order from the order book
                book['ask'] = book['ask'][book['ask']['oid'] != best_ask['oid']]
                if new_size > 0:
                    # If part of the ask order remains, reinsert it with reduced size
                    book['ask'] = pd.concat([book['ask'], pd.DataFrame({
                        'oid': [best_ask['oid']], 'price': [best_ask['price']], 'size': [new_size]
                    })], ignore_index=True)

                book = sort(book)  # Sort the order book after modification
            else:
                break  # No more matching orders

        # If part of the buy order remains, add it to the bid book
        if size > 0:
            new_order = pd.DataFrame({'oid': [oid], 'price': [price], 'size': [size]})
            book['bid'] = pd.concat([book['bid'], new_order], ignore_index=True)
            book = sort(book)  # Ensure correct order in bid book

    elif side == 'S':  # Sell Order
        while size > 0 and not book['bid'].empty:  # Check if there's an order to match
            best_bid = book['bid'].iloc[0]  # Get the highest available buy order (best bid)
            best_bid_price = best_bid['price']

            if price <= best_bid_price:  # If sell order price is lower/equal, match
                trade_size = min(size, best_bid['size'])  # Amount of shares to trade
                size -= trade_size  # Reduce the remaining size of the incoming order
                new_size = best_bid['size'] - trade_size  # Remaining size in bid order

                # Remove matched order from the order book
                book['bid'] = book['bid'][book['bid']['oid'] != best_bid['oid']]
                if new_size > 0:
                    # If part of the bid order remains, reinsert it with reduced size
                    book['bid'] = pd.concat([book['bid'], pd.DataFrame({
                        'oid': [best_bid['oid']], 'price': [best_bid['price']], 'size': [new_size]
                    })], ignore_index=True)

                book = sort(book)  # Sort the order book after modification
            else:
                break  # No more matching orders

        # If part of the sell order remains, add it to the ask book
        if size > 0:
            new_order = pd.DataFrame({'oid': [oid], 'price': [price], 'size': [size]})
            book['ask'] = pd.concat([book['ask'], new_order], ignore_index=True)
            book = sort(book)  # Ensure correct order in ask book

    return book


def reduce(book, message) -> dict:
    """
    Reduces the size of an existing order or removes it entirely if fully reduced.
    
    Arguments:
        book - A dictionary containing "ask" and "bid", each of which are DataFrames.
        message - A dictionary containing "oid" (order ID) and "amount" (size reduction).
    
    Returns:
        The updated and sorted book.
    """
    
    oid = message['oid']  # Order ID to reduce
    size = message['amount']  # Reduction amount

    # Check in the ask book
    if 'ask' in book and not book['ask'].empty:
        index_order = book['ask'].index[book['ask']['oid'] == oid]

        if not index_order.empty:
            current_size = book['ask'].loc[index_order[0], 'size']

            if size >= current_size:
                # If reduction amount is greater or equal, remove the order
                book['ask'] = book['ask'].drop(index_order[0])
            else:
                # Otherwise, just reduce the size of the order
                book['ask'].loc[index_order[0], 'size'] -= size

            book = sort(book)  # Sort book after modification

    # Check in the bid book
    if 'bid' in book and not book['bid'].empty:
        index_order = book['bid'].index[book['bid']['oid'] == oid]

        if not index_order.empty:
            current_size = book['bid'].loc[index_order[0], 'size']
            
            if size >= current_size:
                book['bid'] = book['bid'].drop(index_order[0])  # Remove order if fully reduced
            else:
                book['bid'].loc[index_order[0], 'size'] -= size  # Otherwise, reduce size

            book = sort(book)  # Sort book after modification

    return book



# Extra functions placeholders
def extra1(book, size):
    """

    Calculate the expected midprice after executing a buy limit order with a random price from ask.

    :param book: Dictionary containing 'ask' and 'bid' books as DataFrames.
    :param size: Integer size of the buy order.
    :return: Expected midprice after execution.
    """

# Simulates executing a buy limit order and estimates the midprice after execution.
# Iterates through the ask book to calculate total cost based on order sizes.

    if book['ask'].empty:
        return None

    remaining_size = size
    total_cost = 0

    for index, order in book['ask'].iloc[::-1].iterrows():  # Iterate from lowest price
        trade_size = min(remaining_size, order['size'])
        total_cost += trade_size * order['price']
        remaining_size -= trade_size

        if remaining_size == 0:
            break

    if remaining_size > 0:
        return None  # Order could not be fully executed

    book_after_trade = copy.deepcopy(book)
    book_after_trade = sort(book_after_trade)

    return midprice(book_after_trade)


def extra2(book, size):
    """
    Calculate the expected midprice after executing a random-sized buy market order.

    :param book: Dictionary containing 'ask' and 'bid' books as DataFrames.
    :return: Expected midprice after execution.
    """

    # Similar to extra1, but simulates a buy market order where price is not fixed.

    if book['ask'].empty:
        return None

    remaining_size = size
    total_cost = 0

    for index, order in book['ask'].iloc[::-1].iterrows():
        trade_size = min(remaining_size, order['size'])
        total_cost += trade_size * order['price']
        remaining_size -= trade_size

        if remaining_size == 0:
            break

    if remaining_size > 0:
        return None  # Order could not be fully executed

    book_after_trade = copy.deepcopy(book)
    book_after_trade = sort(book_after_trade)

    return midprice(book_after_trade)


def extra3(book):
    """
    Calculate the total value of all orders in the order book.

    :param book: Dictionary containing 'ask' and 'bid' books as DataFrames.
    :return: Total value of all orders in the book (float).
    """
    # Calculates the total dollar value of all active orders in the order book.
    # Multiplies price by size for both bid and ask orders and sums them up.
    ask_value = (book['ask']['price'] * book['ask']['size']).sum() if not book['ask'].empty else 0
    bid_value = (book['bid']['price'] * book['bid']['size']).sum() if not book['bid'].empty else 0

    return ask_value + bid_value


def extra4(book, k):
    """
    Finds the maximum buy volume that can be executed before the midprice increases beyond k%.
    
    Arguments:
        book - A dictionary containing "ask" and "bid", each of which are DataFrames.
        k - The maximum percentage increase allowed in the midprice.
    
    Returns:
        Maximum buy volume before the midprice increase exceeds k%.
    """
    # Finds the maximum buy volume that can be executed before the midprice increases beyond k%.
    # Iterates through the ask book, adding volume until the new midprice exceeds the threshold.

    if book['ask'].empty:
        return 0  # No asks available, no volume can be traded

    original_midprice = midprice(book)  # Initial midprice before trade
    target_price = original_midprice * (1 + k / 100)  # Price threshold

    total_volume = 0  # Keeps track of the maximum volume that can be bought
    remaining_size = 0  # Stores remaining order size from the last step

    # Iterate over ask orders from lowest to highest price
    for index, order in book['ask'].iloc[::-1].iterrows():
        total_volume += order['size']  # Accumulate order size
        remaining_size = order['size']

        # Create a temporary book excluding processed orders
        # deepcopy reference - https://docs.python.org/3/library/copy.html
        temp_book = copy.deepcopy(book)
        temp_book['ask'] = temp_book['ask'].iloc[:index].reset_index(drop=True)
        new_midprice = midprice(temp_book)  # Calculate new midprice

        # If midprice exceeds threshold, return the last valid volume
        if new_midprice is not None and new_midprice >= target_price:
            return total_volume - remaining_size

    return total_volume  # If threshold is not reached, return the total volume

