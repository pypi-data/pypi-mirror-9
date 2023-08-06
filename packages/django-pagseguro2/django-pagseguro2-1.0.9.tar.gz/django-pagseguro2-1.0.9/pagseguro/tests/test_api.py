# -*- coding: utf-8 -*-
from django.test import TestCase

from decimal import Decimal
import httpretty
from dateutil.parser import parse

from pagseguro.api import PagSeguroItem, PagSeguroApi
from pagseguro.settings import (
    CHECKOUT_URL, PAYMENT_URL, NOTIFICATION_URL, TRANSACTION_URL
)


class PagSeguroItemTest(TestCase):

    def setUp(self):
        self.data = {
            'id': '0001',
            'description': 'My item 1',
            'amount': '10.00',
            'quantity': 1
        }

    def test_invalid_amount(self):
        self.data['amount'] = 'invalid'
        self.assertRaises(Exception, lambda: PagSeguroItem(**self.data))

        self.data['amount'] = '10.0'
        self.assertRaises(Exception, lambda: PagSeguroItem(**self.data))

        self.data['amount'] = '10.000'
        self.assertRaises(Exception, lambda: PagSeguroItem(**self.data))

    def test_invalid_quantity(self):
        self.data['quantity'] = 'ten'
        self.assertRaises(Exception, lambda: PagSeguroItem(**self.data))

    def test_invalid_id(self):
        self.data['id'] = '0' * 101
        self.assertRaises(Exception, lambda: PagSeguroItem(**self.data))

    def test_invalid_description(self):
        self.data['description'] = 'a' * 101
        self.assertRaises(Exception, lambda: PagSeguroItem(**self.data))

    def test_invalid_shipping_cost(self):
        self.data['shipping_cost'] = 'invalid'
        self.assertRaises(Exception, lambda: PagSeguroItem(**self.data))

        self.data['shipping_cost'] = '10.0'
        self.assertRaises(Exception, lambda: PagSeguroItem(**self.data))

        self.data['shipping_cost'] = '10.000'
        self.assertRaises(Exception, lambda: PagSeguroItem(**self.data))

    def test_invalid_weight(self):
        self.data['weight'] = 'ten'
        self.assertRaises(Exception, lambda: PagSeguroItem(**self.data))

    def test_valid_item(self):
        item = PagSeguroItem(**self.data)
        self.assertEqual(item.id, '0001')
        self.assertEqual(item.description, 'My item 1')
        self.assertEqual(item.amount, Decimal('10.00'))
        self.assertEqual(item.quantity, 1)
        self.assertEqual(item.shipping_cost, None)
        self.assertEqual(item.weight, None)

        self.data['shipping_cost'] = '10.00'
        self.data['weight'] = 300
        item = PagSeguroItem(**self.data)
        self.assertEqual(item.shipping_cost, Decimal('10.00'))
        self.assertEqual(item.weight, 300)


notification_response_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<transaction>
  <date>2014-06-05T22:52:49.000-03:00</date>
  <code>04B68A13-C2CF-4821-8611-F2002636270D</code>
  <reference>REF1234</reference>
  <type>1</type>
  <status>1</status>
  <lastEventDate>2014-06-06T01:10:12.000-03:00</lastEventDate>
  <paymentMethod>
    <type>1</type>
    <code>101</code>
  </paymentMethod>
  <grossAmount>38.00</grossAmount>
  <discountAmount>0.00</discountAmount>
  <feeAmount>2.30</feeAmount>
  <netAmount>35.70</netAmount>
  <extraAmount>0.00</extraAmount>
  <escrowEndDate>2014-06-06T01:05:14.000-03:00</escrowEndDate>
  <installmentCount>1</installmentCount>
  <itemCount>2</itemCount>
  <items>
    <item>
      <id>0001</id>
      <description>Meu item1</description>
      <quantity>1</quantity>
      <amount>14.00</amount>
    </item>
    <item>
      <id>0002</id>
      <description>Meu item2</description>
      <quantity>1</quantity>
      <amount>24.00</amount>
    </item>
  </items>
  <sender>
    <name>Comprador Virtual</name>
    <email>c11004631206281776849@sandbox.pagseguro.com.br</email>
    <phone>
      <areaCode>11</areaCode>
      <number>99999999</number>
    </phone>
  </sender>
  <shipping>
    <address>
      <street>RUA JOSE BRANCO RIBEIRO</street>
      <number>840</number>
      <complement />
      <district>Catolé</district>
      <city>CAMPINA GRANDE</city>
      <state>PB</state>
      <country>BRA</country>
      <postalCode>58410175</postalCode>
    </address>
    <type>3</type>
    <cost>0.00</cost>
  </shipping>
</transaction>'''

transaction_response_xml = '''<?xml version="1.0" encoding="ISO-8859-1" standalone="yes"?>
<transaction>
    <date>2011-02-05T15:46:12.000-02:00</date>
    <lastEventDate>2011-02-15T17:39:14.000-03:00</lastEventDate>
    <code>9E884542-81B3-4419-9A75-BCC6FB495EF1</code>
    <reference>REF1234</reference>
    <type>1</type>
    <status>3</status>
    <paymentMethod>
        <type>1</type>
        <code>101</code>
    </paymentMethod>
    <grossAmount>49900.00</grossAmount>
    <discountAmount>0.00</discountAmount>
    <feeAmount>0.00</feeAmount>
    <netAmount>49900.50</netAmount>
    <extraAmount>0.00</extraAmount>
    <installmentCount>1</installmentCount>
    <itemCount>2</itemCount>
    <items>
        <item>
            <id>0001</id>
            <description>Notebook Prata</description>
            <quantity>1</quantity>
            <amount>24300.00</amount>
        </item>
        <item>
            <id>0002</id>
            <description>Notebook Rosa</description>
            <quantity>1</quantity>
            <amount>25600.00</amount>
        </item>
    </items>
    <sender>
        <name>José Comprador</name>
        <email>comprador@uol.com.br</email>
        <phone>
            <areaCode>11</areaCode>
            <number>56273440</number>
        </phone>
    </sender>
    <shipping>
        <address>
            <street>Av. Brig. Faria Lima</street>
            <number>1384</number>
            <complement>5o andar</complement>
            <district>Jardim Paulistano</district>
            <postalCode>01452002</postalCode>
            <city>Sao Paulo</city>
            <state>SP</state>
            <country>BRA</country>
        </address>
        <type>1</type>
        <cost>21.50</cost>
    </shipping>
</transaction>'''

checkout_response_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<checkout>
  <code>67DB59D3BDBD84EAA4396F929DB350A7</code>
  <date>2014-06-07T00:52:04.000-03:00</date>
</checkout>'''


class PagSeguroApiTest(TestCase):

    def setUp(self):
        self.item1 = PagSeguroItem(
            id='1',
            description='My item 1',
            amount='10.00',
            quantity=1
        )
        self.item2 = PagSeguroItem(
            id='2',
            description='My item 2',
            amount='10.00',
            quantity=1
        )
        self.item3 = PagSeguroItem(
            id='3',
            description='My item 3',
            amount='10.00',
            quantity=1,
            shipping_cost='10.00',
            weight=300
        )
        self.pagseguro_api = PagSeguroApi()

    def test_add_item(self):
        self.pagseguro_api.add_item(self.item1)
        self.assertIn(self.item1, self.pagseguro_api.get_items())

        self.pagseguro_api.add_item(self.item2)
        self.assertIn(self.item1, self.pagseguro_api.get_items())
        self.assertIn(self.item2, self.pagseguro_api.get_items())

        self.pagseguro_api.add_item(self.item3)
        self.assertIn(self.item1, self.pagseguro_api.get_items())
        self.assertIn(self.item2, self.pagseguro_api.get_items())
        self.assertIn(self.item3, self.pagseguro_api.get_items())

    def test_clear_items(self):
        self.pagseguro_api.add_item(self.item1)
        self.pagseguro_api.add_item(self.item2)
        self.pagseguro_api.add_item(self.item3)
        self.pagseguro_api.clear_items()
        self.assertNotIn(self.item1, self.pagseguro_api.get_items())
        self.assertNotIn(self.item2, self.pagseguro_api.get_items())
        self.assertNotIn(self.item3, self.pagseguro_api.get_items())

    @httpretty.activate
    def test_invalid_checkout(self):
        self.pagseguro_api.add_item(self.item1)
        self.pagseguro_api.add_item(self.item2)
        self.pagseguro_api.add_item(self.item3)

        # mock requests
        httpretty.register_uri(
            httpretty.POST,
            CHECKOUT_URL,
            body='Unauthorized',
            status=401,
        )

        data = self.pagseguro_api.checkout()
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unauthorized')
        self.assertEqual(data['status_code'], 401)

    @httpretty.activate
    def test_valid_checkout(self):
        self.pagseguro_api.add_item(self.item1)
        self.pagseguro_api.add_item(self.item2)
        self.pagseguro_api.add_item(self.item3)

        # mock requests
        httpretty.register_uri(
            httpretty.POST,
            CHECKOUT_URL,
            body=checkout_response_xml,
            status=200,
        )

        data = self.pagseguro_api.checkout()
        self.assertEqual(data['success'], True)
        self.assertEqual(data['status_code'], 200)
        self.assertEqual(data['code'], '67DB59D3BDBD84EAA4396F929DB350A7')
        self.assertEqual(data['date'], parse('2014-06-07T00:52:04.000-03:00'))
        self.assertEqual(
            data['redirect_url'],
            '{0}?code={1}'.format(PAYMENT_URL, data['code'])
        )

    @httpretty.activate
    def test_get_invalid_notification(self):
        # mock requests
        httpretty.register_uri(
            httpretty.GET,
            NOTIFICATION_URL + '/{0}'.format(
                'A5182C-C9EF48EF48D2-1FF4AF6FAC82-EB2948'
            ),
            body='Unauthorized',
            status=401,
        )

        response = self.pagseguro_api.get_notification(
            'A5182C-C9EF48EF48D2-1FF4AF6FAC82-EB2948'
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.text, 'Unauthorized')

    @httpretty.activate
    def test_get_valid_notification(self):
        # mock requests
        httpretty.register_uri(
            httpretty.GET,
            NOTIFICATION_URL + '/{0}'.format(
                'A5182C-C9EF48EF48D2-1FF4AF6FAC82-EB2948'
            ),
            body=notification_response_xml,
            status=200,
        )

        response = self.pagseguro_api.get_notification(
            'A5182C-C9EF48EF48D2-1FF4AF6FAC82-EB2948'
        )
        self.assertEqual(response.status_code, 200)

    @httpretty.activate
    def test_get_invalid_transaction(self):
        # mock requests
        httpretty.register_uri(
            httpretty.GET,
            TRANSACTION_URL + '/{0}'.format(
                '9E884542-81B3-4419-9A75-BCC6FB495EF1'
            ),
            body='Unauthorized',
            status=401,
        )

        data = self.pagseguro_api.get_transaction(
            '9E884542-81B3-4419-9A75-BCC6FB495EF1'
        )
        self.assertEqual(data['status_code'], 401)
        self.assertEqual(data['message'], 'Unauthorized')

    @httpretty.activate
    def test_get_valid_transaction(self):
        # mock requests
        httpretty.register_uri(
            httpretty.GET,
            TRANSACTION_URL + '/{0}'.format(
                '9E884542-81B3-4419-9A75-BCC6FB495EF1'
            ),
            body=transaction_response_xml,
            status=200,
        )

        data = self.pagseguro_api.get_transaction(
            '9E884542-81B3-4419-9A75-BCC6FB495EF1'
        )
        self.assertEqual(data['status_code'], 200)
        self.assertEqual(
            data['transaction']['code'],
            '9E884542-81B3-4419-9A75-BCC6FB495EF1'
        )

    def test_base_params_is_instance_variable(self):
        # Regression test
        api1 = PagSeguroApi()
        api2 = PagSeguroApi()
        self.assertIsNot(api1.base_params, api2.base_params)

    def test_params_is_instance_variable(self):
        # Regression test
        api1 = PagSeguroApi()
        api2 = PagSeguroApi()
        self.assertIsNot(api1.params, api2.params)

    def test_items_is_instance_variable(self):
        # Regression test
        api1 = PagSeguroApi()
        api2 = PagSeguroApi()
        self.assertIsNot(api1.items, api2.items)
