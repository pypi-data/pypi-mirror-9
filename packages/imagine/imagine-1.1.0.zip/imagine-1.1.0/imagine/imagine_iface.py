from . import Imagine


def interface():
    # Let's do some tests!
    print("Enter a search term: ", end='')
    st = input()
    print("Initiating search for first 3 results...")

    imaginator = Imagine(st, 3)
    imaginator.execute()

