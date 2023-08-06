# core Python packages
import datetime
import itertools
import logging
import os



# third party packages
import pyhcup


# django packages
from django.utils.timezone import utc
from django.conf import settings
#import shortcuts to use with raw sql (!) later
from django.core.exceptions import ObjectDoesNotExist


# local project and app packages
from djhcup_integration.models import Edition, Definition, Column, ColumnName, IntegrationTable, IntTblStgTblMembers, MappedColumn


# sister app stuff
from djhcup_staging.models import StagingTable
from djhcup_staging.utils.misc import get_pgcnxn


# start a logger
logger = logging.getLogger('default')


# make these tasks app-agnostic with @celery.shared_task
import celery
from celery.result import AsyncResult

@celery.shared_task
def generate_tables(e_pk, d_pk_lst):
    """
    This is the task to call for creating a new set of IntegrationTable
    objects and their corresponding database tables.
    
    Parameters:
    e_pk: integer (required)
    Primary key for integration Edition model object.
    
    Create a new Edition object and pass its primary key as edition_pk.
    
    d_lst: list (required)
    List of primary keys for integration Definition model objects.
    
    In most cases, pass something equivalent to 
    [x.pk for x in Definition.objects.all()]
    """
    integrations = celery.group(integrate_tables.s(d_pk, e_pk) for d_pk in d_pk_lst)
    """
    EDITION_CATS = [
        # a list of categories to include in each edition of an integration table set
        dict(val='CORE_PROCESSED', long_entry=None, ds_abbr='CORE'),
        dict(val='DX', long_entry='DX'),
        dict(val='PR', long_entry='PR'),
        dict(val='CHARGES', long_entry='CHGS'),
        dict(val='UFLAGS', long_entry='UFLAGS'),
    ]
    
    # for each category of data
        # grab StagingTables with that category
        # for each unique DataSource
            # filter StagingTables down to those matching DataSource (within category)
            
    # need to somehow deal with extra columns--might just have to define integration/reporting field sets or something
    create_sql = pyhcup.db.long_table_sql(db_table, str(source.abbreviation))
    index_fields = ['KEY', 'VISITLINK', 'STATE', 'YEAR']
    """
    return integrations()



@celery.shared_task
def integrate_stg_table(stgtbl_in_pk, int_tbl_pk, def_pk, dry_run=False):
    """
    Integrates StagingTable object with pk stgtbl_in_pk
    into IntegrationTable with pk int_tbl_pk
    according to Definition with pk def_pk.
    
    If dry_run == True, no changes will be made to the database.
    """
    
    # initiate a connection
    cnxn = get_pgcnxn()
    
    # find corresponding objects
    try:
        sttbl = StagingTable.objects.get(pk=stgtbl_in_pk)
        int_tbl = IntegrationTable.objects.get(pk=int_tbl_pk)
        d = Definition.objects.get(pk=def_pk)
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist("Unable to find one of StagingTable {s}, IntegrationTable {i}, or Definition {d}" \
            .format(s=stgtbl_in_pk, i=int_tbl_pk, d=def_pk))
    
    # isolate state and year
    state = sttbl.state
    year = sttbl.year
    
    # create a new integration member, which holds staging tables pushed into int table
    if not dry_run:
        int_member = IntTblStgTblMembers(
            integrationtable = int_tbl,
            stagingtable = sttbl,
        )
        int_member.save()
    
    # instantiate lists for fields in and out
    fields_in_lst = []
    fields_out_lst = []
    
    # grab columns present in staging table
    st_cols = [s.lower() for s in pyhcup.db.pg_getcols(cnxn, sttbl.name)]
    
    for c in st_cols:
        matches = d.columns.filter(fields_in__value__iexact=c)
        if len(matches) == 1:
            matched_col = matches[0]
            matched_cn = ColumnName.objects.filter(fields_in=matched_col, value__iexact=c)[0]
            
            if not dry_run:
                mapped_col = MappedColumn(
                    inttblstgtblmembers=int_member,
                    column=matched_col,
                    matched_in=matched_cn)
                mapped_col.save()
            
            fields_in_lst.append(c)
            fields_out_lst.append(matched_cn.value)
        else:
            logger.debug(
                "Unable to resolve {sttbl}.{c}; skipping".format(
                    sttbl=sttbl.name,
                    c=c
                )
            )
    
    # shovel the resolved columns from source to integration table
    if not dry_run:
        shoveled = pyhcup.db.pg_shovel(cnxn, tbl_source=sttbl.name,
                                       tbl_destination=int_tbl.name,
                                       fields_in=fields_in_lst,
                                       fields_out=fields_out_lst)
        int_tbl.wip = False
        int_tbl.save()
    else:
        shoveled = 0
    
    logger.info("Shoveled {ct} rows from StagingTable {st_pk} ({tbl})" \
        .format(ct=shoveled, st_pk=sttbl.pk, tbl=sttbl.name)
    )
    
    logger.debug(
        "TABLE: {tbl}\nROWS: {rows}\nFIELDS IN: {fields_in}\nFIELDS OUT: {fields_out}" \
            .format(
                tbl=sttbl,
                rows=shoveled,
                fields_in=fields_in_lst,
                fields_out=fields_out_lst
            )
    )
    
    return dict(
        state=state,
        year=year,
        shoveled=shoveled,
        StagingTable=sttbl,
        fields_in=fields_in_lst,
        fields_out=fields_out_lst
    )


@celery.shared_task
def integrate_tables(definition_pk, edition_pk, indexes=['key', 'state', 'year', 'visitlink']):
    """
    Creates a new table integration using provided definition and edition.
    
    Dispatches individual table imports in parallel.
    
    TODO: Consider how much, if any, of these things should be preserved
    as provenance somewhere, somehow. Is description field appropriate?
    Alternatively, maybe a logging filter could be used, or an
    additional handler, that sends certain provenance items away for
    safekeeping.
    """
    logger.debug("integrate_tables() called with definition_pk {d} and edition_pk {e}" \
        .format(d=definition_pk, e=edition_pk)
    )
    
    try:
        # grab the definition for which we'll make an integration table
        d = Definition.objects.get(pk=definition_pk)
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist("Function integrate_tables() was unable to find Definition with primary key %s" % definition_pk)
    
    try:
        e = Edition.objects.get(pk=edition_pk)
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist("Function integrate_tables() was unable to find Edition with primary key %s" % edition_pk)
    
    cnxn = get_pgcnxn()

    # use the Edition timestamp for table names and the like down the line
    now = e.created_at.strftime("%Y%m%d%H%M%S")
    
    # get the integration Columns we'll shop for among StagingTables
    def_cols = Column.objects.filter(definition=d)
    logger.debug("Columns in Definition: %s" % ', '.join([str(x) for x in def_cols]))
    
    # create the empty table
    tbl_clauses = []
    for dcol in d.columns.all():
        # construct a clause representing this column, based on its name and data type
        clause = "{f} {type}".format(f=dcol.field_out.value, type=dcol.field_out_data_type)
        
        # only append the clause if it doesn't already exist in the clauses list
        # (avoids duplicates)
        if clause not in tbl_clauses:
            tbl_clauses.append(clause)
    
    int_tbl_name = 'int_{ds_parent}_{cat}_{now}'.format(
        ds_parent=d.data_source.mr_descriptor,
        cat=d.category,
        now=now,
    )
    logger.info("Creating new database table {tbl} for table integration" \
        .format(tbl=int_tbl_name))
    create = "CREATE TABLE {tbl} ({clauses});" \
        .format(tbl=int_tbl_name, clauses=", ".join(tbl_clauses))
    cursor = cnxn.cursor()
    cursor.execute(create)
    cnxn.commit()
    logger.info("Created new database table {tbl}" \
        .format(tbl=int_tbl_name))
    
    logger.info("Creating new IntegrationTable object for table {tbl}" \
        .format(tbl=int_tbl_name))
    # create a new IntegrationTable to hold results and meta
    int_tbl = IntegrationTable(
        name=int_tbl_name,
        definition=d,
        edition=e
    )
    int_tbl.save()
    logger.info("Created new IntegrationTable object for table {tbl}" \
        .format(tbl=int_tbl_name))
    
    logger.info("Checking for indexes to add to table {tbl}" \
        .format(tbl=int_tbl_name))
    for i in indexes:
        logger.info("Attempting to create index on column {i} in table {tbl}" \
            .format(i=i, tbl=int_tbl_name))
        try:
            #print "i is {i}".format(i=i)
            #print "int_tbl_name is {int_tbl_name}".format(int_tbl_name=int_tbl_name)
            i_sql = pyhcup.db.index_sql(i, int_tbl_name)
            #print i_sql
            cursor.execute(i_sql)
            cnxn.commit()
            logger.info("Created index on column {i} in table {tbl}" \
                .format(i=i, tbl=int_tbl_name))
        except:
            logger.warning("Failed to create index on column {i} in table {tbl}" \
                .format(i=i, tbl=int_tbl_name))
            cnxn.rollback()
    
    # get StagingTables to be included in this integration
    # according to category indicated by Definition
    stgtbls = StagingTable.objects \
                .filter(category=d.category, wip=False, void=False) \
                .order_by('-created_at') # most recent first
    
    # extra filter step to make sure these are all in the same family.
    # this cannot be combined with above since this is a property,
    # rather than a model column
    stgtbls = filter(
        lambda x: x.data_source.parent == d.data_source,
        stgtbls
    )
    
    integrated_sy = []
    shoveled_lst = []
    for sttbl in stgtbls:
        # put a check in here to make sure
        # we do not double-add.
        state = sttbl.state
        year = sttbl.year
        sy = dict(state=state, year=year)
        if sy in integrated_sy:
            # do not proceed
            logger.info("StagingTable {st_pk} ({tbl}) will be omitted, as {st} {yr} have already been dispatched for integration" \
                .format(st_pk=sttbl.pk, st=state, yr=year, tbl=sttbl.name)
            )
        else:
            logger.info("Integrating StagingTable {st_pk} ({tbl})" \
                .format(st_pk=sttbl.pk, tbl=sttbl.name)
            )
            integrated_sy.append(sy)
            dispatched = integrate_stg_table.delay(sttbl.pk, int_tbl.pk, d.pk)
            shoveled_lst.append(dispatched)
    
    callback = integration_complete.delay(shoveled_lst, int_tbl.pk)
    
    return int_tbl


@celery.shared_task(bind=True, max_retries=None, default_retry_delay=900)
def integration_complete(self, shoveled_lst, int_tbl_pk):
    
    int_tbl = IntegrationTable.objects.get(pk=int_tbl_pk)
    d = int_tbl.definition
    
    try:
        # test if all completed, one way or another
        if all(s.ready() for s in shoveled_lst):
            
            # test if the outcomes were all SUCCESS
            if all(s.successful() for s in shoveled_lst):
                
                # log a summary about the entire enterprise
                total_shoveled = sum([x.result['shoveled'] if 'shoveled' in x.result else 0 for x in shoveled_lst])
                logger.info("Integrated a total of {total} rows from {ct} tables" \
                    .format(total=total_shoveled, ct=len(shoveled_lst))
                )
                
                # record some details in the integration table description
                int_tbl.description = 'Integration of {ds} {category} as of {now}\n\nDIGEST\n##########\n\n' \
                    .format(ds=d.data_source, category=d.category, now=datetime.datetime.utcnow().replace(tzinfo=utc))
                int_tbl.description += '\n\n'.join([
                    "State: {st}\nYear: {yr}\nTable in: {tbl}\nRows moved: {rows}\nFields in: {fields_in}\nFields out: {fields_out}" \
                        .format(
                            st=x.result['state'],
                            yr=x.result['year'],
                            tbl=str(x.result['StagingTable']),
                            rows=x.result['shoveled'],
                            fields_in=x.result['fields_in'],
                            fields_out=x.result['fields_out'],
                        )
                    for x in shoveled_lst
                ])
                int_tbl.wip = False
                int_tbl.save()
                return int_tbl
        else:
            # since some haven't completed yet, raise IncompleteStream and retry
            raise self.retry(exc=Exception('Integration not yet complete: %s' % int_tbl))
    
    except celery.exceptions.IncompleteStream as exc:
        # try again a little later, when the streams are more complete
        raise self.retry(exc=Exception('Integration not yet complete: %s' % int_tbl))
