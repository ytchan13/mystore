from django.shortcuts import redirect,render

from .forms import ProductForm
from .models import Product

# Create your views here.
def product_list(request):
    products = Product.objects.all()
    return render(request, 'estore/product_list.html', {'products': products})


def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'estore/product_form.html', {'form': form})