from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static

from . import views

urlpatterns = [
    # url(r'^$', views.product_list, name='product_list'),
    # url(r'^create$', views.product_create, name='product_create'),
    # url(r'^(?P<pk>\d+)/update$', views.product_update, name='product_update'),
    url(r'^$', views.ProductList.as_view(), name='product_list'),
    # url(r'^create$', views.ProductCreate.as_view(), name='product_create'),
    url(r'^(?P<pk>\d+)/$', views.ProductDetail.as_view(), name='product_detail'),
    # url(r'^(?P<pk>\d+)/update$', views.ProductUpdate.as_view(), name='product_update'),
    url(r'^(?P<pk>\d+)/addtocart$', views.ProductAddToCart.as_view(), name='product_addtocart'),

    url(r'^cart/$', views.CartDetailFromRequest.as_view(), name='cart_detail'),
    url(r'^cart/checkout$', views.OrderCreateCartCheckout.as_view(), name='cart_checkout'),
    url(r'^cart/clear$', views.CartDelete.as_view(), name='cart_delete'),
    url(r'^cart/(?P<pk>\d+)/remove', views.CartItemDelete.as_view(), name='cart_item_delete'),
    url(r'^cart/(?P<pk>\d+)/update', views.CartItemUpdate.as_view(), name='cart_item_update'),

    url(r'^dashboard/orders/$', views.DashboardOrderList.as_view(), name='dashboard_order_list'),
    url(r'^dashboard/orders/(?P<token>[0-9a-f-]+)/$', views.DashboardOrderDetail.as_view(), name='dashboard_order_detail'),
    url(r'^dashboard/orders/(?P<token>[0-9a-f-]+)/(?P<action>[a-z_]+)$', views.DashboardOrderAction.as_view(), name='dashboard_order_action'),

    url(r'^dashboard/products/$', views.ProductList.as_view(template_name='estore/dashboard_product_list.html', permission_required='estore.change_product'), name='dashboard_product_list'),
    url(r'^dashboard/products/create$', views.ProductCreate.as_view(), name='dashboard_product_create'),
    url(r'^dashboard/products/(?P<pk>\d+)/update$', views.ProductUpdate.as_view(), name='dashboard_product_update'),

    url(r'^dashboard/users/$', views.UserList.as_view(), name='dashboard_user_list'),
    url(r'^dashboard/users/(?P<pk>\d+)/addtostaff$', views.UserAddToStaff.as_view(), name='dashboard_user_addtostaff'),
    url(r'^dashboard/users/(?P<pk>\d+)/removefromstaff$', views.UserRemoveFromStaff.as_view(), name='dashboard_user_removefromstaff'),

    url(r'^order/$', views.OrderList.as_view(), name='order_list'),
    # url(r'^order/(?P<pk>\d+)/', views.OrderDetail.as_view(), name='order_detail')
    url(r'^order/(?P<token>[0-9a-f-]+)/$', views.OrderDetail.as_view(), name='order_detail'),
    url(r'^order/(?P<token>[0-9a-f-]+)/pay_with_credit_card$', views.OrderPayWithCreditCard.as_view(), name='order_pay_with_credit_card'),

    url(r'^sign-up', views.UserCreate.as_view(), name='sign_up'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)