def final_price(subtotal, customer_kind):
    if customer_kind == "staff":
        discount = 0.25
    else:
        if customer_kind == "member":
            discount = 0.1
        else:
            discount = 0
    return round(subtotal * (1 - discount), 2)
