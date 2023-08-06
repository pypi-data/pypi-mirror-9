# core Python packages
from datetime import timedelta
import logging

# django packages
from django.utils import timezone
from django.conf import settings
from django.template.loader import render_to_string

# local project and app packages
from models import DataSet

# sister app stuff
from djhcup_core.utils import get_pgcnxn, make_html_email

# start a logger
logger = logging.getLogger('default')

# make these tasks app-agnostic with @celery.shared_task
from celery import shared_task


@shared_task
def process_dataset(d_pk, dry_run=False, site=None):
    """
    Extracts dataset and bundles into a ZIP archive
    for download.
    """
    # grab the DataSet object
    try:
        d = DataSet.objects.get(pk=d_pk)
    except DataSet.DoesNotExist:
        raise Exception("Unable to find DataSet with pk {pk}" \
            .format(pk=d_pk))
    d.log("tasks.process_dataset called for d_pk=%s" % d_pk,
          status="IN PROCESS")
    #d.save() why is this needed?
    
    result = d._process(dry_run)
    d.wip = False
    d.save()
    email_body = render_to_string('emails/rpt_dataset_done.html', {
        'site': site,
        'dataset': d
    })
    em = make_html_email(email_body, subject="Your dataset is ready (%s)" % (d.name), to=[d.owner.email])
    em.send()
    return result

@shared_task
def prune_datasets():
    DataSet.objects.filter(complete__lte=timezone.now() - timedelta(days=30)).delete()