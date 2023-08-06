# coding=utf-8
import json
from django.http import Http404
from rest_framework_proxy.views import ProxyView
from vtixy_proxy import settings


class VTIXyProxyView(ProxyView):
    proxy_settings = settings.vtixy_uat_proxy_settings

    def get_request_data(self, request):
        return json.dumps(request.DATA)


class ShowsProxy(VTIXyProxyView):
    source = 'shows/'


class EventsProxy(VTIXyProxyView):
    source = 'events/'


class TicketSetProxy(VTIXyProxyView):
    source = 'ticket_set/%(pk)s/'


class PriceCategoriesProxy(VTIXyProxyView):
    source = 'categories/'


class PriceCategoriesDetailsProxy(VTIXyProxyView):
    source = 'categories/%(pk)s/'


class OrdersProxy(VTIXyProxyView):
    source = 'orders/'

    def post(self, request, *args, **kwargs):
        response = super(OrdersProxy, self).post(request, args, kwargs)
        if response.status_code == 201:
            loyalty_name = request.DATA.get('loyalty_name')
            loyalty_card = request.DATA.get('loyalty_card')

            # Создание заказа в loyalty
            if loyalty_name is not None:
                for loyalty_program in settings.settings.VTIXY_LOYALTY:
                    if loyalty_name == loyalty_program[0]:
                        order_id = response.data.get('id', None)
                        price = response.data.get('price', None)
                        model = __import__(loyalty_program[1], globals(), locals(), ['models'], -1).models.Order
                        model.objects.create(number=order_id, amount=price, card=loyalty_card, state=model.STATE_OPEN)
        return response


class OrderDetailsProxy(VTIXyProxyView):
    source = 'orders/%(pk)s/'

    def get(self, request, *args, **kwargs):

        if not request.GET.get('transaction_id', None):
            raise Http404

        response = super(OrderDetailsProxy, self).get(request, *args, **kwargs)
        if not response.data.get('transaction_id', None):
            return response

        transaction_parts = response.data['transaction_id'].split('.')
        order_is_sold = response.data['sold']
        if order_is_sold and request.GET['transaction_id'] != transaction_parts[0]:
            raise Http404

        return response