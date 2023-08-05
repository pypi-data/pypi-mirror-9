import datetime as dt
from decimal import Decimal as D
from blazeutils.containers import HTMLAttributes
from blazeutils.testing import raises
import mock
from nose.tools import eq_

from webgrid import Column, LinkColumnBase, \
    BoolColumn, YesNoColumn, DateTimeColumn, DateColumn, NumericColumn
from webgrid.filters import TextFilter, DateFilter

from webgrid_ta.grids import Grid
from webgrid_ta.model.entities import Person

class FirstNameColumn(LinkColumnBase):
    def create_url(self, record):
        return '/person-edit/{0}'.format(record.id)

class FullNameColumn(LinkColumnBase):
    def extract_data(self, record):
        return '{0.firstname} {0.lastname}'.format(record)

    def create_url(self, record):
        return '/person-edit/{0}'.format(record.id)

class TestColumn(object):

    def test_attr_copy(self):
        class TG(Grid):
            Column('ID', Person.id, TextFilter, can_sort=False)
            FirstNameColumn('First Name', Person.firstname, TextFilter, can_sort=False, link_label='hi')
            YesNoColumn('Active', Person.inactive, TextFilter, can_sort=False, reverse=True)
            # DateColumn & DateTime Column are just subclasses of DateColumnBase
            # so we don't need to explicitly test both
            DateTimeColumn('Created', Person.createdts, DateFilter, can_sort=False, html_format='foo', xls_format='bar')

        g = TG()

        col = g.columns[0]
        eq_(col.key, 'id')
        assert col.expr is Person.id
        assert isinstance(col.filter, TextFilter)
        eq_(col.can_sort, False)

        col = g.columns[1]
        eq_(col.key, 'firstname')
        assert col.expr is Person.firstname
        assert isinstance(col.filter, TextFilter)
        eq_(col.can_sort, False)
        eq_(col.link_label, 'hi')

        col = g.columns[2]
        eq_(col.key, 'inactive')
        assert col.expr is Person.inactive
        assert isinstance(col.filter, TextFilter)
        eq_(col.can_sort, False)
        eq_(col.reverse, True)
        eq_(col.true_label, 'Yes')
        eq_(col.false_label, 'No')

        col = g.columns[3]
        eq_(col.key, 'createdts')
        assert col.expr is Person.createdts
        assert isinstance(col.filter, DateFilter)
        eq_(col.can_sort, False)
        eq_(col.html_format, 'foo')

    def test_nonkeyed_not_sort(self):
        class TG(Grid):
            FullNameColumn('Full Name')

        g = TG()
        col = g.columns[0]
        eq_(col.can_sort, False)

    @raises(ValueError, 'no column-like object is available')
    def test_filter_without_column_key(self):
        class TG(Grid):
            Column('ID', 'id', TextFilter)
        g = TG()

    @raises(ValueError, 'expected.+column-like object', re_esc=False)
    def test_fitler_of_wrong_type(self):
        class TG(Grid):
            Column('ID', Person, TextFilter)
        g = TG()

    def test_fitlers_are_new_instances(self):
        tf = TextFilter
        class TG(Grid):
            Column('Name', Person.firstname, tf)
        g = TG()
        g2 = TG()
        col = g.columns[0]
        col2 = g2.columns[0]
        assert isinstance(col.filter, TextFilter)
        assert col is not col2
        assert col.filter is not tf
        assert col.filter is not col2.filter
        assert g.filtered_cols['firstname'] is col

    def test_xls_width_calc(self):
        class C3(Column):
            xls_width = 15

        class TG(Grid):
            Column('C1', Person.firstname)
            Column('C2', Person.lastname, xls_width=10)
            C3('C3', Person.state)
            DateColumn('Date', Person.due_date)
        g = TG()

        value = '12345'
        eq_(g.columns[0].xls_width_calc(value), 5)
        eq_(g.columns[1].xls_width_calc(value), 10)
        eq_(g.columns[2].xls_width_calc(value), 15)

        value = '123456'
        eq_(g.columns[0].xls_width_calc(value), 6)

        value = 123
        eq_(g.columns[0].xls_width_calc(value), 3)

        value = 123.333
        eq_(g.columns[0].xls_width_calc(value), 7)

        value = dt.date(2012,1,1)
        eq_(g.columns[3].xls_width_calc(value), 10)

    def test_xls_width_setting(self):
        class LinkColumn(LinkColumnBase):
            pass

        class TG(Grid):
            Column('C1', Person.firstname, xls_width=1)
            LinkColumn('C2', Person.lastname, xls_width=1)
            BoolColumn('C3', Person.inactive, xls_width=1)
            YesNoColumn('C4', Person.inactive.label('yesno'), xls_width=1)
            DateColumn('Date', Person.due_date, xls_width=1)
            DateColumn('DateTime', Person.createdts, xls_width=1)
        g = TG()

        eq_(g.columns[0].xls_width_calc('123'), 1)
        eq_(g.columns[1].xls_width_calc('123'), 1)
        eq_(g.columns[2].xls_width_calc('123'), 1)
        eq_(g.columns[3].xls_width_calc('123'), 1)
        eq_(g.columns[4].xls_width_calc(dt.date(2012,1,1)), 1)
        eq_(g.columns[5].xls_width_calc(dt.date(2012,1,1)), 1)

    def test_xls_style_setting(self):
        class LinkColumn(LinkColumnBase):
            pass

        class TG(Grid):
            Column('C1', Person.firstname, xls_style='font: bold True')
            LinkColumn('C2', Person.lastname, xls_style='font: bold True')
            BoolColumn('C3', Person.inactive, xls_style='font: bold True')
            YesNoColumn('C4', Person.inactive.label('yesno'), xls_style='font: bold True')
            DateColumn('Date', Person.due_date, xls_style='font: bold True')
            DateColumn('DateTime', Person.createdts, xls_style='font: bold True')
        g = TG()

        eq_(g.columns[0].xls_style, 'font: bold True')
        eq_(g.columns[1].xls_style, 'font: bold True')
        eq_(g.columns[2].xls_style, 'font: bold True')
        eq_(g.columns[3].xls_style, 'font: bold True')
        eq_(g.columns[4].xls_style, 'font: bold True')
        eq_(g.columns[5].xls_style, 'font: bold True')

    def test_xls_number_format_setting(self):
        class LinkColumn(LinkColumnBase):
            pass

        class TG(Grid):
            Column('C1', Person.firstname, xls_num_format='General')
            LinkColumn('C2', Person.lastname, xls_num_format='General')
            BoolColumn('C3', Person.inactive, xls_num_format='General')
            YesNoColumn('C4', Person.inactive.label('yesno'), xls_num_format='General')
            DateColumn('Date', Person.due_date, xls_num_format='General')
            DateColumn('DateTime', Person.createdts)
        g = TG()

        eq_(g.columns[0].xls_num_format, 'General')
        eq_(g.columns[1].xls_num_format, 'General')
        eq_(g.columns[2].xls_num_format, 'General')
        eq_(g.columns[3].xls_num_format, 'General')
        eq_(g.columns[4].xls_num_format, 'General')
        # should pull from the class if not given when instantiating
        eq_(g.columns[5].xls_num_format, 'm/dd/yyyy')

    def test_render_in_setting(self):
        class LinkColumn(LinkColumnBase):
            pass

        class TG(Grid):
            Column('C1', Person.firstname)
            Column('C1.5', Person.firstname.label('fn2'), render_in=None)
            LinkColumn('C2', Person.lastname, render_in='xls')
            BoolColumn('C3', Person.inactive, render_in=('xls','html'))
            YesNoColumn('C4', Person.inactive.label('yesno'), render_in='xls')
            DateColumn('Date', Person.due_date, render_in='xls')
            DateColumn('DateTime', Person.createdts, render_in='xls')
        g = TG()

        eq_(g.columns[0].render_in, ('html', 'xls'))
        eq_(g.columns[1].render_in, ())
        eq_(g.columns[2].render_in, ('xls',))
        eq_(g.columns[3].render_in, ('xls','html'))
        eq_(g.columns[4].render_in, ('xls',))
        eq_(g.columns[5].render_in, ('xls',))
        eq_(g.columns[6].render_in, ('xls',))

    def test_number_formatting(self):
        class TG(Grid):
            NumericColumn('C1', Person.numericcol, places=1)
        g = TG()

        c = g.columns[0]
        record = {'numericcol': D('1234.16')}
        eq_(c.render_html(record, None), '1,234.2')

        c.format_as = 'accounting'
        eq_(c.render_html(record, None), '$1,234.16')

        # accounting with negative value
        record = {'numericcol': D('-1234.16')}
        hah = HTMLAttributes()
        eq_(c.render_html(record, hah), '($1,234.16)')
        assert hah['class'] == 'negative'

        record = {'numericcol': D('.1673')}
        c.format_as = 'percent'
        eq_(c.render_html(record, None), '16.7%')

    def test_number_formatting_for_excel(self):
        class TG(Grid):
            NumericColumn('C1', Person.numericcol, places=2)
        g = TG()

        c = g.columns[0]
        eq_(c.xls_construct_format(c.xls_fmt_general), '#,##0.00;[RED]-#,##0.00')
        eq_(c.xls_construct_format(c.xls_fmt_accounting), '_($* #,##0.00_);[RED]_($* (#,##0.00);_($* "-"??_);_(@_)')
        eq_(c.xls_construct_format(c.xls_fmt_percent), '0.00%;[RED]-0.00%')

        # no red
        c.xls_neg_red = False
        eq_(c.xls_construct_format(c.xls_fmt_general), '#,##0.00;-#,##0.00')
        eq_(c.xls_construct_format(c.xls_fmt_accounting), '_($* #,##0.00_);_($* (#,##0.00);_($* "-"??_);_(@_)')
        eq_(c.xls_construct_format(c.xls_fmt_percent), '0.00%;-0.00%')

        # adjust places
        c.places = 0
        eq_(c.xls_construct_format(c.xls_fmt_general), '#,##0;-#,##0')
        eq_(c.xls_construct_format(c.xls_fmt_accounting), '_($* #,##0_);_($* (#,##0);_($* "-"??_);_(@_)')
        eq_(c.xls_construct_format(c.xls_fmt_percent), '0%;-0%')

    def test_number_format_xlwt_stymat_init(self):
        # nothing specified defaults to 'general'
        with mock.patch('webgrid.xlwt') as m_xlwt:
            class TG(Grid):
                NumericColumn('C1', Person.numericcol)
            TG()
            m_xlwt.easyxf.assert_called_once_with(None, '#,##0.00;[RED]-#,##0.00')

        # something else as the number format
        with mock.patch('webgrid.xlwt') as m_xlwt:
            class TG(Grid):
                NumericColumn('C1', Person.numericcol, format_as='foo', xls_num_format='bar')
            TG()
            m_xlwt.easyxf.assert_called_once_with(None, 'bar')

        # accounting
        with mock.patch('webgrid.xlwt') as m_xlwt:
            class TG(Grid):
                NumericColumn('C1', Person.numericcol, format_as='accounting')
            TG()
            m_xlwt.easyxf.assert_called_once_with(None, '_($* #,##0.00_);[RED]_($* (#,##0.00);_($* "-"??_);_(@_)')

        # percent
        with mock.patch('webgrid.xlwt') as m_xlwt:
            class TG(Grid):
                NumericColumn('C1', Person.numericcol, format_as='percent')
            TG()
            m_xlwt.easyxf.assert_called_once_with(None, '0.00%;[RED]-0.00%')

        # none
        with mock.patch('webgrid.xlwt') as m_xlwt:
            class TG(Grid):
                NumericColumn('C1', Person.numericcol, format_as=None)
            TG()
            m_xlwt.easyxf.assert_called_once_with(None, None)
