import datetime

from django.core.urlresolvers import RegexURLResolver, RegexURLPattern
from django.conf import settings
from django.conf.urls import patterns, url, include
from django.contrib.auth.models import User
from django.contrib.admindocs.utils import trim_docstring
from django.test import TestCase
from django.test.utils import override_settings
from django.utils.importlib import import_module
from django.views.generic import View

from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from rest_framework import serializers
from rest_framework.routers import DefaultRouter
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view
import rest_framework

from .decorators import wrapper_to_func, func_to_wrapper
from .urlparser import UrlParser
from .docgenerator import DocumentationGenerator
from .introspectors import ViewSetIntrospector, APIViewIntrospector, \
    WrappedAPIViewMethodIntrospector, IntrospectorHelper, \
    APIViewMethodIntrospector


def no_markdown(func):
    def func_sans_markdown(*args, **kwargs):
        import rest_framework.compat
        apply_markdown = rest_framework.compat.apply_markdown
        try:
            rest_framework.compat.apply_markdown = None
            func(*args, **kwargs)
        finally:
            rest_framework.compat.apply_markdown = apply_markdown
    return func_sans_markdown


class MockApiView(APIView):
    """
    A Test View

    This is more commenting
    """
    def get(self, request):
        """
        Get method specific comments
        """
        pass
    pass


class NonApiView(View):
    pass


class CommentSerializer(serializers.Serializer):
    email = serializers.EmailField()
    content = serializers.CharField(max_length=200)
    created = serializers.DateTimeField(default=datetime.datetime.now)


class QuerySerializer(serializers.Serializer):
    query = serializers.CharField(max_length=100)


class UrlParserTest(TestCase):
    def setUp(self):
        self.url_patterns = patterns(
            '',
            url(r'a-view/?$', MockApiView.as_view(), name='a test view'),
            url(r'a-view/child/?$', MockApiView.as_view()),
            url(r'a-view/child2/?$', MockApiView.as_view()),
            url(r'another-view/?$', MockApiView.as_view(), name='another test view'),
        )

    def test_get_apis(self):
        urlparser = UrlParser()
        urls = import_module(settings.ROOT_URLCONF)
        # Overwrite settings with test patterns
        urls.urlpatterns = self.url_patterns
        apis = urlparser.get_apis()

        for api in apis:
            self.assertIn(api['pattern'], self.url_patterns)

    def test_flatten_url_tree(self):
        urlparser = UrlParser()
        apis = urlparser.get_apis(self.url_patterns)

        self.assertEqual(len(self.url_patterns), len(apis))

    def test_flatten_url_tree_url_import(self):
        urls = patterns('', url(r'api/base/path/', include(self.url_patterns)))
        urlparser = UrlParser()
        apis = urlparser.get_apis(urls)

        self.assertEqual(len(self.url_patterns), len(apis))

    def test_resources_starting_with_letters_from_base_path(self):
        base_path = r'api/'
        url_patterns = patterns('',
                                url(r'test', MockApiView.as_view(), name='a test view'),
                                url(r'pai_test', MockApiView.as_view(), name='start with letters a, p, i'),
                                )
        urls = patterns('', url(base_path, include(url_patterns)))
        urlparser = UrlParser()
        apis = urlparser.get_apis(urls)
        resources = urlparser.get_top_level_apis(apis)
        self.assertEqual(set(resources), set([base_path + url_pattern.regex.pattern for url_pattern in url_patterns]))

    def test_flatten_url_tree_with_filter(self):
        urlparser = UrlParser()
        apis = urlparser.get_apis(self.url_patterns, filter_path="a-view")

        self.assertEqual(3, len(apis))

    def test_filter_custom(self):
        urlparser = UrlParser()
        apis = [{'path': '/api/custom'}]
        apis2 = urlparser.get_filtered_apis(apis, 'api/custom')
        self.assertEqual(apis, apis2)

    def test_flatten_url_tree_excluded_namesapce(self):
        urls = patterns(
            '',
            url(r'api/base/path/', include(self.url_patterns, namespace='exclude'))
        )
        urlparser = UrlParser()
        apis = urlparser.__flatten_patterns_tree__(patterns=urls, exclude_namespaces='exclude')

        self.assertEqual([], apis)

    def test_flatten_url_tree_url_import_with_routers(self):

        class MockApiViewSet(ModelViewSet):
            serializer_class = CommentSerializer
            model = User

        class AnotherMockApiViewSet(ModelViewSet):
            serializer_class = CommentSerializer
            model = User

        router = DefaultRouter()
        router.register(r'other_views', MockApiViewSet)
        router.register(r'more_views', MockApiViewSet)

        urls_app = patterns('', url(r'^', include(router.urls)))
        urls = patterns(
            '',
            url(r'api/', include(urls_app)),
            url(r'test/', include(urls_app))
        )
        urlparser = UrlParser()
        apis = urlparser.get_apis(urls)

        self.assertEqual(sum(api['path'].find('api') != -1 for api in apis), 4)
        self.assertEqual(sum(api['path'].find('test') != -1 for api in apis), 4)

    def test_get_api_callback(self):
        urlparser = UrlParser()
        callback = urlparser.__get_pattern_api_callback__(self.url_patterns[0])

        self.assertTrue(issubclass(callback, MockApiView))

    def test_get_api_callback_not_rest_view(self):
        urlparser = UrlParser()
        non_api = patterns(
            '',
            url(r'something', NonApiView.as_view())
        )
        callback = urlparser.__get_pattern_api_callback__(non_api)

        self.assertIsNone(callback)

    def test_get_top_level_api(self):
        urlparser = UrlParser()
        apis = urlparser.get_top_level_apis(urlparser.get_apis(self.url_patterns))

        self.assertEqual(2, len(apis))

    def test_assemble_endpoint_data(self):
        """
        Tests that the endpoint data is correctly packaged
        """
        urlparser = UrlParser()
        pattern = self.url_patterns[0]

        data = urlparser.__assemble_endpoint_data__(pattern)

        self.assertEqual(data['path'], '/a-view/')
        self.assertEqual(data['callback'], MockApiView)
        self.assertEqual(data['pattern'], pattern)

    def test_assemble_data_with_non_api_callback(self):
        bad_pattern = patterns('', url(r'^some_view/', NonApiView.as_view()))

        urlparser = UrlParser()
        data = urlparser.__assemble_endpoint_data__(bad_pattern)

        self.assertIsNone(data)

    def test_exclude_router_api_root(self):
        class MyViewSet(ModelViewSet):
            serializer_class = CommentSerializer
            model = User

        router = DefaultRouter()
        router.register('test', MyViewSet)

        urls_created = len(router.urls)

        parser = UrlParser()
        apis = parser.get_apis(router.urls)

        self.assertEqual(4, urls_created - len(apis))

    def test_get_base_path_for_common_endpoints(self):
        parser = UrlParser()
        paths = ['api/endpoint1', 'api/endpoint2']
        base_path = parser.__get_base_path__(paths)

        self.assertEqual('api/', base_path)

    def test_get_base_path_for_root_level_endpoints(self):
        parser = UrlParser()
        paths = ['endpoint1', 'endpoint2', 'endpoint3']
        base_path = parser.__get_base_path__(paths)

        self.assertEqual('', base_path)


class NestedUrlParserTest(TestCase):
    def setUp(self):
        class FuzzyApiView(APIView):
            def get(self, request):
                pass

        class ShinyApiView(APIView):
            def get(self, request):
                pass

        api_fuzzy_url_patterns = patterns(
            '', url(r'^item/$', FuzzyApiView.as_view(), name='find_me'))
        api_shiny_url_patterns = patterns(
            '', url(r'^item/$', ShinyApiView.as_view(), name='hide_me'))

        fuzzy_app_urls = patterns(
            '', url(r'^api/', include(api_fuzzy_url_patterns,
                                      namespace='api_fuzzy_app')))
        shiny_app_urls = patterns(
            '', url(r'^api/', include(api_shiny_url_patterns,
                                      namespace='api_shiny_app')))

        self.project_urls = patterns(
            '',
            url('my_fuzzy_app/', include(fuzzy_app_urls)),
            url('my_shiny_app/', include(shiny_app_urls)),
        )

    def test_exclude_nested_urls(self):

        url_parser = UrlParser()
        # Overwrite settings with test patterns
        urlpatterns = self.project_urls
        apis = url_parser.get_apis(urlpatterns,
                                   exclude_namespaces=['api_shiny_app'])
        self.assertEqual(len(apis), 1)
        self.assertEqual(apis[0]['pattern'].name, 'find_me')


class DocumentationGeneratorTest(TestCase):
    def setUp(self):
        self.url_patterns = patterns(
            '',
            url(r'a-view/?$', MockApiView.as_view(), name='a test view'),
            url(r'a-view/child/?$', MockApiView.as_view()),
            url(r'a-view/<pk>/?$', MockApiView.as_view(), name="detailed view for mock"),
            url(r'another-view/?$', MockApiView.as_view(), name='another test view'),
        )

    def test_get_operations(self):

        class AnAPIView(APIView):
            def post(self, *args, **kwargs):
                pass

        api = {
            'path': 'a-path/',
            'callback': AnAPIView,
            'pattern': patterns('')
        }
        docgen = DocumentationGenerator()
        operations = docgen.get_operations(api)

        self.assertEqual('POST', operations[0]['method'])

    def test_get_operations_with_no_methods(self):

        class AnAPIView(APIView):
            pass

        api = {
            'path': 'a-path/',
            'callback': AnAPIView,
            'pattern': patterns('')
        }
        docgen = DocumentationGenerator()
        operations = docgen.get_operations(api)

        self.assertEqual([], operations)

    def test_get_models(self):
        class SerializedAPI(ListCreateAPIView):
            serializer_class = CommentSerializer

        urlparser = UrlParser()
        url_patterns = patterns('', url(r'my-api/', SerializedAPI.as_view()))
        apis = urlparser.get_apis(url_patterns)

        docgen = DocumentationGenerator()
        models = docgen.get_models(apis)

        self.assertIn('CommentSerializer', models)

    def test_get_models_resolves_callable_values(self):
        class SerializedAPI(ListCreateAPIView):
            serializer_class = CommentSerializer

        urlparser = UrlParser()
        url_patterns = patterns('', url(r'my-api/', SerializedAPI.as_view()))
        apis = urlparser.get_apis(url_patterns)

        docgen = DocumentationGenerator()
        models = docgen.get_models(apis)

        created_prop = models['CommentSerializer']['properties']['created']
        value = created_prop['defaultValue']
        delta = datetime.timedelta(seconds=1)
        self.assertAlmostEqual(value, datetime.datetime.now(), delta=delta)

    def test_get_models_ordering(self):
        class SerializedAPI(ListCreateAPIView):
            serializer_class = CommentSerializer

        urlparser = UrlParser()
        url_patterns = patterns('', url(r'my-api/', SerializedAPI.as_view()))
        apis = urlparser.get_apis(url_patterns)

        docgen = DocumentationGenerator()
        models = docgen.get_models(apis)

        self.assertIn('CommentSerializer', models)
        self.assertEqual(list(models['CommentSerializer']['properties'].keys()), ["email", "content", "created"])

    def test_get_serializer_set(self):
        class SerializedAPI(ListCreateAPIView):
            serializer_class = CommentSerializer

        urlparser = UrlParser()
        url_patterns = patterns('', url(r'my-api/', SerializedAPI.as_view()))
        apis = urlparser.get_apis(url_patterns)

        docgen = DocumentationGenerator()
        serializers = docgen._get_serializer_set(apis)

        self.assertIn(CommentSerializer, serializers)

    def test_get_serializer_fields(self):
        docgen = DocumentationGenerator()
        fields = docgen._get_serializer_fields(CommentSerializer)

        self.assertEqual(3, len(fields['fields']))
        self.assertEqual(fields['fields']['email']['defaultValue'], None)

    def test_get_serializer_fields_api_with_no_serializer(self):
        docgen = DocumentationGenerator()
        fields = docgen._get_serializer_fields(None)

        self.assertIsNone(fields)

    def test_get_serializer_fields_with_field(self):
        class SomeSerializer(serializers.Serializer):
            thing1 = serializers.Field()

        docgen = DocumentationGenerator()
        fields = docgen._get_serializer_fields(SomeSerializer)

        self.assertEqual(1, len(fields['fields']))

    def test_get_serializer_fields_api_with_nested(self):
        class SomeSerializer(serializers.Serializer):
            thing1 = serializers.CharField()

        class OtherSerializer(serializers.Serializer):
            thing2 = SomeSerializer()
        docgen = DocumentationGenerator()
        fields = docgen._get_serializer_fields(OtherSerializer)

        self.assertEqual(1, len(fields['fields']))
        self.assertEqual("SomeSerializer", fields['fields']['thing2']['type'])

    def test_get_serializer_fields_api_with_nested_many(self):
        class SomeSerializer(serializers.Serializer):
            thing1 = serializers.CharField()

        class OtherSerializer(serializers.Serializer):
            thing2 = SomeSerializer(many=True)
        docgen = DocumentationGenerator()
        fields = docgen._get_serializer_fields(OtherSerializer)

        self.assertEqual(1, len(fields['fields']))
        self.assertEqual("array", fields['fields']['thing2']['type'])

    def test_nested_serializer(self):
        class ASerializer(serializers.Serializer):
            point = CommentSerializer()
            query = QuerySerializer()

        docgen = DocumentationGenerator()
        serializerses = docgen._find_field_serializers([ASerializer])
        self.assertTrue([s for s in serializerses
                         if isinstance(s, CommentSerializer)])
        self.assertTrue([s for s in serializerses
                         if isinstance(s, QuerySerializer)])
        self.assertFalse([s for s in serializerses
                         if isinstance(s, ASerializer)])

    def test_nested_many_serializer(self):
        class ASerializer(serializers.Serializer):
            point = CommentSerializer()
            query = QuerySerializer(many=True)

        docgen = DocumentationGenerator()
        serializerses = docgen._find_field_serializers([ASerializer])
        self.assertTrue([s for s in serializerses
                         if isinstance(s, CommentSerializer)])
        self.assertTrue([s for s in serializerses
                         if isinstance(s, QuerySerializer)])
        self.assertFalse([s for s in serializerses
                         if isinstance(s, ASerializer)])

    def test_get_serializer_class_url_kwargs(self):
        class SerializerFoo(serializers.Serializer):
            pass

        class SerializerBar(serializers.Serializer):
            pass

        class TestView(APIView):
            serializer_class = SerializerFoo

            def get_serializer_class(self):
                if 'b' in self.kwargs:
                    return SerializerFoo
                return SerializerBar
        urlparser = UrlParser()
        url_patterns = patterns(
            '',
            url(r'^a/$', TestView.as_view()),
        )
        apis = urlparser.get_apis(url_patterns)

        docgen = DocumentationGenerator()
        serializer_set = docgen._get_serializer_set(apis)
        self.assertEqual(1, len(serializer_set))
        self.assertEqual(SerializerBar, list(serializer_set)[0])

        urlparser = UrlParser()
        url_patterns = patterns(
            '',
            url(r'^a/b$', TestView.as_view(), {'b': True}),
        )
        apis = urlparser.get_apis(url_patterns)

        docgen = DocumentationGenerator()
        serializer_set = docgen._get_serializer_set(apis)
        self.assertEqual(1, len(serializer_set))
        self.assertEqual(SerializerFoo, list(serializer_set)[0])


class IntrospectorHelperTest(TestCase):
    def test_strip_yaml_from_docstring(self):
        class AnAPIView(APIView):
            """
            My comments are here
            ---
            # This is YAML
            param: my param
            """
            pass

        docstring = IntrospectorHelper.strip_yaml_from_docstring(trim_docstring(AnAPIView.__doc__))

        self.assertEqual("My comments are here", docstring)

    def test_strip_params_from_docstring_multiline(self):
        class TestView(APIView):
            """
            Creates a new user.
            Returns: token - auth token
            ---
            # This is YAML
            param: my param
            foo: 123
            """
            pass

        docstring = IntrospectorHelper.strip_yaml_from_docstring(TestView.__doc__)
        expected = 'Creates a new user.\nReturns: token - auth token'

        self.assertEqual(expected, docstring)

    def test_get_serializer_name1(self):
        self.assertEqual(
            "CommentSerializer",
            IntrospectorHelper.get_serializer_name(CommentSerializer))
        self.assertEqual(
            "CommentSerializer",
            IntrospectorHelper.get_serializer_name(CommentSerializer()))

    def test_get_serializer_name2(self):
        class DaSerializer(serializers.Serializer):
            comments = CommentSerializer(many=True)

        serializer = DaSerializer()
        comments = serializer.get_fields()["comments"]
        self.assertEqual(
            "DaSerializer",
            IntrospectorHelper.get_serializer_name(serializer))
        self.assertEqual(
            "CommentSerializer",
            IntrospectorHelper.get_serializer_name(comments))


class ViewSetTestIntrospectorTest(TestCase):
    def test_get_allowed_methods_list(self):
        class MyViewSet(ModelViewSet):
            serializer_class = CommentSerializer
            model = User

        # Test a list endpoint
        introspector = ViewSetIntrospector(
            MyViewSet,
            '/api/endpoint',
            url(r'^/api/endpoint$', MyViewSet.as_view({
                'get': 'list',
                'post': 'create'
            }))
        )
        allowed_methods = list(introspector)
        self.assertEqual(2, len(allowed_methods))
        allowed_methods = [method.get_http_method() for method in allowed_methods]
        self.assertIn('POST', allowed_methods)
        self.assertIn('GET', allowed_methods)

    def test_get_allowed_methods_object(self):
        class MyViewSet(ModelViewSet):
            serializer_class = CommentSerializer
            model = User

        # Test an object endpoint
        introspector = ViewSetIntrospector(
            MyViewSet,
            '/api/endpoint/{pk}',
            url(
                r'^/api/endpoint/(?P<{pk}>[^/]+)$',
                MyViewSet.as_view({
                    'get': 'retrieve',
                    'put': 'update',
                    'patch': 'partial_update',
                    'delete': 'destroy'
                })
            )
        )
        allowed_methods = list(introspector)
        self.assertEqual(4, len(allowed_methods))
        allowed_methods = [method.get_http_method() for method in allowed_methods]
        self.assertIn('PUT', allowed_methods)
        self.assertIn('PATCH', allowed_methods)
        self.assertIn('DELETE', allowed_methods)
        self.assertIn('GET', allowed_methods)


def get_introspectors(introspector):
    return dict((x.method, x) for x in iter(introspector))


def make_viewset_introspector(view_class):
    return ViewSetIntrospector(
        view_class,
        '/api/endpoint/{pk}',
        url(
            r'^/api/endpoint/(?P<{pk}>[^/]+)$',
            view_class.as_view({
                'get': 'list',
                'post': 'create',
                'put': 'update',
                'patch': 'partial_update',
                'delete': 'destroy'
            })
        )
    )


class ViewSetMethodIntrospectorTests(TestCase):
    def make_view_introspector(self, view_class):
        return make_viewset_introspector(view_class)

    def test_get_serializer_class_access_action(self):
        class MyViewSet(ModelViewSet):
            model = User

            def get_serializer_class(self):
                if self.action == 'create':
                    return CommentSerializer
                else:
                    return QuerySerializer

        introspector = self.make_view_introspector(MyViewSet)
        method_introspectors = get_introspectors(introspector)
        serializer_class = method_introspectors['create'] \
            .get_serializer_class()
        self.assertIs(serializer_class, CommentSerializer)
        serializer_class = method_introspectors['update'] \
            .get_serializer_class()
        self.assertIs(serializer_class, QuerySerializer)

    def test_get_serializer_class_access_method(self):
        class MyViewSet(ModelViewSet):
            model = User

            def get_serializer_class(self):
                if self.request.method == "GET":
                    return CommentSerializer
                return QuerySerializer
        class_introspector = self.make_view_introspector(MyViewSet)
        introspector = get_introspectors(class_introspector)['list']
        self.assertEqual(
            CommentSerializer,
            introspector.get_serializer_class())
        introspector = get_introspectors(class_introspector)['create']
        self.assertEqual(
            QuerySerializer,
            introspector.get_serializer_class())

    def test_builds_pagination_parameters_list(self):
        class MyViewSet(ModelViewSet):
            model = User
            serializer_class = CommentSerializer
            paginate_by = 20
            paginate_by_param = 'page_this_by'

        class_introspector = self.make_view_introspector(MyViewSet)
        introspector = get_introspectors(class_introspector)['list']
        params = introspector.build_query_parameters()
        page = [p for p in params if p['name'] == 'page']
        self.assertEqual(1, len(page))
        page_by = [p for p in params if p['name'] == 'page_this_by']
        self.assertEqual(1, len(page_by))

    def test_no_builds_pagination_parameters_for_create(self):
        class MyViewSet(ModelViewSet):
            model = User
            serializer_class = CommentSerializer
            paginate_by = 20
            paginate_by_param = 'page_this_by'

        class_introspector = self.make_view_introspector(MyViewSet)
        introspector = get_introspectors(class_introspector)['create']
        params = introspector.build_query_parameters()
        page = [p for p in params if p['name'] == 'page']
        self.assertEqual(0, len(page))
        page_by = [p for p in params if p['name'] == 'page_this_by']
        self.assertEqual(0, len(page_by))

    def test_get_summary_empty(self):
        class MyViewSet(ModelViewSet):
            model = User
            serializer_class = CommentSerializer
            paginate_by = 20
            paginate_by_param = 'page_this_by'

        class_introspector = self.make_view_introspector(MyViewSet)
        introspector = get_introspectors(class_introspector)['create']
        summary = introspector.get_summary()
        self.assertEqual("", summary)

    def test_get_summary_view(self):
        class MyViewSet(ModelViewSet):
            """
            *Slimy angels*
            """
            model = User
            serializer_class = CommentSerializer
            paginate_by = 20
            paginate_by_param = 'page_this_by'

        class_introspector = self.make_view_introspector(MyViewSet)
        introspector = get_introspectors(class_introspector)['create']
        summary = introspector.get_summary()
        self.assertEqual("Slimy angels", summary)

    @no_markdown
    def test_get_summary_view_nomarkdown(self):
        class MyViewSet(ModelViewSet):
            """
            *Slimy angels*
            """
            model = User
            serializer_class = CommentSerializer
            paginate_by = 20
            paginate_by_param = 'page_this_by'

        class_introspector = self.make_view_introspector(MyViewSet)
        introspector = get_introspectors(class_introspector)['create']
        summary = introspector.get_summary()
        self.assertEqual("*Slimy angels*", summary)

    def test_get_summary_method(self):
        class MyViewSet(ModelViewSet):
            model = User
            serializer_class = CommentSerializer
            paginate_by = 20
            paginate_by_param = 'page_this_by'

            def create(self, request):
                """
                *Slimy angels*
                """
                pass

        class_introspector = self.make_view_introspector(MyViewSet)
        introspector = get_introspectors(class_introspector)['create']
        summary = introspector.get_summary()
        self.assertEqual("Slimy angels", summary)

    @no_markdown
    def test_get_summary_method_nomarkdown(self):
        class MyViewSet(ModelViewSet):
            model = User
            serializer_class = CommentSerializer
            paginate_by = 20
            paginate_by_param = 'page_this_by'

            def create(self, request):
                """
                *Slimy angels*
                """
                pass

        class_introspector = self.make_view_introspector(MyViewSet)
        introspector = get_introspectors(class_introspector)['create']
        summary = introspector.get_summary()
        self.assertEqual("*Slimy angels*", summary)


class BaseViewIntrospectorTest(TestCase):
    def test_get_description(self):
        introspector = APIViewIntrospector(MockApiView, '/', RegexURLResolver(r'^/', ''))
        self.assertEqual('A Test View', introspector.get_description())


class BaseMethodIntrospectorTest(TestCase):
    def make_introspector(self, view_class):
        return APIViewIntrospector(
            view_class, '/{pk}',
            RegexURLResolver(r'^/(?P<{pk}>[^/]+)$', ''))

    def make_introspector2(self, view_class):
        return APIViewIntrospector(
            view_class, '/', RegexURLResolver(r'^/$', ''))

    def test_get_method_docs(self):

        class TestApiView(APIView):
            def get(self, *args):
                """
                Here are my comments
                """
            pass

        class_introspector = self.make_introspector(TestApiView)
        introspector = APIViewMethodIntrospector(class_introspector, 'GET')
        docs_get = introspector.get_docs()

        self.assertEqual("Here are my comments", docs_get.strip())

    def test_get_serializer_class(self):
        class_introspector = self.make_introspector2(MockApiView)
        introspector = get_introspectors(class_introspector)["GET"]
        self.assertEqual(None, introspector.get_serializer_class())

    def test_get_serializer_class_url_kwargs(self):
        class SerializerFoo(serializers.Serializer):
            pass

        class SerializerBar(serializers.Serializer):
            pass

        class TestView(APIView):
            serializer_class = SerializerFoo

            def get_serializer_class(self):
                if 'b' in self.kwargs:
                    return SerializerFoo
                return SerializerBar
        class_introspector = APIViewIntrospector(
            TestView, '/a', RegexURLPattern(r'^a/$', '', {'b': True}))
        introspector = get_introspectors(class_introspector)['OPTIONS']
        self.assertEqual(SerializerFoo, introspector.get_serializer_class())
        class_introspector = APIViewIntrospector(
            TestView, '/a', RegexURLPattern(r'^a/$', ''))
        introspector = get_introspectors(class_introspector)['OPTIONS']
        self.assertEqual(SerializerBar, introspector.get_serializer_class())

    def test_get_serializer_class_access_user(self):
        class SerializerFoo(serializers.Serializer):
            pass

        class SerializerBar(serializers.Serializer):
            pass

        class TestView(APIView):
            serializer_class = SerializerFoo

            def get_serializer_class(self):
                if self.request.user.id == 1:
                    return SerializerFoo
                return SerializerBar
        class_introspector = self.make_introspector2(TestView)
        introspector = get_introspectors(class_introspector)['OPTIONS']
        self.assertEqual(SerializerBar, introspector.get_serializer_class())

    def test_get_serializer_class_access_method(self):
        class SerializerFoo(serializers.Serializer):
            pass

        class SerializerBar(serializers.Serializer):
            pass

        class TestView(APIView):
            serializer_class = SerializerFoo

            def get(self):
                pass

            def get_serializer_class(self):
                if self.request.method == "GET":
                    return SerializerFoo
                return SerializerBar
        class_introspector = self.make_introspector2(TestView)
        introspector = get_introspectors(class_introspector)['GET']
        self.assertEqual(SerializerFoo, introspector.get_serializer_class())
        introspector = get_introspectors(class_introspector)['OPTIONS']
        self.assertEqual(SerializerBar, introspector.get_serializer_class())

    def test_get_method_summary_without_docstring(self):

        class MyListView(ListCreateAPIView):
            """
            My comment
            """
            pass

        class_introspector = self.make_introspector(MyListView)
        introspector = APIViewMethodIntrospector(class_introspector, 'POST')
        method_docs = introspector.get_summary()

        self.assertEqual("My comment", method_docs)

    def test_build_body_parameters(self):
        class SerializedAPI(ListCreateAPIView):
            serializer_class = CommentSerializer

        class_introspector = self.make_introspector2(SerializedAPI)
        introspector = APIViewMethodIntrospector(class_introspector, 'POST')
        params = introspector.build_body_parameters()

        self.assertEqual('CommentSerializer', params['name'])

    def test_build_form_parameters(self):
        MY_CHOICES = (
            ('val1', "Value1"),
            ('val2', "Value2"),
            ('val3', "Value3"),
            ('val4', "Value4")
        )

        class SomeSerializer(serializers.Serializer):
            email = serializers.EmailField()
            content = serializers.CharField(max_length=200)
            created = serializers.DateTimeField(default=datetime.datetime.now)
            expires = serializers.DateField()
            expires_by = serializers.TimeField()
            age = serializers.IntegerField()
            flagged = serializers.BooleanField()
            url = serializers.URLField()
            slug = serializers.SlugField()
            choice = serializers.ChoiceField(
                choices=MY_CHOICES, default=MY_CHOICES[0][0])
            regex = serializers.RegexField("[a-f]+")
            float = serializers.FloatField()
            decimal = serializers.DecimalField(max_digits=5, decimal_places=1)
            file = serializers.FileField()
            image = serializers.ImageField()
            joop = serializers.PrimaryKeyRelatedField(queryset=1)

        class SerializedAPI(ListCreateAPIView):
            serializer_class = SomeSerializer

        class_introspector = self.make_introspector2(SerializedAPI)
        introspector = APIViewMethodIntrospector(class_introspector, 'POST')
        params = introspector.build_form_parameters()

        self.assertEqual(len(SomeSerializer().get_fields()), len(params))
        self.assertEqual(params[0]['name'], 'email')
        self.assertIsNone(params[0]['defaultValue'])

        url_patterns = patterns('', url(r'my-api/', SerializedAPI.as_view()))
        urlparser = UrlParser()
        generator = DocumentationGenerator()
        apis = urlparser.get_apis(url_patterns)
        models = generator.get_models(apis)
        self.assertIn("SomeSerializer", models)
        properties = models["SomeSerializer"]['properties']
        self.assertEqual("email", properties["email"]["type"])
        self.assertEqual("string", properties["content"]["type"])
        self.assertEqual("datetime", properties["created"]["type"])
        self.assertEqual("date", properties["expires"]["type"])
        self.assertEqual("time", properties["expires_by"]["type"])
        self.assertEqual("integer", properties["age"]["type"])
        self.assertEqual("boolean", properties["flagged"]["type"])
        self.assertEqual("url", properties["url"]["type"])
        self.assertEqual("slug", properties["slug"]["type"])
        self.assertIn(
            properties["choice"]["type"],
            ["choice", "multiple choice"])
        self.assertEqual("regex", properties["regex"]["type"])
        self.assertEqual("float", properties["float"]["type"])
        self.assertEqual("decimal", properties["decimal"]["type"])
        self.assertEqual("file upload", properties["file"]["type"])
        self.assertEqual("image upload", properties["image"]["type"])
        self.assertEqual("field", properties["joop"]["type"])

    def test_build_form_parameters_allowable_values(self):

        class MySerializer(serializers.Serializer):
            content = serializers.CharField(max_length=200, min_length=10, default="Vandalay Industries")
            a_read_only_field = serializers.BooleanField(read_only=True)

        class MyAPIView(ListCreateAPIView):
            serializer_class = MySerializer

        class_introspector = self.make_introspector2(MyAPIView)
        introspector = APIViewMethodIntrospector(class_introspector, 'POST')
        params = introspector.build_form_parameters()

        self.assertEqual(1, len(params))  # Read only field is ignored
        param = params[0]

        self.assertEqual('content', param['name'])
        self.assertEqual('form', param['paramType'])
        if rest_framework.VERSION < '3.0.0':
            self.assertEqual(True, param['required'])
        else:
            self.assertEqual(False, param['required'])
        self.assertEqual('Vandalay Industries', param['defaultValue'])

    def test_build_form_parameters_callable_default_value_is_resolved(self):

        class MySerializer(serializers.Serializer):
            content = serializers.IntegerField(default=lambda: 203)

        class MyAPIView(ListCreateAPIView):
            serializer_class = MySerializer

        class_introspector = self.make_introspector2(MyAPIView)
        introspector = APIViewMethodIntrospector(class_introspector, 'POST')
        params = introspector.build_form_parameters()

        self.assertEqual(1, len(params))
        param = params[0]

        self.assertEqual('content', param['name'])
        self.assertEqual('form', param['paramType'])
        if rest_framework.VERSION < '3.0.0':
            self.assertEqual(True, param['required'])
        else:
            self.assertEqual(False, param['required'])
        self.assertEqual(203, param['defaultValue'])

    def test_build_form_parameters_enum_values(self):
        MY_CHOICES = (
            ('val1', "Value1"),
            ('val2', "Value2"),
            ('val3', "Value3"),
            ('val4', "Value4")
        )

        default_value = MY_CHOICES[0][0]

        class MySerializer(serializers.Serializer):
            choice_default = serializers.ChoiceField(choices=MY_CHOICES, default=default_value)
            char_field = serializers.CharField()

        class MyAPIView(ListCreateAPIView):
            serializer_class = MySerializer
        class_introspector = self.make_introspector2(MyAPIView)
        introspector = APIViewMethodIntrospector(class_introspector, 'POST')
        params = introspector.build_form_parameters()
        self.assertEqual(2, len(params))
        param = params[0]
        self.assertEqual(default_value, param['defaultValue'])
        self.assertEqual(4, len(param['enum']))
        self.assertEqual([item for item, _ in MY_CHOICES], param['enum'])
        param = params[1]
        self.assertFalse(hasattr(param, 'enum'))


class YAMLDocstringParserTests(TestCase):
    def make_introspector(self, view_class):
        return APIViewIntrospector(
            view_class, '/', RegexURLResolver(r'^/$', ''))

    def make_fbv_introspector(self, view):
        from .introspectors import WrappedAPIViewIntrospector
        return WrappedAPIViewIntrospector(
            func_to_wrapper(view), '/', RegexURLResolver(r'^/$', '')
        )

    def test_yaml_loader(self):
        class AnAPIView(APIView):
            def get(self):
                """
                My comments are here
                ---
                # This is YAML
                param: my param
                """
                pass

        class_introspector = self.make_introspector(AnAPIView)
        introspector = APIViewMethodIntrospector(class_introspector, 'GET')
        doc_parser = introspector.get_yaml_parser()
        self.assertEqual(doc_parser.object['param'], 'my param')

    def test_yaml_loader_class_yaml(self):
        class AnAPIView(APIView):
            """
            ---
            GET:
                param: my param
            """
            def get(self):
                """
                My comments are here
                ---
                # This is YAML
                param: your param
                """
                pass

        class_introspector = self.make_introspector(AnAPIView)
        class_introspector.methods = lambda: ['GET']
        introspector = APIViewMethodIntrospector(class_introspector, 'GET')
        doc_parser = introspector.get_yaml_parser()
        self.assertEqual(doc_parser.object['param'], 'your param')

    def test_yaml_loader_class_yaml2(self):
        class AnAPIView(APIView):
            """
            ---
            GET:
                param: my param
            """
            def get(self):
                """
                My comments are here
                ---
                # This is YAML
                """
                pass

        class_introspector = self.make_introspector(AnAPIView)
        class_introspector.methods = lambda: ['GET']
        introspector = APIViewMethodIntrospector(class_introspector, 'GET')
        doc_parser = introspector.get_yaml_parser()
        self.assertEqual(doc_parser.object['param'], 'my param')

    def test_yaml_loader_class_yaml3(self):
        class MyViewSet(ModelViewSet):
            """
            ---
            GET:
                param: my param
            """
            serializer_class = CommentSerializer
            model = User

        # Test a list endpoint
        introspector = ViewSetIntrospector(
            MyViewSet,
            '/api/endpoint',
            url(r'^/api/endpoint$', MyViewSet.as_view({
                'get': 'list',
                'post': 'create'
            }))
        )
        allowed_methods = list(introspector)
        self.assertEqual(2, len(allowed_methods))
        allowed_methods = [method.get_http_method() for method in allowed_methods]
        self.assertIn('POST', allowed_methods)
        self.assertIn('GET', allowed_methods)
        self.assertIn('list', introspector.methods())
        self.assertIn('create', introspector.methods())
        try:
            introspector = APIViewMethodIntrospector(introspector, 'get')
            introspector.get_yaml_parser()
        except Exception as e:
            self.assertIn('in class docstring are not in view methods', str(e))
        else:
            self.assertTrue(False)

    def test_yaml_loader_class_yaml4(self):
        class MyViewSet(ModelViewSet):
            """
            ---
            list:
                param: my param
            """
            serializer_class = CommentSerializer
            model = User

        # Test a list endpoint
        introspector = ViewSetIntrospector(
            MyViewSet,
            '/api/endpoint',
            url(r'^/api/endpoint$', MyViewSet.as_view({
                'get': 'list',
                'post': 'create'
            }))
        )
        allowed_methods = list(introspector)
        self.assertEqual(2, len(allowed_methods))
        allowed_methods = [method.get_http_method() for method in allowed_methods]
        self.assertIn('POST', allowed_methods)
        self.assertIn('GET', allowed_methods)
        self.assertIn('list', introspector.methods())
        self.assertIn('create', introspector.methods())
        introspector = APIViewMethodIntrospector(introspector, 'list')
        doc_parser = introspector.get_yaml_parser()
        self.assertEqual(doc_parser.object['param'], 'my param')

    def test_merge_parameters(self):
        class SerializedAPI(ListCreateAPIView):
            serializer_class = CommentSerializer

            def post(self, request, *args, **kwargs):
                """
                My post view with custom post parameters

                ---
                parameters:
                    - name: name
                      type: string
                      required: true
                """
                return super(SerializedAPI, self).post(request, *args, **kwargs)

        class_introspector = self.make_introspector(SerializedAPI)
        introspector = APIViewMethodIntrospector(class_introspector, 'POST')
        parser = introspector.get_yaml_parser()
        params = parser.discover_parameters(introspector)

        self.assertEqual(len(CommentSerializer().get_fields()) + 1, len(params))

    def test_replace_parameters(self):
        class SerializedAPI(ListCreateAPIView):
            serializer_class = CommentSerializer

            def post(self, request, *args, **kwargs):
                """
                My post view with custom post parameters

                ---
                parameters_strategy: replace
                parameters:
                    - name: name
                      type: string
                      required: true
                """
                return super(SerializedAPI, self).post(request, *args, **kwargs)

        class_introspector = self.make_introspector(SerializedAPI)
        introspector = APIViewMethodIntrospector(class_introspector, 'POST')
        parser = introspector.get_yaml_parser()
        params = parser.discover_parameters(introspector)

        self.assertEqual(1, len(params))

    def test_omit_parameters(self):
        class SerializedAPI(ListCreateAPIView):
            serializer_class = CommentSerializer

            def post(self, request, *args, **kwargs):
                """
                My post view with custom post parameters

                ---
                omit_parameters:
                    - form
                parameters:
                    - name: name
                      type: string
                      required: true
                """
                return super(SerializedAPI, self).post(request, *args, **kwargs)

        class_introspector = self.make_introspector(SerializedAPI)
        introspector = APIViewMethodIntrospector(class_introspector, 'POST')
        parser = introspector.get_yaml_parser()
        params = parser.discover_parameters(introspector)

        self.assertEqual(0, len(params))

    def test_complex_parameters_strategy(self):
        class SerializedAPI(ListCreateAPIView):
            serializer_class = CommentSerializer

            def get(self, request, *args, **kwargs):
                """
                My list view with custom query parameters

                ---
                parameters_strategy:
                    form: replace
                    query: merge
                parameters:
                    - name: search
                      type: string
                      required: true
                      paramType: query
                    - name: foo
                      paramType: form
                """
                return super(SerializedAPI, self).post(request, *args, **kwargs)

        class_introspector = self.make_introspector(SerializedAPI)
        introspector = APIViewMethodIntrospector(class_introspector, 'GET')
        parser = introspector.get_yaml_parser()
        params = introspector.build_form_parameters()
        self.assertEqual(len(CommentSerializer().get_fields()), len(params))

        params = parser.discover_parameters(introspector)
        self.assertEqual(2, len(params))
        query_params = parser._filter_params(params, 'paramType', 'query')
        form_params = parser._filter_params(params, 'paramType', 'form')
        self.assertEqual(1, len(list(query_params)))
        self.assertEqual(1, len(list(form_params)))

    def test_parameters_minimum_is_string(self):
        '''
        minimum and maximum of Parameter Object required by Swagger 1.2 spec to be string.
        '''
        class SerializedAPI(ListCreateAPIView):
            serializer_class = CommentSerializer

            def post(self, request, *args, **kwargs):
                """
                My post view with custom post parameters

                ---
                parameters_strategy:
                    form: replace
                    query: replace
                parameters:
                    - name: name
                      type: integer
                      required: true
                      minimum: 1
                      maximum: 100
                """
                return super(SerializedAPI, self).post(request, *args, **kwargs)

        class_introspector = self.make_introspector(SerializedAPI)
        introspector = APIViewMethodIntrospector(class_introspector, 'POST')
        parser = introspector.get_yaml_parser()
        params = parser.discover_parameters(introspector)
        self.assertEqual(len(params), 1)
        self.assertIn('minimum', params[0])
        self.assertEqual(params[0]['minimum'], '1')
        self.assertIn('maximum', params[0])
        self.assertEqual(params[0]['maximum'], '100')

    def test_response_messages(self):
        class SerializedAPI(ListCreateAPIView):
            serializer_class = CommentSerializer

            def post(self, request, *args, **kwargs):
                """
                ---
                responseMessages:
                    - code: 403
                      message: Not authorized.
                    - code: 404
                      message: Not found.
                """
                return super(SerializedAPI, self).post(request, *args, **kwargs)

        class_introspector = self.make_introspector(SerializedAPI)
        introspector = APIViewMethodIntrospector(class_introspector, 'POST')
        parser = introspector.get_yaml_parser()
        messages = parser.get_response_messages()

        self.assertEqual(2, len(messages))
        self.assertEqual(messages[0]['message'], 'Not authorized.')
        self.assertEqual(messages[1]['message'], 'Not found.')

    def test_custom_serializer(self):
        class SerializedAPI(ListCreateAPIView):
            serializer_class = CommentSerializer

            def post(self, request, *args, **kwargs):
                """
                ---
                serializer: serializers.Serializer
                """
                return super(SerializedAPI, self).post(request, *args, **kwargs)

        class_introspector = self.make_introspector(SerializedAPI)
        introspector = APIViewMethodIntrospector(class_introspector, 'POST')
        generator = DocumentationGenerator()
        serializer = generator._get_method_serializer(introspector)
        self.assertTrue(serializer, serializers.Serializer)

        DocumentationGenerator.explicit_serializers.clear()

    def test_fbv_custom_serializer_explicit(self):

        @api_view(['POST'])
        def SerializedAPI2(request):
            """
            ---
            serializer: rest_framework_swagger.tests.CommentSerializer
            """
            return "blarg"

        class_introspector = self.make_fbv_introspector(SerializedAPI2)
        introspector = WrappedAPIViewMethodIntrospector(class_introspector, 'POST')
        generator = DocumentationGenerator()
        serializer = generator._get_method_serializer(introspector)
        self.assertEqual(serializer, CommentSerializer)

    def test_fbv_custom_serializer_relative1(self):

        @api_view(['POST'])
        def SerializedAPI2(request):
            """
            ---
            serializer: ..tests.CommentSerializer
            """
            return "blarg"

        class_introspector = self.make_fbv_introspector(SerializedAPI2)
        wrapper_to_func(SerializedAPI2.cls)
        introspector = WrappedAPIViewMethodIntrospector(class_introspector, 'POST')
        generator = DocumentationGenerator()
        serializer = generator._get_method_serializer(introspector)
        self.assertEqual(serializer, CommentSerializer)

    def test_fbv_custom_serializer(self):

        @api_view(['POST'])
        def SerializedAPI2(request):
            """
            ---
            serializer: CommentSerializer
            """
            return "blarg"

        class_introspector = self.make_fbv_introspector(SerializedAPI2)
        wrapper_to_func(SerializedAPI2.cls)
        introspector = WrappedAPIViewMethodIntrospector(class_introspector, 'POST')
        generator = DocumentationGenerator()
        serializer = generator._get_method_serializer(introspector)
        self.assertEqual(serializer, CommentSerializer)

    def test_fbv_custom_serializer_noisy_fail(self):

        @api_view(['POST'])
        def SerializedAPI2(request):
            """
            ---
            serializer: HonkSerializer
            """
            return "blarg"

        class_introspector = self.make_fbv_introspector(SerializedAPI2)
        introspector = WrappedAPIViewMethodIntrospector(class_introspector, 'POST')
        generator = DocumentationGenerator()
        try:
            generator._get_method_serializer(introspector)
        except Exception as e:
            self.assertTrue("Could not find HonkSerializer" in str(e))
        else:
            self.assertTrue(False)

    def test_omit_serializer(self):
        class SerializedAPI(ListCreateAPIView):
            serializer_class = CommentSerializer

            def post(self, request, *args, **kwargs):
                """
                ---
                omit_serializer: true
                """
                return super(SerializedAPI, self).post(request, *args, **kwargs)

        class_introspector = self.make_introspector(SerializedAPI)
        introspector = APIViewMethodIntrospector(class_introspector, 'POST')
        generator = DocumentationGenerator()
        serializer = generator._get_method_serializer(introspector)
        self.assertEqual(serializer, None)

    def test_request_response_serializers1(self):
        class SerializedAPI(ListCreateAPIView):
            serializer_class = CommentSerializer

            def post(self, request, *args, **kwargs):
                """
                ---
                request_serializer: QuerySerializer
                response_serializer: CommentSerializer
                """
                return super(SerializedAPI, self).post(request, *args, **kwargs)

        class_introspector = self.make_introspector(SerializedAPI)
        introspector = APIViewMethodIntrospector(class_introspector, 'POST')
        generator = DocumentationGenerator()
        serializer = generator._get_method_serializer(introspector)
        url_patterns = patterns('', url(r'my-api/', SerializedAPI.as_view()))
        urlparser = UrlParser()
        apis = urlparser.get_apis(url_patterns)
        models = generator.get_models(apis)
        self.assertIn('SerializedAPIPostResponse', models)
        self.assertIn('WriteCommentSerializer', models)
        self.assertIn('CommentSerializer', models)
        self.assertNotIn('QuerySerializer', models)
        self.assertNotIn('WriteQuerySerializer', models)
        self.assertEqual(serializer, CommentSerializer)
        body_parameters = introspector.build_body_parameters()
        form_parameters = introspector.build_form_parameters()
        self.assertEqual(body_parameters['name'], "QuerySerializer")
        self.assertEqual(len(form_parameters), 1)
        self.assertEqual(form_parameters[0]['name'], "query")

    def test_request_response_serializers2(self):
        class SerializedAPI(ListCreateAPIView):
            serializer_class = CommentSerializer

            def post(self, request, *args, **kwargs):
                """
                ---
                serializer: QuerySerializer
                response_serializer: CommentSerializer
                """
                return super(SerializedAPI, self).post(request, *args, **kwargs)

        class_introspector = self.make_introspector(SerializedAPI)
        introspector = APIViewMethodIntrospector(class_introspector, 'POST')
        generator = DocumentationGenerator()
        serializer = generator._get_method_serializer(introspector)
        self.assertEqual(serializer, CommentSerializer)
        body_parameters = introspector.build_body_parameters()
        form_parameters = introspector.build_form_parameters()
        self.assertEqual(body_parameters['name'], "QuerySerializer")
        self.assertEqual(len(form_parameters), 1)
        self.assertEqual(form_parameters[0]['name'], "query")

    def test_request_response_serializers3(self):
        class SerializedAPI(ListCreateAPIView):
            serializer_class = CommentSerializer

            def post(self, request, *args, **kwargs):
                """
                ---
                request_serializer: QuerySerializer
                serializer: CommentSerializer
                """
                return super(SerializedAPI, self).post(request, *args, **kwargs)

        class_introspector = self.make_introspector(SerializedAPI)
        introspector = APIViewMethodIntrospector(class_introspector, 'POST')
        generator = DocumentationGenerator()
        serializer = generator._get_method_serializer(introspector)
        self.assertEqual(serializer, CommentSerializer)
        body_parameters = introspector.build_body_parameters()
        form_parameters = introspector.build_form_parameters()
        self.assertEqual(body_parameters['name'], "QuerySerializer")
        self.assertEqual(len(form_parameters), 1)
        self.assertEqual(form_parameters[0]['name'], "query")

    def test_request_response_serializers4(self):
        class SerializedAPI(ListCreateAPIView):
            serializer_class = CommentSerializer

            def post(self, request, *args, **kwargs):
                """
                ---
                request_serializer: QuerySerializer
                """
                return super(SerializedAPI, self).post(request, *args, **kwargs)

        class_introspector = self.make_introspector(SerializedAPI)
        introspector = APIViewMethodIntrospector(class_introspector, 'POST')
        generator = DocumentationGenerator()
        serializer = generator._get_method_serializer(introspector)
        self.assertEqual(serializer, CommentSerializer)
        body_parameters = introspector.build_body_parameters()
        form_parameters = introspector.build_form_parameters()
        self.assertEqual(body_parameters['name'], "QuerySerializer")
        self.assertEqual(len(form_parameters), 1)
        self.assertEqual(form_parameters[0]['name'], "query")

    def test_request_response_serializers5(self):
        class SerializedAPI(ListCreateAPIView):
            serializer_class = QuerySerializer

            def post(self, request, *args, **kwargs):
                """
                ---
                response_serializer: CommentSerializer
                """
                return super(SerializedAPI, self).post(request, *args, **kwargs)

        class_introspector = self.make_introspector(SerializedAPI)
        introspector = APIViewMethodIntrospector(class_introspector, 'POST')
        generator = DocumentationGenerator()
        serializer = generator._get_method_serializer(introspector)
        self.assertEqual(serializer, CommentSerializer)
        body_parameters = introspector.build_body_parameters()
        form_parameters = introspector.build_form_parameters()
        self.assertEqual(body_parameters['name'], "QuerySerializer")
        self.assertEqual(len(form_parameters), 1)
        self.assertEqual(form_parameters[0]['name'], "query")

    def test_request_response_serializers5_1(self):
        class SerializedAPI(ListCreateAPIView):
            """
                ---
                POST:
                    request_serializer: QuerySerializer
                    response_serializer: CommentSerializer
            """
            serializer_class = QuerySerializer

            def post(self, request, *args, **kwargs):
                return super(SerializedAPI, self).post(request, *args, **kwargs)
        class_introspector = self.make_introspector(SerializedAPI)
        introspector = APIViewMethodIntrospector(class_introspector, 'POST')
        generator = DocumentationGenerator()
        serializer = generator._get_method_serializer(introspector)
        self.assertEqual(serializer, CommentSerializer)
        body_parameters = introspector.build_body_parameters()
        form_parameters = introspector.build_form_parameters()
        self.assertEqual(body_parameters['name'], "QuerySerializer")
        self.assertEqual(len(form_parameters), 1)
        self.assertEqual(form_parameters[0]['name'], "query")

    def test_request_response_serializers6(self):
        class SerializedAPI(ListCreateAPIView):
            """
                ---
                POST:
                    serializer: QuerySerializer
                    response_serializer: CommentSerializer
            """
            serializer_class = QuerySerializer

            def post(self, request, *args, **kwargs):
                return super(SerializedAPI, self).post(request, *args, **kwargs)
        class_introspector = self.make_introspector(SerializedAPI)
        introspector = APIViewMethodIntrospector(class_introspector, 'POST')
        generator = DocumentationGenerator()
        serializer = generator._get_method_serializer(introspector)
        self.assertEqual(serializer, CommentSerializer)
        body_parameters = introspector.build_body_parameters()
        form_parameters = introspector.build_form_parameters()
        self.assertEqual(body_parameters['name'], "QuerySerializer")
        self.assertEqual(len(form_parameters), 1)
        self.assertEqual(form_parameters[0]['name'], "query")

    def test_request_response_serializers7(self):
        class SerializedAPI(ListCreateAPIView):
            """
                ---
                POST:
                    request_serializer: QuerySerializer
                    serializer: CommentSerializer
            """
            serializer_class = QuerySerializer

            def post(self, request, *args, **kwargs):
                return super(SerializedAPI, self).post(request, *args, **kwargs)
        class_introspector = self.make_introspector(SerializedAPI)
        introspector = APIViewMethodIntrospector(class_introspector, 'POST')
        generator = DocumentationGenerator()
        serializer = generator._get_method_serializer(introspector)
        self.assertEqual(serializer, CommentSerializer)
        body_parameters = introspector.build_body_parameters()
        form_parameters = introspector.build_form_parameters()
        self.assertEqual(body_parameters['name'], "QuerySerializer")
        self.assertEqual(len(form_parameters), 1)
        self.assertEqual(form_parameters[0]['name'], "query")

    def test_request_response_serializers8(self):
        class SerializedAPI(ListCreateAPIView):
            """
                ---
                POST:
                    request_serializer: QuerySerializer
            """
            serializer_class = CommentSerializer

            def post(self, request, *args, **kwargs):
                return super(SerializedAPI, self).post(request, *args, **kwargs)
        class_introspector = self.make_introspector(SerializedAPI)
        introspector = APIViewMethodIntrospector(class_introspector, 'POST')
        generator = DocumentationGenerator()
        serializer = generator._get_method_serializer(introspector)
        self.assertEqual(serializer, CommentSerializer)
        body_parameters = introspector.build_body_parameters()
        form_parameters = introspector.build_form_parameters()
        self.assertEqual(body_parameters['name'], "QuerySerializer")
        self.assertEqual(len(form_parameters), 1)
        self.assertEqual(form_parameters[0]['name'], "query")

    def test_request_response_serializers9(self):
        class SerializedAPI(ListCreateAPIView):
            """
                ---
                POST:
                    response_serializer: CommentSerializer
            """
            serializer_class = QuerySerializer

            def post(self, request, *args, **kwargs):
                return super(SerializedAPI, self).post(request, *args, **kwargs)
        class_introspector = self.make_introspector(SerializedAPI)
        introspector = APIViewMethodIntrospector(class_introspector, 'POST')
        generator = DocumentationGenerator()
        serializer = generator._get_method_serializer(introspector)
        self.assertEqual(serializer, CommentSerializer)
        body_parameters = introspector.build_body_parameters()
        form_parameters = introspector.build_form_parameters()
        self.assertEqual(body_parameters['name'], "QuerySerializer")
        self.assertEqual(len(form_parameters), 1)
        self.assertEqual(form_parameters[0]['name'], "query")

    def test_request_response_serializers10(self):
        class SerializedAPI(ListCreateAPIView):
            """
                ---
                POST:
                    request_serializer: CommentSerializer
                    response_serializer: QuerySerializer
            """
            serializer_class = QuerySerializer

            def post(self, request, *args, **kwargs):
                """
                    ---
                    request_serializer: QuerySerializer
                    response_serializer: CommentSerializer
                """
                return super(SerializedAPI, self).post(request, *args, **kwargs)
        class_introspector = self.make_introspector(SerializedAPI)
        introspector = APIViewMethodIntrospector(class_introspector, 'POST')
        generator = DocumentationGenerator()
        serializer = generator._get_method_serializer(introspector)
        self.assertEqual(serializer, CommentSerializer)
        body_parameters = introspector.build_body_parameters()
        form_parameters = introspector.build_form_parameters()
        self.assertEqual(body_parameters['name'], "QuerySerializer")
        self.assertEqual(len(form_parameters), 1)

    def test_custom_response_class(self):
        class SerializedAPI(ListCreateAPIView):
            serializer_class = CommentSerializer

            def post(self, request, *args, **kwargs):
                """
                ---
                type:
                  name:
                    required: true
                    type: string
                  url:
                    required: false
                    type: url
                """
                return super(SerializedAPI, self).post(request, *args, **kwargs)

        class_introspector = self.make_introspector(SerializedAPI)
        introspector = APIViewMethodIntrospector(class_introspector, 'POST')
        parser = introspector.get_yaml_parser()
        generator = DocumentationGenerator()
        serializer = generator._get_method_serializer(introspector)
        response_class = generator._get_method_response_type(
            parser, serializer, class_introspector, introspector)

        self.assertEqual(response_class, 'SerializedAPIPostResponse')
        self.assertEqual(serializer, None)
        self.assertIn('SerializedAPIPostResponse',
                      generator.explicit_response_types)

    @no_markdown
    def test_fbv_notes(self):

        @api_view(["POST"])
        def a_view(request):
            """
            Slimy toads
            """
            return "blarg"

        class_introspector = self.make_fbv_introspector(a_view)
        notes = class_introspector.get_notes()
        self.assertEqual(notes, "Slimy toads")
        introspector = WrappedAPIViewMethodIntrospector(class_introspector, 'POST')

        notes = introspector.get_notes()

        self.assertEqual(notes, "Slimy toads")

    def test_fbv_markdown(self):

        @api_view(["POST"])
        def a_view(request):
            """
            Slimy *toads*
            """
            return "blarg"

        class_introspector = self.make_fbv_introspector(a_view)
        url_patterns = patterns('', url(r'my-api/', a_view))
        urlparser = UrlParser()
        generator = DocumentationGenerator()
        apis = urlparser.get_apis(url_patterns)
        notes = class_introspector.get_notes()
        self.assertEqual(notes, "<p>Slimy <em>toads</em></p>")
        introspector = WrappedAPIViewMethodIntrospector(class_introspector, 'POST')

        notes = introspector.get_notes()

        self.assertEqual(notes, "<p>Slimy <em>toads</em></p>")
        api_docs = generator.generate(apis)
        self.assertEqual(len(api_docs), 1)
        self.assertIn("description", api_docs[0])
        self.assertEqual(api_docs[0]["description"], "Slimy toads")
        self.assertIn('operations', api_docs[0])
        self.assertEqual(api_docs[0]["operations"][0]['summary'], "Slimy toads")

    def test_apiview_models(self):
        from rest_framework.views import Response

        class MyCustomView(APIView):
            """
            Slimy toads
            """

            def get(self, *args, **kwargs):
                """
                param1 -- my param
                """
                return Response({'foo': 'bar'})

            def post(self, request, *args, **kwargs):
                """
                horse -- the name of your horse
                """
                return Response({'horse': request.GET.get('horse')})

        url_patterns = patterns('', url(r'my-api/', MyCustomView.as_view()))
        urlparser = UrlParser()
        apis = urlparser.get_apis(url_patterns)
        generator = DocumentationGenerator()
        models = generator.get_models(apis)
        self.assertEqual(type(models), dict)

    def test_view_mocker(self):

        class_introspector = self.make_introspector(ViewMockerNeedingAPI)
        introspector = APIViewMethodIntrospector(class_introspector, 'POST')
        generator = DocumentationGenerator()
        serializer = generator._get_method_serializer(introspector)
        self.assertEqual(CommentSerializer, serializer)

    def test_view_mocker_null(self):
        class SerializedAPI(ListCreateAPIView):
            def get_serializer_class(self):
                if self.request.tacos == 'tasty':
                    return CommentSerializer
                else:
                    return QuerySerializer

            def post(self, request, *args, **kwargs):
                """
                ---
                view_mocker: my_view_mocker2
                """
                return super(SerializedAPI, self).post(request, *args, **kwargs)
        class_introspector = self.make_introspector(SerializedAPI)
        introspector = APIViewMethodIntrospector(class_introspector, 'POST')
        generator = DocumentationGenerator()
        serializer = generator._get_method_serializer(introspector)
        self.assertIsNone(serializer)

    def test_pytype(self):
        @api_view(["POST"])
        def a_view(request):
            """
            ---
            response_serializer: CommentSerializer
            parameters:
                - name: stuff
                  paramType: body
                  pytype: QuerySerializer
                  type: int
            """
            from rest_framework.views import Response
            return Response("o noes!")
        generator = DocumentationGenerator()
        urlparser = UrlParser()
        url_patterns = patterns('', url(r'my-api/', a_view))
        apis = urlparser.get_apis(url_patterns)
        serializers = generator._get_serializer_set(apis)
        self.assertIn(CommentSerializer, serializers)
        self.assertIn(QuerySerializer, serializers)
        api = {
            'path': 'a-path/',
            'callback': func_to_wrapper(a_view),
            'pattern': patterns('')
        }
        operations = generator.get_operations(api)
        self.assertEqual(len(operations), 1)
        parameters = operations[0]['parameters']
        self.assertEqual(len(parameters), 1)
        self.assertNotIn("pytype", parameters[0])
        self.assertEqual(parameters[0]['name'], 'stuff')
        self.assertEqual(parameters[0]['type'], 'QuerySerializer')


class ViewMockerNeedingAPI(ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.tacos == 'tasty':
            return CommentSerializer
        else:
            return QuerySerializer

    def post(self, request, *args, **kwargs):
        """
        ---
        view_mocker: my_view_mocker
        """
        return super(ViewMockerNeedingAPI, self).post(request, *args, **kwargs)


def my_view_mocker(view):
    view.request.tacos = 'tasty'
    return view


def my_view_mocker2(view):
    pass


reST_SETTINGS = {
    'REST_FRAMEWORK': {
        'VIEW_DESCRIPTION_FUNCTION':
        'rest_framework_swagger.views.get_restructuredtext'
    }
}


@override_settings(**reST_SETTINGS)
class RESTDocstringTests(TestCase):
    def test_get_summary_empty(self):
        class MyViewSet(ModelViewSet):
            model = User
            serializer_class = CommentSerializer
            paginate_by = 20
            paginate_by_param = 'page_this_by'

        class_introspector = make_viewset_introspector(MyViewSet)
        introspector = get_introspectors(class_introspector)['create']
        summary = introspector.get_summary()
        self.assertEqual("", summary)

    def test_get_summary_view(self):
        class MyViewSet(ModelViewSet):
            """
            Oh yes this is reST
            ============
            """
            model = User
            serializer_class = CommentSerializer
            paginate_by = 20
            paginate_by_param = 'page_this_by'

        class_introspector = make_viewset_introspector(MyViewSet)
        introspector = get_introspectors(class_introspector)['create']
        summary = introspector.get_summary()
        self.assertEqual("Oh yes this is reST", summary)

    def test_get_yaml(self):
        class MyViewSet(ModelViewSet):
            """
            Oh yes this is reST
            ---
            # Oh no, this isn't reST
            create:
                param: my param
            """
            model = User
            serializer_class = CommentSerializer
            paginate_by = 20
            paginate_by_param = 'page_this_by'

        class_introspector = make_viewset_introspector(MyViewSet)
        introspector = get_introspectors(class_introspector)['create']
        docs = introspector.get_notes()
        self.assertIn('Oh yes this is reST', docs)
        doc_parser = introspector.get_yaml_parser()
        self.assertEqual(doc_parser.object['param'], 'my param')

    def test_dont_get_yaml(self):
        class MyViewSet(ModelViewSet):
            """
            Oh yes this is reST
            -------------------
            Oh yes so is this
            """
            model = User
            serializer_class = CommentSerializer
            paginate_by = 20
            paginate_by_param = 'page_this_by'

        class_introspector = make_viewset_introspector(MyViewSet)
        introspector = get_introspectors(class_introspector)['create']
        docs = introspector.get_notes()
        self.assertIn('Oh yes this is reST', docs)
        self.assertIn('Oh yes so is this', docs)

    def test_dont_get_params(self):
        class MyViewSet(ModelViewSet):
            """
            Oh yes this is reST
            -------------------
            Oh yes so is this
            -- this isnt
            """
            model = User
            serializer_class = CommentSerializer
            paginate_by = 20
            paginate_by_param = 'page_this_by'

        class_introspector = make_viewset_introspector(MyViewSet)
        introspector = get_introspectors(class_introspector)['create']
        docs = introspector.get_notes()
        self.assertIn('Oh yes this is reST', docs)
        self.assertIn('Oh yes so is this', docs)
