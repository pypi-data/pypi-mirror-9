from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

DATABASE_SCRIPTS_DIR = "scripts/raw_sql/"

def add_psuedo_encrypt(model_class_names):
    import os
    from django.db import connection
    cursor = connection.cursor()
    from django.conf import settings
    import db_obfuscate
    app_path = os.path.abspath(db_obfuscate.__path__[0])
    file_path =  os.path.join(app_path, DATABASE_SCRIPTS_DIR + 'add_model_encryption.SQL')
    with open (file_path, "r") as alter_to_add_encrypt_func_file:
        alter_func=alter_to_add_encrypt_func_file.read()
        cursor.execute(alter_func)
    import importlib
    for model_class in model_class_names:
        if isinstance(model_class, str):
            module_name, model_class_name = model_class.rsplit(".",1)
            module = importlib.import_module(module_name)
            model_class = getattr(module, model_class_name)
        from django.db.models import AutoField
        if isinstance(model_class._meta.get_field_by_name("id")[0], AutoField):
            table_name = model_class._meta.db_table
            set_function = "ALTER TABLE {0} ALTER COLUMN id SET DEFAULT pseudo_encrypt(nextval('{0}_id_seq')::int);".format(table_name)
            cursor.execute(set_function)
            print "encrypted " + str(model_class) + "'s id"
        else:
            import warnings
            warnings.warn("Model {0} does not have id as Autofield, can't encrypt, skip.".format(model_class))
    
class Command(BaseCommand):
    args = '<...>'
    help = "encrypt models' ids, the id field of the encrypted model has to be autofield"
    option_list = BaseCommand.option_list + (
        make_option('--encrypt-model',
            action='store_true',
            dest='add_psuedo_encrypt',
            default="",
            help="encrypt some model's id with pseudo_encrypt."),
        ) + (
        make_option('--all',
            action='store_true',
            dest='encrypt_all',
            default="",
            help="encrypt all models with encrypt field set to True"),
        )

    def handle(self, *args, **options):
        if options["add_psuedo_encrypt"]:
            all_models = args
            add_psuedo_encrypt(all_models)
        elif options["encrypt_all"]:
            from django.db import models
            from django.conf import settings
            auto_models = filter(lambda model: getattr(model, "pseudo_encrypt_id", False), models.get_models(include_auto_created=True))
            all_models = list(auto_models) + list(getattr(settings, "ENCRYPT_ID_FOR_MODELS", []))
            add_psuedo_encrypt(all_models)
        self.stdout.write("Done!")

