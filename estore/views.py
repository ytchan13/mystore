import uuid

from django.contrib import messages
# from django.contrib.auth.decorators import permission_required
# from django.shortcuts import get_object_or_404,redirect,render
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group, User
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import generic

# from .forms import ProductForm
from .forms import OrderInfoForm, EstoreUserCreationForm
# from .models import Order, Product
from .models import Cart_Items, Order, OrderItem, Product
from .helpers import send_order_mail

# Create your views here.

class CartItemDelete(generic.DeleteView):
    # def delete(self, request, *args, **kwargs):
    #     self.object = self.get_object()
    #     success_url = self.get_success_url()
    #     self.request.cart.items.remove(self.object)
    #     return HttpResponseRedirect(success_url)

    def get_object(self, queryset=None):
        # return self.request.cart.items.get(id=self.kwargs.get('pk'))
        return self.request.cart.cart_items_set.get(id=self.kwargs.get('pk'))

    def get_success_url(self):
        # messages.warning(self.request, '成功將 {} 從購物車刪除!'.format(self.object.title))
        messages.warning(self.request, '成功將 {} 從購物車刪除!'.format(self.object.product.title))
        return reverse('cart_detail')

# def product_list(request):
#     products = Product.objects.all()
#     return render(request, 'estore/product_list.html', {'products': products})
# class ProductList(generic.ListView):
# class CartDetailFromRequest(generic.DetailView):
class CartDetailMixin(object):
    def get_object(self):
        return self.request.cart

class CartDetailFromRequest(CartDetailMixin, generic.DetailView):
    # pass
    def get_context_data(self, **kwargs):
        context = {
            'quantity_iter': range(1, 6)
        }
        context.update(kwargs)
        return super(CartDetailFromRequest, self).get_context_data(**context)

class CartDelete(CartDetailMixin, generic.DeleteView):
    def get_success_url(self):
        messages.warning(self.request, '已清空購物車')
        return reverse('cart_detail')

    def get(self, request, *args, **kwargs):
        return redirect('cart_detail')

# class OrderDetail(generic.DetailView):
#     # model = Order
#     def get_object(self):
#         return get_object_or_404(Order.objects, token=uuid.UUID(self.kwargs.get('token')))

class CartItemUpdate(generic.UpdateView):
    model = Cart_Items
    fields = ['quantity']
    http_method_names = ['post']

    def get_object(self):
        return self.request.cart.cart_items_set.get(id=self.kwargs.get('pk'))

    def get_success_url(self):
        messages.success(self.request, '成功變更數量')
        return reverse('cart_detail')

class DashboardOrderAction(generic.UpdateView):
    fields = []
    accept_acctions = ['make_payment', 'ship', 'deliver', 'return_good', 'cancell_order']

    def get_object(self):
        return Order.objects.get(token=uuid.UUID(self.kwargs.get('token')))

    def form_valid(self, form):
        action = self.kwargs.get('action')
        if action in self.accept_acctions:
            action_func = getattr(self.object, action)
            try:
                action_func()
                form.save()
            except:
                return self.form_invalid(form)

            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, '無法處理訂單操作')
        return HttpResponseRedirect(reverse('dashboard_order_detail', kwargs={'token': self.object.token}))

    def get_success_url(self):
        messages.success(self.request, '訂單狀態已改變')
        return reverse('dashboard_order_detail', kwargs={'token': self.object.token})

class DashboardOrderDetail(generic.DetailView):
    permission_required = 'estore.change_order'
    template_name = 'estore/dashboard_order_detail.html'

    def get_object(self):
        return Order.objects.get(token=uuid.UUID(self.kwargs.get('token')))

    def get_context_data(self, **kwargs):
        if 'render_order_paid_state' not in kwargs:
            if self.object.is_paid:
                kwargs['paid_state'] = '已付款'
            else:
                kwargs['paid_state'] = '未付款'

        return super(DashboardOrderDetail, self).get_context_data(**kwargs)


class DashboardOrderList(PermissionRequiredMixin, generic.ListView):
    permission_required = 'estore.change_order'
    template_name = 'estore/dashboard_order_list.html'

    def get_queryset(self):
        return Order.objects.all().order_by('-created')

class OrderList(LoginRequiredMixin, generic.ListView):
    def get_queryset(self):
        return self.request.user.order_set.all()

class OrderDetailMixin(object):
    def get_object(self):
        return get_object_or_404(self.request.user.order_set, token=uuid.UUID(self.kwargs.get('token')))


class OrderDetail(OrderDetailMixin, LoginRequiredMixin, generic.DetailView):
    pass

# class OrderPayWithCreditCard(generic.DetailView):
class OrderPayWithCreditCard(OrderDetailMixin, LoginRequiredMixin, generic.DetailView):
    def get_object(self):
        return get_object_or_404(Order.objects, token=uuid.UUID(self.kwargs.get('token')))

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)

        self.object.payment_method = 'credit_card'
        # self.object.is_paid = True
        self.object.make_payment()
        self.object.save()

        # return redirect('order_detail', token=self.object.token)
        messages.success(self.request, '成功完成付款')

        return redirect('order_list')

class OrderCreateCartCheckout(LoginRequiredMixin, generic.CreateView):
    model = Order
    fields = []

    def form_valid(self, form, **kwargs):
        for each_item in self.request.cart.cart_items_set.all():
            if each_item.product.quantity < each_item.quantity:
                if each_item.product.quantity:
                    messages.error(self.request, '{} 庫存不足, 請重新確認該商品數量'.format(each_item.product.title))
                    each_item.quantity = each_item.product.quantity
                    each_item.save()
                else:
                    messages.error(self.request, '{} 已售完, 請重新確認訂單'.format(each_item.product.title))
                    self.request.cart.cart_items_set.remove(each_item)
                return self.form_invalid(form, **kwargs)

        form_orderinfo = kwargs['form_orderinfo'].save()

        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.total = self.request.cart.total_price()
        self.object.info = form_orderinfo
        self.object.save()

        # for each_item in self.request.cart.items.all():
        for each_item in self.request.cart.cart_items_set.all():
            self.object.orderitem_set.create(
                # title=each_item.title,
                # price=each_item.price,
                title=each_item.product.title,
                price=each_item.product.price,
                # quantity=1,
                quantity=each_item.quantity,
            )
            # each_item.product.quantity = each_item.product.quantity - 1
            each_item.product.quantity = each_item.product.quantity - each_item.quantity
            each_item.product.save()

            self.request.cart.cart_items_set.all().delete()   #訂單產生時清空購物車

            send_order_mail(
            from_email=None,
            recipient_list=[self.request.user.email],
            request=self.request,
            order=self.object,
            )

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, **kwargs):
        return self.render_to_response(self.get_context_data(form=form, **kwargs))

    def get_context_data(self, **kwargs):
        if 'form_orderinfo' not in kwargs:
            kwargs['form_orderinfo'] = OrderInfoForm()
        return super(OrderCreateCartCheckout, self).get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        form_orderinfo = OrderInfoForm(request.POST)
        if form.is_valid() and form_orderinfo.is_valid():
            return self.form_valid(form, form_orderinfo=form_orderinfo)
        else:
            return self.form_invalid(form, form_orderinfo=form_orderinfo)

    def get_success_url(self):
        messages.success(self.request, '訂單已生成')
        # return reverse('product_list')
        #return reverse('order_detail', kwargs={'pk': self.object.pk})
        return reverse('order_detail', kwargs={'token': self.object.token})

class ProductList(PermissionRequiredMixin, generic.ListView):
    model = Product

    def has_permission(self):
        if self.permission_required:
            return super(ProductList, self).has_permission()
        else:
            return True

class ProductDetail(generic.DetailView):
    model = Product

# @permission_required('estore.add_product')
# def product_create(request):
#     if request.method == "POST":
#         form = ProductForm(request.POST)
#         if form.is_valid():
#             product = form.save()
#             return redirect('product_list')
#     else:
#         form = ProductForm()
#     return render(request, 'estore/product_form.html', {'form': form})
class ProductCreate(PermissionRequiredMixin, generic.CreateView):
    permission_required = 'estore.add_product'
    model = Product
    fields = ('title', 'description', 'quantity', 'price', 'image')

    def get_success_url(self):
        messages.success(self.request, '產品已新增')
        # return reverse('product_list')
        return reverse('dashboard_product_list')

# @permission_required('estore.change_product')
# def product_update(request, pk):
#     product = get_object_or_404(Product, pk=pk)
#     form = ProductForm(request.POST or None, instance=product)

#     if request.POST and form.is_valid():
#         form.save()
#         messages.success(request, '產品已變更')

#     return render(request, 'estore/product_form.html', {'form': form})
class ProductUpdate(PermissionRequiredMixin, generic.UpdateView):
    permission_required = 'estore.change_product'
    model = Product
    fields = ('title', 'description', 'quantity', 'price', 'image')

    def get_success_url(self):
        messages.success(self.request, '產品已變更')
        # return reverse('product_update', kwargs=self.kwargs)
        return reverse('dashboard_product_update', kwargs=self.kwargs)

class ProductAddToCart(generic.DetailView):
    model = Product
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        # self.request.cart.items.add(self.object)
        self.request.cart.cart_items_set.create(product=self.object, quantity=1)

        messages.success(self.request, '已加入購物車')
        return redirect('product_detail', pk=self.object.id)

class UserList(PermissionRequiredMixin, generic.ListView):
    permission_required = 'auth.change_user'
    model = User
    template_name = 'estore/dashboard_user_list.html'


class UserAddToStaff(PermissionRequiredMixin, generic.UpdateView):
    permission_required = 'auth.change_user'
    model = User
    fields = []

    def get_success_url(self):
        if self.request.method == 'POST':
            group = Group.objects.get(name='estore_staff')
            group.user_set.add(self.object)
            messages.success(self.request, '已變更使用者身份為管理者')
        return reverse('dashboard_user_list')


class UserRemoveFromStaff(PermissionRequiredMixin, generic.UpdateView):
    permission_required = 'auth.change_user'
    model = User
    fields = []

    def get_success_url(self):
        if self.request.method == 'POST':
            group = Group.objects.get(name='estore_staff')
            group.user_set.remove(self.object)
            messages.success(self.request, '已變更使用者身份為一般使用者')
        return reverse('dashboard_user_list')

class UserCreate(generic.CreateView):
    model = User
    form_class = EstoreUserCreationForm

    def get_success_url(self):
        messages.success(self.request, '帳戶已創立')
        return reverse('login')

