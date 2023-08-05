__author__ = 'mnowotka'

from django.core.management.base import BaseCommand
from django.core.management.commands.syncdb import *
from django.utils.datastructures import SortedDict
from optparse import make_option
from django import db
from django.db import DEFAULT_DB_ALIAS
from django.db import transaction
from django.conf import settings
from django.db.utils import IntegrityError, DatabaseError
from django.db import connections
import multiprocessing as mp
from subprocess import check_call
import os, sys
import re

try:
    EXPORT = settings.MODEL_TO_BE_EXPORTED
except AttributeError:
    EXPORT = 'chembl_migration_model'

#-----------------------------------------------------------------------------------------------------------------------

def migrate_table((name, src, dest, format, verbosity)):
    import django.core.management
    django.core.management.call_command('migrate_table', targetDatabase=dest, sourceDatabase=src, modelName=name, format=format, verbosity=verbosity)
    return name

#-----------------------------------------------------------------------------------------------------------------------

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--format', default='json', dest='format',
            help='Specifies the output serialization format for migration.'),
        make_option('--targetDatabase', dest='targetDatabase',
            default=DEFAULT_DB_ALIAS, help='Target database'),
        make_option('--sourceDatabase', dest='sourceDatabase',
            default=None, help='Source database'),
        make_option('--onlySync', dest='onlySync',
            default=None, help="Don't migrate, just create schema"),
        make_option('--printDependencies', dest='printDeps',
            default=None, help="Don't migrate, just show dependencies"),
        )
    help = ("Migrate data from one database to another.")
    args = '[appname appname.ModelName ...]'

#-----------------------------------------------------------------------------------------------------------------------

    def __init__(self):
        self.dag = None
        self.format = None
        self.targetDatabase = None
        self.sourceDatabase = None
        super(Command, self).__init__()

#-----------------------------------------------------------------------------------------------------------------------

    def checkForSync(self, app_list, target_db, verbosity):
        from django.db.models import get_model, get_models
        for app, model_list in app_list:
            if model_list is None:
                model_list = get_models(app)

            for model in model_list:
                self.checkTable(model, target_db, verbosity)

#-----------------------------------------------------------------------------------------------------------------------

    def checkTable(self, model, target_db, verbosity):
        transaction.commit_unless_managed(using=target_db)
        transaction.enter_transaction_management(using=target_db)
        transaction.managed(True, using=target_db)
        try:
            model.objects.using(target_db).count()
        except DatabaseError as e:
            transaction.rollback(using=target_db)
            if "doesn't exist" or 'does not exist' in str(e):
                print 'Some tables are missing in target, syncing DBS...'
                self.syncApp(EXPORT, target_db, verbosity)
            else:
                raise e
        transaction.commit(using=target_db)
        transaction.leave_transaction_management(using=target_db)

#-----------------------------------------------------------------------------------------------------------------------

    def escape_comments(self, comment):
            return re.sub('%', '%%', re.sub(r"'", "''", comment))

#-----------------------------------------------------------------------------------------------------------------------

    def get_previous_column_definition(self, f, style, connection):
        if connection.vendor != 'mysql':
            return
        col_type = f.db_type(connection=connection)
        if col_type is None:
            # Skip ManyToManyFields, because they're not represented as
            # database columns in this table.
            return
        # Make the definition (e.g. 'foo VARCHAR(30)') for this field.
        field_output = [style.SQL_COLTYPE(col_type)]
        # Oracle treats the empty string ('') as null, so coerce the null
        # option whenever '' is a possible value.
        null = f.null
        if (f.empty_strings_allowed and not f.primary_key and
                connection.features.interprets_empty_strings_as_nulls):
            null = True
        if not null:
            field_output.append(style.SQL_KEYWORD('NOT NULL'))
        elif f.unique:
            field_output.append(style.SQL_KEYWORD('UNIQUE'))
        return ' '.join(field_output)

#-----------------------------------------------------------------------------------------------------------------------

    def sql_for_column_comments(self, model, style, connection):
        """
        Returns SQL statements to decorate columns with comments.
        This method is a bit hacky because django backends ignore comments by default.
        If you don't like hacks, simply remove this method, it's not that important.
        """
        try:
            qn = connection.ops.quote_name
            output = []
            opts = model._meta
            table = opts.db_table
            for f in opts.local_fields:
                col_type = f.db_type(connection=connection)
                if col_type is None:
                    continue
                if connection.vendor in ('oracle', 'postgresql'):
                    output.extend(
                        (style.SQL_KEYWORD("COMMENT ON COLUMN") + " " +
                        style.SQL_TABLE(qn(table)) + "." + style.SQL_FIELD(qn(f.column)) + " " +
                        style.SQL_KEYWORD("IS")  + " " +
                        "'%s';" % self.escape_comments(f.help_text),))
                elif connection.vendor == 'mysql':
                    previous_column_definition = self.get_previous_column_definition(f, style, connection)
                    output.extend(
                        (style.SQL_KEYWORD("ALTER TABLE") + " " +
                        style.SQL_TABLE(qn(table)) + " " +
                        style.SQL_KEYWORD("MODIFY COLUMN")  + " " +
                        style.SQL_FIELD(qn(f.column)) + " " +
                        previous_column_definition + " " +
                        style.SQL_KEYWORD("COMMENT") + " " +
                        "'%s';" % self.escape_comments(f.help_text),))
                else:
                    continue
            return output
        except:
            print "failed generating column comments for model %s" % model

#-----------------------------------------------------------------------------------------------------------------------

    def sql_for_pending_references(self, model, style, pending_references, connection):
        """
        Returns any ALTER TABLE statements to add constraints after the fact.
        """
        from django.db.backends.util import truncate_name

        opts = model._meta
        qn = connection.ops.quote_name
        final_output = []
        if model in pending_references:
            for rel_class, f in pending_references[model]:
                rel_opts = rel_class._meta
                r_table = rel_opts.db_table
                r_col = f.column
                table = opts.db_table
                col = opts.get_field(f.rel.field_name).column
                # For MySQL, r_name must be unique in the first 64 characters.
                # So we are careful with character usage here.
                r_name = '%s_refs_%s_%s' % (
                    r_col, col, connection.creation._digest(r_table, table))
                final_output.append(style.SQL_KEYWORD('ALTER TABLE') +
                    ' %s ADD CONSTRAINT %s FOREIGN KEY (%s) REFERENCES %s (%s)%s;' %
                    (qn(r_table), qn(truncate_name(
                        r_name, connection.ops.max_name_length())),
                    qn(r_col), qn(table), qn(col),
                    connection.ops.deferrable_sql()))
            del pending_references[model]
        return final_output

#-----------------------------------------------------------------------------------------------------------------------

    def sql_indexes_for_model(self, model, style, connection):
        """
        Returns the CREATE INDEX SQL statements for a single model.
        """
        try:
            output = []
            for f in model._meta.local_fields:
                output.extend(connection.creation.sql_indexes_for_field(model, f, style))
            for fs in model._meta.index_together:
                fields = [model._meta.get_field_by_name(f)[0] for f in fs]
                output.extend(connection.creation.sql_indexes_for_fields(model, fields, style))
            return output
        except:
            print "failed generating indexes for model %s" % model

#-----------------------------------------------------------------------------------------------------------------------

    def syncApp(self, appName, database, verbosity):

        connection = connections[database]
        cursor = connection.cursor()
        style = no_style()

        # Get a list of already installed *models* so that references work right.
        tables = connection.introspection.table_names()
        seen_models = connection.introspection.installed_models(tables)
        created_models = set()
        pending_references = {}

        if verbosity >= 3:
            print "tables = %s" % tables
            print "seen_models = %s" % seen_models

        # Build the manifest of apps and models that are to be synchronized
        all_models = [
        (app.__name__.split('.')[-2],
         [m for m in models.get_models(app, include_auto_created=True, only_installed=False)])
        for app in [models.get_app(appName)]
        ]

        manifest = SortedDict(
            (app_name, model_list)
                for app_name, model_list in all_models
        )

        # Create the tables for each model
        if verbosity >= 1:
            print "Creating tables ..."
        for app_name, model_list in manifest.items():
            for model in model_list:
                if model in seen_models:
                    continue
                managed = model._meta.managed
                model._meta.managed = True
                if verbosity >= 3:
                    print "Processing %s.%s model" % (app_name, model._meta.object_name)
                sql, references = connection.creation.sql_create_model(model, style, seen_models)
                seen_models.add(model)
                created_models.add(model)
                for refto, refs in references.items():
                    pending_references.setdefault(refto, []).extend(refs)
                    if refto in seen_models:
                        sql.extend(self.sql_for_pending_references(refto, style, pending_references, connection))
                sql.extend(self.sql_for_pending_references(model, style, pending_references, connection))
                if verbosity >= 3:
                    print "pending references for table %s = %s" % (model._meta.db_table, pending_references)
                    print "SQL for pending references for table %s = %s" % (model._meta.db_table, self.sql_for_pending_references(model, style, pending_references, connection))
                if verbosity >= 3:
                    print "decorating columns with comments..."
                sql.extend(self.sql_for_column_comments(model, style, connection))
                if verbosity >= 3:
                    print "SQL for column comments for table %s = %s" % (model._meta.db_table, self.sql_for_column_comments(model, style, connection))
                if verbosity >= 1 and sql:
                    print "Creating table %s" % model._meta.db_table
                for statement in sql:
                    if verbosity >= 3:
                        print statement
                    cursor.execute(statement)
                tables.append(connection.introspection.table_name_converter(model._meta.db_table))
                model._meta.managed = managed

        if verbosity >= 1:
            print "Installing indexes ..."
            # Install SQL indices for all newly created models
        for app_name, model_list in manifest.items():
            for model in model_list:
                if model in created_models:
                    index_sql = self.sql_indexes_for_model(model, style, connection)
                    if index_sql:
                        if verbosity >= 2:
                            print "Installing index for %s.%s model" % (app_name, model._meta.object_name)
                        try:
                            for sql in index_sql:
                                cursor.execute(sql)
                        except Exception, e:
                            print "Failed to install index for %s.%s model: %s" % (app_name, model._meta.object_name, e)

        if verbosity >= 3:
            print "indexes created"

#-----------------------------------------------------------------------------------------------------------------------

    def callback(self, name=None):
        if not self.dag:
            return

        if name:
            for (m,d) in self.dag:
                if name == m.__name__:
                    self.dag.remove((m,d))
            for (m,d) in self.dag:
                if name in map(lambda x: x.__name__, d):
                    while name in map(lambda x: x.__name__, d):
                        for dep in d:
                            if name == dep.__name__:
                                d.remove(dep)

        if not self.dag:
            print "Export completed."
            return

        chunk = []
        for (m,d) in self.dag:
            if not d:
                chunk.append(m.__name__)

        for model in chunk:
            for (m,d) in self.dag:
                if m.__name__ == model:
                    self.dag.remove((m,d))

        if not chunk:
            return

        pool = mp.Pool(len(chunk))
        for model in chunk:
            pool.apply_async(migrate_table, args=((model, self.sourceDatabase, self.targetDatabase, self.format, self.verbosity),), callback = self.callback)
        pool.close()
        pool.join()

#-----------------------------------------------------------------------------------------------------------------------

    def handle(self, *args, **options):
        from django.db.models import get_app
        import copy
        if settings.DEBUG:
            print "Django is in debug mode, which causes memory leak. Set settings.DEBUG to False and run again."
            return

        db.reset_queries()
        deps = options.get('printDeps', False)
        sync = options.get('onlySync', False)
        app_list = SortedDict((app, None) for app in [get_app(EXPORT)])
        if not deps:
            self.format = options.get('format')
            self.targetDatabase = options.get('targetDatabase')
            self.sourceDatabase = options.get('sourceDatabase')
            self.verbosity = int(options.get('verbosity'))
            print "Migrating app " + EXPORT
            print "Migrating " + settings.DATABASES[self.sourceDatabase]['NAME'] + " to " + settings.DATABASES[self.targetDatabase]['NAME']
            self.checkForSync(app_list.items(), self.targetDatabase, self.verbosity)
        self.dag = get_dependencies(app_list.items())
        check_dependencies(copy.deepcopy(self.dag))
        if sync:
            return
        if deps:
            self.showDependencies()
            return
        self.callback()

#-----------------------------------------------------------------------------------------------------------------------

    def showDependencies(self):
        dotFile = 'dependencies.dot'
        outFormat = 'svg'
        outFile = 'dependencies.%s' % outFormat
        program = 'sfdp'
        graphBuffer = '''digraph G {
node [color=lightblue2, style=filled, shape = circle];
ratio = "auto" ;
mincross = 2.0 ;
'''
        for row in self.dag:
            key = row[0].__name__
            deps = set(map(lambda x : x.__name__, row[1]))
            if not deps:
                graphBuffer += '%s;\n' % key
            else:
                for dep in deps:
                    graphBuffer += '%s->%s;\n' % (key, dep)
        graphBuffer += 'overlap=false\n}'
        f = open(dotFile, 'w')
        f.write(graphBuffer)
        f.close()
        check_call([program,'-T%s' % outFormat, dotFile,'-o',outFile])
        os.system('display -resize 25%% %s' % outFile)

#-----------------------------------------------------------------------------------------------------------------------

def get_dependencies(app_list):
    from django.db.models import get_model, get_models
    # Process the list of models, and get the list of dependencies
    model_dependencies = []
    models = set()
    for app, model_list in app_list:
        if model_list is None:
            model_list = get_models(app)

        for model in model_list:
            models.add(model)
            deps = []

            # Now add a dependency for any FK or M2M relation with
            # a model that defines a natural key
            for field in model._meta.fields:
                if hasattr(field.rel, 'to'):
                    rel_model = field.rel.to
                    deps.append(rel_model)
            for field in model._meta.many_to_many:
                rel_model = field.rel.to
                deps.append(rel_model)
            model_dependencies.append((model, deps))

    model_dependencies.reverse()
    return model_dependencies

#-----------------------------------------------------------------------------------------------------------------------

def check_dependencies(dep):

    while dep:
        #print "model_dependencies = " + str(model_dependencies) + "\n\n"
        models = []
        changed = False
        for (m, d) in dep:
            if not len(d):
                models.append(m)
                changed = True
        if not changed:
            #print "ERROR model_dependencies = " + str(model_dependencies) + "\n\n"
            raise NameError

        for model in models:
            for (m,d) in dep:
                if model == m:
                    dep.remove((m,d))
        for model in models:
            #print "removing " + str(model) + " from dependencies" + "\n\n"
            for (m,d) in dep:
                while model in d:
                    d.remove(model)
                    #print "dependencies after removal: " + str(model_dependencies) + "\n\n"

#-----------------------------------------------------------------------------------------------------------------------
