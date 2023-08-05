__author__ = 'mnowotka'

from django.core.management.commands.inspectdb import Command as InspectCommand
from django.db import connections, DEFAULT_DB_ALIAS
import keyword
import ConfigParser
from optparse import make_option
from django.core.management.base import CommandError
from django.conf import settings
import tempfile
import os

try:
    DEFAULT_LAYOUT_PATH = settings.DEFAULT_LAYOUT_PATH
except AttributeError:
    DEFAULT_LAYOUT_PATH = 1000

LINE = '#' + '-' * 119
NAME_SUBSTITUTIONS = {'molregno' : 'molecule', 'tid' : 'target', 'level5': 'atc_classification',
                      'parent_molregno': 'parent_molecule', 'active_molregno': 'active_molecule', 'mec':'mechanism',
                      'related_tid' : 'related_target'}

KNOWN_SINGLE_VALUED_COLUMNS = ['db_version', 'updated_by']
KNOWN_SINGLE_VALUED_TABLES = ['version']

table2model = lambda table_name: table_name.title().replace('_', '').replace(' ', '').replace('-', '')

PROPERTIES = {'molecule_dictionary':
                  {'compoundproperties':'compoundProperty',
                   'compoundstructures' : 'compoundStructure',
                   'compoundimages': 'compoundImage',
                   'compoundmols': 'compoundMol',
                   'moleculehierarchy':'moleculeHierarchy'}
}

#-----------------------------------------------------------------------------------------------------------------------

class Command(InspectCommand):
    help = "Introspects the ChEMBL database and outputs a Django model module."

    option_list = InspectCommand.option_list + (
        make_option('--layout', action='store', dest='layout',
            default=DEFAULT_LAYOUT_PATH, help='Path to .INI file with logical database table layout.'),
        )

    connection = None
    cursor = None
    tables_relations = {}

#-----------------------------------------------------------------------------------------------------------------------

    def handle_noargs(self, **options):
        try:
            self.handle_inspection(options)
        except NotImplementedError:
            raise CommandError("Database inspection isn't supported for the currently selected database backend.")

#-----------------------------------------------------------------------------------------------------------------------

    def write_file_header(self, fp, filename):
        fp.write("# This is an auto-generated Django model module.\n")
        fp.write("# You'll have to do the following manually to clean this up:\n")
        fp.write("#     * Rearrange models' order\n")
        fp.write("#     * Make sure each model has one field with primary_key=True\n")
        fp.write("# Feel free to rename the models, but don't rename db_table values or field names.\n")
        fp.write("#\n")
        fp.write("# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'\n")
        fp.write("# into your database.\n")
        fp.write('\n')
        fp.write('import datetime\n')
        fp.write('from django.db import models\n')
        fp.write('from chembl_core_model.models import *\n')
        fp.write('from chembl_core_db.db.customFields import BlobField, ChemblCharField\n')
        if filename == 'compounds.py':
            fp.write('from chembl_core_db.db.customManagers import CompoundMolsManager\n')
        fp.write('from chembl_core_db.db.models.abstractModel import ChemblCoreAbstractModel\n')
        fp.write('from chembl_core_db.db.models.abstractModel import ChemblModelMetaClass\n')
        fp.write('from django.utils import six\n')
        fp.write('\n')

#-----------------------------------------------------------------------------------------------------------------------

    def write_file_footer(self, fp):
        fp.write(LINE + '\n')
        fp.write('\n')
        fp.close()

#-----------------------------------------------------------------------------------------------------------------------

    def write_class_declaration(self, fp, table_name):
        fp.write(LINE + '\n')
        fp.write('\n')
        fp.write('class %s(six.with_metaclass(ChemblModelMetaClass, ChemblCoreAbstractModel)):\n' % table2model(table_name))
        fp.write('\n')
        if table_name == 'compound_mols':
            fp.write('    objects = CompoundMolsManager()\n')
        fp.write('\n')

#-----------------------------------------------------------------------------------------------------------------------

    def get_relations(self, table_name):
        if not table_name in self.tables_relations:
            try:
                relations = self.connection.introspection.get_relations(self.cursor, table_name)
            except NotImplementedError:
                relations = {}
            self.tables_relations[table_name] = relations
        else:
            relations = self.tables_relations[table_name]

        return relations

#-----------------------------------------------------------------------------------------------------------------------

    def get_indexes(self, table_name):
        try:
            indexes = self.connection.introspection.get_indexes(self.cursor, table_name)
        except NotImplementedError:
            indexes = {}
        return indexes

#-----------------------------------------------------------------------------------------------------------------------

    def get_arity(self, table_name):
        try:
            arity = self.connection.introspection.get_arity(self.cursor, table_name)
        except NotImplementedError:
            arity = {}
        return arity

#-----------------------------------------------------------------------------------------------------------------------

    def get_constraints(self, table_name):
        try:
            constrains = self.connection.introspection.get_contraints(self.cursor, table_name)
        except NotImplementedError:
            constrains = []
        return constrains

#-----------------------------------------------------------------------------------------------------------------------

    def get_comments(self, table_name):
        try:
            comments = self.connection.introspection.get_comments(self.cursor, table_name)
        except NotImplementedError:
            comments = {}
        return comments

#-----------------------------------------------------------------------------------------------------------------------

    def get_defaults(self, table_name):
        try:
            defaults = self.connection.introspection.get_defaults(self.cursor, table_name)
        except NotImplementedError:
            defaults = {}
        return defaults

#-----------------------------------------------------------------------------------------------------------------------

    def get_unique_together(self, table_name):
        try:
            unique_together = self.connection.introspection.get_unique_together(self.cursor, table_name)
        except NotImplementedError:
            unique_together = {}
        return  unique_together

#-----------------------------------------------------------------------------------------------------------------------

    def get_triggers(self, table_name):
        try:
            triggers = self.connection.introspection.get_sequence_incrementing_triggers(self.cursor, table_name)
        except NotImplementedError:
            triggers = []
        return triggers

#-----------------------------------------------------------------------------------------------------------------------

    def get_nonunique_index_columns(self, table_name):
        try:
            nonunique_index_columns = self.connection.introspection.get_nonunique_indexes(self.cursor, table_name)
        except NotImplementedError:
            nonunique_index_columns = []

        return nonunique_index_columns

#-----------------------------------------------------------------------------------------------------------------------

    def validate_empty_and_stale_columns(self, arity, table_name):
        empty_columns = filter(lambda x:arity[x][0] == 0, arity)
        if empty_columns:
            print "\033[0m\033[1;%dmWarning [%s]: empty columns detected in %s table: %s\033[0m" % (30, 1, table_name, ', '.join(empty_columns))

        if table_name not in KNOWN_SINGLE_VALUED_TABLES:
            stale_columns = filter(lambda x:arity[x][0] == 1 and x not in KNOWN_SINGLE_VALUED_COLUMNS, arity)
            if stale_columns:
                print "\033[0m\033[1;%dmWarning [%s]: columns with single distinct value " \
                      "detected in %s table: %s\033[0m" % (31, 2, table_name,  ', '.join(stale_columns))

#-----------------------------------------------------------------------------------------------------------------------

    def get_choices(self, table_name, constrains, arity, relations, comments, defaults):
        try:
            choices, null_flags, flags, tri_state_flags = \
                                self.connection.introspection.get_choices(constrains, arity, self.cursor, table_name, comments)
            choices = dict((k,v) for k,v in choices.items() if v not in
                                                            [((0, '0'), (1, '1')), ((-1, '-1'), (0, '0'), (1, '1'))])
        except NotImplementedError:
            choices = {}
            null_flags = []
            flags = []
            tri_state_flags = []

        if table_name.lower() != 'chembl_id_lookup' and (table_name.lower().endswith('_type') or table_name.lower().endswith('_lookup')):
            choices = {}

        foreign_choices = []

        for column in choices:
            if len(column) >=2 and column[0] == 'l' and column[1:].isdigit():
                foreign_choices.append(column)
            if arity[column][4] in relations and (column.lower().endswith('_type') or relations[arity[column][4]][1].endswith('_lookup') ):
                foreign_choices.append(column)

        choices = dict(filter(lambda x: x[0] not in foreign_choices, choices.items()))

        for column in choices:
            if column in defaults:
                default = defaults[column]
                if isinstance(default, unicode):
                    default = str(default)
                defchoice = (default, str(default))
                if defchoice not in choices[column]:
                    print "\033[0m\033[1;%dmWarning [%s]: %s.%s: default value is out of possible choices\033[0m" % (33, 11, table_name,  column)
                    choices[column] = choices[column] + (defchoice,)

        return choices, null_flags, flags, tri_state_flags

#-----------------------------------------------------------------------------------------------------------------------

    def add_indexes_to_params(self, extra_params, column_name, table_meta_desc):
        # Add primary_key and unique, if necessary.
        indexes = table_meta_desc['indexes']
        unique_together = table_meta_desc['unique_together']
        nonunique_index_columns = table_meta_desc['nonunique_index_columns']

        if column_name in indexes:
            if indexes[column_name]['primary_key']:
                extra_params['primary_key'] = True
            elif indexes[column_name]['unique']:
                if not len(unique_together) or not any(map(lambda x : x.lower() == column_name,
                    reduce(lambda x, y: x+y, unique_together.values()))):
                    extra_params['unique'] = True

        if column_name.lower() in nonunique_index_columns:
            if not column_name in indexes or not indexes[column_name]['primary_key']:
                extra_params['db_index'] = True

#-----------------------------------------------------------------------------------------------------------------------

    def modify_field_name(self, row, table_meta_desc, table_name):
        comment_notes = [] # Holds Field notes, to be displayed in a Python comment.
        extra_params = {}  # Holds Field parameters such as 'db_column'.

        column_name = row[0]
        if column_name.startswith('old_') or column_name.endswith('_old'):
            print "\033[0m\033[1;%dmWarning [%s]: column %s.%s may be deprecated \033[0m" % (32, 10, table_name, column_name)
        att_name = column_name.lower()
        column_constraints = [c for c in table_meta_desc['constrains'] if att_name in c] or []
        desc = tuple(list(row) + [column_constraints])

        # If the column name can't be used verbatim as a Python
        # attribute, set the "db_column" for this Field.
        if ' ' in att_name or '-' in att_name or keyword.iskeyword(att_name) or column_name != att_name:
            extra_params['db_column'] = column_name

        self.add_indexes_to_params(extra_params, column_name, table_meta_desc)

        # Modify the field name to make it Python-compatible.
        if ' ' in att_name:
            att_name = att_name.replace(' ', '_')
            comment_notes.append('Field renamed to remove spaces.')

        if '-' in att_name:
            att_name = att_name.replace('-', '_')
            comment_notes.append('Field renamed to remove dashes.')

        if column_name != att_name:
            comment_notes.append('Field name made lowercase.')

        return comment_notes, column_name, extra_params, att_name, desc

#-----------------------------------------------------------------------------------------------------------------------

    def find_field_type(self, i, table_name, row, column_name, att_name, extra_params, comment_notes, table_meta_desc):
        relations = table_meta_desc['relations']
        null_flags = table_meta_desc['null_flags']
        flags = table_meta_desc['flags']
        tri_state_flags = table_meta_desc['tri_state_flags']

        defaults = table_meta_desc['defaults']

        if column_name in defaults:
            extra_params['default'] = defaults[column_name]

        if i in relations:
            rel_to = relations[i][1] == table_name and "'self'" or table2model(relations[i][1])
            if not extra_params.get('primary_key', False):
                if rel_to in map(lambda x: table2model(relations[x][1]) if x !=i else None, relations):
                    extra_params['related_name'] = att_name.split('_')[0]
                field_type = 'ForeignKey(%s' % rel_to
            else:
                field_type = 'OneToOneField(%s' % rel_to
            if att_name.endswith('_id'):
                att_name = att_name[:-3]
            else:
                extra_params['db_column'] = column_name
            if att_name in NAME_SUBSTITUTIONS:
                att_name = NAME_SUBSTITUTIONS[att_name]
                extra_params['db_column'] = column_name
            if 'db_index' in extra_params:
                del extra_params['db_index']
        else:
            # Calling `get_field_type` to get the field type string and any
            # additional paramters and notes.
            field_type, field_params, field_notes = self.get_field_type(self.connection, table_name, row)
            extra_params.update(field_params)
            comment_notes.extend(field_notes)

            if column_name in null_flags:
                field_type = 'ChemblNullableBooleanField'
            elif column_name in flags:
                field_type = 'ChemblBooleanField'
            elif column_name in tri_state_flags:
                field_type = 'ChemblNullBooleanField'

            field_type += '('

        if field_type == 'ChemblIntegerField(':
            if 'default' not in extra_params or extra_params['default'] >= 0:
                if 'choices' not in table_meta_desc or column_name not in table_meta_desc['choices'] or \
                                        all(map(lambda x: x[0] >= 0, table_meta_desc['choices'][column_name])):
                    if self.connection.introspection.is_positive(self.cursor, table_name, column_name):
                        if not column_name.endswith(('_count', '_id', 'year', '_pk', 'molregno', 'month', 'day', 'issue', 'volume', '_mrn', '_mwt')) and not column_name.startswith(('num_', 'mw_')):
                            print "\033[0m\033[1;%dmWarning [%s]: column %s.%s contains only positive values but doesn't have constraint\033[0m" % \
                                                                                            (32,3, table_name, column_name)
                        field_type = 'ChemblPositiveIntegerField('

        if field_type == 'DecimalField(':
            if self.connection.introspection.is_positive(self.cursor, table_name, column_name):
                if not column_name.endswith(('_count', '_id', 'year', '_pk', 'molregno', 'month', 'day', 'issue', 'volume', '_mrn', '_mwt')) and not column_name.startswith(('num_', 'mw_')):
                    print "\033[0m\033[1;%dmWarning [%s]: column %s.%s contains only positive values but doesn't have constraint\033[0m" % \
                                                                                            (32, 3, table_name, column_name)
                field_type = 'ChemblPositiveDecimalField('

        if column_name.endswith('_flag') and not 'Boolean' in field_type:
            print "\033[0m\033[1;%dmWarning [%s]: column %s.%s is supposed to be a flag but is %s instead\033[0m" % (33, 4, table_name, column_name,
                                                                            str(table_meta_desc['arity'][column_name]))
        if extra_params.get('primary_key', False) and 'integer' in field_type.lower() and \
                                                                                    len(table_meta_desc['triggers']):
            field_type = 'ChemblAutoField('

        return field_type, att_name

#-----------------------------------------------------------------------------------------------------------------------

    def enhance_extra_params(self, extra_params, column_name, field_type, att_name, row,
                                                                        comment_notes, table_meta_desc, table_name):
        if column_name in table_meta_desc['choices']:
            extra_params['choices'] = column_name.upper() + '_CHOICES'

        defaults = table_meta_desc['defaults']

        if column_name in defaults:
            extra_params['default'] = defaults[column_name]

        # Add 'null' and 'blank', if the 'null_ok' flag was present in the
        # table description.
        if row[6]: # If it's NULL...
            extra_params['blank'] = True
            extra_params['null'] = True
        else:
            extra_params['blank'] = False
            extra_params['null'] = False

        if field_type == 'ChemblCharField(':
            extra_params['max_length'] = row[3]
        if field_type in ['ChemblAutoField(', 'ChemblIntegerField(', 'ChemblPositiveIntegerField(']:
            extra_params['length'] = row[4]
        if field_type == 'ChemblNoLimitDecimalField(':
            del extra_params['decimal_places']
            del extra_params['max_digits']
            print '\033[0m\033[1;%dmWarning [%s]: No precision and scale defined for %s.%s' % (34, 12, table_name, column_name)

        help_text = table_meta_desc['comments'].get(column_name.lower(), False)
        if help_text:
            extra_params['help_text'] = help_text

        if keyword.iskeyword(att_name):
            att_name += '_field'
            comment_notes.append('Field renamed because it was a Python reserved word.')

        if att_name[0].isdigit():
            att_name = 'number_%s' % att_name
            extra_params['db_column'] = unicode(column_name)
            comment_notes.append("Field renamed because it wasn't a "
                                 "valid Python identifier.")

        return att_name

#-----------------------------------------------------------------------------------------------------------------------

    def get_field_description(self, table_name, row, i, table_meta_desc):
        comment_notes, column_name, extra_params, att_name, desc = self.modify_field_name(row, table_meta_desc, table_name)

        field_type, att_name = self.find_field_type(i, table_name, desc, column_name, att_name, extra_params,
                                                                                        comment_notes, table_meta_desc)
        att_name = self.enhance_extra_params(extra_params, column_name, field_type, att_name, desc, comment_notes, table_meta_desc, table_name)

        for u in table_meta_desc['unique_together']:
            try:
                idx = map(lambda x: x.lower(), table_meta_desc['unique_together'][u]).index(column_name)
                table_meta_desc['unique_together'][u][idx] = att_name
            except ValueError:
                continue

        # Don't output 'id = meta.AutoField(primary_key=True)', because
        # that's assumed if it doesn't exist.
        if att_name == 'id' and field_type == 'AutoField(' and extra_params.get('primary_key', False):
            return None

        if field_type.startswith('Chembl') or field_type == 'BlobField(':
            field_desc = '%s = %s' % (att_name, field_type)
        else:
            field_desc = '%s = models.%s' % (att_name, field_type)

        if ('blank' in extra_params and 'null' in extra_params and not extra_params['blank']
            and not extra_params['null']) or\
           field_type in ['ChemblNullableBooleanField(', 'ChemblNullBooleanField(',
                                                                            'ChemblBooleanField(', 'ChemblAutoField(']:
            del extra_params['blank']
            del extra_params['null']

        if field_type == 'BlobField(' and 'db_index' in extra_params:
            del extra_params['db_index']

        if field_type == 'OneToOneField(' and 'unique' in extra_params:
            del extra_params['unique']

        if extra_params:
            if not field_desc.endswith('('):
                field_desc += ', '
            for i in ['primary_key', 'length', 'max_length', 'unique', 'db_index', 'blank', 'null']:
                if i in extra_params:
                    field_desc += '%s=%r' % (i, extra_params[i])
                    del extra_params[i]
                    if len(extra_params):
                        field_desc += ', '
            if 'default' in extra_params:
                if field_type.endswith('DateField(') and extra_params['default'] == 'sysdate':
                    field_desc += 'default=datetime.date.today'
                elif 'Boolean' in field_type and field_type != 'ChemblNullBooleanField(':
                    if extra_params['default']:
                        field_desc += 'default=True'
                    else:
                        field_desc += 'default=False'
                else:
                    field_desc += '%s=%r' % ('default', extra_params['default'])
                del extra_params['default']
                if len(extra_params):
                    field_desc += ', '

            field_desc += ', '.join(['%s=%r' % (k, v) for k, v in extra_params.items() if k not in
                                                                                          ['choices', 'help_text']])

            if 'choices' in extra_params:
                if not field_desc.endswith(', '):
                    field_desc += ', '
                field_desc += '%s=%s' % ('choices', extra_params['choices'])

            if 'help_text' in extra_params:
                if not field_desc.endswith(', ') and not len(extra_params) == 1:
                    field_desc += ', '
                field_desc += '%s=%r' % ('help_text', extra_params['help_text'])
        field_desc += ')'
        if comment_notes:
            field_desc += ' # ' + ' '.join(comment_notes)

        return field_desc

#-----------------------------------------------------------------------------------------------------------------------

    def write_choices(self, fp, choices, table_name):
        for choice in sorted(choices.keys()):
            fp.write('    %s = (\n' % (choice.upper() + '_CHOICES'))
            for bla in choices[choice]:
                fp.write('        %s,\n' % str(bla))
            fp.write('        )\n\n')

#-----------------------------------------------------------------------------------------------------------------------

    def write_properties(self, fp, table_name):
        if table_name in PROPERTIES:
            for property in sorted(PROPERTIES[table_name].items()):
                fp.write('''    @property
    def %s(self):
        if hasattr(self, '%s'):
            return self.%s
        return None\n\n''' % (property[1], property[0], property[0]))

#-----------------------------------------------------------------------------------------------------------------------

    def get_table_meta_description(self, table_name):
        meta_desc = {}

        relations = self.get_relations(table_name)
        meta_desc['relations'] = relations
        meta_desc['indexes'] = self.get_indexes(table_name)
        meta_desc['nonunique_index_columns'] = self.get_nonunique_index_columns(table_name)
        meta_desc['unique_together'] = self.get_unique_together(table_name)
        arity = self.get_arity(table_name)
        meta_desc['arity'] = arity
        comments = self.get_comments(table_name)
        meta_desc['comments'] = comments
        defaults = self.get_defaults(table_name)
        meta_desc['defaults'] = defaults
        meta_desc['triggers'] = self.get_triggers(table_name)
        constrains = self.get_constraints(table_name)
        meta_desc['constrains'] = constrains
        choices, null_flags, flags, tri_state_flags = self.get_choices(table_name, constrains, arity, relations, comments, defaults)
        meta_desc['choices'] = choices
        meta_desc['null_flags'] = null_flags
        meta_desc['flags'] = flags
        meta_desc['tri_state_flags'] = tri_state_flags

        return meta_desc

#-----------------------------------------------------------------------------------------------------------------------

    def write_model(self, fp, table_name):
        self.write_class_declaration(fp, table_name)

        table_meta_desc = self.get_table_meta_description(table_name)

        self.validate_empty_and_stale_columns(table_meta_desc['arity'], table_name)
        self.write_choices(fp, table_meta_desc['choices'], table_name)
        self.write_properties(fp, table_name)

        for i, row in enumerate(self.connection.introspection.get_table_description(self.cursor, table_name)):
            field_desc = self.get_field_description(table_name, row, i, table_meta_desc)
            fp.write('    %s\n' % field_desc)
        fp.write('\n')
        for meta_line in self.get_meta(table_name, table_meta_desc['unique_together']):
            fp.write(meta_line + '\n')

#-----------------------------------------------------------------------------------------------------------------------

    def write_module(self, path, name, sect, order):
        filename = table2model(name) + '.py'
        filename = filename[0].lower() + filename[1:]
        fp = open(os.path.join(path, filename), 'w')

        self.write_file_header(fp, filename)

        fileTables = filter(lambda x: x in sect[name], order)

        for table_name in fileTables:
            self.write_model(fp, table_name)

        self.write_file_footer(fp)

#-----------------------------------------------------------------------------------------------------------------------

    def get_configuration(self, filename):
        config = ConfigParser.ConfigParser()
        config.read(filename)

        sect = {}
        sections = config.sections()
        printed_tables = []
        for section in sections:
            options = map(lambda x: x.lower(), config.options(section))
            printed_tables.extend(options)
            sect[section] = options

        tables = [table for table in self.connection.introspection.get_table_list(self.cursor) if
                  table in printed_tables]

        return sect, tables

#-----------------------------------------------------------------------------------------------------------------------

    def sort_dependencies(self, tables):

        dependencies = []
        for table_name in tables:
            relations = self.get_relations(table_name)
            rels = map(lambda x: relations[x][1], relations)
            dependencies.append([table_name,rels])

        order = []
        while len(dependencies):
            for dep in dependencies:
                if not len(dep[1]):
                    order.append(dep[0])
            dependencies = filter(lambda x: x[0] not in order, dependencies)
            for dep in dependencies:
                dep[1] = filter(lambda x : x not in order, dep[1])

        return order

#-----------------------------------------------------------------------------------------------------------------------

    def handle_inspection(self, options):
        self.connection = connections[options.get('database')]
        self.cursor = self.connection.cursor()

        layout_path = options.get('layout')
        sect, tables = self.get_configuration(layout_path)
        sections = sect.keys()
        order = self.sort_dependencies(tables)

        tmp = tempfile.mkdtemp()
        print 'Saving in ' + str(tmp)
        fp = open(os.path.join(tmp,'__init__.py'), 'w')
        fp.close()
        for name in sections:
            self.write_module(tmp, name, sect, order)

#-----------------------------------------------------------------------------------------------------------------------

    def get_field_type(self, connection, table_name, row):
        """
        Given the database connection, the table name, and the cursor row
        description, this routine will return the given field type name, as
        well as any additional keyword parameters and notes for the field.
        """
        field_params = {}
        field_notes = []

        try:
            field_type = connection.introspection.get_field_type(row[1], row)
        except KeyError:
            field_type = 'TextField'
            field_notes.append('This field type is a guess.')

        # This is a hook for DATA_TYPES_REVERSE to return a tuple of
        # (field_type, field_params_dict).
        if type(field_type) is tuple:
            field_type, new_params = field_type
            field_params.update(new_params)

        # Add max_length for all CharFields.
        if field_type == 'CharField' and row[3]:
            field_params['max_length'] = row[3]

        if 'DecimalField' in field_type:
            field_params['max_digits'] = row[4]
            field_params['decimal_places'] = row[5]

        return field_type, field_params, field_notes

#-----------------------------------------------------------------------------------------------------------------------

    def get_meta(self, table_name, uniqueTogether = None):
        """
        Return a sequence comprising the lines of code necessary
        to construct the inner Meta class for the model corresponding
        to the given database table name.
        """
        meta = 'pass'
        if uniqueTogether:
            fields = ''
            for u in uniqueTogether:
                fields += '(%s), ' % ", ".join(map(lambda x: '"%s"' %
                                                    x, uniqueTogether[u]))
            fields = '( ' + fields + ' )'
            meta = 'unique_together = %s' % fields
        return ['    class Meta(ChemblCoreAbstractModel.Meta):',
                '        %s' % meta,
                '']

#-----------------------------------------------------------------------------------------------------------------------