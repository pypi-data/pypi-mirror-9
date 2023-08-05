from django.utils.importlib import import_module
from django.utils.module_loading import module_has_submodule
from django.utils.encoding import force_text
from django.utils.six import string_types
from django.conf.urls import url
from django.core.paginator import Paginator

from django.contrib.auth.models import AnonymousUser

from django.conf import settings
from rest_framework.routers import DefaultRouter, Route
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.settings import api_settings
from rest_framework.response import Response

from .models import get_ct
from .permissions import has_perm
from .views import SimpleViewSet, ModelViewSet

PREDICATES = ('annotated', 'identified', 'located', 'marked', 'related')


class Router(DefaultRouter):
    _models = set()
    _serializers = {}
    _querysets = {}
    _filters = {}
    _viewsets = {}
    _extra_pages = {}
    _config = {}
    _page_names = {}
    _page_models = {}
    _extra_config = {}

    include_root_view = False
    include_config_view = True
    include_multi_view = True

    def __init__(self, trailing_slash=False):
        # Add trailing slash for HTML list views
        self.routes.append(Route(
            url=r'^{prefix}/$',
            mapping={
                'get': 'list',
                'post': 'create'
            },
            name='{basename}-list',
            initkwargs={'suffix': 'List'}
        ))
        super(Router, self).__init__(trailing_slash=trailing_slash)

    def register_model(self, model, viewset=None, serializer=None,
                       queryset=None, filter=None, **kwargs):
        if isinstance(model, string_types) and '.' in model:
            from django.db.models import get_model
            model = get_model(*model.split('.'))
        self._models.add(model)
        ct = get_ct(model)

        if viewset:
            self.register_viewset(model, viewset)
        if serializer:
            self.register_serializer(model, serializer)
        if queryset:
            self.register_queryset(model, queryset)
        if filter:
            self.register_filter(model, filter)

        if 'name' not in kwargs:
            kwargs['name'] = ct.identifier
        if 'url' not in kwargs:
            url = force_text(model._meta.verbose_name_plural)
            kwargs['url'] = url.replace(' ', '')

        self.register_config(model, kwargs)
        self._page_names[model] = kwargs['name']
        self._page_models[kwargs['name']] = model

    def register_viewset(self, model, viewset):
        self._viewsets[model] = viewset

    def register_serializer(self, model, serializer):
        self._serializers[model] = serializer

    def register_queryset(self, model, queryset):
        self._querysets[model] = queryset

    def register_filter(self, model, queryset):
        self._filters[model] = queryset

    def register_config(self, model, config):
        self._config[model] = config
        self._base_config = None

    def update_config(self, model, **kwargs):
        if model not in self._config:
            raise RuntimeError("%s must be registered first" % model)
        self._config[model].update(kwargs)
        self._base_config = None

    def set_extra_config(self, **extra):
        self._extra_config.update(extra)
        self._base_config = None

    def get_serializer_for_model(self, model_class, serializer_depth=None):
        if model_class in self._serializers:
            serializer = self._serializers[model_class]
        else:
            # Make sure we're not dealing with a proxy
            real_model = get_ct(model_class, True).model_class()
            if real_model in self._serializers:
                serializer = self._serializers[real_model]
            else:
                serializer = api_settings.DEFAULT_MODEL_SERIALIZER_CLASS

        class Serializer(serializer):
            class Meta(serializer.Meta):
                depth = serializer_depth
                model = model_class
        return Serializer

    def serialize(self, obj, many=False, depth=None):
        if many:
            # assume obj is a queryset
            model = obj.model
            if depth is None:
                depth = 0
        else:
            model = obj
            if depth is None:
                depth = 1
        serializer = self.get_serializer_for_model(model, depth)
        return serializer(obj, many=many, context={'router': self}).data

    def get_paginate_by_for_model(self, model_class):
        config = self.get_model_config(model_class) or {}
        paginate_by = config.get('per_page', None)
        if paginate_by:
            return paginate_by
        return api_settings.PAGINATE_BY

    def paginate(self, model, page_num, request=None):
        obj_serializer = self.get_serializer_for_model(model)
        paginate_by = self.get_paginate_by_for_model(model)
        viewset = self.get_viewset_for_model(model)
        qs = self.get_queryset_for_model(model, request)
        # FIXME: should copy() before modifying but doing so causes recursion
        request.GET = {}
        qs = viewset(
            action="list",
            request=request,
            kwargs={}
        ).filter_queryset(qs)

        paginator = Paginator(qs, paginate_by)
        page = paginator.page(page_num)

        class Serializer(api_settings.DEFAULT_PAGINATION_SERIALIZER_CLASS):
            class Meta:
                object_serializer_class = obj_serializer
        return Serializer(
            instance=page,
            context={'router': self, 'request': request}
        ).data

    def get_queryset_for_model(self, model, request=None):
        if model in self._querysets:
            qs = self._querysets[model]
        else:
            qs = model.objects.all()
        if request and model in self._filters:
            qs = self._filters[model](qs, request)
        return qs

    def get_lookup_for_model(self, model_class):
        if get_ct(model_class).is_identified:
            return 'primary_identifiers__slug'
        else:
            config = self.get_model_config(model_class) or {}
            return config.get('lookup', 'pk')

    def get_viewset_for_model(self, model_class):
        if model_class in self._viewsets:
            viewset = self._viewsets[model_class]
        else:
            # Make sure we're not dealing with a proxy
            real_model = get_ct(model_class, True).model_class()
            if real_model in self._viewsets:
                viewset = self._viewsets[real_model]
            else:
                viewset = ModelViewSet
        lookup = self.get_lookup_for_model(model_class)

        class ViewSet(viewset):
            model = model_class
            router = self
            lookup_field = lookup

        return ViewSet

    _base_config = None

    @property
    def base_config(self):
        if self._base_config:
            return self._base_config

        user = AnonymousUser()
        pages = {}
        for page in self._extra_pages:
            conf, view = self.get_page(page)
            pages[page] = conf
        for model in self._models:
            ct = get_ct(model)
            if not has_perm(user, ct, 'view'):
                continue
            info = self._config[model].copy()
            info['list'] = True
            for perm in ('add', 'change', 'delete'):
                if has_perm(user, ct, perm):
                    info['can_' + perm] = True

            if 'parents' not in info:
                parents = {}
                as_dict = False
                for pct, fields in ct.get_foreign_keys().items():
                    if pct.is_registered():
                        if has_perm(user, pct, 'view'):
                            if len(fields) > 1 or fields[0] != pct.identifier:
                                as_dict = True
                            parents[pct.identifier] = fields
                if as_dict:
                    info['parents'] = parents
                else:
                    info['parents'] = list(parents.keys())

            if 'children' not in info:
                info['children'] = []
                for cct in ct.get_children():
                    if cct.is_registered():
                        if has_perm(user, cct, 'view'):
                            info['children'].append(cct.identifier)

            for name in PREDICATES:
                if getattr(ct, 'is_' + name):
                    info[name] = True

            if ct.is_located or ct.has_geo_fields:
                info['map'] = True

            for field in model._meta.fields:
                if field.choices:
                    info.setdefault('choices', {})
                    info['choices'][field.name] = [{
                        'value': val,
                        'label': str(label)
                    } for val, label in field.choices]

            for name in ('annotationtype', 'annotation'):
                if ct.identifier != name and getattr(ct, 'is_' + name):
                    pages[name] = {'alias': ct.identifier}

            pages[info['name']] = info

        self._base_config = {'pages': pages}
        self._base_config.update(self._extra_config)
        return self._base_config

    def get_config(self, user=None):
        if user is None or not user.is_authenticated():
            return self.base_config

        # Add user-specific permissions to configuration
        config = {
            key: val.copy() if hasattr(val, 'copy') else val
            for key, val in self.base_config.items()
        }
        for page, info in config['pages'].items():
            if not info.get('list', False):
                continue
            ct = get_ct(self._page_models[page])
            info = info.copy()
            for perm in ('add', 'change', 'delete'):
                if has_perm(user, ct, perm):
                    info['can_' + perm] = True
            config['pages'][page] = info

        return config

    def add_page(self, name, config, view=None):
        if view is None:
            class PageView(SimpleViewSet):
                template_name = name + '.html'

                def list(self, request, *args, **kwargs):
                    return Response(config)
            view = PageView
        if 'name' not in config:
            config['name'] = name
        if 'url' not in config:
            config['url'] = name
        self._extra_pages[name] = config, view
        self._base_config = None

    def get_page(self, page):
        return self._extra_pages[page]

    def get_page_config(self, name, user=None):
        config = self.get_config(user)
        return config['pages'].get(name, None)

    def get_model_config(self, model, user=None):
        # First, check models registered with API
        if model in self._page_names:
            config = self.get_config(user)
            return config['pages'][self._page_names[model]]

        # Then check config cache directly (in case model was configured but
        # not fully registered as part of API)
        if model in self._config:
            return self._config[model]
        return None

    def model_is_registered(self, model):
        return model in self._models

    def get_config_view(self):
        class ConfigView(SimpleViewSet):
            def list(this, request, *args, **kwargs):
                return Response(self.get_config(request.user))
        return ConfigView

    def get_multi_view(self):
        class MultipleListView(SimpleViewSet):
            def list(this, request, *args, **kwargs):
                urls = request.GET.get('lists', '').split(',')
                return self.get_multi(request, urls)
        return MultipleListView

    def get_multi(self, request, urls):
        conf = self.get_config(request.user)
        conf_by_url = {
            conf['url']: (page, conf)
            for page, conf
            in self.get_config(request.user)['pages'].items()
        }
        result = {}
        for listurl in urls:
            if listurl not in conf_by_url:
                continue
            page, conf = conf_by_url[listurl]
            model = self._page_models[page]
            result[listurl] = self.paginate(model, 1, request)
        return Response(result)

    def get_urls(self):
        # Register viewsets with DefaultRouter just before returning urls

        # The root viewset (with a url of "") should be registered last
        root = {}

        def register(config, viewset):
            if config['url'] == "":
                root['view'] = viewset
                root['name'] = config['name']
            else:
                self.register(config['url'], viewset, config['name'])

        # List (model) views
        for model in self._models:
            viewset = self.get_viewset_for_model(model)
            config = self._config[model]
            register(config, viewset)

        # Extra/custom viewsets
        for name in self._extra_pages:
            register(*self._extra_pages[name])

        if self.include_config_view:
            # /config.js
            self.register('config', self.get_config_view(), 'config')

        if self.include_multi_view:
            # /multi.json
            self.register('multi', self.get_multi_view(), 'multi')

        urls = super(Router, self).get_urls()

        if root:
            # / - Skip registration and directly generate custom URLs
            urls.extend(self.get_root_urls(root['view'], root['name']))

        return urls

    def get_root_urls(self, viewset, name):
        lookup = self.get_lookup_regex(viewset)
        routes = self.get_routes(viewset)
        urls = []
        for route in routes:
            pattern = route.url.format(
                prefix='',
                lookup=lookup,
                trailing_slash=self.trailing_slash,
            )

            # Remove leading slash from detail view URLs
            pattern = pattern.replace('/', '', 1)

            mapping = self.get_method_map(viewset, route.mapping)
            if not mapping:
                continue
            view = viewset.as_view(mapping, **route.initkwargs)
            urls.append(url(pattern, view, name=name))

        return format_suffix_patterns(urls)

    def get_routes(self, viewset):
        routes = super(Router, self).get_routes(viewset)
        model = getattr(viewset, "model", None)
        if not model:
            return routes

        # Custom routes

        ct = get_ct(model)
        for pct in ct.get_all_parents():
            if not pct.is_registered():
                continue
            if pct.urlbase == '':
                purlbase = ''
            else:
                purlbase = pct.urlbase + '/'

            purl = (
                '^' + purlbase + r'(?P<' + pct.identifier
                + '>[^\/\?]+)/{prefix}{trailing_slash}$'
            )
            routes.append(Route(
                url=purl,
                mapping={'get': 'list'},
                name="{basename}-for-%s" % pct.identifier,
                initkwargs={'suffix': 'List'},
            ))

        for cct in ct.get_all_children():
            if not cct.is_registered():
                continue
            cbase = cct.urlbase
            routes.append(Route(
                url='^%s-by-{prefix}' % cbase,
                mapping={'get': 'list'},
                name="%s-by-%s" % (cct.identifier, ct.identifier),
                initkwargs={'target': cbase, 'suffix': 'List'},
            ))

        return routes

    @property
    def version(self):
        if not hasattr(self, '_version'):
            vtxt = getattr(settings, 'VERSION_TXT', None)
            if vtxt is None:
                self._version = None
            else:
                vfile = open(vtxt, 'r')
                self._version = vfile.read()
                vfile.close()
        return self._version

router = Router()


def autodiscover():
    for app_name in settings.INSTALLED_APPS:
        app = import_module(app_name)
        if module_has_submodule(app, 'rest'):
            import_module(app_name + '.rest')
