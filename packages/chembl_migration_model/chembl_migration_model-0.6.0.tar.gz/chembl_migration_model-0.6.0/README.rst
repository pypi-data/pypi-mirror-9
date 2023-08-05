chembl_migration_model
======

This is chembl_migration_model package developed at Chembl group, EMBL-EBI, Cambridge, UK.

This package contains Django ORM model suitable for data exports and migrations.
It excludes some tables present in chembl_core_model (such as COMPOUND_MOLS and COMPOUND_IMAGES) as well as some columns in remaining tables.

The model is generated dynamically from chembl_core_model and this is why models.py file is empty.
Whole logic sits in __init__.py.
All classes are unmanaged by default so you can't use them to syncdb.
To create tables from the model you have to run migrate command from chembl_migrate.