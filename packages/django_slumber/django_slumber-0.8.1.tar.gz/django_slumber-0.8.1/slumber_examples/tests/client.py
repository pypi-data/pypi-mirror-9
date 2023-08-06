from mock import patch

from django.contrib.auth.models import User
from django.test import TestCase

from slumber import client
from slumber.connector import Client, DictObject
from slumber.connector.api import get_instance
from slumber.connector.ua import get

from slumber_examples.models import Pizza, PizzaPrice, PizzaSizePrice
from slumber_examples.tests.configurations import ConfigureUser
from slumber_examples.tests.views import ServiceTestsWithDirectory


class TestDirectoryURLs(ConfigureUser, TestCase):
    def test_get_default_url_with_made_client(self):
        client = Client()
        self.assertEqual('http://localhost:8000/slumber/', client._directory)

    def test_get_default_url_with_default_client(self):
        self.assertEqual('http://localhost:8000/slumber/', client._directory)

    def test_get_default_url_with_services(self):
        with patch('slumber.server._get_slumber_directory', lambda: {
                'pizzas': 'http://localhost:8001/slumber/pizzas/',
                'takeaway': 'http://localhost:8002/slumber/'}):
            client = Client()
        self.assertIsNone(client._directory)


class TestLoads(ConfigureUser, TestCase):
    def test_applications_local(self):
        client = Client('http://localhost:8000/slumber')
        self.assertTrue(hasattr(client, 'slumber_examples'))

    def test_applications_remote(self):
        def request(k, u, headers):
            self.assertEquals(u, 'http://slumber.example.com/')
            return DictObject(status=200), '''{"apps":{}}'''
        with patch('slumber.connector.ua.Http.request', self.fail):
            client = Client('http://slumber.example.com/')
        with patch('slumber.connector.ua.Http.request', request):
            try:
                client.no_module
                self.fail("This should have given an attribute error")
            except AttributeError:
                pass

    def test_applications_with_dots_in_name(self):
        client = Client()
        self.assertTrue(hasattr(client, 'django'), client.__dict__.keys())
        self.assertTrue(hasattr(client.django, 'contrib'), client.django.__dict__.keys())
        self.assertTrue(hasattr(client.django.contrib, 'auth'),
            (type(client.django.contrib), client.django.contrib.__dict__.keys()))
        try:
            client.django.NotAModelOrApp
            self.fail("This should have given an attribute error")
        except AttributeError:
            pass

    def test_new_client_gives_AttributeError_on_invalid_model(self):
        client = Client()
        try:
            client.django.contrib.auth.NotAModelOrApp
            self.fail("This should have given an attribute error")
        except AttributeError:
            pass

    def test_module_attributes(self):
        self.assertTrue(client.slumber_examples.Pizza.module, 'slumber_examples')
        self.assertTrue(client.slumber_examples.Pizza.name, 'Pizza')
        try:
            client.slumber_examples.Pizza.not_a_module_attr
            self.fail("This should have thrown an attribute error")
        except AttributeError:
            pass

    def test_can_create_instance(self):
        self.user.is_superuser = True
        self.user.save()
        rpizza = client.slumber_examples.Pizza.create(
            name='P1', for_sale=True)
        lpizza = Pizza.objects.get(name='P1')
        self.assertEquals(rpizza.id, lpizza.id)


class TestAuth(ConfigureUser, TestCase):
    def test_has_attributes(self):
        user = client.django.contrib.auth.User.get(pk=self.user.pk)
        for attr in ['is_active', 'is_staff', 'date_joined', 'is_superuser',
                'first_name', 'last_name', 'email', 'username']:
            self.assertTrue(hasattr(user, attr), user.__dict__.keys())


class TestsWithPizza(ConfigureUser, TestCase):
    def setUp(self):
        super(TestsWithPizza, self).setUp()
        self.s = Pizza(name='S1', for_sale=True)
        self.s.save()
        self.pizza = client.slumber_examples.Pizza.get(pk=self.s.pk)

    def test_instance_type(self):
        self.assertEqual(self.s.pk, self.pizza.id)
        self.assertEqual(type(self.pizza).__name__,
            'http://localhost:8000/slumber/slumber_examples/Pizza/data/1/')
        pizza_type = str(type(self.pizza))
        self.assertTrue(pizza_type.endswith("slumber_examples/Pizza/data/1/'>"),
            pizza_type)

    def test_cache_ttl(self):
        self.assertEqual(self.pizza._CACHE_TTL, 0)

    def test_instance_data(self):
        self.assertEqual('S1', self.pizza.name)
        prices = self.pizza.prices
        self.assertEqual(len(prices), 0)
        self.assertTrue(self.pizza.exclusive_to is None, self.pizza.exclusive_to)
        try:
            self.pizza.not_a_field
            self.fail("This should have thrown an AttributeError")
        except AttributeError:
            pass

    def test_instance_data_with_data_array(self):
        for p in range(15):
            PizzaPrice(pizza=self.s, date='2011-04-%s' % (p+1)).save()
        self.assertEqual('S1', self.pizza.name)
        prices = self.pizza.prices
        self.assertEquals(len(prices), 15)
        first_price = prices[0]
        self.assertEquals(unicode(first_price), "PizzaPrice object")
        self.assertEquals(first_price.pizza.for_sale, True)

    def test_instance_data_with_nested_data_array(self):
        p = PizzaPrice(pizza=self.s, date='2010-06-20')
        p.save()
        PizzaSizePrice(price=p, size='s', amount='13.95').save()
        PizzaSizePrice(price=p, size='m', amount='15.95').save()
        PizzaSizePrice(price=p, size='l', amount='19.95').save()
        self.assertEqual('S1', self.pizza.name)
        self.assertEqual(len(self.pizza.prices), 1)
        self.assertEqual(len(self.pizza.prices[0].amounts), 3)
        for a in self.pizza.prices[0].amounts:
            self.assertTrue(a.size in ['s', 'm', 'l'], a.size)

    def test_instance_no_pk(self):
        with self.assertRaises(AssertionError):
            pizza = client.slumber_examples.Pizza.get()

    def test_2nd_pizza_comes_from_cache(self):
        # Force a cache read
        self.assertEqual(unicode(self.pizza), u"S1")
        # Make a 2nd alias to the same object
        fail = lambda *a, **f: self.fail("_InstanceConnector.__init__ called again %s, %s" % (a, f))
        with patch('slumber.connector.api._InstanceConnector.__init__', fail):
            pizza2 = client.slumber_examples.Pizza.get(pk=self.s.pk)
            self.assertEqual(unicode(pizza2), u"S1")

    def test_pizza_not_found(self):
        with self.assertRaises(AssertionError):
            p2 = client.slumber_examples.Pizza.get(pk=2)


class TestGetInstance(ConfigureUser, ServiceTestsWithDirectory, TestCase):
    def setUp(self):
        super(TestGetInstance, self).setUp()
        self.pizza = Pizza.objects.create(name='S1', for_sale=True)

    def test_get_instance_with_slumber_urls(self):
        pizza = get_instance(
            'slumber://pizzas/slumber_examples/Pizza/',
            'slumber://pizzas/slumber_examples/Pizza/data/%s/' % self.pizza.id,
            None)
        self.assertEqual(pizza._url,
            'http://localhost:8000/slumber/pizzas/slumber_examples/'
                'Pizza/data/%s/' % self.pizza.id)
        self.assertEqual(pizza.id, self.pizza.id)
        self.assertEqual(pizza.name, self.pizza.name)


class AppServiceTests(ConfigureUser, TestCase):
    """Used to get service view tests where the service is configured
    on the application.
    """
    def setUp(self):
        super(AppServiceTests, self).setUp()
        pizzas = lambda: 'pizzas'
        directory = lambda: {
                'auth': 'django.contrib.auth',
                'pizzas': 'http://localhost:8000/slumber/pizzas/',
            }
        self.__patchers = [
            patch('slumber.server._get_slumber_service', pizzas),
            patch('slumber.server._get_slumber_directory', directory),
        ]
        [p.start() for p in self.__patchers]
    def tearDown(self):
        [p.stop() for p in self.__patchers]
        super(AppServiceTests, self).tearDown()

    def test_directory(self):
        request, json = get('http://localhost:8000/slumber/')
        self.assertEquals(json['services'], {
            'auth': 'http://localhost:8000/slumber/pizzas/django/contrib/auth/',
            'pizzas': 'http://localhost:8000/slumber/pizzas/'})

    def test_auth(self):
        self.client = Client()
        self.assertTrue(hasattr(self.client, 'auth'), self.client.__dict__)
        self.assertTrue(hasattr(self.client.auth, 'User'), self.client.auth.__dict__)

    def test_pizzas(self):
        self.client = Client()
        self.assertTrue(hasattr(self.client, 'pizzas'), self.client.__dict__)
        self.assertTrue(hasattr(self.client.pizzas, 'slumber_examples'),
            self.client.pizzas.__dict__)
