import datetime
import logging
import os
import re
import zipfile
from io import StringIO
from sqlalchemy.sql import select, column, subquery
from sqlalchemy.sql.expression import alias, and_, or_

import pyhcup


# django imports
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import utc
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth.models import User


# sister app imports
from djhcup_core import database
from djhcup_core.utils import get_pgcnxn
from djhcup_core.utils import salt
from djhcup_integration.models import IntegrationTable, Column as IntegrationColumn, Definition as IntegrationDefinition, Edition as IntegrationEdition


from djhcup_reporting.utils.config import RPT_COLUMN_META


DATASET_DIR = os.path.join(settings.BASE_DIR, 'datasets')


# this should almost certainly go in the install for one of these apps
if not os.path.exists(DATASET_DIR):
    os.mkdir(DATASET_DIR)
logger = logging.getLogger('default')
DEFAULT_LOGGER = logger


FILTER_OPERATOR_MAP = {
    # no operator is represented here for
    # values in list.
    # instead, if value passed to Filter instantiation
    # is a list, then operator is ignored
    "eq": "=",
    "neq": "!=",
    "gt": ">",
    "lt": "<",
    "gte": ">=",
    "lte": "<="
}

FILTER_OPERATOR_CHOICES = [
    ('=','equal to'),
    ('!=','not equal to'),
    ('>','greater than'),
    ('<','less than'),
    ('>=','greater than or equal to'),
    ('<=','less than or equal to'),
    ('IN','in list (comma-separated)'),
    ('NOT IN','not in list (comma-separated)')
]

COL_CATGORY_CHOICES = [
    ('REC_ID','Record Identifiers'),
    ('DEMO','Demographics'),
    ('VISIT','Visit characteristics'),
    ('HOSPITAL','Hospital characteristics'),
    ('CCS_MHSA','Clinical Classifications Software Mental Health and Substance Abuse flags'),
    ('CCI','Chronic condition indicators (CCI)'),
    ('COMORBIDITY','Comorbidity flags'),
    ('DX_BASIC','Diagnoses basics'),
    ('DX_EXTRA','Diagnoses extras'),
    ('PR_BASIC','Procedures basics'),
    ('PR_EXTRA','Procedures extras'),
    ('UFLAG','Utilization flags')
]

ALLOWED_LOG_LEVELS = ['NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']


def is_numeric(s):
    if type(s) is bool:
        return False
    else:
        try:
            float(s)
            return True
        except ValueError:
            return False


# Create your models here.
class DataSet(models.Model):
    name = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    query = models.OneToOneField('Query', blank=False)
    created = models.DateTimeField(auto_now_add=True)
    start = models.DateTimeField(blank=True, null=True)
    complete = models.DateTimeField(blank=True, null=True)
    dbo_name = models.CharField(max_length=53, blank=True, default=None,
                                null=True, editable=False)
    dbo_name_prefix = models.CharField(max_length=12, default='rpt_dataset_',
                                       editable=False)
    rows = models.IntegerField(blank=True, editable=False, null=True,
                               default=None)
    # linked visits
    bundle_previsit_file = models.BooleanField(default=False)
    previsit_dbo_name = models.CharField(max_length=53, blank=True,
                                         default=None, null=True,
                                         editable=False)
    previsit_rows = models.IntegerField(blank=True, editable=False,
                                        null=True, default=None)
    bundle_postvisit_file = models.BooleanField(default=False)
    postvisit_dbo_name = models.CharField(max_length=53, blank=True,
                                         default=None, null=True,
                                         editable=False)
    postvisit_rows = models.IntegerField(blank=True, editable=False,
                                         null=True, default=None)
    
    owner = models.ForeignKey(User, db_index=True)
    # link # pre-generate and cache here?
    void = models.BooleanField(default=False)
    void_at = models.DateTimeField(blank=True, default=None, null=True)
    # voided_by? # fk django user object 
    
    STATUS_CHOICES = [
        ('NEW', 'Not started'),
        ('QUEUED', 'Request for processing sent'),
        ('DISPATCHED', 'Sent to Celery'),
        ('RECEIVED', 'Received by Celery'),
        ('IN PROCESS', 'Running'),
        ('FAILED', 'Failed to complete'),
        ('SUCCESS', 'Completed successfully'),
    ]
    status = models.CharField(max_length=25, choices=STATUS_CHOICES,
                              default='NEW')

    wip = models.BooleanField(default=True) # True if the output ZIP file is yet to be completely generated
    
    
    def _get_salt(self):
        try:
            return str(self.dbo_name).split(self.dbo_name_prefix)[-1]
        except:
            return None

    
    def _refresh_rowcounts(self):
        original = self._get_rowcount()
        if original:
            self.rows = original
        
        pre = self._get_rowcount('previsits')
        if pre:
            self.previsit_rows = pre
        
        post = self._get_rowcount('postvisits')
        if post:
            self.postvisit_rows = post
        
        self.save()
        
        return True
    
    
    def _get_rowcount(self, target='original'):
        template = "SELECT COUNT(*) FROM {tbl};"
        
        if target == 'previsits':
            stmt = template.format(tbl=self.previsit_dbo_name)
        
        elif target == 'postvisits':
            stmt = template.format(tbl=self.postvisit_dbo_name)
        
        else:
            stmt = template.format(tbl=self.dbo_name)
        
        cnxn = get_pgcnxn()
        cursor = cnxn.cursor()
        
        try:
            cursor.execute(stmt)    
            return cursor.fetchone()[0]
        except:
            return False
    
    
    def _hr_name(self):
        if self.name is not None and len(self.name) > 0:
            return self.name
        else:
            return self.dbo_name
    
    
    def _archive_path(self):
        candidate = os.path.join(DATASET_DIR, self.dbo_name + '.zip')
        if os.path.exists(candidate):
            return candidate
        else:
            return None

    
    def get_dbo_names(self):
        lst = [self.dbo_name]
        if self.bundle_previsit_file:
            lst.append(self.previsit_dbo_name)
        
        if self.bundle_postvisit_file:
            lst.append(self.postvisit_dbo_name)
        
        return lst
    
    
    def _process(self, dry_run=False):
        self.extract()
        self.status = 'PACKAGING'
        self.save()
        
        zip_path = self.zip_archive()
        
        if zip_path:
            self.success("Successfully extracted/packaged %s" % self._hr_name)
        
        return zip_path
    
    
    def extract(self, dry_run=False):
        """Generates SQL and runs a query to extract a dataset into
        a database table. It does not, on its own, make a zip archive
        or other download available.
        
        Parameters
        ===============
        dry_run: boolean (default False)
            If True, the database will be read but not modified.
        """
        
        self.start = datetime.datetime.utcnow().replace(tzinfo=utc)
        
        if (
            self.dbo_name is None or len(self.dbo_name) == 0
            or (
                self.bundle_previsit_file and (
                    self.previsit_dbo_name is None or
                    len(self.previsit_dbo_name) == 0
                )
            ) or (
                self.bundle_postvisit_file and (
                    self.postvisit_dbo_name is None or
                    len(self.postvisit_dbo_name) == 0
                )
            )):
            self.gen_dbo(overwrite=True)
            
            if not dry_run:
                self.save()
                self.log("Set dbo_name to %s" % self.dbo_name)
        
        # grab a psycopg2 connection and cursor
        # TODO: use a limited-permission account
        # (to prevent sql injection)
        # SECURITY WARNING: this is presently a major risk for malicious behavior
        cnxn = get_pgcnxn()
        cursor = cnxn.cursor()
        
        # for any tables we ought to be extracting,
        # be sure they do not already exist in the database
        for tbl in self.get_dbo_names():
            if database.check_table_exists(tbl):
                self.log("Table {tbl} already exists in database; extraction halted." \
                    .format(tbl=tbl))
                return False
        
        # build query (or queries, for linked visits)
        # and store the fully concatenated statement in the related
        # Query object.
        q = self.query
        stmt_template = "CREATE TABLE {des} AS\n{src};\n\n"
        stmt = stmt_template.format(des=self.dbo_name, src=database.compile_pg(q.sql()))
        
        if self.bundle_previsit_file:
            stmt += stmt_template.format(des=self.previsit_dbo_name,
                                         src=database.compile_pg(q._linked_sql()))
        
        if self.bundle_postvisit_file:
            stmt += stmt_template.format(des=self.postvisit_dbo_name,
                                         src=database.compile_pg(q._linked_sql(previsits=False)))
        
        q.statement = stmt
        print q.statement
        q.statement_last_update = datetime.datetime.utcnow().replace(tzinfo=utc)
        if not dry_run:
            # save mostly the generated statement
            q.save()

            try:
                cursor.execute(q.statement)
                cnxn.commit()
            except:
                self.fail("Failed to execute statement")
                raise
            
            try:
                self._refresh_rowcounts()
            except:
                self.log("Unable to log rowcount", level="WARNING")
            
            # This more properly should follow zip_archive()
            #self.success("Populated dataset in %s" % self.dbo_name)
            
            # log update instead of calling success()
            self.log("Populated dataset in %s" % self.dbo_name)
            
        cursor.close()
        
        return q.statement
    
    
    def zip_archive(self):
        """Will save a zip-compressed archive containing a csv
        of the DataSet result, plus extra "meta" files.
        """
        # make a new zipfile which will receive various files
        out_path = os.path.join(DATASET_DIR, self.dbo_name + '.zip')
        zf = zipfile.ZipFile(out_path,
                            mode='w',
                            compression=zipfile.ZIP_DEFLATED,
                            allowZip64=True # for large file support
                            )
        
        # grab a psycopg2 connection and cursor
        cnxn = get_pgcnxn()
        cursor = cnxn.cursor()
        
        # Step 1
        # Export
        targets = self.get_dbo_names()
        for t in targets:
            # Step 1-a
            # dump data
            
            """
            # WARNING
            # This approach is deprecated in favor of on-disk file
            # objects. Unfortunately, using StringIO in this fashion
            # bumps up against memory limits when exporting large
            # data sets. Originally this was expected to behave as
            # a buffer that didn't actually stream its content until
            # sending it to the ZipFile.writestr() method, but it is
            # holding the entire string in memory instead.
            
            # create a stream which will receive output from Postgres
            data_stream = StringIO()
            
            # capture a COPY stream; copy_export routes stdout to args[1]
            template = "COPY {tbl} TO STDOUT WITH CSV HEADER"
            stmt = template.format(tbl=t)
            cursor.copy_expert(stmt, data_stream)
            
            # establish a name for the csv within the zipfile
            dataset_filename = t + '.csv'
            zf.writestr(dataset_filename, data_stream.getvalue())
            """
            
            # create a file which will receive output from Postgres
            target_filename = t + '.csv'
            target_path = os.path.join(DATASET_DIR, target_filename)
            
            with open(target_path, "w") as target_handle:
                # capture a COPY stream; copy_export routes stdout to args[1]
                template = "COPY {tbl} TO STDOUT WITH CSV HEADER"
                stmt = template.format(tbl=t)
                cursor.copy_expert(stmt, target_handle)
                
            zf.write(target_path, target_filename)
        
            # Step 1-b
            # generate and add in a STATA loading file for each data file
            dofile_filename = t + '.do'
            dofile_stream = StringIO()
            
            # move the data from the stata loading file lines into an IO stream
            statalines = self._stataload(dofile_filename)
            dofile_stream.write(unicode("\n".join([l for l in statalines])))
            
            zf.writestr(dofile_filename, dofile_stream.getvalue())
            
        # Step 2
        # generate and add in a small description file
        description = self._describe()
        describe_stream = StringIO()
        describe_stream.write(unicode("\n".join([l for l in description])))
        zf.writestr('DESCRIPTION.txt',
                    describe_stream.getvalue())
        
        # once fished, close the zipfile handle
        zf.close()
        
        self.log("Packaged ZIP archive in %s" % target_path)
        
        # and delete any temporary files
        for t in targets:
            target_filename = t + '.csv'
            target_path = os.path.join(DATASET_DIR, target_filename)
            os.remove(target_path)
        
        self.log("Cleaned up temporary files")
        
        return out_path
    
    
    def _stataload(self, filename):
        """Returns a list object whose lines contain code to build a
        STATA loading program.
        
        filename is the data file (csv) the do file will act on
        """
        lines = []
        
        # the part that imports the csv file
        lines.append('import delimited "%s", clear' % filename)
        
        # the part that relabels the columns
        colset = self.query._get_colset()
        lines.extend([
            'label variable {n} "{hr}"'.format(n=str(c.name).lower(), hr=c.hr_name)
            for c in colset
        ])
        
        return lines
    
    
    def _describe(self):
        """Returns a list object whose lines contain summary info
        describing this DataSet.
        """
        lines = []
        
        # header
        lines.append("HCUP Hachoir DataSet %s (%s)" % (self.pk, self.hr_name))
        lines.append("%s rows" % self.rows)
        if self.bundle_previsit_file is not None:
            lines.append("Pre-visits: %s rows" % self.previsit_rows)
        if self.bundle_postvisit_file is not None:
            lines.append("Post-visits: %s rows" % self.postvisit_rows)
        lines.append("Generated %s" % self.complete)
        
        if self.description and len(self.description) > 0:
            lines.append("\n" + self.description)
        
        lines.append("")
        lines.append("==============================")
        lines.append("")
        lines.extend(self.universe._describe())
        
        lines.append("")
        lines.append("==============================")
        lines.append("")
        lines.append("Columns in DataSet:")
        
        for c in self.query._get_colset():
            lines.append("%s (#%s)" % (c.filter_display, c.pk))
        lines.append("")
        lines.append("==============================")
        lines.append("")
        lines.append("SQL used to generate DataSet:")
        lines.append(self.query.statement)
        
        lines.append("\n")
        
        return lines
    
    
    def log(self, message, level='INFO', status=None, logger=None):
        """Emit a log message at the specified log level and optionally update the ImportQueue object status attribute.
        """
        
        if level not in ALLOWED_LOG_LEVELS:
            raise Exception("Invalid log level specified: %s" % level)
        else:
            level = getattr(logging, level)
        
        if logger is None:
            logger = DEFAULT_LOGGER
        
        if status is not None:
            self.status = status
        
        logger_message = "[DataSet %s] %s" % (self.pk, message)
        logger.log(level, logger_message)
        return message    
    
    
    def fail(self, message=None, logger=None, level='ERROR'):
        self.status = 'FAILED'
        self.complete = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.save()
        
        if message is not None:
            self.log(message, level=level, logger=logger)
        
        return message
    
    
    def success(self, message=None, logger=None):
        self.status = 'SUCCESS'
        self.complete = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.save()
        
        if message is not None:
            self.log(message, logger=logger)
        
        return message
    
    
    def _universe(self):
        return self.query.universe
    
    
    def delete(self, drop_table=True, *args, **kwargs):
        """Extends normal delete() method behavior to include dropping
        the database table associated with this DataSet.
        """
        if drop_table:
            cnxn = get_pgcnxn()
            drop_result = pyhcup.db.pg_drop(cnxn, self.dbo_name)
            if drop_result == True:
                self.log('Dropped table {table} from database'.format(table=self.dbo_name))
            else:
                self.log('Unable to drop table {table} from database. If the table had not yet been populated, this is normal. Otherwise, check for an orphaned table.'.format(table=self.dbo_name),
                         level='ERROR')
        super(DataSet, self).delete(*args, **kwargs)

    
    def get_absolute_url(self):
        return reverse(
            'dataset_details',
            kwargs={'dataset_dbo_name': self.dbo_name}
        )
    
    
    def get_download_url(self):
        return reverse(
            'download_archive',
            kwargs={'dataset_dbo_name': self.dbo_name}
        )
    
    
    def gen_dbo(self, overwrite=False):
        """Find a table name not presently in use, and
        save it as the table name for this DataSet.
        
        Pseudo-randomly generated.
        """
        unused = False
        while unused == False:
            candidate = self.dbo_name_prefix + salt()
            check = DataSet.objects.filter(dbo_name=candidate)
            if len(check) == 0:
                unused = True
        
        if overwrite:
            self.dbo_name = candidate
            self.previsit_dbo_name = candidate + '_previsits'
            self.postvisit_dbo_name = candidate + '_postvisits'
            self.save()
        
        return candidate
    
    
    archive_path = property(_archive_path)
    hr_name = property(_hr_name)
    salt = property(_get_salt)
    universe = property(_universe)
    
    
    def __unicode__(self):
        template = '<DataSet {pk}: name=\'{nm}\', query={qpk},'
        template += ' bundle_previsits={bpre}, bundle_postvisits={bpost},'
        template += ' started={st}, completed={cd},'
        template += ' dbo_name={dbo}>'
        
        if self.pk == None:
            pk = '[unsaved]'
        else:
            pk = self.pk
        
        return template.format(
            pk = pk,
            nm = self.name,
            qpk = self.query.pk,
            bpre = self.bundle_previsit_file,
            bpost = self.bundle_postvisit_file,
            st = self.start,
            cd = self.complete,
            dbo = self.dbo_name
        )
    
    def __repr__(self):
        return self.__unicode__()


class Query(models.Model):
    """Brings together a universe and a filtergroup. Can then generate
    (and store) an SQL statement
    """
    statement = models.TextField(default=None, blank=True, null=True,
                                 help_text='Generated from filtergroup')
    statement_last_update = models.DateTimeField(default=None, blank=True, null=True)
    explain = models.TextField(default=None, blank=True, null=True, 
                               help_text='Generated from statement')
    explain_last_update = models.DateTimeField(default=None, blank=True, null=True)
    universe = models.ForeignKey('Universe')
    columns = models.ManyToManyField(
        'Column',
        help_text="Columns in the Universe.data table to include in output. " + \
            "Columns from lookup tables will be ignored.")
    filtergroup = models.OneToOneField('FilterGroup', blank=False)
    #owner = # fk django user object
    
    
    def _linked_sql(self, previsits=True):
        """Generates a SQL statement for finding linked visits.
        
        Parameters
        =========================
        previsits: boolean, required (default: True)
            If True, generates SQL for linking previous visits. Otherwise,
            generates SQL for linking subsequent (re-) visits.
        """
        
        template = """
        SELECT {cols}
        FROM {data_tbl} AS linked_visits
        INNER JOIN
            (
            {orig_visits_sql}
            ) AS orig_visits
        ON
            orig_visits.visitlink = linked_visits.visitlink
            AND orig_visits.state = linked_visits.state
        WHERE
            orig_visits.key != linked_visits.key
            AND orig_visits.daystoevent - linked_visits.daystoevent {gtorlt} 0
        """
        
        linked_visits = alias(database.get_table(self.clause_from), name='linked_visits')
        orig_visits = alias(self.sql(identifiers_only=True), name='orig_visits')
        if previsits:
            # orig_dte > linked_dte implies we linked up PRE-visits
            gtorlt = '>'
        else:
            # orig_dte < linked_dte implies we linked up RE-visits
            gtorlt = '<'

        j = linked_visits.join(orig_visits, orig_visits.c.visitlink == linked_visits.c.visitlink and
                orig_visits.c.state == linked_visits.c.state)
        q = select(self.clause_select(parent_dbo=self.clause_from)) \
            .select_from(j) \
            .where(orig_visits.c.key != linked_visits.c.key) \
            .where((orig_visits.c.daystoevent - linked_visits.c.daystoevent).op(gtorlt)(0))
            
        return q
    
    def _get_colset(self):
        # use the specified columns via m2m manager
        column_set = self.columns.all()
        if len(column_set) == 0:
            # if none of those, use the whole universe.
            # this should be an extraordinarily rare occurence,
            # mainly found with legacy Query objects prior
            # to "select fields" paradigm.
            column_set = self.universe.data.column_set.all()
        
        return column_set

    def clause_select(self, parent_dbo=None, col_lst=None):
        if col_lst is None:
            col_lst = [c.name.lower() for c in self._get_colset()]
        if parent_dbo:
            return [database.get_table(parent_dbo).c[c] for c in col_lst]
        else:
            return [database.get_table(self.clause_from).c[c] for c in col_lst]
    
    @property
    def clause_from(self):
        # NOTE: this may be extended in the future for multi-table support
        return self.universe.data.dbo_name
    
    @property
    def clause_where(self):
        return self.filtergroup.sql
    
    def sql(self, update_statement=True, use_fqdbo=False, identifiers_only=False):
        # set general template

        template = """
        SELECT {fields}
        FROM {table}
        """
        
        if identifiers_only:
            col_lst = ['key', 'visitlink', 'state', 'daystoevent']
            cols = [database.get_table(self.clause_from).c[c] for c in col_lst]
        else:
            cols = self.clause_select()

        query = select(cols).where(self.clause_where)
        
        # update, if requested
        if update_statement:
            self.statement = database.compile_pg(query)
            self.statement_last_update = datetime.datetime.utcnow().replace(tzinfo=utc)
            self.save()
        
        return query
    
    def __unicode__(self):
        template = '<Query {pk}: universe={u}, valid_select={vs},'
        template += ' valid_from={vf}, valid_where={vw}>'
        
        if self.pk == None:
            pk = '[unsaved]'
        else:
            pk = self.pk
            
        if len(self.universe.name) > 0:
            u = self.universe.name
        else:
            u = self.universe.pk
        
        return template.format(
            pk = pk,
            u = u,
            vs = self.clause_select() is not None,
            vf = self.clause_from is not None,
            vw = self.clause_where is not None
        )
    
    def __repr__(self):
        return self.__unicode__()
    

class FilterGroup(models.Model):
    any = models.BooleanField(default=False)
    # default False, e.g. join the related filters with an OR
    parent = models.ForeignKey('self', default=None, null=True,
                               blank=True)
    # may be None; start with FilterGroup(parent=None)
    
    @property	
    def filters(self):
        children = [x for x in FilterGroup.objects.filter(parent=self)
                    if x.filter_set.count() > 0]
        members = [x for x in self.filter_set.all()]
        return children + members
    
    @property
    def sql(self):
        members = [f.sql for f in self.filters]
        if not len(members):
            return None
        if self.any:
            f = or_
        else:
            f = and_
        return f(*members)
    
    @property
    def tables(self):
        tables = []
        t_lst = []
        for f in self.filters:
            if isinstance(f, Filter):
                try:
                    t_lst.append(f.tbl_dbo)
                except:
                    pass
            else: # ought to be FilterGroup
                try:
                    t_lst.extend(f.tables)
                except:
                    pass
        for t in t_lst:
            if t not in tables:
                tables.append(t)
        return tables
    
    # TODO:
    # If parent == None, need to round up all the required
    # table names, plus format this stuff properly within a
    # SELECT * FROM the_big_table WHERE ({filter_sql}) stmt
    
    def __unicode__(self):
        return "<FilterGroup {pk}>".format(pk=self.pk)


class Filter(models.Model):
    filtergroup = models.ForeignKey('FilterGroup')
    column = models.ForeignKey('Column', blank=False)
    value = models.TextField(blank=False)
    # comparison value e.g. column operator [not] value
        
    operator = models.CharField(
        max_length=6, choices=FILTER_OPERATOR_CHOICES,
        default='==', blank=False
    )
    
    def operator_is_valid(self):
        return self.operator in [x[0] for x in FILTER_OPERATOR_CHOICES]
    
    def operator_is_list_type(self):
        if self.operator in set(['IN', 'NOT IN']):
            return True
        else:
            return False
    
    @property
    def tbl_dbo(self):
        try:
            return self.column.table.dbo_name
        except:
            return None
    
    @property
    def sql(self):
        # noun verb noun
        # column operator value
        
        if self.value is None:
            return None
        else:
            o = self.operator
            v = self.value
            if not self.operator_is_valid():
                raise Exception("Cannot build sql clause without valid operator. (got '%s')" % self.operator)
            
            q = None
            t = database.get_table(self.column.table.dbo_name)
            col = t.c[self.column.name.lower()]
            if self.operator_is_list_type():
                q = col.in_(str(x).strip() for x in self.value.split(','))
                if self.operator == 'NOT IN':
                    q = ~q
            else:
                q = col.op(o)(v)


            if self.column.is_lookup:
                # template takes the form of a subquery, returning KEY values only
                sq = select([column('key')]).select_from(database.get_table(self.column.table.dbo_name)) \
                    .where(q)
                q = column('key').in_(sq)

        return q
    
    
    def __unicode__(self):
        template = '<Filter: {c} {o} {v}, in FilterGroup {fg}>'
        return template.format(
            c = self.column.fqdbo,
            o = self.operator,
            v = self.value,
            fg = self.filtergroup.pk
        )
    
    def __repr__(self):
        return self.__unicode__()


class Definition(models.Model):
    name = models.CharField(max_length=200, blank=False)
    description = models.TextField(blank=True, null=True, default=None)
    data = models.ForeignKey(
        IntegrationDefinition,
        related_name = 'data',
        help_text = 'Integration module Definition which should be used as a data table in a reporting universe.'
    )
    lookups = models.ManyToManyField(
        IntegrationDefinition,
        related_name = 'lookups',
        help_text = 'Integration module Definitions to be used as lookup tables in a reporting universe.',
        through = 'DefLookups'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    void = models.BooleanField(default=False)
    void_at = models.DateTimeField(blank=True, default=None, null=True)
    
    
    def refresh_universe(self, name, description=None):
        """
        Returns djhcup_reporting.models.Universe object if a newer Edition
        is available for all the inputs in this Definition.
        
        Returns False if no newer Edition exists with all the required inputs.
        
        Parameters
        ===============
        name: string (required)
            Name for the newly-created Universe object.
        
        decription: string (optional)
            Description for the newly-created Universe object.
        """
        # TODO: Add a name template for ReportingTable objects
        # this is where latest edition with all elements should be found
        # and a new universe should be made.
        
        e_qs = IntegrationEdition.objects.filter(
            void=False,
        ).order_by(
            '-created_at'
        )
        print "e_qs prior to filtering for timestamp greater than universes is %s" % e_qs
        
        def_u_qs = Universe.objects.filter(definition=self)
        #print "def_u_qs is %s" % def_u_qs
        
        if len(def_u_qs) > 0:
            # make sure the editions we're choosing from are
            # more recent than the current most recent universe
            e_qs = e_qs.filter(created_at__gt=def_u_qs[0].created_at)
            print "e_qs after filtering for timestamp greater than universes is %s" % e_qs
        
        if len(e_qs) == 0:
            logger.debug('No e_qs members after filtering for timestamp greater than universes')
            return False
        
        # need not indent here; will have exited already from the return call
        u = None
        for e in e_qs:
            # cycle through these Edition objects in descending order
            # by creation timestamp.
            
            if u == None:
                # proceed
                # u will be overwritten if something is found
                data_int_tables = IntegrationTable.objects.filter(
                    definition=self.data,
                    void=False,
                    wip=False,
                    edition=e
                )
                print "data_int_tables is %s" % data_int_tables
                logger.debug("Found {ct} IntegrationTable objects for " +\
                        "definition {d}, edition {e}".format(
                            ct=len(data_int_tables), d=self.data, e=e
                        )
                )
                
                if len(data_int_tables) > 0:
                    # set this aside for Universe later
                    data_int_tbl = data_int_tables[0]
                    
                    # proceed to looking for lookup tables
                    lu_table_lst = []
                    lu_defs = self.deflookups_set.all()
                    
                    for def_lu in lu_defs:
                        #LookupTable
                        print "looking for IntegrationTable objects with definition %s" % def_lu.int_definition
                        lu_tables = IntegrationTable.objects.filter(
                            definition=def_lu.int_definition,
                            void=False,
                        ).order_by(
                            '-created_at'
                        )
                        
                        # have at least one lookup table matching these criteria
                        # just use the first
                        if len(lu_tables) > 0:
                            lu_table_lst.append(dict(
                                int_definition=def_lu.int_definition,
                                table=lu_tables[0],
                                lu_type=def_lu.lu_type
                            ))
                    
                    # make col objects for ReportingTable
                    if len(lu_defs) == len(lu_table_lst):
                        # got all the required ones (hootie hooooo!)
                        print "found all required lookup tables"
                        name_template = "Reporting Definition {d}, Edition {e}"
                        
                        # make a ReportingTable obj for data
                        data_tbl = ReportingTable(
                            via=data_int_tbl,
                            name=name_template.format(d=self.data.pk, e=e)
                        )
                        data_tbl.save()
                        
                        # make col objects for ReportingTable
                        for icol in self.data.columns.all():
                            try:
                                meta = RPT_COLUMN_META[str(icol.name).lower()]
                            except:
                                meta = dict()
                            dcol = Column(
                                table=data_tbl,
                                int_column=icol,
                                **meta
                            )
                            dcol.save()
                        
                        # proceed to make Universe and populate it
                        # (have to do this before lookups, as m2m
                        # require a key on each table to create)
                        u = Universe(
                            definition=self,
                            name=name,
                            description=description,
                            edition=e,
                            data=data_tbl
                        )
                        u.save()
                        
                        for lu in lu_table_lst:
                            # bake the lookups back in, via intermediate table
                            r_tbl = ReportingTable(
                                is_lookup=True,
                                via=lu['table'],
                                name=name_template.format(d=self.data.pk, e=e)
                            )
                            r_tbl.save()
                            
                            # make col objects for ReportingTable
                            for icol in lu['int_definition'].columns.all():
                                try:
                                    meta = RPT_COLUMN_META[str(icol.name).lower()]
                                except:
                                    meta = dict()
                                dcol = Column(
                                    table=r_tbl,
                                    int_column=icol,
                                    **meta
                                )
                                dcol.save()
                            
                            lu_tbl = LookupTable(
                                universe=u,
                                table=r_tbl,
                                lu_type=lu['lu_type']
                            )
                            lu_tbl.save()
                        
                        u.wip = False
                        u.save()
        return u        


    def __unicode__(self):
        return '<Reporting Definition {pk}: {name}>' \
            .format(pk=self.pk, name=self.name)

        
    def __repr__(self):
        return self.__unicode__()


class DefLookups(models.Model):
    """The lookup table part of a definition for universe generation.
    """
    definition = models.ForeignKey('Definition')
    int_definition = models.ForeignKey(IntegrationDefinition)
    lu_type = models.CharField(
        max_length = 10,
        choices = [
            ('DX', 'Diagnoses (long format)'),
            ('PR', 'Procedures (long format)'),
            ('UFLAGS', 'Utilization flags (long format)'),
            ('CHGS', 'Charges (long format)'),
        ],
        blank = False
    )
    created_at = models.DateTimeField(auto_now_add=True)
    void = models.BooleanField(default=False)
    void_at = models.DateTimeField(blank=True, default=None, null=True)
    
    def __unicode__(self):
        return "<DefLookups {pk}: reporting definition={d}, integration definition={i}>" \
            .format(pk=self.pk, d=self.definition.pk, i=self.int_definition.pk)


class Universe(models.Model):
    definition = models.ForeignKey('Definition')
    name = models.CharField(max_length=200, blank=False)
    description = models.TextField(blank=True, null=True, default=None)
    edition = models.ForeignKey(IntegrationEdition)
    data = models.ForeignKey(
        'ReportingTable',
        related_name = 'data',
        help_text = 'ReportingTable with actual reporting data (ie, CORE PROCESSED integration)'
    )
    lookups = models.ManyToManyField(
        'ReportingTable',
        related_name = 'lookups',
        help_text = "Connects ReportingTable objects to use as lookup tables",
        through = 'LookupTable',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    wip = models.BooleanField(default=True)
    void = models.BooleanField(default=False)
    void_at = models.DateTimeField(blank=True, default=None,
                                   null=True)
    
    def _describe(self):
        lines = []
        title = "Reporting Universe: "
        if self.name and len(self.name) > 0:
            title += self.name + " (#%s)" % self.pk
        else:
            title += "#%s" % self.pk
        lines.append(title)
        
        if self.description and len(self.description) > 0:
            lines.append(self.description)
        
        e_title = "Table integration Edition: "
        e = self.edition
        if e.name and len(e.name) > 0:
            e_title += e.name + " (#%s)" % e.pk
        else:
            e_title += "#%s" % e.pk
        lines.append(e_title)
        
        lines.append("Edition timestamp: %s" % e.created_at)
        
        lines.append("\n")
        lines.append("StagingTables integrated to generate reporting Universe data:")
        for t in self.data.via.stagingtables.all().order_by('name'):
            lines.append("  StagingTable %s: %s" % (t.pk, t.name))
        
        return lines
    
    
    def filters_for_display(self):
        filters = []
        
        # gather cols for lookup tables
        lookup_tables = self.lookuptable_set.all()
        for lu in lookup_tables:
            t = lu.table
            for c in t.column_set.filter(is_filter_option=True).order_by('int_column__field_out__value'):
                f = {'group': "Lookup Table: " + lu.get_lu_type_display()}
                f['name'] = c.name
                f['value'] = c.pk
                f['display'] = c.filter_display
                f['help_url'] = c.help_url
                filters.append(f)
        
        # gather cols from the "data" table in this definition
        try:
            t = self.data
        except:
            raise Exception("Unable to find a data table from Universe {pk} for determining filters".format(pk=self.pk))
        
        for c in t.column_set.filter(is_filter_option=True).order_by('int_column__field_out__value'):
            f = {'group': 'Data Fields'}
            f['name'] = c.name
            f['value'] = c.pk
            f['display'] = c.filter_display
            f['help_url'] = c.help_url
            filters.append(f)

        return filters
    
    
    def _hr_name(self):
        try:
            if self.name and len(self.name) > 0:
                return "%s (Universe #%s)" % (self.name, self.pk)
            else:
                return "Universe #%s" % self.pk
        except:
            return self.__unicode__()
    hr_name = property(_hr_name)
    
    def get_absolute_url(self):
        return reverse(
            'universe_details',
            kwargs={'universe_pk': self.pk}
        )
    
    def __unicode__(self):
        try:
            d = self.data.dbo_name
        except:
            d = None
        template = '<Universe {pk}: {n}, data={d} with {l_ct} lookups>'
        return template.format(pk=self.pk, n=self.name, d=d, l_ct=self.lookups.all().count())
    
    def __repr__(self):
        return self.__unicode__()


class LookupTable(models.Model):
    universe = models.ForeignKey('Universe') # fk Universe
    table = models.ForeignKey('ReportingTable') # fk ReportingTable
    lu_type = models.CharField(
        max_length = 10,
        choices = [
            ('DX', 'Diagnoses (long format)'),
            ('PR', 'Procedures (long format)'),
            ('UFLAGS', 'Utilization flags (long format)'),
            ('CHGS', 'Charges (long format)'),
        ],
        blank = False
    )
    created_at = models.DateTimeField(auto_now_add=True)
    void = models.BooleanField(default=False)
    void_at = models.DateTimeField(blank=True, default=None, null=True)
    
    def __unicode__(self):
        template = '<LookupTable {pk}: {lu} ({dbo})>'
        return template.format(pk=self.pk, lu=self.get_lu_type_display(), dbo=self.table.dbo_name)
    
    def __repr__(self):
        return self.__unicode__()


class ReportingTable(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True, default=None)
    description = models.TextField(blank=True, null=True, default=None)
    is_lookup = models.BooleanField(default=False)
    via = models.ForeignKey(IntegrationTable)
    created_at = models.DateTimeField(auto_now_add=True)
    void = models.BooleanField(default=False)
    void_at = models.DateTimeField(blank=True, default=None, null=True)
    
    columns = models.ManyToManyField(IntegrationColumn, through='Column')
    
    def _dbo_name(self): # database object name
        try:
            return self.via.name
        except:
            return None
    dbo_name = property(_dbo_name)
    
    def __unicode__(self):
        template = '<ReportingTable {pk}: {t} ({dbo})>'
        return template.format(pk=self.pk, t=self.name, dbo=self.dbo_name)
    
    def __repr__(self):
        return self.__unicode__()


class Column(models.Model):
    table = models.ForeignKey('ReportingTable', blank=False, null=True)
    int_column = models.ForeignKey(IntegrationColumn, blank=False, null=True)
    label = models.CharField(max_length=200, blank=True, null=True, default=None,
                             help_text="Human-readable label for this column")
    description = models.TextField(blank=True, null=True, default=None,
                                   help_text="Verbose description")
    category = models.CharField(max_length=200, blank=True, null=True, default=None,
                                choices=COL_CATGORY_CHOICES,
                                help_text="Category for grouping during filtering")
    extract_by_default = models.BooleanField(
        default=False,
        help_text="If in a Universe.data table, include by default in datasets."
    )
    is_filter_option = models.BooleanField(
        default=False,
        help_text="This field can be used as a filter in the DataSet builder"
    )
    #distinct_values # m2m Value, cached here for reference
    # need a method to return fully qualified name
    # also need to build filterset stuff so that it has
    # a reference to each required table (via JOIN?).
    # there's probably a way to get a queryset that pulls a distinct list of
    # tables involved here
    
    @property
    def filter_display(self):
        display = ''
        if self.name and len(self.name) > 0:
            display += self.name
            if self.label and len(self.label) > 0:
                display += ': '
            
        if self.label and len(self.label) > 0:
            display += self.label
        
        return display
    
    @property
    def help_url(self):
        excluded = (
            'ZIP',
            'PAY',
            'DISPUB',
        )
        if self.name.startswith(excluded):
            slug = self.name.lower()
        else:
            slug = re.sub(r'[0-9]+$', 'n', self.name).lower()
        return "http://www.hcup-us.ahrq.gov/db/vars/%s/nisnote.jsp" % (slug)

    def _name(self):
        try:
            return self.int_column.field_out.value
        except:
            return None
    name = property(_name)
    
    def _hr_name(self):
        if self.label and len(self.label) > 0:
            return self.label
        else:
            return self.name
    hr_name = property(_hr_name)
    
    def _is_lookup(self):
        """Returns True if column is from a lookup table.
        Otherwise, returns False.
        """
        try:
            if self.table.is_lookup == True:
                return True
            else:
                return False
        except:
            logger.warning("Caught an Exception while calling" +\
                "_is_lookup() on Column {pk}".format(pk=pk))
            return False
    is_lookup = property(_is_lookup)
    
    def _fqdbo(self):
        """Returns fully-qualified database object (column name with
        dot-notated table).
        """
        return '{t}.{c}'.format(c=self.name, t=self.table.dbo_name)
    fqdbo = property(_fqdbo)
    
    def __unicode__(self):
        template = '<Reporting Column: {fqdbo}>'
        return template.format(fqdbo=self.fqdbo)
    
    def __repr__(self):
        return self.__unicode__()
