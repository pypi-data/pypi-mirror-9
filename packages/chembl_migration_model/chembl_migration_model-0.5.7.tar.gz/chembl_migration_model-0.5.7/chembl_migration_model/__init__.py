__author__ = 'mnowotka'

try:
    __version__ = __import__('pkg_resources').get_distribution('chembl_migration_model').version
except Exception as e:
    __version__ = 'development'

import chembl_core_model.models as LegacyModels
import models as mod
import sys
from chembl_core_db.db.models.abstractModel import ChemblCoreAbstractModel
from chembl_core_db.db.models.abstractModel import ModifiedModelMetaclass
from django.utils import six

#-----------------------------------------------------------------------------------------------------------------------

EXCLUDED_MODELS = ('CompoundImages',
                   'CompoundMols',
                   'Journals',
                   'JournalArticles',
    )

EXCLUDED_FIELDS = {'Activities': ('activity_type', 'updated_by', 'updated_on', 'manual_curation_flag', 'original_activity_id'),
                   'CellDictionary': ('downgraded',),
                   'CompoundProperties': ('updated_on',),
                   'CompoundRecords': ('old_compound_key', 'updated_by', 'updated_on', 'removed', 'src_compound_id_version', 'curated', 'filename'),
                   'CompoundStructures': ('structure_exclude_flag',),
                   'Products': ('information_source', 'load_date', 'removed_date', 'product_class', 'tmp_ingred_count', 'exclude'),
                   'ProteinClassification': ('downgraded', 'replaced_by', 'sort_order'),
                   'MoleculeDictionary': ('structure_key', 'exclude', 'insert_date', 'molfile_update', 'downgraded', 'downgrade_reason', 'replacement_mrn', 'checked_by', 'nomerge', 'nomerge_reason', 'chebi_id'),
                   'BioComponentSequences': ('updated_by', 'updated_on', 'insert_date', 'accession', 'db_source', 'db_version'),
                   'Assays':('activity_count', 'assay_source', 'updated_on', 'updated_by', 'orig_description', 'a2t_complex', 'a2t_multi', 'mc_tax_id', 'mc_organism', 'mc_target_type', 'mc_target_name', 'mc_target_accession', 'a2t_assay_tax_id', 'a2t_assay_organism', 'a2t_updated_on', 'a2t_updated_by'),
                   'Docs': ('journal_id', 'updated_by', 'updated_on'),
                   'TargetDictionary': ('updated_by', 'updated_on', 'popularity', 'insert_date', 'target_parent_type', 'in_starlite', 'downgraded'),
                   'ComponentSequences':('updated_by', 'updated_on', 'insert_date'),
                   'TargetComponents':('relationship', 'stoichiometry'),
                   'UsanStems':('downgraded',),
                   'DrugMechanism':('curated_by', 'date_added', 'date_removed', 'downgraded', 'downgrade_reason', 'uniprot_accessions', 'curator_comment', 'curation_status')
}

#-----------------------------------------------------------------------------------------------------------------------

def createModelClass(modelClass):

    exclude = EXCLUDED_FIELDS.get(modelClass.__name__, None)

    d = dict()
    d["Meta"] = type('Meta', (ChemblCoreAbstractModel.Meta, object), {'unique_together': modelClass._meta.unique_together, 'app_label': 'chembl_migration_model', 'exclude': exclude, 'model': modelClass, 'managed':False })
    d["__module__"] = mod.__name__
    if not six.PY3:
        d["__metaclass__"] = ModifiedModelMetaclass
    else:
        d["metaclass"] = ModifiedModelMetaclass

    return  ModifiedModelMetaclass(modelClass.__name__, (ChemblCoreAbstractModel, ), d)

#-----------------------------------------------------------------------------------------------------------------------

def getCoreModelClasses(module):
    from django.db.models import get_app
    from django.core.management.commands.dumpdata import sort_dependencies
    from django.utils.datastructures import SortedDict

    app_list = SortedDict((app, None) for app in [get_app('chembl_core_model')])
    return [model for model in sort_dependencies(app_list.items()) if model.__name__ not in EXCLUDED_MODELS and issubclass(model, ChemblCoreAbstractModel) and not model._meta.abstract]

#-----------------------------------------------------------------------------------------------------------------------

def createModelClassesFrom(module):
    for coreClass in getCoreModelClasses(module):
        yield createModelClass(coreClass)

#-----------------------------------------------------------------------------------------------------------------------

for resource in createModelClassesFrom(LegacyModels):
    setattr(sys.modules[mod.__name__], resource.__name__, resource)

#-----------------------------------------------------------------------------------------------------------------------
