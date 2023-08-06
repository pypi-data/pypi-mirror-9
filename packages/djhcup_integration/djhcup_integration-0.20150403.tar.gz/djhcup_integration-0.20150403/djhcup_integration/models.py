import psycopg2
import logging
import pyhcup

from django.conf import settings
from django.db import models


from djhcup_staging.models import StagingTable, DataSource


# pull these into local ns for psycopg2/dbapi2 objects
DB_DEF = settings.DATABASES['djhcup']

# start a logger
default_logger = logging.getLogger('default')


class Edition(models.Model):
    name = models.CharField(max_length=250, blank=False)
    description = models.TextField(blank=True, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    void = models.BooleanField(default=False)
    voided_at = models.DateTimeField(blank=True, null=True, default=None)
    
    def __unicode__(self):
        return "<Edition {pk}>".format(pk=self.pk)
    
    def __repr__(self):
        return self.__unicode__()


class IntegrationTable(models.Model):
    """This is a record of integration tables created/populated.
    
    stagingtables should share category and data_source
    
    IntegrationTables should always have state and year fields.
    """
    stagingtables = models.ManyToManyField(
        StagingTable,
        help_text="StagingTable objects comprising this IntegrationTable",
        through = 'IntTblStgTblMembers'
        )
    name = models.CharField(max_length=250, blank=False)
    description = models.TextField(blank=True, null=True, default=None)
    edition = models.ForeignKey('Edition')
    definition = models.ForeignKey('Definition', blank=True, null=True)
    schema = models.CharField(max_length=250, blank=True)
    database = models.CharField(max_length=250, blank=True, help_text="Leave blank to use default connection specified in Django's setings.py file")
    wip = models.BooleanField(
        default=True,
        help_text="This table is work-in-progress, and should not be used."
    )
    
    #meta cruft
    created_at = models.DateTimeField(auto_now_add=True)
    void = models.BooleanField(default=False)
    voided_at = models.DateTimeField(blank=True, null=True, default=None)
    records = models.IntegerField(blank=True, null=True, default=None)
    
    # overwrite to drop associated table by default when deleting
    def delete(self, drop_table=True, *args, **kwargs):
        if drop_table:
            cnxn = psycopg2.connect(
                host=DB_DEF['HOST'],
                port=DB_DEF['PORT'],
                user=DB_DEF['USER'],
                password=DB_DEF['PASSWORD'],
                database=DB_DEF['NAME'],
            )
            drop_result = pyhcup.db.pg_drop(cnxn, self.name)
            if drop_result == True:
                default_logger.info('Dropped table {table} from database'.format(table=self.name))
            else:
                default_logger.error('Unable to drop table {table} from database'.format(table=self.name))
        
        super(IntegrationTable, self).delete(*args, **kwargs)
    
    
    def __unicode__(self):
        try:
            d = self.definition.pk
        except:
            d = None
        
        try:
            e = self.edition.pk
        except:
            e = None
        
        return "<IntegrationTable {pk}: {n}, definition={d} edition={e}>".format(pk=self.pk, n=self.name, d=d, e=e)
    
    def __repr__(self):
        return self.__unicode__()
    
    """
    def get_absolute_url(self):
        return reverse(
            'djhcup_integration.views.obj_detail',
            kwargs={'obj_id': self.pk, 'obj_type': 'IntegrationTable'}
        )
    """


class Definition(models.Model):
    """
    Groups a set of integration Column objects. More or less.
    
    Subsequently used to create an IntegrationTable.
    """
    
    data_source = models.ForeignKey(
        DataSource,
        verbose_name="DataSource Family",
        help_text="""
            DataSource object from djhcup_staging. Restricts integration to tables
            with this DataSource as parent to their own; e.g., HCUP SID.
            """,
        blank=True, # this is optional,
        null=True
    )
    TBL_CAT_CHOICES = [
        ('CHARGES','Charges data in long format (converted from wide source if necessary)'),
        ('DX','Diagnoses data in long format (from CORE_SOURCE)'),
        ('PR','Procedures data in long format (from CORE_SOURCE)'),
        ('UFLAGS','Utilization flag data, long format (from CORE_SOURCE, CHARGES, and PR)'),
        ('CORE_PROCESSED','CORE Processed: CORE, DaysToEvent/VisitLink, wide charges, wide uflags'),
    ]
    
    category = models.CharField(
        max_length=100,
        choices=TBL_CAT_CHOICES,
        blank=False
    )
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    columns = models.ManyToManyField('Column')
    # record index columns here? as extra info on M2M?
    
    def __unicode__(self):
        return '<Integration Definition: {n} ({c})>' \
            .format(n=self.name, c=self.category)
    
    def __repr__(self):
        return self.__unicode__()


class IntTblStgTblMembers(models.Model):
    integrationtable = models.ForeignKey('IntegrationTable')
    stagingtable = models.ForeignKey(StagingTable)
    mappedcols = models.ManyToManyField('Column', through='MappedColumn')
    unmappedcols = models.ManyToManyField('Column', related_name='unmappedcols')
    
    def __unicode__(self):
        return '<IntTblStgTblMember: StgTbl {s} in IntTbl {i}>' \
            .format(s=self.stagingtable.pk, i=self.integrationtable.pk)
    
    def __repr__(self):
        return self.__unicode__()


class MappedColumn(models.Model):
    inttblstgtblmembers = models.ForeignKey('IntTblStgTblMembers')
    column = models.ForeignKey('Column')
    matched_in = models.ForeignKey('ColumnName')


class Column(models.Model):
    """
    Defines a single ColumnName object which will be the surviving column in
    the database table (field_out), and one or more ColumnName objects whose
    contents are all eligible for inclusion (fields_in).
    
    Personally I believe this would be better if fields_in actually referred
    to djhcup_staging.models.Column objects, but then I'd need another layer
    that establishes the list of column names which qualify for inclusion.
    Reason being that staging columns are not propagated as part of table
    processing--they exist only as part of import loading.
    
    Might still be good to do at a future date but right now is kind of a
    hassle.
    """
    fields_in = models.ManyToManyField('ColumnName', related_name='fields_in')
    field_out = models.ForeignKey('ColumnName', related_name='field_out')
    TYPE_CHOICES = [
            ('INT', 'Integer'),
            ('BIGINT', 'Very Large Integer'),
            ('TEXT', 'Text field'),
            ('VARCHAR', 'Character varying'),
            ('NUMERIC(2, 15)', 'Decimal, out to hundredths'),
        ]
    field_out_data_type = models.CharField(max_length=15, choices=TYPE_CHOICES, default='VARCHAR')
    field_out_scale = models.IntegerField(blank=True, null=True, default=None)
    field_out_precision = models.IntegerField(blank=True, null=True, default=None)
    
    def _is_numeric(self):
        lower_type = self.field_out_data_type.lower()
        if (lower_type in ['int', 'bigint'] or
            'numeric' in lower_type):
            return True
        else:
            return False
    
    def _name(self):
        return self.field_out.value
    name = property(_name)
    
    def __unicode__(self):
        return '<Integration Column: {i} to {o} ({pk})>' \
            .format(i=[str(x.value) for x in self.fields_in.all()],
                    o=self.field_out.value, pk=self.pk)


class ColumnName(models.Model):
    value = models.CharField(max_length=150, blank=False)
    
    def __unicode__(self):
        return 'ColumnName: {v}'.format(v=self.value)
