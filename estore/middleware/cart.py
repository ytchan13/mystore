from ..models import Cart


class CartMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def find_cart(self, request):
        cart_id = request.session.get('cart_id')
        cart, cart_is_created = Cart.objects.get_or_create(id__exact=cart_id)

        request.session['cart_id'] = cart.id

        return cart

    def __call__(self, request):
        request.cart = self.find_cart(request)

        response = self.get_response(request)

        return response