import re
import sys

from sqlalchemy import MetaData, Column, Table, Integer, String, Text, \
    Numeric, CHAR, ForeignKey, INTEGER, Index, UniqueConstraint, \
    TypeDecorator, CheckConstraint, text, PrimaryKeyConstraint
from sqlalchemy.types import NULLTYPE
from sqlalchemy.engine.reflection import Inspector

from alembic import autogenerate
from alembic.migration import MigrationContext
from alembic.testing import TestBase
from alembic.testing import config
from alembic.testing import assert_raises_message
from alembic.testing.mock import Mock
from alembic.testing.env import staging_env, clear_staging_env
from alembic.testing import eq_
from alembic.ddl.base import _fk_spec
from alembic.util import CommandError

py3k = sys.version_info >= (3, )

names_in_this_test = set()


def _default_include_object(obj, name, type_, reflected, compare_to):
    if type_ == "table":
        return name in names_in_this_test
    else:
        return True

_default_object_filters = [
    _default_include_object
]
from sqlalchemy import event


@event.listens_for(Table, "after_parent_attach")
def new_table(table, parent):
    names_in_this_test.add(table.name)


class _ComparesFKs(object):
    def _assert_fk_diff(
            self, diff, type_, source_table, source_columns,
            target_table, target_columns, name=None, conditional_name=None,
            source_schema=None):
        # the public API for ForeignKeyConstraint was not very rich
        # in 0.7, 0.8, so here we use the well-known but slightly
        # private API to get at its elements
        (fk_source_schema, fk_source_table,
         fk_source_columns, fk_target_schema, fk_target_table,
         fk_target_columns) = _fk_spec(diff[1])

        eq_(diff[0], type_)
        eq_(fk_source_table, source_table)
        eq_(fk_source_columns, source_columns)
        eq_(fk_target_table, target_table)
        eq_(fk_source_schema, source_schema)

        eq_([elem.column.name for elem in diff[1].elements],
            target_columns)
        if conditional_name is not None:
            if config.requirements.no_fk_names.enabled:
                eq_(diff[1].name, None)
            elif conditional_name == 'servergenerated':
                fks = Inspector.from_engine(self.bind).\
                    get_foreign_keys(source_table)
                server_fk_name = fks[0]['name']
                eq_(diff[1].name, server_fk_name)
            else:
                eq_(diff[1].name, conditional_name)
        else:
            eq_(diff[1].name, name)


class AutogenTest(_ComparesFKs):

    @classmethod
    def _get_bind(cls):
        return config.db

    configure_opts = {}

    @classmethod
    def setup_class(cls):
        staging_env()
        cls.bind = cls._get_bind()
        cls.m1 = cls._get_db_schema()
        cls.m1.create_all(cls.bind)
        cls.m2 = cls._get_model_schema()

    @classmethod
    def teardown_class(cls):
        cls.m1.drop_all(cls.bind)
        clear_staging_env()

    def setUp(self):
        self.conn = conn = self.bind.connect()
        ctx_opts = {
            'compare_type': True,
            'compare_server_default': True,
            'target_metadata': self.m2,
            'upgrade_token': "upgrades",
            'downgrade_token': "downgrades",
            'alembic_module_prefix': 'op.',
            'sqlalchemy_module_prefix': 'sa.',
        }
        if self.configure_opts:
            ctx_opts.update(self.configure_opts)
        self.context = context = MigrationContext.configure(
            connection=conn,
            opts=ctx_opts
        )

        connection = context.bind
        self.autogen_context = {
            'imports': set(),
            'connection': connection,
            'dialect': connection.dialect,
            'context': context
        }

    def tearDown(self):
        self.conn.close()


class AutogenFixtureTest(_ComparesFKs):

    def _fixture(
            self, m1, m2, include_schemas=False,
            opts=None, object_filters=_default_object_filters):
        self.metadata, model_metadata = m1, m2
        self.metadata.create_all(self.bind)

        with self.bind.connect() as conn:
            ctx_opts = {
                'compare_type': True,
                'compare_server_default': True,
                'target_metadata': model_metadata,
                'upgrade_token': "upgrades",
                'downgrade_token': "downgrades",
                'alembic_module_prefix': 'op.',
                'sqlalchemy_module_prefix': 'sa.',
            }
            if opts:
                ctx_opts.update(opts)
            self.context = context = MigrationContext.configure(
                connection=conn,
                opts=ctx_opts
            )

            connection = context.bind
            autogen_context = {
                'imports': set(),
                'connection': connection,
                'dialect': connection.dialect,
                'context': context
            }
            diffs = []
            autogenerate._produce_net_changes(
                connection, model_metadata, diffs,
                autogen_context,
                object_filters=object_filters,
                include_schemas=include_schemas
            )
            return diffs

    reports_unnamed_constraints = False

    def setUp(self):
        staging_env()
        self.bind = config.db

    def tearDown(self):
        if hasattr(self, 'metadata'):
            self.metadata.drop_all(self.bind)
        clear_staging_env()


class AutogenCrossSchemaTest(AutogenTest, TestBase):
    __only_on__ = 'postgresql'

    @classmethod
    def _get_db_schema(cls):
        m = MetaData()
        Table('t1', m,
              Column('x', Integer)
              )
        Table('t2', m,
              Column('y', Integer),
              schema=config.test_schema
              )
        Table('t6', m,
              Column('u', Integer)
              )
        Table('t7', m,
              Column('v', Integer),
              schema=config.test_schema
              )

        return m

    @classmethod
    def _get_model_schema(cls):
        m = MetaData()
        Table('t3', m,
              Column('q', Integer)
              )
        Table('t4', m,
              Column('z', Integer),
              schema=config.test_schema
              )
        Table('t6', m,
              Column('u', Integer)
              )
        Table('t7', m,
              Column('v', Integer),
              schema=config.test_schema
              )
        return m

    def test_default_schema_omitted_upgrade(self):
        metadata = self.m2
        connection = self.context.bind
        diffs = []

        def include_object(obj, name, type_, reflected, compare_to):
            if type_ == "table":
                return name == "t3"
            else:
                return True
        autogenerate._produce_net_changes(connection, metadata, diffs,
                                          self.autogen_context,
                                          object_filters=[include_object],
                                          include_schemas=True
                                          )
        eq_(diffs[0][0], "add_table")
        eq_(diffs[0][1].schema, None)

    def test_alt_schema_included_upgrade(self):
        metadata = self.m2
        connection = self.context.bind
        diffs = []

        def include_object(obj, name, type_, reflected, compare_to):
            if type_ == "table":
                return name == "t4"
            else:
                return True
        autogenerate._produce_net_changes(connection, metadata, diffs,
                                          self.autogen_context,
                                          object_filters=[include_object],
                                          include_schemas=True
                                          )
        eq_(diffs[0][0], "add_table")
        eq_(diffs[0][1].schema, config.test_schema)

    def test_default_schema_omitted_downgrade(self):
        metadata = self.m2
        connection = self.context.bind
        diffs = []

        def include_object(obj, name, type_, reflected, compare_to):
            if type_ == "table":
                return name == "t1"
            else:
                return True
        autogenerate._produce_net_changes(connection, metadata, diffs,
                                          self.autogen_context,
                                          object_filters=[include_object],
                                          include_schemas=True
                                          )
        eq_(diffs[0][0], "remove_table")
        eq_(diffs[0][1].schema, None)

    def test_alt_schema_included_downgrade(self):
        metadata = self.m2
        connection = self.context.bind
        diffs = []

        def include_object(obj, name, type_, reflected, compare_to):
            if type_ == "table":
                return name == "t2"
            else:
                return True
        autogenerate._produce_net_changes(connection, metadata, diffs,
                                          self.autogen_context,
                                          object_filters=[include_object],
                                          include_schemas=True
                                          )
        eq_(diffs[0][0], "remove_table")
        eq_(diffs[0][1].schema, config.test_schema)


class AutogenDefaultSchemaTest(AutogenFixtureTest, TestBase):
    __only_on__ = 'postgresql'

    def test_uses_explcit_schema_in_default_one(self):

        default_schema = self.bind.dialect.default_schema_name

        m1 = MetaData()
        m2 = MetaData()

        Table('a', m1, Column('x', String(50)))
        Table('a', m2, Column('x', String(50)), schema=default_schema)

        diffs = self._fixture(m1, m2, include_schemas=True)
        eq_(diffs, [])

    def test_uses_explcit_schema_in_default_two(self):

        default_schema = self.bind.dialect.default_schema_name

        m1 = MetaData()
        m2 = MetaData()

        Table('a', m1, Column('x', String(50)))
        Table('a', m2, Column('x', String(50)), schema=default_schema)
        Table('a', m2, Column('y', String(50)), schema="test_schema")

        diffs = self._fixture(m1, m2, include_schemas=True)
        eq_(len(diffs), 1)
        eq_(diffs[0][0], "add_table")
        eq_(diffs[0][1].schema, "test_schema")
        eq_(diffs[0][1].c.keys(), ['y'])

    def test_uses_explcit_schema_in_default_three(self):

        default_schema = self.bind.dialect.default_schema_name

        m1 = MetaData()
        m2 = MetaData()

        Table('a', m1, Column('y', String(50)), schema="test_schema")

        Table('a', m2, Column('x', String(50)), schema=default_schema)
        Table('a', m2, Column('y', String(50)), schema="test_schema")

        diffs = self._fixture(m1, m2, include_schemas=True)
        eq_(len(diffs), 1)
        eq_(diffs[0][0], "add_table")
        eq_(diffs[0][1].schema, default_schema)
        eq_(diffs[0][1].c.keys(), ['x'])


class ModelOne(object):
    __requires__ = ('unique_constraint_reflection', )

    schema = None

    @classmethod
    def _get_db_schema(cls):
        schema = cls.schema

        m = MetaData(schema=schema)

        Table('user', m,
              Column('id', Integer, primary_key=True),
              Column('name', String(50)),
              Column('a1', Text),
              Column("pw", String(50)),
              Index('pw_idx', 'pw')
              )

        Table('address', m,
              Column('id', Integer, primary_key=True),
              Column('email_address', String(100), nullable=False),
              )

        Table('order', m,
              Column('order_id', Integer, primary_key=True),
              Column("amount", Numeric(8, 2), nullable=False,
                     server_default=text("0")),
              CheckConstraint('amount >= 0', name='ck_order_amount')
              )

        Table('extra', m,
              Column("x", CHAR),
              Column('uid', Integer, ForeignKey('user.id'))
              )

        return m

    @classmethod
    def _get_model_schema(cls):
        schema = cls.schema

        m = MetaData(schema=schema)

        Table('user', m,
              Column('id', Integer, primary_key=True),
              Column('name', String(50), nullable=False),
              Column('a1', Text, server_default="x")
              )

        Table('address', m,
              Column('id', Integer, primary_key=True),
              Column('email_address', String(100), nullable=False),
              Column('street', String(50)),
              UniqueConstraint('email_address', name="uq_email")
              )

        Table('order', m,
              Column('order_id', Integer, primary_key=True),
              Column('amount', Numeric(10, 2), nullable=True,
                     server_default=text("0")),
              Column('user_id', Integer, ForeignKey('user.id')),
              CheckConstraint('amount > -1', name='ck_order_amount'),
              )

        Table('item', m,
              Column('id', Integer, primary_key=True),
              Column('description', String(100)),
              Column('order_id', Integer, ForeignKey('order.order_id')),
              CheckConstraint('len(description) > 5')
              )
        return m


class AutogenerateDiffTest(ModelOne, AutogenTest, TestBase):
    __only_on__ = 'sqlite'

    def test_diffs(self):
        """test generation of diff rules"""

        metadata = self.m2
        connection = self.context.bind
        diffs = []
        autogenerate._produce_net_changes(
            connection, metadata, diffs,
            self.autogen_context,
            object_filters=_default_object_filters,
        )

        eq_(
            diffs[0],
            ('add_table', metadata.tables['item'])
        )

        eq_(diffs[1][0], 'remove_table')
        eq_(diffs[1][1].name, "extra")

        eq_(diffs[2][0], "add_column")
        eq_(diffs[2][1], None)
        eq_(diffs[2][2], "address")
        eq_(diffs[2][3], metadata.tables['address'].c.street)

        eq_(diffs[3][0], "add_constraint")
        eq_(diffs[3][1].name, "uq_email")

        eq_(diffs[4][0], "add_column")
        eq_(diffs[4][1], None)
        eq_(diffs[4][2], "order")
        eq_(diffs[4][3], metadata.tables['order'].c.user_id)

        eq_(diffs[5][0][0], "modify_type")
        eq_(diffs[5][0][1], None)
        eq_(diffs[5][0][2], "order")
        eq_(diffs[5][0][3], "amount")
        eq_(repr(diffs[5][0][5]), "NUMERIC(precision=8, scale=2)")
        eq_(repr(diffs[5][0][6]), "Numeric(precision=10, scale=2)")

        self._assert_fk_diff(
            diffs[6], "add_fk",
            "order", ["user_id"],
            "user", ["id"]
        )

        eq_(diffs[7][0][0], "modify_default")
        eq_(diffs[7][0][1], None)
        eq_(diffs[7][0][2], "user")
        eq_(diffs[7][0][3], "a1")
        eq_(diffs[7][0][6].arg, "x")

        eq_(diffs[8][0][0], 'modify_nullable')
        eq_(diffs[8][0][5], True)
        eq_(diffs[8][0][6], False)

        eq_(diffs[9][0], 'remove_index')
        eq_(diffs[9][1].name, 'pw_idx')

        eq_(diffs[10][0], 'remove_column')
        eq_(diffs[10][3].name, 'pw')

    def test_render_nothing(self):
        context = MigrationContext.configure(
            connection=self.bind.connect(),
            opts={
                'compare_type': True,
                'compare_server_default': True,
                'target_metadata': self.m1,
                'upgrade_token': "upgrades",
                'downgrade_token': "downgrades",
            }
        )
        template_args = {}
        autogenerate._produce_migration_diffs(context, template_args, set())

        eq_(re.sub(r"u'", "'", template_args['upgrades']),
            """### commands auto generated by Alembic - please adjust! ###
    pass
    ### end Alembic commands ###""")
        eq_(re.sub(r"u'", "'", template_args['downgrades']),
            """### commands auto generated by Alembic - please adjust! ###
    pass
    ### end Alembic commands ###""")

    def test_render_nothing_batch(self):
        context = MigrationContext.configure(
            connection=self.bind.connect(),
            opts={
                'compare_type': True,
                'compare_server_default': True,
                'target_metadata': self.m1,
                'upgrade_token': "upgrades",
                'downgrade_token': "downgrades",
                'alembic_module_prefix': 'op.',
                'sqlalchemy_module_prefix': 'sa.',
                'render_as_batch': True
            }
        )
        template_args = {}
        autogenerate._produce_migration_diffs(
            context, template_args, set(),
            include_symbol=lambda name, schema: False
        )
        eq_(re.sub(r"u'", "'", template_args['upgrades']),
            """### commands auto generated by Alembic - please adjust! ###
    pass
    ### end Alembic commands ###""")
        eq_(re.sub(r"u'", "'", template_args['downgrades']),
            """### commands auto generated by Alembic - please adjust! ###
    pass
    ### end Alembic commands ###""")

    def test_render_diffs_standard(self):
        """test a full render including indentation"""

        template_args = {}
        autogenerate._produce_migration_diffs(
            self.context, template_args, set())
        eq_(re.sub(r"u'", "'", template_args['upgrades']),
            """### commands auto generated by Alembic - please adjust! ###
    op.create_table('item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(length=100), nullable=True),
    sa.Column('order_id', sa.Integer(), nullable=True),
    sa.CheckConstraint('len(description) > 5'),
    sa.ForeignKeyConstraint(['order_id'], ['order.order_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('extra')
    op.add_column('address', sa.Column('street', sa.String(length=50), \
nullable=True))
    op.create_unique_constraint('uq_email', 'address', ['email_address'])
    op.add_column('order', sa.Column('user_id', sa.Integer(), nullable=True))
    op.alter_column('order', 'amount',
               existing_type=sa.NUMERIC(precision=8, scale=2),
               type_=sa.Numeric(precision=10, scale=2),
               nullable=True,
               existing_server_default=sa.text('0'))
    op.create_foreign_key(None, 'order', 'user', ['user_id'], ['id'])
    op.alter_column('user', 'a1',
               existing_type=sa.TEXT(),
               server_default='x',
               existing_nullable=True)
    op.alter_column('user', 'name',
               existing_type=sa.VARCHAR(length=50),
               nullable=False)
    op.drop_index('pw_idx', table_name='user')
    op.drop_column('user', 'pw')
    ### end Alembic commands ###""")

        eq_(re.sub(r"u'", "'", template_args['downgrades']),
            """### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('pw', sa.VARCHAR(length=50), \
nullable=True))
    op.create_index('pw_idx', 'user', ['pw'], unique=False)
    op.alter_column('user', 'name',
               existing_type=sa.VARCHAR(length=50),
               nullable=True)
    op.alter_column('user', 'a1',
               existing_type=sa.TEXT(),
               server_default=None,
               existing_nullable=True)
    op.drop_constraint(None, 'order', type_='foreignkey')
    op.alter_column('order', 'amount',
               existing_type=sa.Numeric(precision=10, scale=2),
               type_=sa.NUMERIC(precision=8, scale=2),
               nullable=False,
               existing_server_default=sa.text('0'))
    op.drop_column('order', 'user_id')
    op.drop_constraint('uq_email', 'address', type_='unique')
    op.drop_column('address', 'street')
    op.create_table('extra',
    sa.Column('x', sa.CHAR(), nullable=True),
    sa.Column('uid', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['uid'], ['user.id'], )
    )
    op.drop_table('item')
    ### end Alembic commands ###""")

    def test_render_diffs_batch(self):
        """test a full render in batch mode including indentation"""

        template_args = {}
        self.context.opts['render_as_batch'] = True
        autogenerate._produce_migration_diffs(
            self.context, template_args, set())

        eq_(re.sub(r"u'", "'", template_args['upgrades']),
            """### commands auto generated by Alembic - please adjust! ###
    op.create_table('item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(length=100), nullable=True),
    sa.Column('order_id', sa.Integer(), nullable=True),
    sa.CheckConstraint('len(description) > 5'),
    sa.ForeignKeyConstraint(['order_id'], ['order.order_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('extra')
    with op.batch_alter_table('address', schema=None) as batch_op:
        batch_op.add_column(sa.Column('street', sa.String(length=50), nullable=True))
        batch_op.create_unique_constraint('uq_email', ['email_address'])

    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.alter_column('amount',
               existing_type=sa.NUMERIC(precision=8, scale=2),
               type_=sa.Numeric(precision=10, scale=2),
               nullable=True,
               existing_server_default=sa.text('0'))
        batch_op.create_foreign_key(None, 'order', 'user', ['user_id'], ['id'])

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('a1',
               existing_type=sa.TEXT(),
               server_default='x',
               existing_nullable=True)
        batch_op.alter_column('name',
               existing_type=sa.VARCHAR(length=50),
               nullable=False)
        batch_op.drop_index('pw_idx')
        batch_op.drop_column('pw')

    ### end Alembic commands ###""")

        eq_(re.sub(r"u'", "'", template_args['downgrades']),
            """### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('pw', sa.VARCHAR(length=50), nullable=True))
        batch_op.create_index('pw_idx', ['pw'], unique=False)
        batch_op.alter_column('name',
               existing_type=sa.VARCHAR(length=50),
               nullable=True)
        batch_op.alter_column('a1',
               existing_type=sa.TEXT(),
               server_default=None,
               existing_nullable=True)

    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.alter_column('amount',
               existing_type=sa.Numeric(precision=10, scale=2),
               type_=sa.NUMERIC(precision=8, scale=2),
               nullable=False,
               existing_server_default=sa.text('0'))
        batch_op.drop_column('user_id')

    with op.batch_alter_table('address', schema=None) as batch_op:
        batch_op.drop_constraint('uq_email', type_='unique')
        batch_op.drop_column('street')

    op.create_table('extra',
    sa.Column('x', sa.CHAR(), nullable=True),
    sa.Column('uid', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['uid'], ['user.id'], )
    )
    op.drop_table('item')
    ### end Alembic commands ###""")

    def test_include_symbol(self):
        context = MigrationContext.configure(
            connection=self.bind.connect(),
            opts={
                'compare_type': True,
                'compare_server_default': True,
                'target_metadata': self.m2,
                'include_symbol': lambda name, schema=None:
                name in ('address', 'order'),
                'upgrade_token': "upgrades",
                'downgrade_token': "downgrades",
                'alembic_module_prefix': 'op.',
                'sqlalchemy_module_prefix': 'sa.',
            }
        )
        template_args = {}
        autogenerate._produce_migration_diffs(context, template_args, set())
        template_args['upgrades'] = \
            template_args['upgrades'].replace("u'", "'")
        template_args['downgrades'] = template_args['downgrades'].\
            replace("u'", "'")
        assert "alter_column('user'" not in template_args['upgrades']
        assert "alter_column('user'" not in template_args['downgrades']
        assert "alter_column('order'" in template_args['upgrades']
        assert "alter_column('order'" in template_args['downgrades']

    def test_include_object(self):
        def include_object(obj, name, type_, reflected, compare_to):
            assert obj.name == name
            if type_ == "table":
                if reflected:
                    assert obj.metadata is not self.m2
                else:
                    assert obj.metadata is self.m2
                return name in ("address", "order", "user")
            elif type_ == "column":
                if reflected:
                    assert obj.table.metadata is not self.m2
                else:
                    assert obj.table.metadata is self.m2
                return name != "street"
            else:
                return True

        context = MigrationContext.configure(
            connection=self.bind.connect(),
            opts={
                'compare_type': True,
                'compare_server_default': True,
                'target_metadata': self.m2,
                'include_object': include_object,
                'upgrade_token': "upgrades",
                'downgrade_token': "downgrades",
                'alembic_module_prefix': 'op.',
                'sqlalchemy_module_prefix': 'sa.',
            }
        )
        template_args = {}
        autogenerate._produce_migration_diffs(context, template_args, set())

        template_args['upgrades'] = \
            template_args['upgrades'].replace("u'", "'")
        template_args['downgrades'] = template_args['downgrades'].\
            replace("u'", "'")
        assert "op.create_table('item'" not in template_args['upgrades']
        assert "op.create_table('item'" not in template_args['downgrades']

        assert "alter_column('user'" in template_args['upgrades']
        assert "alter_column('user'" in template_args['downgrades']
        assert "'street'" not in template_args['upgrades']
        assert "'street'" not in template_args['downgrades']
        assert "alter_column('order'" in template_args['upgrades']
        assert "alter_column('order'" in template_args['downgrades']

    def test_skip_null_type_comparison_reflected(self):
        diff = []
        autogenerate.compare._compare_type(None, "sometable", "somecol",
                                           Column("somecol", NULLTYPE),
                                           Column("somecol", Integer()),
                                           diff, self.autogen_context
                                           )
        assert not diff

    def test_skip_null_type_comparison_local(self):
        diff = []
        autogenerate.compare._compare_type(None, "sometable", "somecol",
                                           Column("somecol", Integer()),
                                           Column("somecol", NULLTYPE),
                                           diff, self.autogen_context
                                           )
        assert not diff

    def test_affinity_typedec(self):
        class MyType(TypeDecorator):
            impl = CHAR

            def load_dialect_impl(self, dialect):
                if dialect.name == 'sqlite':
                    return dialect.type_descriptor(Integer())
                else:
                    return dialect.type_descriptor(CHAR(32))

        diff = []
        autogenerate.compare._compare_type(
            None, "sometable", "somecol",
            Column("somecol", Integer, nullable=True),
            Column("somecol", MyType()),
            diff, self.autogen_context
        )
        assert not diff

    def test_dont_barf_on_already_reflected(self):
        diffs = []
        from sqlalchemy.util import OrderedSet
        inspector = Inspector.from_engine(self.bind)
        autogenerate.compare._compare_tables(
            OrderedSet([(None, 'extra'), (None, 'user')]),
            OrderedSet(), [], inspector,
            MetaData(), diffs, self.autogen_context
        )
        eq_(
            [(rec[0], rec[1].name) for rec in diffs],
            [('remove_table', 'extra'), ('remove_table', 'user')]
        )


class AutogenerateDiffTestWSchema(ModelOne, AutogenTest, TestBase):
    __only_on__ = 'postgresql'
    schema = "test_schema"

    def test_diffs(self):
        """test generation of diff rules"""

        metadata = self.m2
        connection = self.context.bind
        diffs = []
        autogenerate._produce_net_changes(
            connection, metadata, diffs,
            self.autogen_context,
            object_filters=_default_object_filters,
            include_schemas=True
        )

        eq_(
            diffs[0],
            ('add_table', metadata.tables['%s.item' % self.schema])
        )

        eq_(diffs[1][0], 'remove_table')
        eq_(diffs[1][1].name, "extra")

        eq_(diffs[2][0], "add_column")
        eq_(diffs[2][1], self.schema)
        eq_(diffs[2][2], "address")
        eq_(diffs[2][3], metadata.tables['%s.address' % self.schema].c.street)

        eq_(diffs[3][0], "add_constraint")
        eq_(diffs[3][1].name, "uq_email")

        eq_(diffs[4][0], "add_column")
        eq_(diffs[4][1], self.schema)
        eq_(diffs[4][2], "order")
        eq_(diffs[4][3], metadata.tables['%s.order' % self.schema].c.user_id)

        eq_(diffs[5][0][0], "modify_type")
        eq_(diffs[5][0][1], self.schema)
        eq_(diffs[5][0][2], "order")
        eq_(diffs[5][0][3], "amount")
        eq_(repr(diffs[5][0][5]), "NUMERIC(precision=8, scale=2)")
        eq_(repr(diffs[5][0][6]), "Numeric(precision=10, scale=2)")

        self._assert_fk_diff(
            diffs[6], "add_fk",
            "order", ["user_id"],
            "user", ["id"],
            source_schema=config.test_schema
        )

        eq_(diffs[7][0][0], "modify_default")
        eq_(diffs[7][0][1], self.schema)
        eq_(diffs[7][0][2], "user")
        eq_(diffs[7][0][3], "a1")
        eq_(diffs[7][0][6].arg, "x")

        eq_(diffs[8][0][0], 'modify_nullable')
        eq_(diffs[8][0][5], True)
        eq_(diffs[8][0][6], False)

        eq_(diffs[9][0], 'remove_index')
        eq_(diffs[9][1].name, 'pw_idx')

        eq_(diffs[10][0], 'remove_column')
        eq_(diffs[10][3].name, 'pw')

    def test_render_nothing(self):
        context = MigrationContext.configure(
            connection=self.bind.connect(),
            opts={
                'compare_type': True,
                'compare_server_default': True,
                'target_metadata': self.m1,
                'upgrade_token': "upgrades",
                'downgrade_token': "downgrades",
                'alembic_module_prefix': 'op.',
                'sqlalchemy_module_prefix': 'sa.',
            }
        )
        template_args = {}
        autogenerate._produce_migration_diffs(
            context, template_args, set(),
            include_symbol=lambda name, schema: False
        )
        eq_(re.sub(r"u'", "'", template_args['upgrades']),
            """### commands auto generated by Alembic - please adjust! ###
    pass
    ### end Alembic commands ###""")
        eq_(re.sub(r"u'", "'", template_args['downgrades']),
            """### commands auto generated by Alembic - please adjust! ###
    pass
    ### end Alembic commands ###""")

    def test_render_diffs_extras(self):
        """test a full render including indentation (include and schema)"""

        template_args = {}
        autogenerate._produce_migration_diffs(
            self.context, template_args, set(),
            include_object=_default_include_object,
            include_schemas=True
        )

        eq_(re.sub(r"u'", "'", template_args['upgrades']),
            """### commands auto generated by Alembic - please adjust! ###
    op.create_table('item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(length=100), nullable=True),
    sa.Column('order_id', sa.Integer(), nullable=True),
    sa.CheckConstraint('len(description) > 5'),
    sa.ForeignKeyConstraint(['order_id'], ['%(schema)s.order.order_id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='%(schema)s'
    )
    op.drop_table('extra', schema='%(schema)s')
    op.add_column('address', sa.Column('street', sa.String(length=50), \
nullable=True), schema='%(schema)s')
    op.create_unique_constraint('uq_email', 'address', ['email_address'], \
schema='test_schema')
    op.add_column('order', sa.Column('user_id', sa.Integer(), nullable=True), \
schema='%(schema)s')
    op.alter_column('order', 'amount',
               existing_type=sa.NUMERIC(precision=8, scale=2),
               type_=sa.Numeric(precision=10, scale=2),
               nullable=True,
               existing_server_default=sa.text('0'),
               schema='%(schema)s')
    op.create_foreign_key(None, 'order', 'user', ['user_id'], ['id'], \
source_schema='%(schema)s', referent_schema='%(schema)s')
    op.alter_column('user', 'a1',
               existing_type=sa.TEXT(),
               server_default='x',
               existing_nullable=True,
               schema='%(schema)s')
    op.alter_column('user', 'name',
               existing_type=sa.VARCHAR(length=50),
               nullable=False,
               schema='%(schema)s')
    op.drop_index('pw_idx', table_name='user', schema='test_schema')
    op.drop_column('user', 'pw', schema='%(schema)s')
    ### end Alembic commands ###""" % {"schema": self.schema})

        eq_(re.sub(r"u'", "'", template_args['downgrades']),
            """### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('pw', sa.VARCHAR(length=50), \
autoincrement=False, nullable=True), schema='%(schema)s')
    op.create_index('pw_idx', 'user', ['pw'], unique=False, schema='%(schema)s')
    op.alter_column('user', 'name',
               existing_type=sa.VARCHAR(length=50),
               nullable=True,
               schema='%(schema)s')
    op.alter_column('user', 'a1',
               existing_type=sa.TEXT(),
               server_default=None,
               existing_nullable=True,
               schema='%(schema)s')
    op.drop_constraint(None, 'order', schema='%(schema)s', type_='foreignkey')
    op.alter_column('order', 'amount',
               existing_type=sa.Numeric(precision=10, scale=2),
               type_=sa.NUMERIC(precision=8, scale=2),
               nullable=False,
               existing_server_default=sa.text('0'),
               schema='%(schema)s')
    op.drop_column('order', 'user_id', schema='%(schema)s')
    op.drop_constraint('uq_email', 'address', schema='test_schema', type_='unique')
    op.drop_column('address', 'street', schema='%(schema)s')
    op.create_table('extra',
    sa.Column('x', sa.CHAR(length=1), autoincrement=False, nullable=True),
    sa.Column('uid', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['uid'], ['%(schema)s.user.id'], \
name='extra_uid_fkey'),
    schema='%(schema)s'
    )
    op.drop_table('item', schema='%(schema)s')
    ### end Alembic commands ###""" % {"schema": self.schema})


class AutogenerateCustomCompareTypeTest(AutogenTest, TestBase):
    __only_on__ = 'sqlite'

    @classmethod
    def _get_db_schema(cls):
        m = MetaData()

        Table('sometable', m,
              Column('id', Integer, primary_key=True),
              Column('value', Integer))
        return m

    @classmethod
    def _get_model_schema(cls):
        m = MetaData()

        Table('sometable', m,
              Column('id', Integer, primary_key=True),
              Column('value', String))
        return m

    def test_uses_custom_compare_type_function(self):
        my_compare_type = Mock()
        self.context._user_compare_type = my_compare_type

        diffs = []
        autogenerate._produce_net_changes(self.context.bind, self.m2,
                                          diffs, self.autogen_context)

        first_table = self.m2.tables['sometable']
        first_column = first_table.columns['id']

        eq_(len(my_compare_type.mock_calls), 2)

        # We'll just test the first call
        _, args, _ = my_compare_type.mock_calls[0]
        (context, inspected_column, metadata_column,
         inspected_type, metadata_type) = args
        eq_(context, self.context)
        eq_(metadata_column, first_column)
        eq_(metadata_type, first_column.type)
        eq_(inspected_column.name, first_column.name)
        eq_(type(inspected_type), INTEGER)

    def test_column_type_not_modified_custom_compare_type_returns_False(self):
        my_compare_type = Mock()
        my_compare_type.return_value = False
        self.context._user_compare_type = my_compare_type

        diffs = []
        autogenerate._produce_net_changes(self.context.bind, self.m2,
                                          diffs, self.autogen_context)

        eq_(diffs, [])

    def test_column_type_modified_custom_compare_type_returns_True(self):
        my_compare_type = Mock()
        my_compare_type.return_value = True
        self.context._user_compare_type = my_compare_type

        diffs = []
        autogenerate._produce_net_changes(self.context.bind, self.m2,
                                          diffs, self.autogen_context)

        eq_(diffs[0][0][0], 'modify_type')
        eq_(diffs[1][0][0], 'modify_type')


class PKConstraintUpgradesIgnoresNullableTest(AutogenTest, TestBase):
    __backend__ = True

    # test workaround for SQLAlchemy issue #3023, alembic issue #199
    @classmethod
    def _get_db_schema(cls):
        m = MetaData()

        Table(
            'person_to_role', m,
            Column('person_id', Integer, autoincrement=False),
            Column('role_id', Integer, autoincrement=False),
            PrimaryKeyConstraint('person_id', 'role_id')
        )
        return m

    @classmethod
    def _get_model_schema(cls):
        return cls._get_db_schema()

    def test_no_change(self):
        metadata = self.m2
        connection = self.context.bind

        diffs = []

        autogenerate._produce_net_changes(connection, metadata, diffs,
                                          self.autogen_context
                                          )
        eq_(diffs, [])


class AutogenKeyTest(AutogenTest, TestBase):
    __only_on__ = 'sqlite'

    @classmethod
    def _get_db_schema(cls):
        m = MetaData()

        Table('someothertable', m,
              Column('id', Integer, primary_key=True),
              Column('value', Integer, key="somekey"),
              )
        return m

    @classmethod
    def _get_model_schema(cls):
        m = MetaData()

        Table('sometable', m,
              Column('id', Integer, primary_key=True),
              Column('value', Integer, key="someotherkey"),
              )
        Table('someothertable', m,
              Column('id', Integer, primary_key=True),
              Column('value', Integer, key="somekey"),
              Column("othervalue", Integer, key="otherkey")
              )
        return m

    symbols = ['someothertable', 'sometable']

    def test_autogen(self):
        metadata = self.m2
        connection = self.context.bind

        diffs = []

        autogenerate._produce_net_changes(connection, metadata, diffs,
                                          self.autogen_context,
                                          include_schemas=False
                                          )
        eq_(diffs[0][0], "add_table")
        eq_(diffs[0][1].name, "sometable")
        eq_(diffs[1][0], "add_column")
        eq_(diffs[1][3].key, "otherkey")


class AutogenVersionTableTest(AutogenTest, TestBase):
    __only_on__ = 'sqlite'
    version_table_name = 'alembic_version'
    version_table_schema = None

    @classmethod
    def _get_db_schema(cls):
        m = MetaData()
        Table(
            cls.version_table_name, m,
            Column('x', Integer), schema=cls.version_table_schema)
        return m

    @classmethod
    def _get_model_schema(cls):
        m = MetaData()
        return m

    def test_no_version_table(self):
        diffs = []
        autogenerate._produce_net_changes(self.context.bind, self.m2,
                                          diffs, self.autogen_context)
        eq_(diffs, [])

    def test_version_table_in_target(self):
        diffs = []
        Table(
            self.version_table_name,
            self.m2, Column('x', Integer), schema=self.version_table_schema)

        autogenerate._produce_net_changes(self.context.bind, self.m2,
                                          diffs, self.autogen_context)
        eq_(diffs, [])


class AutogenCustomVersionTableSchemaTest(AutogenVersionTableTest):
    __only_on__ = 'postgresql'
    version_table_schema = 'test_schema'
    configure_opts = {'version_table_schema': 'test_schema'}


class AutogenCustomVersionTableTest(AutogenVersionTableTest):
    version_table_name = 'my_version_table'
    configure_opts = {'version_table': 'my_version_table'}


class AutogenCustomVersionTableAndSchemaTest(AutogenVersionTableTest):
    __only_on__ = 'postgresql'
    version_table_name = 'my_version_table'
    version_table_schema = 'test_schema'
    configure_opts = {
        'version_table': 'my_version_table',
        'version_table_schema': 'test_schema'}


class AutogenerateDiffOrderTest(AutogenTest, TestBase):
    __only_on__ = 'sqlite'

    @classmethod
    def _get_db_schema(cls):
        return MetaData()

    @classmethod
    def _get_model_schema(cls):
        m = MetaData()
        Table('parent', m,
              Column('id', Integer, primary_key=True)
              )

        Table('child', m,
              Column('parent_id', Integer, ForeignKey('parent.id')),
              )

        return m

    def test_diffs_order(self):
        """
        Added in order to test that child tables(tables with FKs) are generated
        before their parent tables
        """

        metadata = self.m2
        connection = self.context.bind
        diffs = []

        autogenerate._produce_net_changes(connection, metadata, diffs,
                                          self.autogen_context
                                          )

        eq_(diffs[0][0], 'add_table')
        eq_(diffs[0][1].name, "parent")
        eq_(diffs[1][0], 'add_table')
        eq_(diffs[1][1].name, "child")


class CompareMetadataTest(ModelOne, AutogenTest, TestBase):
    __only_on__ = 'sqlite'

    def test_compare_metadata(self):
        metadata = self.m2

        diffs = autogenerate.compare_metadata(self.context, metadata)

        eq_(
            diffs[0],
            ('add_table', metadata.tables['item'])
        )

        eq_(diffs[1][0], 'remove_table')
        eq_(diffs[1][1].name, "extra")

        eq_(diffs[2][0], "add_column")
        eq_(diffs[2][1], None)
        eq_(diffs[2][2], "address")
        eq_(diffs[2][3], metadata.tables['address'].c.street)

        eq_(diffs[3][0], "add_constraint")
        eq_(diffs[3][1].name, "uq_email")

        eq_(diffs[4][0], "add_column")
        eq_(diffs[4][1], None)
        eq_(diffs[4][2], "order")
        eq_(diffs[4][3], metadata.tables['order'].c.user_id)

        eq_(diffs[5][0][0], "modify_type")
        eq_(diffs[5][0][1], None)
        eq_(diffs[5][0][2], "order")
        eq_(diffs[5][0][3], "amount")
        eq_(repr(diffs[5][0][5]), "NUMERIC(precision=8, scale=2)")
        eq_(repr(diffs[5][0][6]), "Numeric(precision=10, scale=2)")

        self._assert_fk_diff(
            diffs[6], "add_fk",
            "order", ["user_id"],
            "user", ["id"]
        )

        eq_(diffs[7][0][0], "modify_default")
        eq_(diffs[7][0][1], None)
        eq_(diffs[7][0][2], "user")
        eq_(diffs[7][0][3], "a1")
        eq_(diffs[7][0][6].arg, "x")

        eq_(diffs[8][0][0], 'modify_nullable')
        eq_(diffs[8][0][5], True)
        eq_(diffs[8][0][6], False)

        eq_(diffs[9][0], 'remove_index')
        eq_(diffs[9][1].name, 'pw_idx')

        eq_(diffs[10][0], 'remove_column')
        eq_(diffs[10][3].name, 'pw')

    def test_compare_metadata_include_object(self):
        metadata = self.m2

        def include_object(obj, name, type_, reflected, compare_to):
            if type_ == "table":
                return name in ("extra", "order")
            elif type_ == "column":
                return name != "amount"
            else:
                return True

        context = MigrationContext.configure(
            connection=self.bind.connect(),
            opts={
                'compare_type': True,
                'compare_server_default': True,
                'include_object': include_object,
            }
        )

        diffs = autogenerate.compare_metadata(context, metadata)

        eq_(diffs[0][0], 'remove_table')
        eq_(diffs[0][1].name, "extra")

        eq_(diffs[1][0], "add_column")
        eq_(diffs[1][1], None)
        eq_(diffs[1][2], "order")
        eq_(diffs[1][3], metadata.tables['order'].c.user_id)

    def test_compare_metadata_include_symbol(self):
        metadata = self.m2

        def include_symbol(table_name, schema_name):
            return table_name in ('extra', 'order')

        context = MigrationContext.configure(
            connection=self.bind.connect(),
            opts={
                'compare_type': True,
                'compare_server_default': True,
                'include_symbol': include_symbol,
            }
        )

        diffs = autogenerate.compare_metadata(context, metadata)

        eq_(diffs[0][0], 'remove_table')
        eq_(diffs[0][1].name, "extra")

        eq_(diffs[1][0], "add_column")
        eq_(diffs[1][1], None)
        eq_(diffs[1][2], "order")
        eq_(diffs[1][3], metadata.tables['order'].c.user_id)

        eq_(diffs[2][0][0], "modify_type")
        eq_(diffs[2][0][1], None)
        eq_(diffs[2][0][2], "order")
        eq_(diffs[2][0][3], "amount")
        eq_(repr(diffs[2][0][5]), "NUMERIC(precision=8, scale=2)")
        eq_(repr(diffs[2][0][6]), "Numeric(precision=10, scale=2)")

        eq_(diffs[2][1][0], 'modify_nullable')
        eq_(diffs[2][1][2], 'order')
        eq_(diffs[2][1][5], False)
        eq_(diffs[2][1][6], True)

    def test_compare_metadata_as_sql(self):
        context = MigrationContext.configure(
            connection=self.bind.connect(),
            opts={'as_sql': True}
        )
        metadata = self.m2

        assert_raises_message(
            CommandError,
            "autogenerate can't use as_sql=True as it prevents "
            "querying the database for schema information",
            autogenerate.compare_metadata, context, metadata
        )


class PGCompareMetaData(ModelOne, AutogenTest, TestBase):
    __only_on__ = 'postgresql'
    schema = "test_schema"

    def test_compare_metadata_schema(self):
        metadata = self.m2

        context = MigrationContext.configure(
            connection=self.bind.connect(),
            opts={
                "include_schemas": True
            }
        )

        diffs = autogenerate.compare_metadata(context, metadata)

        eq_(
            diffs[0],
            ('add_table', metadata.tables['test_schema.item'])
        )

        eq_(diffs[1][0], 'remove_table')
        eq_(diffs[1][1].name, "extra")

        eq_(diffs[2][0], "add_column")
        eq_(diffs[2][1], "test_schema")
        eq_(diffs[2][2], "address")
        eq_(diffs[2][3], metadata.tables['test_schema.address'].c.street)

        eq_(diffs[3][0], "add_constraint")
        eq_(diffs[3][1].name, "uq_email")

        eq_(diffs[4][0], "add_column")
        eq_(diffs[4][1], "test_schema")
        eq_(diffs[4][2], "order")
        eq_(diffs[4][3], metadata.tables['test_schema.order'].c.user_id)

        eq_(diffs[5][0][0], 'modify_nullable')
        eq_(diffs[5][0][5], False)
        eq_(diffs[5][0][6], True)
