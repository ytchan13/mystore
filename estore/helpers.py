from django.core.mail import send_mail
from django.template.loader import render_to_string


def send_order_mail(from_email, recipient_list, request, order, **kwargs):
    if 'order_full_url' not in kwargs:
        order_full_url = request.build_absolute_uri(str(order.get_absolute_url()))
        kwargs['order_full_url'] = order_full_url
    if 'object' not in kwargs:
        kwargs['object'] = order
    msg_html = render_to_string('estore/order_notify_mail.html', kwargs)

    return send_mail(
        '[Estore] 感謝您完成本次的下單，以下是您這次購物明細 {}'.format(order.token.hex),
        '',
        from_email,
        recipient_list,
        html_message=msg_html,
    )