"""JSON views for API."""
from django.contrib.postgres.aggregates import ArrayAgg
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView
from movies.models import Filmwork, PersonFilmworkRoleChoices


class MoviesApiMixin(object):
    """Basic mixin for API calls."""

    model = Filmwork
    http_method_names = ['get']
    paginate_by = 50

    def get_queryset(self):
        """Prepare QuerySet for movies.

        Returns:
            QuerySet prepared query set

        """
        ds = Filmwork.objects.values(
            'id',
            'title',
            'description',
            'creation_date',
            'rating',
            'type',
            )
        ds = ds.annotate(genres=ArrayAgg('genres__name', distinct=True))
        for role, _ in PersonFilmworkRoleChoices.choices:
            ds = ds.filter(personfilmwork__role=role)
            args = {role + 's': ArrayAgg('persons__full_name', distinct=True)}
            ds = ds.annotate(**args)
        return ds.order_by('id')

    def render_to_response(self, context, **response_kwargs):
        """Render JSON using context.

        Args:
            context (dict): data to transform to json
            **response_kwargs (kw-extracted): additional kw-args

        Returns:
            str json-formatted response
        """
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):
    """MoviesList context preparation + pagination."""

    def get_context_data(self, *, object_list=None, **kwargs):
        """Prepare QuerySet for movies.

        Args:
            **kwargs (kw-extracted): additional kw-args
            object_list (list): list of returned objects

        Returns:
            QuerySet: prepared query set
        """
        paginator, page, queryset, is_paginated = self.paginate_queryset(
            self.get_queryset(),
            self.paginate_by,
        )
        pprev = page.previous_page_number() if page.has_previous() else None
        pnext = page.next_page_number() if page.has_next() else None
        return {
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'prev': pprev,
            'next': pnext,
            'results': list(queryset),
        }


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):
    """Fetch exact movie."""

    def get_context_data(self, **kwargs):
        """Prepare QuerySet for movies.

        Args:
            **kwargs (kw-extracted): additional kw-args

        Returns:
            dict: context as dict
        """
        return self.object
