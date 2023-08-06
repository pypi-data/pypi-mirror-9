# core Python packages
import datetime
import logging
import os
import sys
import psycopg2


# third party packages
import pandas as pd
import pyhcup


# django packages
from django.shortcuts import render
from django.http import HttpResponse
from django.utils.timezone import utc
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.db import connections as cnxns
from django.db import transaction as tx


# local project and app packages
from djhcup_integration.models import Edition, Definition, Column, ColumnName, IntegrationTable, IntTblStgTblMembers, MappedColumn


# sister app stuff
from djhcup_staging.models import DataSource, StagingTable, File
from djhcup_staging.utils.misc import dead_batches, get_pgcnxn


# start a logger
logger = logging.getLogger('default')


def master_table(ds_id, category, timestamp=None, extra=None):
    """
    Generates a master table for the DataSource corresponding to ds_id. Returns an IntegrationTable.
    
    Uses all known loadfiles for source and generates one master table.
    
    # deprecated; ran up against max 1600 column limit in PostgreSQL
    # (which is a lot, admittedly).
    # only still in here for historical reasons.
    """
    
    source = DataSource.objects.get(pk=ds_id)
    logger.info('Attempting to generate master table for %s' % source)
    
    cursor = cnxns[DJHCUP_DB_ENTRY].cursor()

    # need later for table creation, but want the value to be based on the start of the process
    if timestamp == None:
        timestamp = datetime.datetime.utcnow().replace(tzinfo=utc).strftime("%Y%m%d%H%M%S")
    
    db_table = "int_%s_%s_%s" % (source.mr_descriptor, category, timestamp)
    db_table = db_table.lower()
    pk_fields = []
    index_fields = []
    
    # check to see whether this source has a LONG_MAPS entry, which would indicate it ought to be a long table
    if source.abbreviation in pyhcup.parser.LONG_MAPS.keys():
        logger.warning("The indicated data source has an analog in pyhcup.parser.LONG_MAPS. Generation will proceed, but this may indicate an error.")
    
    src_loadfiles = File.objects.filter(
        file_type__content_type__in=['LOAD'],
        file_type__source=source
    )
    logger.info('Found %d loadfile records matching source' % len(src_loadfiles))
    
    meta_list = []
    excluded = []
    for lf in src_loadfiles:
        mdf = pyhcup.sas.meta_from_sas(lf.full_path)
        augmented = pyhcup.meta.augment(mdf)
        meta_list.append(augmented)
    
    merged_meta = pyhcup.meta.merge(meta_list)
    logger.info('Merged %d meta DataFrames successfully, with %d columns after de-duplication' % (len(meta_list), len(merged_meta)))
    
    constraints = ['NULL']
    pk_fields = ['year', 'state', 'key']
    index_fields += pk_fields
    
    create_sql = pyhcup.db.table_sql(
        merged_meta, db_table, pk_fields=pk_fields, ine=True,
        append_state=True, default_constraints=constraints
    )
        
    try:
        cursor.execute(create_sql)
        tx.commit(using=DJHCUP_DB_ENTRY)
    except:
        e = sys.exc_info()[0]
        raise Exception("Failed to create master table with query %s (%s)" % (create_sql, e))
    
    logger.info('Created master table %s with on database %s' % (db_table, DJHCUP_DB_ENTRY))
    
    if category in EXTRA_COLUMNS.keys():
        # clean out any columns that will be added back on
        # re-add them with proper definitions
        for c in EXTRA_COLUMNS[category]:
            dropif_sql = 'ALTER TABLE {t} DROP COLUMN IF EXISTS {c};' \
                .format(t=db_table, c=c['field'])
            add_sql = 'ALTER TABLE {t} ADD COLUMN {c} {coltype};' \
                .format(t=db_table, c=c['field'], coltype=c['type'])
            logger.info('Dropping column if exists: {c}' \
                .format(c=c['field']))
            cursor.execute(dropif_sql)
            logger.info('Adding column: {c} {coltype}' \
                .format(c=c['field'], coltype=c['type']))
            cursor.execute(add_sql)
        
        tx.commit(using=DJHCUP_DB_ENTRY)
    
    if index_fields != None:
        try:
            for col in index_fields:
                index = pyhcup.db.index_sql(col, db_table)
                cursor.execute(index)
                tx.commit(using=DJHCUP_DB_ENTRY)
                logger.info('Created index for column %s with on table %s' % (col, db_table))
        except:
            raise Exception("Failed to create indexes on table, particularly one that should have resulted from this query: %s" % index)
    
    table_record = IntegrationTable(
        data_source=source,
        name=db_table,
        database=DJHCUP_DB_ENTRY,
        category=category
    )
    table_record.save()
    logger.info('Saved master table details as IntegrationTable record %d' % table_record.pk)
    
    return table_record
