import flask
from nose.tools import eq_
from werkzeug.datastructures import MultiDict

from webgrid import Column, BoolColumn, YesNoColumn
from webgrid.filters import TextFilter, IntFilter
from webgrid_ta.model.entities import Person, Status, db
from webgrid_ta.grids import Grid, PeopleGrid
from .helpers import assert_in_query, assert_not_in_query, query_to_str, inrequest


class TestGrid(object):
    class TG(Grid):
        Column('First Name', Person.firstname)

    @classmethod
    def setup_class(self):
        Status.delete_cascaded()
        Person.testing_create()
        Person.testing_create()
        Person.testing_create()
        Person.testing_create()
        Person.testing_create()

    def test_column_key(self):
        g = self.TG()
        g.build_query()
        eq_(g.columns[0].key, 'firstname')

    def test_columns_are_new_instances(self):
        g = self.TG()
        g2 = self.TG()
        assert g.columns[0] is not self.TG.__cls_cols__[0]
        assert g.columns[0].__class__ is self.TG.__cls_cols__[0].__class__
        assert g.columns[0] is not g2.columns[0]
        assert g.columns[0] is g.key_column_map['firstname']

    def test_grid_ident(self):
        class Grid1(Grid):
            identifier = 'cars'

        class Grid2(Grid):
            pass

        mg = Grid2()
        eq_(mg.ident, 'grid2')

        mg = Grid1()
        eq_(mg.ident, 'cars')

        mg = Grid1('foo')
        eq_(mg.ident, 'foo')

    def test_base_query(self):
        class CTG(Grid):
            Column('First Name', Person.firstname)
        g = CTG()
        query = g.build_query()
        assert_not_in_query(query, 'WHERE')
        assert_not_in_query(query, 'ORDER BY')
        rs = g.records
        assert len(rs) > 0, rs

    def test_query_prep_sorting(self):
        class CTG(Grid):
            Column('First Name', Person.firstname)

            def query_prep(self, query, has_sort, has_filters):
                assert not has_sort
                assert not has_filters
                return query.order_by(Person.lastname)

        g = CTG()
        assert_in_query(g, 'ORDER BY persons.last_name')

    def test_filter_class(self):
        class CTG(Grid):
            Column('First Name', Person.firstname, TextFilter)

        g = CTG()
        g.set_filter('firstname', 'eq', 'foo')
        assert_in_query(g, "WHERE persons.firstname = 'foo'")

    def test_filter_instance(self):
        class CTG(Grid):
            Column('First Name', Person.firstname, TextFilter(Person.lastname))

        g = CTG()
        g.set_filter('firstname', 'eq', 'foo')
        assert_in_query(g, "WHERE persons.last_name = 'foo'")

    def test_order_by(self):
        class CTG(Grid):
            Column('First Name', Person.firstname)

        g = CTG()
        g.set_sort('-firstname')
        assert_in_query(g, 'ORDER BY persons.firstname')

    def test_redundant_order_by(self):
        class CTG(Grid):
            Column('First Name', Person.firstname)
            Column('Last Name', Person.lastname)

        g = CTG()
        g.set_sort('firstname', 'lastname', '-firstname')
        assert_in_query(g, 'ORDER BY persons.firstname, persons.last_name\n')

    def test_paging(self):
        g = self.TG()
        assert_in_query(g, 'LIMIT 50 OFFSET 0')

        g.set_paging(2, 1)
        assert_in_query(g, 'LIMIT 2 OFFSET 0')

        g.set_paging(10, 5)
        assert_in_query(g, 'LIMIT 10 OFFSET 40')

    def test_paging_disabled(self):
        class TG(Grid):
            pager_on = False
            Column('First Name', Person.firstname)
        g = TG()
        assert_not_in_query(g, 'LIMIT 50 OFFSET 0')
        eq_(g.page_count, 1)

    def test_page_count(self):
        g = self.TG()
        eq_(g.page_count, 1)

        g.set_paging(1, 2)
        eq_(g.page_count, 5)

        g = self.TG(per_page=None)
        eq_(g.page_count, 1)

    def test_record_count(self):
        g = self.TG()
        eq_(g.record_count, 5)

    def test_column_iterators_for_rendering(self):
        class TG(Grid):
            Column('C1', Person.firstname)
            Column('C1.5', Person.firstname.label('fn2'), render_in=None)
            Column('C2', Person.lastname, render_in='xls')
            BoolColumn('C3', Person.inactive, render_in=('xls', 'html'))
            YesNoColumn('C4', Person.inactive.label('yesno'), render_in='html')
        tg = TG()

        html_cols = tuple(tg.iter_columns('html'))
        eq_(html_cols[0].key, 'firstname')
        eq_(html_cols[1].key, 'inactive')
        eq_(html_cols[2].key, 'yesno')

        xls_cols = tuple(tg.iter_columns('xls'))
        eq_(xls_cols[0].key, 'firstname')
        eq_(xls_cols[1].key, 'lastname')
        eq_(xls_cols[2].key, 'inactive')

    def test_grid_inheritance(self):
        class SomeGrid(Grid):
            Column('n1', Person.firstname)

        class SomeGrid2(SomeGrid):
            Column('n2', Person.lastname)

        pg = SomeGrid2()
        eq_(len(pg.columns), 2)
        assert pg.columns[1].key == 'lastname'


class TestQueryStringArgs(object):

    @classmethod
    def setup_class(cls):
        Status.delete_cascaded()
        Status.testing_create('pending')
        Status.testing_create('in process')
        Status.testing_create('complete')
        Person.testing_create('bob')
        Person.testing_create('bob')
        Person.testing_create()

    @inrequest('/foo?dg_perpage=1&dg_onpage=2')
    def test_qs_prefix(self):
        pg = PeopleGrid(qs_prefix='dg_')
        pg.apply_qs_args()
        eq_(pg.on_page, 2)
        eq_(pg.per_page, 1)

    @inrequest('/foo?perpage=1&onpage=2')
    def test_qs_paging(self):
        pg = PeopleGrid()
        pg.apply_qs_args()
        eq_(pg.on_page, 2)
        eq_(pg.per_page, 1)

        # make sure the corret values get applied to the query
        assert 'LIMIT 1 OFFSET 1' in query_to_str(pg.build_query())

    @inrequest('/foo?perpage=5&onpage=foo')
    def test_qs_onpage_invalid(self):
        pg = PeopleGrid()
        pg.apply_qs_args()
        eq_(pg.on_page, 1)
        eq_(pg.per_page, 5)
        eq_(pg.user_warnings[0], '"onpage" grid argument invalid, ignoring')

    @inrequest('/foo?perpage=5&onpage=-1')
    def test_qs_onpage_negative(self):
        pg = PeopleGrid()
        pg.apply_qs_args()
        eq_(pg.on_page, 1)
        eq_(pg.per_page, 5)
        eq_(len(pg.user_warnings), 0)

    @inrequest('/foo?perpage=1&onpage=100')
    def test_qs_onpage_too_high(self):
        pg = PeopleGrid()
        pg.apply_qs_args()
        eq_(pg.on_page, 3)
        eq_(pg.per_page, 1)
        eq_(len(pg.user_warnings), 0)

        # the records should be the same as if we were on the last page
        eq_(len(pg.records), 1)

    @inrequest('/foo?perpage=foo&onpage=2')
    def test_qs_perpage_invalid(self):
        pg = PeopleGrid()
        pg.apply_qs_args()
        eq_(pg.on_page, 2)
        eq_(pg.per_page, 1)
        eq_(pg.user_warnings[0], '"perpage" grid argument invalid, ignoring')

    @inrequest('/foo?perpage=-1&onpage=2')
    def test_qs_perpage_negative(self):
        pg = PeopleGrid()
        pg.apply_qs_args()
        eq_(pg.on_page, 2)
        eq_(pg.per_page, 1)
        eq_(len(pg.user_warnings), 0)

    @inrequest('/foo?sort1=foo&sort2=firstname&sort3=-status')
    def test_qs_sorting(self):
        pg = PeopleGrid()
        pg.apply_qs_args()
        eq_(pg.order_by, [('firstname', False), ('status', True)])
        eq_(pg.user_warnings[0], 'can\'t sort on invalid key "foo"')

    @inrequest('/foo?sort1=fullname&sort2=firstname&sort3=-status')
    def test_qs_sorting_not_allowed(self):
        pg = PeopleGrid()
        pg.apply_qs_args()
        eq_(pg.order_by, [('firstname', False), ('status', True)])
        eq_(pg.user_warnings[0], 'can\'t sort on invalid key "fullname"')

    @inrequest('/foo?sort1=')
    def test_qs_sorting_ignores_emptystring(self):
        pg = PeopleGrid()
        pg.apply_qs_args()
        eq_(pg.order_by, [])
        eq_(len(pg.user_warnings), 0)

    @inrequest('/foo?op(firstname)=eq&v1(firstname)=fn001&op(status)=is&v1(status)=1&v1(status)=2')
    def test_qs_filtering(self):
        pg = PeopleGrid()
        pg.apply_qs_args()
        eq_(pg.columns[0].filter.op, 'eq')
        eq_(pg.columns[0].filter.value1, 'fn001')
        assert pg.columns[0].filter.value2 is None

        eq_(pg.columns[4].filter.op, 'is')
        eq_(pg.columns[4].filter.value1, [1, 2])
        assert pg.columns[4].filter.value2 is None

    @inrequest('/foo?op(firstname)=eq&v1(firstname)=bob&perpage=1&onpage=100')
    def test_qs_paging_doesnt_get_page_count_before_filters_are_handled(self):
        pg = PeopleGrid()
        pg.apply_qs_args()
        # this ensures that the filtering in apply_qs_args() takes place before
        # the paging.  Since the paging section uses .page_count, we have to
        # make sure the filters get processed first.  Otherwise an incorrect
        # page count gets cached.
        eq_(pg.record_count, 2)

    @inrequest('/foo')
    def test_qs_no_session(self):
        pg = PeopleGrid()
        pg.apply_qs_args()
        assert pg.column('firstname').filter.op is None

    @inrequest('/foo?op(firstname)=eq&v1(firstname)=bob&perpage=1&onpage=100')
    def test_qs_default_session(self):
        pg = PeopleGrid()
        pg.apply_qs_args()
        flask.request.args = MultiDict()
        pg2 = PeopleGrid()
        pg2.apply_qs_args()
        eq_(pg2.column('firstname').filter.op, 'eq')
        assert '_PeopleGrid' in flask.session['dgsessions']
        assert pg.session_key in flask.session['dgsessions']
        assert pg2.session_key in flask.session['dgsessions']

    @inrequest('/foo?op(firstname)=eq&v1(firstname)=bob&perpage=1&onpage=100')
    def test_qs_keyed_session(self):
        pg = PeopleGrid()
        pg.apply_qs_args()
        flask.request.args['op(firstname)'] = '!eq'
        pg2 = PeopleGrid()
        pg2.apply_qs_args()
        eq_(pg2.column('firstname').filter.op, '!eq')
        flask.request.args = MultiDict([('session_key', pg.session_key)])
        pg = PeopleGrid()
        pg.apply_qs_args()
        eq_(pg.column('firstname').filter.op, 'eq')

    @inrequest('/foo?op(firstname)=eq&v1(firstname)=bob&perpage=1&onpage=100')
    def test_qs_keyed_session_with_export(self):
        pg = PeopleGrid()
        pg.apply_qs_args()
        flask.request.args['op(firstname)'] = '!eq'
        pg2 = PeopleGrid()
        pg2.apply_qs_args()
        eq_(pg2.column('firstname').filter.op, '!eq')
        flask.request.args = MultiDict([
            ('session_key', pg.session_key),
            ('export_to', 'xls'),
        ])
        pg = PeopleGrid()
        pg.apply_qs_args()
        eq_(pg.column('firstname').filter.op, 'eq')

    @inrequest('/foo?op(firstname)=&v1(firstname)=foo&op(status)=&v1(status)=1')
    def test_qs_blank_operator(self):
        pg = PeopleGrid()
        pg.apply_qs_args()
        assert pg.columns[0].filter.op is None
        assert pg.columns[0].filter.value1 is None
        assert pg.columns[0].filter.value2 is None

        assert pg.columns[4].filter.op is None
        assert pg.columns[4].filter.value1 is None
        assert pg.columns[4].filter.value2 is None

    @inrequest('/foo?sort1=legacycol1&sort2=legacycol2')
    def test_sa_expr_sort(self):
        class AGrid(Grid):
            firstname = Column('First Name')
            legacycol1 = Column('LC1')
            legacycol2 = Column('LC2')

            def query_base(self, has_sort, has_filters):
                query = db.session.query(
                    Person.id, Person.firstname,
                    Person.legacycol1, Person.legacycol2
                )
                return query

        g = AGrid()
        g.apply_qs_args()

        # this will fail if we are not using SA expressions correctly to sort
        g.records

    @inrequest('/thepage?export_to=xls')
    def test_export_to(self):
        g = PeopleGrid()
        g.apply_qs_args()
        eq_(g.export_to, 'xls')

    @inrequest('/thepage?export_to=foo')
    def test_export_to_unrecognized(self):
        g = PeopleGrid()
        g.apply_qs_args()
        eq_(g.export_to, None)

    @inrequest('/foo?op(id)=eq&v1(id)=d')
    def test_exc_msg_in_warnings(self):
        class TGrid(Grid):
            Column('T', Person.id, IntFilter)
        g = TGrid()
        g.apply_qs_args()
        eq_(g.user_warnings[0], 'T: Please enter an integer value')
