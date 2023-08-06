# core Python packages
import logging


# third party packages


# django packages
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned


# local project and app packages
from djhcup_integration.models import ColumnName, Column, Definition
from djhcup_staging.models import DataSource

# move these into the local namespace
from djhcup_integration.config import DEFAULT_DEFINITIONS

# kludge workaround--move to config later
DJHCUP_DB_ENTRY = 'djhcup'

# start a logger
logger = logging.getLogger('default')


def populate():
    definitions = []
    colnames = []
    cols = []
    
    for d in DEFAULT_DEFINITIONS:
        try:
            name = d['name']
            category = d['category']
            abbr = d['ds_family_abbr']
            p_abbr = d['ds_parent_abbr']
            
            try:
                # isolate the DataSource
                ds = DataSource.objects.get(
                    abbreviation=abbr,
                    parent__abbreviation=p_abbr
                )
                
                try:
                    def_obj = Definition.objects.get(
                        data_source=ds,
                        category=category,
                        name=name
                    )
                    logger.info("Found existing Definition object {pk}" \
                        .format(pk=def_obj.pk))
                    
                except (ObjectDoesNotExist, MultipleObjectsReturned):
                    def_obj = Definition(
                        data_source=ds,
                        category=category,
                        name=name,
                    )
                    def_obj.save()
                    logger.info("Added Definition object {pk} for {name}" \
                        .format(pk=def_obj.pk, name=def_obj.name))
                
                for i in d['columns']:
                    # move on to column logging
                    try:
                        cn = ColumnName.objects.get(value__iexact=i['field'])
                    except:
                        cn = ColumnName(value=i['field'])
                        cn.save()
                        colnames.append(cn)
                    
                    try:
                        col = Column.objects.get(fields_in=cn, field_out__value__iexact=i['field'])
                    except:
                        col = Column(field_out=cn, field_out_data_type=i['type'])
                        col.save()
                        col.fields_in.add(cn)
                        cols.append(col)
                    
                    def_obj.columns.add(col)
                
                logger.info("Added or verified {ct} Column objects for Definition object {pk}" \
                    .format(ct=str(def_obj.columns.all().count()), pk=def_obj.pk))
                
                definitions.append(def_obj)
            
            except (ObjectDoesNotExist, MultipleObjectsReturned):
                logger.warning(
                    "Unable to isolate djhcup_staging.models.DataSource " +\
                    "object with abbreviation {a} and parent " +\
                    "abbreviation {p}. Definition for {d} will not " +\
                    "proceed".format(a=abbr, p=p_abbr, d=name)
                )
        except KeyError:
            logger.error(
                "Definition lacks critical components. Will not " +\
                "proceed.\n\n{d}".format(d=d)
            )
    
    return definitions, colnames, cols
