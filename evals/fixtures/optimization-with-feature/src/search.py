ITEMS = [{"id": index, "name": f"item-{index}"} for index in range(10_000)]


def search(limit=20, offset=0):
    return ITEMS[offset : offset + limit]
