import yaml
import copy


class SchemaObject(object):
    """docstring for SchemaObject"""

    def __init__(self, parent, d):
        self.parent = parent
        if d is not None:
            cs = {'fields': Field, 'indexes': Index, 'references': Reference}
            for a, b in d.items():
                c = SchemaObject
                if a in cs:
                    c = cs[a]
                    if a == "fields" \
                        and isinstance(b, dict) \
                            and 'reference' in b:
                        c = Reference
                if isinstance(b, (list, tuple)):
                    o = [c(self, x) if isinstance(x, dict) else x for x in b]
                    setattr(self, a, o)
                else:
                    o = c(self, b) if isinstance(b, dict) else b
                    setattr(self, a, o)


class FieldType(SchemaObject):
    """docstring for FieldType"""

    def __init__(self, schema, d=None):
        self.schema = schema
        self.name = None
        self.type = 'string'
        self.size = 100
        self.nullable = False
        self.indexed = False
        self.unique = False
        SchemaObject.__init__(self, schema, d)


class Field(SchemaObject):
    """docstring for Field"""

    def __init__(self, model, d=None):
        self.model = model
        self.name = 'field'
        self.type = 'string'
        self.size = 100
        self.nullable = False
        self.indexed = False
        self.unique = False
        self.sequential = False
        self.key = False
        self.reference = None
        self.default = None
        SchemaObject.__init__(self, model, d)


class Reference(SchemaObject):
    """docstring for Reference"""

    def __init__(self, model, d=None):
        self.model = model
        self.name = ''
        self.to = None
        self.key = False
        self.nullable = False
        self.indexed = False
        self.unique = False
        SchemaObject.__init__(self, model, d)

    def get_referenced_model(self):
        return next(m for m in self.model.schema.models if m.name == self.to)


class Index(SchemaObject):
    """docstring for Index"""

    def __init__(self, model, d=None):
        self.model = model
        self.model = None
        self.fields = []
        self.unique = False
        SchemaObject.__init__(self, model, d)


class Model(SchemaObject):
    """docstring for Model"""

    def __init__(self, schema, d=None):
        self.schema = schema
        self.name = None
        self.type = 'persistent'
        self.inherits = None
        self.references = []
        self.fields = []
        self.indexes = []
        SchemaObject.__init__(self, schema, d)

    def get_super_model(self):
        sm = None
        if self.inherits is not None:
            sm = next(
                mi for mi
                in self.schema.models
                if mi.name == self.inherits
                )
        return sm

    def get_references(self):
        rs = []
        sm = self.get_super_model()
        if sm is not None:
            sm_rs = sm.get_references()
            for r in sm_rs:
                r.inherited = True
            rs.extend(sm_rs)
        rs.extend(self.references)
        return rs

    def get_indexes(self):
        xs = []
        sm = self.get_super_model()
        if sm is not None:
            xs.extend(sm.get_indexes())
        for f in (f for f in self.fields if f.indexed or f.unique):
            x = Index(self)
            if f.name not in x.fields:
                x.fields.append(f.name)
            x.unique = f.unique
            xs.append(x)
        if len(self.indexes) > 0:
            xs.extend(self.indexes)
        return xs

    def get_key_fields(self):
        ks = []
        sm = self.get_super_model()
        if sm is not None:
            ks.extend(sm.get_key_fields())
        ks.extend(list(n for n in self.fields if n.key))
        for r in (r for r in self.references if r.key):
            rm = r.get_referenced_model();
            for k in rm.get_key_fields():
                kk = copy.copy(k)
                kk.name = '_'.join([r.name or r.to, kk.name])
                ks.append(kk)
        return ks

    def get_reference_fields(self):
        rfs = []
        rs = self.get_references()
        for r in (r for r in rs if not r.key):
            rm = r.get_referenced_model();
            for k in rm.get_key_fields():
                kk = copy.copy(k)
                kk.name = '_'.join([r.name or r.to, kk.name])
                kk.sequential = False
                rfs.append(kk)
        return rfs

    def get_fields(self):
        fs = []
        sm = self.get_super_model()
        if sm is not None:
            sm_fs = sm.get_fields()
            for f in sm_fs:
                f.inherited = True
            fs.extend(sm_fs)
        fs.extend(list(f for f in self.fields if not f.key))
        return fs

    def render_field(self, f):
        b = [f.name]
        ft = next((ft for ft in self.schema.field_types if ft.name == f.type), None)
        if ft is not None:
            f = copy.copy(f)
            f.name = f.name or ft.name
            f.type = ft.type
            f.size = ft.size
            f.nullable = f.nullable or ft.nullable
            f.indexed = f.indexed or ft.indexed
            f.unique = f.unique or ft.unique
        if f.sequential:
            if f.type == 'bigint':
                b.append('bigserial')
            else:
                b.append('serial')
        else:
            if f.type == 'string':
                if f.size == -1:
                    b.append('text')
                else:
                    b.append('varchar({0})'.format(f.size))
            else:
                b.append(f.type)
        if f.nullable is False:
            b.append('not null')
        if f.default is not None:
            wrap = ''
            if f.type == 'string' or f.type == 'text':
                wrap = '\''
            b.append('default {1}{0}{1}'.format(f.default, wrap))
        return '    ' + ' '.join(b)

    def render_fields(self):
        b = []
        fs = []
        fs.extend(self.get_key_fields())
        fs.extend(self.get_reference_fields())
        fs.extend(self.get_fields())
        for f in fs:
            b.append(self.render_field(f))
        return ',\n'.join(b)

    def render_key(self):
        ks = self.get_key_fields()
        return 'alter table {0} add constraint pk_{0} primary key ({1});'.format(self.name, ', '.join(k.name for k in ks))

    def render_references(self):
        b = []
        rs = self.get_references()
        for r in rs:
            rm = r.get_referenced_model()
            rm_ks = rm.get_key_fields()
            b.append(
                'alter table {0} add constraint fk_{0}_{1} foreign key ({2}) references {1} ({3});'.format(
                    self.name,
                    r.to,
                    ', '.join('_'.join([r.name or r.to, k.name]) for k in rm_ks),
                    ', '.join(k.name for k in rm_ks)
                    )
                )
        return '\n'.join(b)

    def render_indexes(self):
        b = []
        xs = self.get_indexes()
        for x in xs:
            b.append('create index ix_{0}_{1} on {0} ({2});'.format(self.name, '_'.join(x.fields), ', '.join(x.fields)))
        return '\n'.join(b)

    def render(self, include_references=True, include_indexes=True):
        b = []
        b.append('drop table if exists {0} cascade;'.format(self.name))
        b.append('create table {0} ('.format(self.name))
        b.append(self.render_fields())
        b.append(');')
        b.append(self.render_key())
        if include_references and len(self.get_references()) > 0:
            b.append(self.render_references())
        if include_indexes and len(self.get_indexes()) > 0:
            b.append(self.render_indexes())
        b.append('\n')
        return '\n'.join(b)


class Schema(object):
    """docstring for Schema"""

    def __init__(self, path):
        super(Schema, self).__init__()
        self.path = path
        self.name = None
        self.field_types = []
        self.models = []

    def load(self):
        f = open(self.path, 'r')
        s = f.read()
        f.close()
        o = yaml.load(s)
        self.name = o['name']
        if 'fieldTypes' in o:
            for oo in o['fieldTypes']:
                self.field_types.append(FieldType(self, oo))

        if 'models' in o:
            for oo in o['models']:
                self.models.append(Model(self, oo))

    def render(self):
        field_map = {
            'string': 'varchar'
        }
        with open('sql/schema-generated.sql', 'w') as sql:
            for m in self.models:
                if m.type == 'abstract':
                    continue
                sql.write(m.render(False, False))

            b = []
            for m in self.models:
                if m.type == 'abstract':
                    continue
                b.append(m.render_references())
            b.append('')
            for m in self.models:
                if m.type == 'abstract':
                    continue
                b.append(m.render_indexes())
            sql.write('\n'.join(b))

s = Schema('sql/schema.yaml')
s.load()
s.render()