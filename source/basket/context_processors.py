def basket_context(request):
    basket = request.session.get("basket", {})
    item_count = sum(basket.values())

    return {
        "cart": {"item_count": item_count},
    }
