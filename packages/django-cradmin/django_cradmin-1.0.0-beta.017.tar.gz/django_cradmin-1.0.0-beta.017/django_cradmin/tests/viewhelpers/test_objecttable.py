import htmls
import mock
from django.test import TestCase, RequestFactory

from django_cradmin.tests.viewhelpers.cradmin_viewhelpers_testapp.models import TestModel
from django_cradmin.viewhelpers import objecttable
from django_cradmin.django_cradmin_testapp import models as testmodels


class TestColumn(TestCase):
    def setUp(self):
        class TestColSubclass(objecttable.Column):
            modelfield = 'testfield'

            def __init__(self, **kwargs):
                super(TestColSubclass, self).__init__(**kwargs)

        self.model_testobject = TestModel()
        view = mock.MagicMock()
        view.model = self.model_testobject
        self.column_subclass = TestColSubclass(view=view, columnindex=0)

    def test_get_header_not_implemented(self):
        test = objecttable.Column(view=None, columnindex=0)

        with self.assertRaises(NotImplementedError):
            test.get_header()

    def test_get_header(self):
        self.assertEqual("Test Value", self.column_subclass.get_header())

    def test_render_value(self):
        self.model_testobject.testfield = u'test_value'
        self.assertEqual("test_value", self.column_subclass.render_value(self.model_testobject))

    # check that you get an exception when running render_value without having modelfield..
    def test_render_value_not_implemented(self):
        col = objecttable.Column(view=None, columnindex=0)

        with self.assertRaises(NotImplementedError):
            col.render_value(None)

    # check that you get an exception when running render_cell_content without overriding with subclass..
    def test_render_cell_not_implemented(self):
        col = objecttable.Column(view=None, columnindex=0)

        with self.assertRaises(NotImplementedError):
            col.render_cell_content(None)


class TestPlainTextColumn(TestCase):
    def setUp(self):
        class TestColSubclass(objecttable.PlainTextColumn):
            modelfield = 'testfield'

            def __init__(self, **kwargs):
                super(TestColSubclass, self).__init__(**kwargs)

        self.model_testobject = TestModel()
        view = mock.MagicMock()
        view.model = self.model_testobject
        self.column_subclass = TestColSubclass(view=view, columnindex=0)

    def test_render_cell(self):
        self.model_testobject.testfield = 'test_value'
        self.assertEquals(
            '<span class="objecttable-cellvalue">test_value</span>',
            self.column_subclass.render_cell_content(self.model_testobject).strip())


class TestSingleActionColumn(TestCase):
    def setUp(self):
        class TestIncompleteColSubclass(objecttable.SingleActionColumn):
            modelfield = 'testfield'

            def __init__(self, **kwargs):
                super(TestIncompleteColSubclass, self).__init__(**kwargs)

        class TestColSubclass(objecttable.SingleActionColumn):
            modelfield = 'testfield'

            def __init__(self, **kwargs):
                super(TestColSubclass, self).__init__(**kwargs)

            def get_actionurl(self, obj):
                return 'www.example.com/{}'.format(obj.testfield)

        self.model_testobject = TestModel(testfield="test_value")
        view = mock.MagicMock()
        view.model = self.model_testobject
        self.column_subclass = TestColSubclass(view=view, columnindex=0)
        self.column_subclass_incomplete = TestIncompleteColSubclass(view=view, columnindex=0)

    def test_get_actionurl_ExceptionRaised(self):
        with self.assertRaises(NotImplementedError):
            self.column_subclass_incomplete.get_actionurl(self.model_testobject)

    def test_render_cell_ExceptionRaised(self):
        with self.assertRaises(NotImplementedError):
            self.column_subclass_incomplete.render_cell_content(self.model_testobject)

    def test_render_cell(self):
        expected = '<a href="www.example.com/test_value" class="objecttable-cellvalue-link">test_value</a>'
        self.assertEquals(self.column_subclass.render_cell_content(self.model_testobject), expected)


class TestMultiActionColumn(TestCase):
    def setUp(self):
        class TestIncompleteColSubclass(objecttable.MultiActionColumn):
            modelfield = 'testfield'

            def __init__(self, **kwargs):
                super(TestIncompleteColSubclass, self).__init__(**kwargs)

        class TestColSubclass(objecttable.MultiActionColumn):
            modelfield = 'testfield'

            def __init__(self, **kwargs):
                super(TestColSubclass, self).__init__(**kwargs)

            def get_buttons(self, obj):
                return [objecttable.Button(label="Btn1", url="www.example.com/btn1"),
                        objecttable.Button(label="Btn2", url="www.example.com/btn2")]

        self.model_testobject = TestModel(testfield="test_value")
        view = mock.MagicMock()
        view.model = self.model_testobject
        self.column_subclass = TestColSubclass(view=view, columnindex=0)
        self.column_subclass_incomplete = TestIncompleteColSubclass(view=view, columnindex=0)

    def test_get_buttons_ExceptionRaised(self):
        with self.assertRaises(NotImplementedError):
            self.column_subclass_incomplete.get_buttons(self.model_testobject)

    def test_render_cell_ExceptionRaised(self):
        with self.assertRaises(NotImplementedError):
            self.column_subclass_incomplete.render_cell_content(self.model_testobject)

    def test_render_cell(self):
        expected = [
            '<p', 'class="objecttable-cellvalue">test_value</p>',
            '<p', 'class="objecttable-cellbuttons">',
            '<a', 'href="www.example.com/btn1"', 'class="btn', 'btn-default', 'btn-sm"', '>', 'Btn1', '</a>',
            '<a', 'href="www.example.com/btn2"', 'class="btn', 'btn-default', 'btn-sm"', '>', 'Btn2', '</a>',
            '</p>'
        ]
        result = self.column_subclass.render_cell_content(self.model_testobject).split()
        self.assertEquals(result, expected)


class TestButton(TestCase):
    def test_render_with_icon_and_class(self):
        btn = objecttable.Button(
            label="My Btn", url="www.example.com/mybtnurl",
            buttonclass="danger",
            icon="glyphicon glyphicon-shopping-cart")
        expected = [
            '<a', 'href="www.example.com/mybtnurl"', 'class="btn', 'btn-danger', 'btn-sm"', '>',
            '<span', 'class="glyphicon', 'glyphicon-shopping-cart"></span>', 'My', 'Btn', '</a>'
        ]
        result = btn.render().split()
        self.assertEquals(result, expected)

    def test_render_simple(self):
        btn = objecttable.Button(label="My Btn", url="www.example.com/mybtnurl")
        expected = [
            '<a', 'href="www.example.com/mybtnurl"', 'class="btn', 'btn-default', 'btn-sm"', '>',
            'My', 'Btn', '</a>']
        result = btn.render().split()
        self.assertEquals(result, expected)


class TestOrderingStringParser(TestCase):
    def test_parse_empty(self):
        orderingqueryarg = objecttable.OrderingStringParser('')
        self.assertEquals(len(orderingqueryarg.orderingdict), 0)

    def test_parse_single(self):
        orderingqueryarg = objecttable.OrderingStringParser('a3')
        self.assertEquals(len(orderingqueryarg.orderingdict), 1)
        self.assertTrue(orderingqueryarg.orderingdict[3])

    def test_parse_multi(self):
        orderingqueryarg = objecttable.OrderingStringParser('a3.d1')
        self.assertEquals(len(orderingqueryarg.orderingdict), 2)
        self.assertTrue(orderingqueryarg.orderingdict[3].order_ascending)
        self.assertFalse(orderingqueryarg.orderingdict[1].order_ascending)

    def test_remove_column(self):
        self.assertEqual(
            objecttable.OrderingStringParser('a3.d1.a6').remove_column(6),
            'a3.d1')
        self.assertEqual(
            objecttable.OrderingStringParser('a3.d1.a6').remove_column(1),
            'a3.a6')

    def test_remove_nonexisting_colum(self):
        self.assertEqual(
            objecttable.OrderingStringParser('').remove_column(2),
            '')
        self.assertEqual(
            objecttable.OrderingStringParser('a1').remove_column(2),
            'a1')
        self.assertEqual(
            objecttable.OrderingStringParser('a3.d1.a6').remove_column(2),
            'a3.d1.a6')

    def test_flip_existing_column(self):
        self.assertEqual(
            objecttable.OrderingStringParser('d1').flip_column(1),
            'a1')
        self.assertEqual(
            objecttable.OrderingStringParser('a3.d1.a6').flip_column(1),
            'a3.a1.a6')
        self.assertEqual(
            objecttable.OrderingStringParser('a3.d1.a6').flip_column(3),
            'd3.d1.a6')

    def test_flip_new_column(self):
        self.assertEqual(
            objecttable.OrderingStringParser('').flip_column(1),
            'a1')
        self.assertEqual(
            objecttable.OrderingStringParser('a3').flip_column(1),
            'a3.a1')


class TestObjectTableView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _mock_request(self, request):
        request.cradmin_role = mock.MagicMock()
        request.cradmin_app = mock.MagicMock()

    def test_paginate_by_singlepage(self):
        testmodels.SomeItem.objects.bulk_create(
            [testmodels.SomeItem(name=unicode(x)) for x in xrange(4)])

        class MyObjectTableView(objecttable.ObjectTableView):
            model = testmodels.SomeItem
            paginate_by = 4

            def get_queryset_for_role(self, role):
                return testmodels.SomeItem.objects.all()

        request = self.factory.get('/test')
        self._mock_request(request)
        response = MyObjectTableView.as_view()(request)
        response.render()
        selector = htmls.S(response.content)
        # selector.one('#django_cradmin_contentwrapper').prettyprint()
        self.assertEqual(selector.count('#objecttableview-table>tbody>tr'), 4)
        self.assertFalse(selector.exists('#django_cradmin_contentwrapper .pager'))

    def test_paginate_by_firstpage(self):
        testmodels.SomeItem.objects.bulk_create(
            [testmodels.SomeItem(name=unicode(x)) for x in xrange(5)])

        class MyObjectTableView(objecttable.ObjectTableView):
            model = testmodels.SomeItem
            paginate_by = 4

            def get_queryset_for_role(self, role):
                return testmodels.SomeItem.objects.all()

        request = self.factory.get('/test')
        self._mock_request(request)
        response = MyObjectTableView.as_view()(request)
        response.render()
        selector = htmls.S(response.content)
        self.assertEqual(selector.count('#objecttableview-table>tbody>tr'), 4)
        self.assertTrue(selector.exists('#django_cradmin_contentwrapper .pager'))
        self.assertTrue(selector.exists('#django_cradmin_contentwrapper .pager .previous.disabled'))
        self.assertTrue(selector.exists('#django_cradmin_contentwrapper .pager .next'))
        self.assertFalse(selector.exists('#django_cradmin_contentwrapper .pager .next.disabled'))

    def test_paginate_by_lastpage(self):
        testmodels.SomeItem.objects.bulk_create(
            [testmodels.SomeItem(name=unicode(x)) for x in xrange(5)])

        class MyObjectTableView(objecttable.ObjectTableView):
            model = testmodels.SomeItem
            paginate_by = 4

            def get_queryset_for_role(self, role):
                return testmodels.SomeItem.objects.all()

        request = self.factory.get('/test', {
            'page': 2
        })
        self._mock_request(request)
        response = MyObjectTableView.as_view()(request)
        response.render()
        selector = htmls.S(response.content)
        self.assertEqual(selector.count('#objecttableview-table>tbody>tr'), 1)
        self.assertTrue(selector.exists('#django_cradmin_contentwrapper .pager'))
        self.assertTrue(selector.exists('#django_cradmin_contentwrapper .pager .previous'))
        self.assertFalse(selector.exists('#django_cradmin_contentwrapper .pager .previous.disabled'))
        self.assertTrue(selector.exists('#django_cradmin_contentwrapper .pager .next.disabled'))

    def test_paginate_by_middlepage(self):
        testmodels.SomeItem.objects.bulk_create(
            [testmodels.SomeItem(name=unicode(x)) for x in xrange(9)])

        class MyObjectTableView(objecttable.ObjectTableView):
            model = testmodels.SomeItem
            paginate_by = 4

            def get_queryset_for_role(self, role):
                return testmodels.SomeItem.objects.all()

        request = self.factory.get('/test', {
            'page': 2
        })
        self._mock_request(request)
        response = MyObjectTableView.as_view()(request)
        response.render()
        selector = htmls.S(response.content)
        # selector.one('#django_cradmin_contentwrapper').prettyprint()
        self.assertEqual(selector.count('#objecttableview-table>tbody>tr'), 4)
        self.assertTrue(selector.exists('#django_cradmin_contentwrapper .pager'))
        self.assertTrue(selector.exists('#django_cradmin_contentwrapper .pager .previous'))
        self.assertTrue(selector.exists('#django_cradmin_contentwrapper .pager .next'))
        self.assertFalse(selector.exists('#django_cradmin_contentwrapper .pager .previous.disabled'))
        self.assertFalse(selector.exists('#django_cradmin_contentwrapper .pager .next.disabled'))

    def test_render_single_simple_column(self):
        testmodels.SomeItem.objects.create(name='Item One')

        class MyObjectTableView(objecttable.ObjectTableView):
            model = testmodels.SomeItem
            columns = ['name']

            def get_queryset_for_role(self, role):
                return testmodels.SomeItem.objects.all()

        request = self.factory.get('/test')
        self._mock_request(request)
        response = MyObjectTableView.as_view()(request)
        response.render()
        selector = htmls.S(response.content)

        self.assertEquals(selector.count('#objecttableview-table>thead>tr>th'), 1)
        self.assertEquals(
            selector.one('#objecttableview-table>thead>tr>th').alltext_normalized,
            'The name - Ordered descending - Click to order ascending')

        self.assertEqual(selector.count('#objecttableview-table>tbody>tr'), 1)
        self.assertEquals(selector.count('#objecttableview-table>tbody>tr>td'), 1)
        self.assertEquals(
            selector.one('#objecttableview-table>tbody>tr>td').alltext_normalized,
            'Item One')

    def test_render_multiple_simple_columns(self):
        testmodels.SomeItem.objects.create(name='Item One', somenumber=10)

        class MyObjectTableView(objecttable.ObjectTableView):
            model = testmodels.SomeItem
            columns = ['name', 'somenumber']

            def get_queryset_for_role(self, role):
                return testmodels.SomeItem.objects.all()

        request = self.factory.get('/test')
        self._mock_request(request)
        response = MyObjectTableView.as_view()(request)
        response.render()
        selector = htmls.S(response.content)

        self.assertEquals(selector.count('#objecttableview-table>thead>tr>th'), 2)
        self.assertEquals(
            selector.one('#objecttableview-table>thead>tr>th:first-child').alltext_normalized,
            'The name - Ordered descending - Click to order ascending')
        self.assertEquals(
            selector.one('#objecttableview-table>thead>tr>th:last-child').alltext_normalized,
            'Somenumber - Ordered descending - Click to order ascending')

        self.assertEqual(selector.count('#objecttableview-table>tbody>tr'), 1)
        self.assertEquals(selector.count('#objecttableview-table>tbody>tr>td'), 2)
        self.assertEquals(
            selector.one('#objecttableview-table>tbody>tr>td:first-child').alltext_normalized,
            'Item One')
        self.assertEquals(
            selector.one('#objecttableview-table>tbody>tr>td:last-child').alltext_normalized,
            '10')

    def test_render_order_ascending_singlecolumn(self):
        testmodels.SomeItem.objects.create(name='Item A')
        testmodels.SomeItem.objects.create(name='Item B')
        testmodels.SomeItem.objects.create(name='Item C')

        class MyObjectTableView(objecttable.ObjectTableView):
            model = testmodels.SomeItem
            columns = ['name']

            def get_queryset_for_role(self, role):
                return testmodels.SomeItem.objects.all()

        request = self.factory.get('/test', {
            'ordering': 'a0'
        })
        self._mock_request(request)
        response = MyObjectTableView.as_view()(request)
        response.render()
        selector = htmls.S(response.content)

        self.assertEqual(selector.count('#objecttableview-table>tbody>tr'), 3)
        self.assertEquals(
            selector.one('#objecttableview-table>tbody>tr:first-child>td').alltext_normalized,
            'Item A')
        self.assertEquals(
            selector.one('#objecttableview-table>tbody>tr:last-child>td').alltext_normalized,
            'Item C')

        self.assertEquals(
            selector.one('#objecttableview-table>thead>tr>th').alltext_normalized,
            'The name - Ordered ascending - Click to order descending')

    def test_render_order_descending_column(self):
        testmodels.SomeItem.objects.create(name='Item A')
        testmodels.SomeItem.objects.create(name='Item B')
        testmodels.SomeItem.objects.create(name='Item C')

        class MyObjectTableView(objecttable.ObjectTableView):
            model = testmodels.SomeItem
            columns = ['name']

            def get_queryset_for_role(self, role):
                return testmodels.SomeItem.objects.all()

        request = self.factory.get('/test', {
            'ordering': 'd0'
        })
        self._mock_request(request)
        response = MyObjectTableView.as_view()(request)
        response.render()
        selector = htmls.S(response.content)
        # selector.one('#django_cradmin_contentwrapper thead').prettyprint()

        self.assertEqual(selector.count('#objecttableview-table>tbody>tr'), 3)
        self.assertEquals(
            selector.one('#objecttableview-table>tbody>tr:first-child>td').alltext_normalized,
            'Item C')
        self.assertEquals(
            selector.one('#objecttableview-table>tbody>tr:last-child>td').alltext_normalized,
            'Item A')

        self.assertEquals(
            selector.one('#objecttableview-table>thead>tr>th').alltext_normalized,
            'The name - Ordered descending - Click to order ascending')

    def test_render_order_multicolumn(self):
        testmodels.SomeItem.objects.create(name='Item A', somenumber=1)
        testmodels.SomeItem.objects.create(name='Item B', somenumber=2)
        testmodels.SomeItem.objects.create(name='Item C', somenumber=2)

        class MyObjectTableView(objecttable.ObjectTableView):
            model = testmodels.SomeItem
            columns = ['name', 'somenumber']

            def get_queryset_for_role(self, role):
                return testmodels.SomeItem.objects.all()

        request = self.factory.get('/test', {
            'ordering': 'a1.d0'
        })
        self._mock_request(request)
        response = MyObjectTableView.as_view()(request)
        response.render()
        selector = htmls.S(response.content)
        # selector.one('#django_cradmin_contentwrapper thead').prettyprint()

        self.assertEquals(selector.count('#objecttableview-table>thead>tr>th'), 2),
        self.assertEquals(
            selector.one('#objecttableview-table>thead>tr>th:first-child').alltext_normalized,
            'The name - Ordered descending - Click to order ascending - Ordering priority 2')
        self.assertEquals(
            selector.one('#objecttableview-table>thead>tr>th:last-child').alltext_normalized,
            'Somenumber - Ordered ascending - Click to order descending - Ordering priority 1')

        self.assertEqual(selector.count('#objecttableview-table>tbody>tr'), 3)
        self.assertEquals(
            selector.one('#objecttableview-table>tbody>tr:first-child>td:first-child').alltext_normalized,
            'Item A')
        self.assertEquals(
            selector.one('#objecttableview-table>tbody>tr:last-child>td:first-child').alltext_normalized,
            'Item B')

    def test_render_search_nomatch(self):
        testmodels.SomeItem.objects.create(name='Item One')

        class MyObjectTableView(objecttable.ObjectTableView):
            model = testmodels.SomeItem
            columns = ['name']
            searchfields = ['name']

            def get_queryset_for_role(self, role):
                return testmodels.SomeItem.objects.all()

        request = self.factory.get('/test', {
            'search': 'Nothing matches this'
        })
        self._mock_request(request)
        response = MyObjectTableView.as_view()(request)
        response.render()
        selector = htmls.S(response.content)
        self.assertEqual(selector.count('#objecttableview-table>tbody>tr'), 0)

    def test_render_search_match(self):
        testmodels.SomeItem.objects.create(name='Item One')
        testmodels.SomeItem.objects.create(name='Item Two')
        testmodels.SomeItem.objects.create(name='Item Three')

        class MyObjectTableView(objecttable.ObjectTableView):
            model = testmodels.SomeItem
            columns = ['name']
            searchfields = ['name']

            def get_queryset_for_role(self, role):
                return testmodels.SomeItem.objects.all()

        request = self.factory.get('/test', {
            'search': 'Item Two'
        })
        self._mock_request(request)
        response = MyObjectTableView.as_view()(request)
        response.render()
        selector = htmls.S(response.content)

        self.assertEqual(selector.count('#objecttableview-table>tbody>tr'), 1)
        self.assertEquals(
            selector.one('#objecttableview-table>tbody>tr>td').alltext_normalized,
            'Item Two')
