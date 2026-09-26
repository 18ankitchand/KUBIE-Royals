class Cart:
    def __init__(self, request):
        self.session = request.session
        self.cart = self.session.get("cart", {})

    def add(self, product_id):
        pid = str(product_id)

        if pid not in self.cart:
            self.cart[pid] = 0

        self.cart[pid] += 1
        self.save()

    def update(self, product_id, quantity):
        pid = str(product_id)

        if quantity <= 0:
            self.cart.pop(pid, None)
        else:
            self.cart[pid] = quantity

        self.save()

    def remove(self, product_id):
        self.cart.pop(str(product_id), None)
        self.save()

    def count(self):
        return sum(self.cart.values())

    def save(self):
        self.session["cart"] = self.cart
        self.session.modified = True

    def clear(self):
        self.session["cart"] = {}
        self.session.modified = True