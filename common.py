# Change template.py to solution.py before running this line.
from solution import *

def nice_print(book):
    for key in book:
        print(key + " book:")
        print(book[key])

def handle(book, row):
    if row['type'] == 'A':
        return add(book, {
            'oid': row['oid'],
            'side': row['side'],
            'price': float(row['price']),
            'size': int(row['size'])
        })
    elif row['type'] == 'R':
        return reduce(book, {
            'oid': row['oid'],
            'amount': int(row['size'])
        })
    else:
        print("Unknown row type.")
        return book

def load(path):
    df = pd.read_csv(path)
    ask_df = df[df['side'] == 'S'][['oid', 'price', 'size']]
    bid_df = df[df['side'] == 'B'][['oid', 'price', 'size']]

    ask_df['price'] = ask_df['price'].astype(float)
    bid_df['price'] = bid_df['price'].astype(float)

    book = {
        'ask': ask_df,
        'bid': bid_df
    }
    return sort(book)

def summarise(book, with_stats=True):

    book['ask'] = book['ask'][['oid', 'price', 'size']]
    book['bid'] = book['bid'][['oid', 'price', 'size']]

    nice_print(book)

    if with_stats:
        def clean(x): return None if pd.isna(x) else x

        _total_volumes = total_volumes(book)
        _best_prices = {k: clean(v) for k, v in best_prices(book).items()}
        _midprice = clean(midprice(book))
        _spread = clean(spread(book))

        print("--Stats--")
        print("Total volume:", _total_volumes['ask'], _total_volumes['bid'])
        print("Best prices:", _best_prices['ask'], _best_prices['bid'])
        print("Mid-price:", _midprice)
        print("Spread:", _spread)


def book_init():
    book = {
        'ask': pd.DataFrame(columns=['oid', 'price', 'size']),
        'bid': pd.DataFrame(columns=['oid', 'price', 'size'])
    }
    return sort(book)

def reconstruct(data, init=None, log=False):
    if init is None:
        init = book_init()
    if len(data) == 0:
        return init

    def reducer(b, i):
        new_book = handle(b, data.iloc[i])
        if log:
            print(f"Step {i}\n\n")
            summarise(new_book, with_stats=False)
            print("====================\n\n")
        return new_book

    book = init
    for i in range(len(data)):
        # if len(book['ask']) > 0:
        #     book['ask'] = book['ask'].iloc[::-1]
        book = reducer(book, i)

    return sort(book)


def load_data(data_path, n_rows=None):
    # Read the data from the file
    data = pd.read_csv(
        data_path,
        delim_whitespace=True,
        header=None,
        names=["type", "oid", "side", "price", "size"],
        nrows=n_rows
    )

    # Modify the data as per the logic in the R function
    data.loc[data['type'] == 'R', 'size'] = data.loc[data['type'] == 'R', 'side']
    data.loc[data['type'] == 'R', 'side'] = None

    return data
