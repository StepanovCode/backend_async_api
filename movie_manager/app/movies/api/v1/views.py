from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView
from config.components.dev_setting import DEBUG

from movies.models import Filmwork

import json

class MoviesApiMixin:
    model = Filmwork
    http_method_names = ['get']

    def get_queryset(self):
        """
            Я отдебажил и попытался поменять на prefetch_related
            и там и там 1 sql запрос, и 1 на пагинацию.
            К тому же sql запросы индентичные получаются.
        """
        query = Filmwork.objects.prefetch_related('persons', 'genres').values()\
            .annotate(actors=ArrayAgg('persons__full_name', filter=Q(personfilmwork__role='actor'),
                                     distinct=True),
                      directors=ArrayAgg('persons__full_name', filter=Q(personfilmwork__role='director'),
                                         distinct=True),
                      writers=ArrayAgg('persons__full_name', filter=Q(personfilmwork__role='writer'),
                                       distinct=True),
                      genres=ArrayAgg('genres__name', distinct=True))
        return query

    def render_to_response(self, context, **response_kwargs):
        if DEBUG:
            body = f'<body>{json.dumps(context, indent=4, default=str)}</body>'
            return HttpResponse(body)
        return JsonResponse(context, json_dumps_params={'indent': 2})


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):
    def get_context_data(self, **kwargs):
        return dict(self.object)


class MoviesListApi(MoviesApiMixin, BaseListView):
    model = Filmwork
    paginate_by = 50
    http_method_names = ['get']

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = self.get_queryset()
        paginator, page, queryset, is_paginated = self.paginate_queryset(
            queryset,
            self.paginate_by
        )

        return {
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'prev': page.previous_page_number() if page.has_previous() else None,
            'next': page.next_page_number() if page.has_next() else None,
            'results': list(page)
        }
