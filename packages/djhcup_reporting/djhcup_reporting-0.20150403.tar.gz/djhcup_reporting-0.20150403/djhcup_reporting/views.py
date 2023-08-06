# core Python packages
import os
import logging
import json
import zipfile
from io import StringIO


# third party packages


# django packages
from django.core.exceptions import ObjectDoesNotExist
from django.core.servers.basehttp import FileWrapper
from django.core.urlresolvers import reverse
from django.http import HttpResponse, StreamingHttpResponse, HttpResponseRedirect, Http404, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import utc
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.views.generic import FormView, ListView, TemplateView, View
from django.contrib.sites.models import RequestSite


# sister app imports
from djhcup_core.utils import installed_modules


# local imports
from djhcup_reporting.models import ReportingTable, LookupTable, Universe, FILTER_OPERATOR_CHOICES, Query, DataSet, Column
from djhcup_reporting.utils.reporting import filterbundle_from_json
from djhcup_reporting.forms import PublicDataSetForm
from djhcup_reporting.tasks import process_dataset


# start a logger
logger = logging.getLogger('default')


"""
Create your views here.
"""

class Index(TemplateView):
    template_name = 'rpt_base.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(Index, self).dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        return redirect('datasets_browse')

    # def get_context_data(self, **kwargs):
    #     context = super(Index, self).get_context_data(**kwargs)
    #     context['title'] = 'Reporting Index'
    #     return context

class QueryBuilder(TemplateView):
    template_name = 'rpt_new.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):

        return super(QueryBuilder, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        universes = context['universes']
        if len(universes) == 1:
            # there is only one Universe.
            # go ahead and get started with it.
            u = universes[0]
            return QueryBuilderFilters.as_view()(request, universe_pk=u.pk)
        return super(QueryBuilder, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        universes = self.get_context_data(**kwargs)['universes']
        if len(universes) == 1:
            u_pk = universes[0].pk
        elif 'universe_pk' in request.GET:
            u_pk = request.GET['universe_pk']
        else:
            return HttpResponseBadRequest('universe_pk must be specified since more than one universe exists.')
        if 'filter_json' in request.POST:
            return QueryBuilderSave.as_view()(request, u_pk)
        else:
            return QueryBuilderFilters.as_view()(request, u_pk)
    
    def get_context_data(self, **kwargs):
        context = super(QueryBuilder, self).get_context_data(**kwargs)
        universes = Universe.objects.all()
        context['title'] = 'Query Builder: Choose Reporting Universe'
        context['universes'] = universes
        return context

class QueryBuilderFilters(TemplateView):
    template_name = 'rpt_builder.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(QueryBuilderFilters, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(QueryBuilderFilters, self).get_context_data(**kwargs)
        u = get_object_or_404(Universe, pk=self.kwargs['universe_pk'])        
        filter_fields = u.filters_for_display()
        filter_operators = [{"display": f[1], "value": f[0]} for f in FILTER_OPERATOR_CHOICES]
        try:
            available_columns = u.data.column_set.all().order_by('category', 'int_column__field_out', 'label')
        except:
            available_columns = None
    
        context.update({
            'title': 'DataSet Builder',
            'json_filter_fields': json.dumps(filter_fields),
            'json_filter_operators': json.dumps(filter_operators),
            'universe': u,
            'form': PublicDataSetForm(),
            'available_columns': available_columns
        })

        #print context
        return context

class QueryBuilderSave(View):
    """Saves objects associated with the query builder process,
    and then opens them for further editing (assign a name, etc).
    """

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(QueryBuilderSave, self).dispatch(*args, **kwargs)

    def post(self, request, universe_pk, *args, **kwargs):
        u = get_object_or_404(Universe, pk=universe_pk)        
        try:
            fg = filterbundle_from_json(request.POST['filter_json'])
        except:
            # return render(unable to process filter bundle error)
            # ask people to use their back button to make changes
            return HttpResponseBadRequest('Unable to process filter_json')
        q = Query(filtergroup=fg, universe=u)
        q.save()
        
        # add all dem columns
        col_lst = request.POST.getlist('columns[]', [])
        for c_pk in col_lst:
            try:
                c = Column.objects.get(pk=int(c_pk))
                q.columns.add(c)
            except Column.DoesNotExist:
                logger.warning("Unable to find Column with pk %s" % c_pk)
        d = DataSet(query=q)
        form = PublicDataSetForm(request.POST)
        if form.is_valid():
            cleaned = form.cleaned_data
            d.name = cleaned['name']
            d.description = cleaned['description']
        
        # check for pre- and post-visit requests
        d.bundle_previsit_file = request.POST.get('bundle_previsit_file', False)
        d.bundle_postvisit_file = request.POST.get('bundle_postvisit_file', False)

        d.owner = request.user
        d.gen_dbo(overwrite=True)
        d.save()

        # call the extraction as an asynchronous task
        result = process_dataset.delay(d.pk, site=RequestSite(request))
        
        # meanwhile proceed to show the details page
        return HttpResponseRedirect(reverse('dataset_details', kwargs={'dataset_dbo_name': d.dbo_name}))

class BrowseDatasets(ListView):
    template_name = 'rpt_datasets.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(BrowseDatasets, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        return DataSet.objects.filter(owner=self.request.user).order_by('-created')

    def get_context_data(self, **kwargs):
        context = super(BrowseDatasets, self).get_context_data(**kwargs)
        context['title'] = 'My DataSets'
        return context

class DatasetDetails(FormView):
    form_class = PublicDataSetForm
    template_name = 'rpt_dataset_details.html'

    @method_decorator(login_required)
    def dispatch(self, request, dataset_dbo_name):
        self.dataset = get_object_or_404(DataSet, dbo_name=dataset_dbo_name, owner=request.user)
        return super(DatasetDetails, self).dispatch(request, dataset_dbo_name)

    def get(self, request, *args, **kwargs):
        if self.dataset.status == 'NEW':
            messages.warning(request,
                'Your query has been placed in the queue. Once it has finished, you will be able to download the result from this page.')
    
        if not self.dataset.name:
            messages.warning(request,
                'Your DataSet does not have a name. Please enter one below.')

        return super(DatasetDetails, self).get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(DatasetDetails, self).get_form_kwargs()
        kwargs.update({
            'instance': self.dataset
        })
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Dataset updated successfully.')
        return super(DatasetDetails, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(DatasetDetails, self).get_context_data(**kwargs)
        context.update({
            'title': 'DataSet #{pk} Details'.format(pk=self.dataset.pk),
            'universe': self.dataset.query.universe,
            'query': self.dataset.query,
            'dataset': self.dataset,
        })
        return context

    def get_success_url(self):
        return self.request.path

class UniverseDetails(TemplateView):
    template_name = 'rpt_universe_details.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UniverseDetails, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UniverseDetails, self).get_context_data(**kwargs)
        u = get_object_or_404(Universe, pk=self.kwargs['universe_pk'])
        context['universe'] = u
        context['title'] = 'Universe #{pk} Details'.format(pk=u.pk)
        return context

class DownloadArchive(View):
    """Returns a data stream for a zip archive associated
    with the requested dataset_dbo_name.
    """

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DownloadArchive, self).dispatch(*args, **kwargs)

    def get(self, request, dataset_dbo_name):
        d = get_object_or_404(DataSet, dbo_name=dataset_dbo_name, status='SUCCESS', wip=False)
        h = open(d.archive_path, 'r')
        wrapper = FileWrapper(h)
        response = StreamingHttpResponse(wrapper, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(d.archive_path)
        
        return response