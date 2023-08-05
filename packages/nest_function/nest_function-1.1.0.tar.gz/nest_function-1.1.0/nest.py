def print_lol(the_list, indent=False, level=0):
    """Prints each item in a list, recursively descending
       into nested lists (if necessary)."""

    for item in the_list:
        if isinstance(item, list):
            print_lol(item, indent, level+1)
        else:
            if indent:
                for l in range(level):
                    print("\t", end='')
            print(item)
