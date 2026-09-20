def unique_rows(rows):
    result = []
    comparisons = 0
    for row in rows:
        duplicate = False
        for existing in result:
            comparisons += 1
            if existing["id"] == row["id"]:
                duplicate = True
                break
        if not duplicate:
            result.append(row)
    return result, comparisons
