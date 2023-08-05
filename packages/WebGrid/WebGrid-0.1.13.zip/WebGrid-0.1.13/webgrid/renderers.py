from collections import defaultdict

from blazeutils.containers import HTMLAttributes
from blazeutils.datastructures import BlankObject
from blazeutils.helpers import tolist
from blazeutils.jsonh import jsonmod
from blazeutils.spreadsheets import Writer
from blazeutils.strings import reindent, randnumerics
import jinja2 as jinja
from webhelpers.html import HTML as _HTML, literal, tags
from werkzeug import Href, MultiDict

from .utils import current_url

try:
    import xlwt
except ImportError:
    xlwt = None


class HTML(object):
    # by default, the renderer will use the display value from the operator,
    # but that can be overriden by subclassing and setting this dictionary
    # like:
    #
    #   filtering_operator_labels['eq'] = 'equals'
    filtering_operator_labels = {}

    def __init__(self, grid):
        self.grid = grid
        self.manager = grid.manager
        self.jinja_env = jinja.Environment(
            loader=jinja.PackageLoader('webgrid', 'templates'),
            autoescape=True,
        )
        self.jinja_env.filters['wg_safe'] = jinja.filters.do_mark_safe

    def __call__(self):
        return self.render()

    def render(self):
        return self.load_content('grid.html')

    def grid_otag(self):
        return _HTML.div(_closed=False, **self.grid.hah)

    def grid_ctag(self):
        return literal('</div>')

    def header(self):
        if self.grid.hide_controls_box:
            return ''
        return self.load_content('grid_header.html')

    def header_form_otag(self, **kwargs):
        return _HTML.form(_closed=False, method='get', action=self.form_action_url(), **kwargs)

    def form_action_url(self):
        return self.reset_url(session_reset=False)

    def header_filtering(self):
        return self.load_content('header_filtering.html')

    def filtering_table_otag(self, **kwargs):
        kwargs.setdefault('cellpadding', 1)
        kwargs.setdefault('cellspacing', 0)
        return _HTML.table(_closed=False, **kwargs)

    def filtering_session_key(self):
        return _HTML.input(
            name='session_key',
            type='hidden',
            value=self.grid.session_key
        )

    def filtering_fields(self):
        rows = []
        for col in self.grid.filtered_cols.itervalues():
            rows.append(self.filtering_table_row(col))
        return literal('\n'.join(rows))

    def filtering_table_row(self, col):
        extra = getattr(col.filter, 'html_extra', {})
        return _HTML.tr(
            _HTML.th(self.filtering_col_label(col), class_='filter-label')
            + _HTML.td(self.filtering_col_op_select(col), class_='operator')
            + _HTML.td(
                _HTML.div(self.filtering_col_inputs1(col), class_='inputs1')
                + _HTML.div(self.filtering_col_inputs2(col), class_='inputs2')
            ),
            class_=col.key,
            **extra
        )

    def filtering_col_label(self, col):
        return col.label

    def filtering_col_op_select_options(self, filter):
        options = [('',literal('&nbsp;'))]
        for op in filter.operators:
            options.append((
                op.key,
                self.filtering_operator_labels.get(op.key, op.display)
            ))
        return options

    def filtering_col_op_select(self, col):
        filter = col.filter
        if not filter.is_display_active:
            current_selected = ''
        else:
            current_selected = filter.op

        field_name = 'op({0})'.format(col.key)
        field_name = self.grid.prefix_qs_arg_key(field_name)

        return tags.select(field_name, current_selected, self.filtering_col_op_select_options(filter))

    def filtering_col_inputs1(self, col):
        filter = col.filter
        field_name = 'v1({0})'.format(col.key)
        field_name = self.grid.prefix_qs_arg_key(field_name)

        inputs = ''
        if 'input' in filter.input_types:
            ident = '{0}_input1'.format(col.key)
            inputs += _HTML.input(name=field_name, type='text', value=filter.value1_set_with, id=ident)
        if 'select' in filter.input_types:
            ident = '{0}_select1'.format(col.key)
            current_selected = tolist(filter.value1) or []
            multiple = None
            if len(current_selected) > 1:
                multiple = 'multiple'
            inputs += tags.select(field_name, current_selected, self.filtering_filter_options(filter), multiple=multiple)
            inputs += self.filtering_toggle_image()
        return inputs

    def filtering_toggle_image(self):
        img_url = self.manager.static_url('bullet_toggle_plus.png')
        img_tag = tags.image(img_url, 'multi-select toggle', 16, 16, class_='toggle-button')
        return img_tag

    def filtering_filter_options(self, filter):
        return filter.options_seq

    def filtering_col_inputs2(self, col):
        filter = col.filter
        field_name = 'v2({0})'.format(col.key)
        field_name = self.grid.prefix_qs_arg_key(field_name)

        # field will get modified by JS
        inputs = ''
        if 'input2' in filter.input_types:
            ident = '{0}_input2'.format(col.key)
            inputs += _HTML.input(name=field_name, type='text', value=filter.value2_set_with, id=ident)
        return inputs

    def filtering_add_filter_select(self):
        options = [('',literal('&nbsp;'))]
        for col in self.grid.filtered_cols.itervalues():
            options.append((col.key, col.label))
        return tags.select('datagrid-add-filter', None, options)

    def filtering_json_data(self):
        for_js = {}
        for col_key, col in self.grid.filtered_cols.iteritems():
            for_js[col_key] = opdict =  {}
            for op in col.filter.operators:
                opdict[op.key] = {
                    'field_type': op.field_type,
                    'hint': op.hint
                }
        return jsonmod.dumps(for_js)

    def header_sorting(self):
        return self.load_content('header_sorting.html')

    def sorting_select_options(self):
        options = [('',literal('&nbsp;'))]
        for col in self.grid.columns:
            if col.can_sort:
                options.append((col.key, col.label))
                options.append(('-' + col.key, col.label + ' DESC'))
        return options

    def sorting_select(self, number):
        key = 'sort{0}'.format(number)
        sort_qsk = self.grid.prefix_qs_arg_key(key)

        if len(self.grid.order_by) < number:
            currently_selected = ''
        else:
            currently_selected, flag_desc = self.grid.order_by[number - 1]
            if flag_desc:
                currently_selected = '-' + currently_selected
        return tags.select(sort_qsk, currently_selected, self.sorting_select_options())

    def sorting_select1(self):
        return self.sorting_select(1)

    def sorting_select2(self):
        return self.sorting_select(2)

    def sorting_select3(self):
        return self.sorting_select(3)

    def header_paging(self):
        return self.load_content('header_paging.html')

    def paging_select_options(self):
        options = []
        for page in xrange(1, self.grid.page_count + 1):
            label = '{0} of {1}'.format(page, self.grid.page_count)
            options.append((page, label))
        return options

    def paging_select(self):
        op_qsk = self.grid.prefix_qs_arg_key('onpage')
        return tags.select(op_qsk, self.grid.on_page, self.paging_select_options())

    def paging_input(self):
        pp_qsk = self.grid.prefix_qs_arg_key('perpage')
        return _HTML.input(type='text', name=pp_qsk, value=self.grid.per_page)

    def paging_url_first(self):
        return self.current_url(onpage=1, perpage=self.grid.per_page)

    def paging_img_first(self):
        img_url = self.manager.static_url('b_firstpage.png')
        return _HTML.img(src=img_url, width=16, height=13, alt='<<')

    def paging_img_first_dead(self):
        img_url = self.manager.static_url('bd_firstpage.png')
        return _HTML.img(src=img_url, width=16, height=13, alt='<<')

    def paging_url_prev(self):
        prev_page = self.grid.on_page - 1
        return self.current_url(onpage=prev_page, perpage=self.grid.per_page)

    def paging_img_prev(self):
        img_url = self.manager.static_url('b_prevpage.png')
        return _HTML.img(src=img_url, width=8, height=13, alt='<')

    def paging_img_prev_dead(self):
        img_url = self.manager.static_url('bd_prevpage.png')
        return _HTML.img(src=img_url, width=8, height=13, alt='<')

    def paging_url_next(self):
        next_page = self.grid.on_page + 1
        return self.current_url(onpage=next_page, perpage=self.grid.per_page)

    def paging_img_next(self):
        img_url = self.manager.static_url('b_nextpage.png')
        return _HTML.img(src=img_url, width=8, height=13, alt='>')

    def paging_img_next_dead(self):
        img_url = self.manager.static_url('bd_nextpage.png')
        return _HTML.img(src=img_url, width=8, height=13, alt='>')

    def paging_url_last(self):
        return self.current_url(onpage=self.grid.page_count, perpage=self.grid.per_page)

    def paging_img_last(self):
        img_url = self.manager.static_url('b_lastpage.png')
        return _HTML.img(src=img_url, width=16, height=13, alt='>>')

    def paging_img_last_dead(self):
        img_url = self.manager.static_url('bd_lastpage.png')
        return _HTML.img(src=img_url, width=16, height=13, alt='>>')

    def table(self):
        return self.load_content('grid_table.html')

    def no_records(self):
        return _HTML.p('No records to display', class_='no-records')

    def table_otag(self, **kwargs):
        kwargs.setdefault('class_', 'records')
        return _HTML.table(_closed=False, **kwargs)

    def table_column_headings(self):
        headings = []
        for col in self.grid.iter_columns('html'):
            headings.append(self.table_th(col))
        th_str = '\n'.join(headings)
        th_str = reindent(th_str, 12)
        return literal(th_str)

    def table_th(self, col):
        label = col.label
        if self.grid.sorter_on and col.can_sort:
            url_args = {}
            url_args['dgreset'] = None
            url_args['sort2'] = None
            url_args['sort3'] = None
            cls = None
            if self.grid.order_by and len(self.grid.order_by) == 1:
                current_sort, flag_desc = self.grid.order_by[0]
                if current_sort == col.key:
                    cls = 'sort-'+('desc' if flag_desc else 'asc')
                if current_sort != col.key or flag_desc:
                    url_args['sort1'] = col.key
                else:
                    url_args['sort1'] = '-{0}'.format(col.key)
            else:
                url_args['sort1'] = col.key
            label = _HTML.a(
                label,
                href=self.current_url(**url_args),
                class_=cls
            )
        return _HTML.th(label, **col.head.hah)

    def table_rows(self):
        rows = []
        # loop through rows
        for rownum, record in enumerate(self.grid.records):
            rows.append(self.table_tr(rownum, record))
        # process subtotals (if any)
        if rows and self.grid.subtotals in ('page','all') and \
            self.grid.subtotal_cols:
            rows.append(
                self.table_pagetotals(rownum+1,self.grid.page_totals)
            )
        if rows and self.grid.subtotals in ('grand','all') and \
            self.grid.subtotal_cols:
            rows.append(
                self.table_grandtotals(rownum+2,self.grid.grand_totals)
            )
        rows_str = '\n        '.join(rows)
        return literal(rows_str)

    def table_tr_styler(self, rownum, record):
        # handle row styling
        row_hah = HTMLAttributes()

        # add odd/even classes to the rows
        if (rownum + 1) % 2 == 1:
            row_hah.class_ += 'odd'
        else:
            row_hah.class_ += 'even'

        for styler in self.grid._rowstylers:
            styler(self.grid, rownum, row_hah, record)

        return row_hah

    def table_tr_output(self, cells, row_hah):
        # do some formatting so that the source code is properly indented
        tds_str = u'\n'.join(cells)
        tds_str = reindent(tds_str, 12)
        tds_str = u'\n{0}\n        '.format(tds_str)

        return _HTML.tr(literal(tds_str), **row_hah)

    def table_tr(self, rownum, record):
        row_hah = self.table_tr_styler(rownum, record)

        # get the <td>s for this row
        cells = []
        for col in self.grid.iter_columns('html'):
            cells.append(self.table_td(col, record))

        return self.table_tr_output(cells, row_hah)

    def table_totals(self, rownum, record, label, numrecords):
        row_hah = self.table_tr_styler(rownum, record)
        row_hah.class_ += 'totals'

        # get the <td>s for this row
        cells = []
        colspan = 0
        firstcol = True
        for col in self.grid.iter_columns('html'):
            if col.key not in self.grid.subtotal_cols.keys():
                if firstcol:
                    colspan += 1
                else:
                    cells.append(_HTML.td(literal('&nbsp;')))
                continue
            if firstcol:
                bufferval = '{0} Totals ({1} record{2}):'.format(
                    label,
                    numrecords,
                    's' if numrecords != 1 else '',
                )
                buffer_hah = HTMLAttributes(
                    colspan=colspan,
                    class_='totals-label'
                )
                if colspan:
                    cells.append(_HTML.td(bufferval, **buffer_hah))
                firstcol = False
                colspan = 0
            cells.append(self.table_td(col, record))

        return self.table_tr_output(cells, row_hah)

    def table_pagetotals(self, rownum, record):
        return self.table_totals(rownum, record, 'Page', rownum)

    def table_grandtotals(self, rownum, record):
        count = self.grid.record_count
        return self.table_totals(rownum, record, 'Grand', count)

    def table_td(self, col, record):
        col_hah = HTMLAttributes(col.body.hah)

        # allow column stylers to set attributes
        for styler, cname in self.grid._colstylers:
            for_column = self.grid.column(cname)
            if col.key == for_column.key:
                styler(self.grid, col_hah, record)

        # extract the value from the record for this column and prep
        col_value = col.render('html', record, col_hah)

        # turn empty values into a non-breaking space so table cells don't
        # collapse
        if col_value is None:
            styled_value = literal('&nbsp;')
        elif isinstance(col_value, basestring) and col_value.strip() == '':
            styled_value = literal('&nbsp;')
        else:
            styled_value = col_value

        return _HTML.td(styled_value, **col_hah)

    def footer(self):
        return self.load_content('grid_footer.html')

    def load_content(self, endpoint, **kwargs):
        kwargs['renderer'] = self
        kwargs['grid'] = self.grid

        try:
            # give the adapter a chance to render
            if hasattr(self.grid.manager, 'render_template'):
                return self.grid.manager.render_template(endpoint, **kwargs)
        except jinja.exceptions.TemplateNotFound:
            # fail silently, will fail on the next step if there's really a problem
            pass

        # if the adapter doesn't want it, default to raw Jinja2
        template = self.jinja_env.get_template(endpoint)
        return template.render(**kwargs)

    def current_url(self, **kwargs):
        curl = current_url(self.grid.manager, strip_querystring=True, strip_host=True)
        href = Href(curl, sort=True)

        req_args = MultiDict(self.grid.manager.request_args())

        for key in kwargs.keys():

            # arg keys may need to be prefixed
            if self.grid.qs_prefix:
                prefixed_key = self.grid.qs_prefix + key
                kwargs[prefixed_key] = kwargs[key]
                del kwargs[key]
                key = prefixed_key

            # multidicts extend, not replace, so we need to get rid of the
            # keys first
            try:
                del req_args[key]
            except KeyError:
                pass

        # convert to md first so that if we have lists in the kwargs, they
        # are converted appropriately
        req_args.update(MultiDict(kwargs))
        return href(req_args)

    def reset_url(self, session_reset=True):
        url_args = {}
        url_args['perpage'] = None
        url_args['onpage'] = None
        url_args['sort1'] = None
        url_args['sort2'] = None
        url_args['sort3'] = None
        url_args['export_to'] = None
        url_args['datagrid-add-filter'] = None

        for col in self.grid.filtered_cols.itervalues():
            url_args['op({0})'.format(col.key)] = None
            url_args['v1({0})'.format(col.key)] = None
            url_args['v2({0})'.format(col.key)] = None

        url_args['session_key'] = self.grid.session_key
        if session_reset:
            url_args['dgreset'] = 1

        return self.current_url(**url_args)

    def xls_url(self):
        return self.current_url(export_to='xls')

class XLS(object):
    def __init__(self, grid, max_col_width=150):
        self.grid = grid
        self.define_styles()
        self.col_contents_widths = defaultdict(int)
        self.max_col_width = max_col_width

    def __call__(self):
        return self.build_sheet()

    def define_styles(self):
        self.style = BlankObject()
        self.style.bold = xlwt.easyxf('font: bold True;')

    def build_sheet(self, wb=None, sheet_name=None):
        if xlwt is None:
            raise ImportError('you must have xlwt installed to use Excel renderer')
        if wb is None:
            wb = xlwt.Workbook()
        sheet = wb.add_sheet(sheet_name or self.grid.ident)
        xlh = Writer(sheet)

        self.sheet_header(xlh)
        self.sheet_body(xlh)
        self.sheet_footer(xlh)
        self.adjust_col_widths(sheet)

        return wb

    def sheet_header(self, xlh):
        pass

    def sheet_body(self, xlh):
        self.body_headings(xlh)
        self.body_records(xlh)

    def sheet_footer(self, xlh):
        pass

    def register_col_width(self, col, value):
        if value is None:
            return
        self.col_contents_widths[col.key] = max(
            self.col_contents_widths[col.key],
            col.xls_width_calc(value)
        )

    def adjust_col_widths(self, ws):
        for idx, col in enumerate(self.grid.iter_columns('xls')):
            max_registered_width = self.col_contents_widths[col.key]
            final_width = min(max_registered_width, self.max_col_width)

            # width calculation is 1/256th of width of zero character, using the
            # first font that occurs in the Excel file
            # the following calculation seems to get it done alright
            ws.col(idx).width = int((final_width + 3) * 256)

    def body_headings(self, xlh):
        for col in self.grid.iter_columns('xls'):
            self.register_col_width(col, col.label)
            xlh.awrite(col.label, self.style.bold)
        xlh.newrow()

    def body_records(self, xlh):
        # turn off paging
        self.grid.set_paging(None, None)

        rownum = 0
        for rownum, record in enumerate(self.grid.records):
            self.record_row(xlh, rownum, record)

        # totals
        if rownum and self.grid.subtotals != 'none' \
            and self.grid.subtotal_cols:
            self.totals_row(xlh, rownum+1, self.grid.grand_totals)

    def record_row(self, xlh, rownum, record):
        for col in self.grid.iter_columns('xls'):
            self.record_cell(xlh, col, record)
        xlh.newrow()

    def totals_row(self, xlh, rownum, record):
        colspan = 0
        firstcol = True
        totals_xf = xlwt.easyxf('font: bold on; border: top thin')
        for col in self.grid.iter_columns('xls'):
            if col.key not in self.grid.subtotal_cols.keys():
                if firstcol:
                    colspan += 1
                else:
                    xlh.awrite('', totals_xf)
                continue
            if firstcol:
                numrecords = self.grid.record_count
                bufferval = 'Totals ({0} record{1}):'.format(
                    numrecords,
                    's' if numrecords != 1 else '',
                )
                xlh.ws.write_merge(
                    xlh.rownum,
                    xlh.rownum,
                    xlh.colnum,
                    xlh.colnum+colspan-1,
                    bufferval,
                    totals_xf
                )
                xlh.colnum = xlh.colnum+colspan
                firstcol = False
                colspan = 0
            self.total_cell(xlh, col, record)
        xlh.newrow()

    def record_cell(self, xlh, col, record):
        value = col.render('xls', record)
        self.register_col_width(col, value)
        stymat = col.xlwt_stymat_calc(value)
        xlh.awrite(value, stymat)

    def total_cell(self, xlh, col, record):
        value = col.render('xls', record)
        self.register_col_width(col, value)
        stymat = col.xlwt_stymat_init()
        stymat.font.bold = True
        stymat.borders.top = xlwt.Formatting.Borders.THIN
        xlh.awrite(value, stymat)

    def file_name(self):
        return '{0}_{1}.xls'.format(self.grid.ident, randnumerics(6))

    def as_response(self, wb=None, sheet_name=None):
        wb = self.build_sheet(wb, sheet_name)
        self.grid.manager.xls_as_response(wb, self.file_name())
