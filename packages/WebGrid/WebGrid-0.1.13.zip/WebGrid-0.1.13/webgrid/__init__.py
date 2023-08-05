import inspect
import re
import sys

from blazeutils.containers import HTMLAttributes
from blazeutils.datastructures import BlankObject, OrderedDict
from blazeutils.helpers import ensure_tuple
from blazeutils.numbers import decimalfmt
from blazeutils.strings import case_cw2us, randchars
from formencode import Invalid
import formencode.validators as fev
import sqlalchemy.sql as sasql
from webhelpers.html.tags import link_to
from werkzeug.datastructures import MultiDict

from .renderers import HTML, XLS

try:
    import xlwt
except ImportError:
    xlwt = None

# subtotals functions
sum_ = sasql.functions.sum
avg_ = sasql.func.avg


class _None(object):
    """
        A sentinal object to indicate no value
    """
    pass


class ExtractionError(TypeError):
    """ raised when we are unable to extract a value from the record """
    pass


class DuplicateQueryNameError(TypeError):
    """
        Raised when an SQ query is used that has more than one column with
        the same name
    """
    pass


class _DeclarativeMeta(type):

    def __new__(cls, name, bases, class_dict):
        class_dict['_rowstylers'] = []
        class_dict['_colstylers'] = []
        class_dict['_colfilters'] = []
        class_columns = []

        # add columns from base classes
        for base in bases:
            base_columns = getattr(base, '__cls_cols__', ())
            class_columns.extend(base_columns)
        class_columns.extend(class_dict.get('__cls_cols__', ()))
        class_dict['__cls_cols__'] = class_columns

        # we have to assign the attribute name
        for k,v in class_dict.iteritems():
            # catalog the row stylers
            if getattr(v, '__grid_rowstyler__', None):
                class_dict['_rowstylers'].append(v)

            # catalog the column stylers
            for_column = getattr(v, '__grid_colstyler__', None)
            if for_column:
                class_dict['_colstylers'].append((v, for_column))

            # catalog the column filters
            for_column = getattr(v, '__grid_colfilter__', None)
            if for_column:
                class_dict['_colfilters'].append((v, for_column))

        return super(_DeclarativeMeta, cls).__new__(cls, name, bases, class_dict)

class Column(object):
    """
        Column represents the fixed settings for a datagrid column
    """
    _creation_counter = 0
    xls_width = None
    xls_num_format = None
    xls_style = None
    render_in = 'html', 'xls'

    def __new__(cls, *args, **kwargs):
        col_inst = super(Column, cls).__new__(cls)
        if '_dont_assign' not in kwargs:
            col_inst._assign_to_grid()
        return col_inst

    def _assign_to_grid(self):
        grid_locals = sys._getframe(2).f_locals
        grid_cls_cols = grid_locals.setdefault('__cls_cols__', [])
        grid_cls_cols.append(self)

    def __init__(self, label, key=None, filter=None, can_sort=True,
                xls_width=None, xls_style=None, xls_num_format=None,
                render_in=_None, has_subtotal=False, **kwargs):
        self.label = label
        self.key = key
        self.filter = filter
        self.filter_for = None
        self.filter_op = None
        self._create_order = False
        self.can_sort = can_sort
        self.has_subtotal = has_subtotal
        self.kwargs = kwargs
        self.grid = None
        self.expr = None
        if render_in is not _None:
            self.render_in = ensure_tuple(render_in)
        if xls_width:
            self.xls_width = xls_width
        if xls_num_format:
            self.xls_num_format = xls_num_format
        if xls_style:
            self.xls_style = xls_style

        # if the key isn't a base string, assume its a column-like object that
        # works with a SA Query instance
        if key is None:
            self.can_sort = False
        elif not isinstance(key, basestring):
            self.expr = col = key
            # use column.key, column.name, or None in that order
            key = getattr(col, 'key', getattr(col, 'name', None))

            if key is None:
                raise ValueError('expected filter to be a SQLAlchemy column-like'
                        ' object, but it did not have a "key" or "name"'
                        ' attribute')
            self.key = key

        # filters can be sent in as a class (not class instance) if needed
        if inspect.isclass(filter):
            if self.expr is None:
                raise ValueError('the filter was a class type, but no'
                    ' column-like object is available from "key" to pass in as'
                    ' as the first argument')
            self.filter = filter(self.expr)

    def new_instance(self, grid):
        cls = self.__class__
        column = cls(self.label, self.key, None, self.can_sort, _dont_assign=True)
        column.grid = grid
        column.expr = self.expr

        if self.filter:
            column.filter = self.filter.new_instance()

        column.head = BlankObject()
        column.head.hah = HTMLAttributes(self.kwargs)
        column.body = BlankObject()
        column.body.hah = HTMLAttributes(self.kwargs)
        if xlwt is not None:
            column.xlwt_stymat = self.xlwt_stymat_init()
        else:
            column.xlwt_stymat = None

        # try to be smart about which attributes should get copied to the
        # new instance by looking for attributes on the class that have the
        # same name as arguments to the classes __init__ method
        for argname in inspect.getargspec(self.__init__).args:
            if argname != 'self' and hasattr(self, argname) and               \
                        argname not in ('label', 'key', 'filter', 'can_sort'):
                setattr(column, argname, getattr(self, argname))

        return column

    def extract_and_format_data(self, record):
        """
            Extract a value from the record for this column and run it through
            the data formaters.
        """
        data = self.extract_data(record)
        data = self.format_data(data)
        for filter, cname in self.grid._colfilters:
            for_column = self.grid.column(cname)
            if self.key == for_column.key:
                data = filter(self.grid, data)
        return data

    def extract_data(self, record):
        """
            Locate the data for this column in the record and return it.
        """
        # key style based on expression
        if self.expr is not None:
            try:
                return record[self.key]
            except (TypeError, KeyError):
                pass

        # key style based on key
        try:
            return record[self.key]
        except (TypeError, KeyError):
            pass

        # attribute style
        try:
            return getattr(record, self.key)
        except AttributeError, e:
            if ("object has no attribute '%s'" % self.key) not in str(e):
                raise

        raise ExtractionError('key "%s" not found in record' % self.key)

    def format_data(self, value):
        """
            Use to adjust the value extracted from the record for this column.
            By default, no change is made. Useful in sub-classes.
        """
        return value

    def render(self, render_type, record, *args, **kwargs):
        render_attr = 'render_{0}'.format(render_type)
        if hasattr(self, render_attr):
           return getattr(self, render_attr)(record, *args, **kwargs)
        return self.extract_and_format_data(record)

    def apply_sort(self, query, flag_desc):
        if self.expr is None:
            direction = 'DESC' if flag_desc else 'ASC'
            return query.order_by('{0} {1}'.format(self.key, direction))
        if flag_desc:
            return query.order_by(self.expr.desc())
        return query.order_by(self.expr)

    def __repr__(self):
        return '<Column "{0.key}" from "{0.grid}">'.format(self)

    def xls_width_calc(self, value):
        if self.xls_width:
            return self.xls_width
        if isinstance(value, basestring):
            return len(value)
        return len(str(value))

    def xlwt_stymat_init(self):
        """
            Because Excel gets picky about a lot of styles, its likely that
            a column will use one style object instance.  This method will
            be called once.

            If a column needs to support more than one style, override
            xlwt_stymat_calc()
        """
        return xlwt.easyxf(self.xls_style, self.xls_num_format)

    def xlwt_stymat_calc(self, value):
        """
            By default, the xlwt style & number format is per-column and not
            based ont he value.
        """
        return self.xlwt_stymat

class LinkColumnBase(Column):
    link_attrs = {}

    def __init__(self, label, key=None, filter=None, can_sort=True, \
                link_label=None, xls_width=None, xls_style=None, xls_num_format=None,
                render_in=_None, **kwargs):
        Column.__init__(self, label, key, filter, can_sort, xls_width,
                        xls_style, xls_num_format, render_in, **kwargs)
        self.link_label = link_label

    def render_html(self, record, hah):
        url = self.create_url(record)
        if self.link_label is not None:
            label = self.link_label
        else:
            label = self.extract_and_format_data(record)
        return link_to(label, url, **self.link_attrs)

    def create_url(self, record):
        raise NotImplementedError('create_url() must be defined on a subclass')

class BoolColumn(Column):

    def __init__(self, label, key_or_filter=None, key=None, can_sort=True, \
                reverse=False, true_label='True', false_label='False', \
                xls_width=None, xls_style=None, xls_num_format=None, \
                render_in=_None, **kwargs):
        Column.__init__(self, label, key_or_filter, key, can_sort, xls_width,
                        xls_style, xls_num_format, render_in, **kwargs)
        self.reverse = reverse
        self.true_label = true_label
        self.false_label = false_label

    def format_data(self, data):
        if self.reverse:
            data = not data
        if data:
            return self.true_label
        return self.false_label

class YesNoColumn(BoolColumn):

    def __init__(self, label, key_or_filter=None, key=None, can_sort=True, \
                reverse=False, xls_width=None, xls_style=None, xls_num_format=None,
                render_in=_None, **kwargs):
        BoolColumn.__init__(self, label, key_or_filter, key, can_sort, reverse, \
                'Yes', 'No', xls_width, xls_style, xls_num_format, render_in, **kwargs)

class DateColumnBase(Column):

    def __init__(self, label, key_or_filter=None, key=None, can_sort=True,
                html_format=None, xls_width=None, xls_style=None, xls_num_format=None,
                render_in=_None, **kwargs):
        Column.__init__(self, label, key_or_filter, key, can_sort, xls_width,
                        xls_style, xls_num_format, render_in, **kwargs)
        if html_format:
            self.html_format = html_format

    def render_html(self, record, hah):
        data = self.extract_and_format_data(record)
        if not data:
            return data
        return data.strftime(self.html_format)

    def xls_width_calc(self, value):
        if self.xls_width:
            return self.xls_width
        try:
            # value will be a date or datetime object, format as if it was going
            # to be in HTML as an approximation of its format in excel
            html_version = value.strftime(self.html_format)
            return len(html_version)
        except AttributeError, e:
            if "has no attribute 'strftime'" not in str(e):
                raise
            # must be the column heading
            return Column.xls_width_calc(self, value)

class DateColumn(DateColumnBase):
    html_format = '%m/%d/%Y'
    xls_num_format = 'm/dd/yyyy'

class DateTimeColumn(DateColumnBase):
    html_format='%m/%d/%Y %I:%M %p'
    xls_num_format = 'mm/dd/yyyy hh:mm am/pm'

class NumericColumn(Column):
    xls_fmt_general = '#,##0{dec_places};{neg_prefix}-#,##0{dec_places}'
    xls_fmt_accounting = '_($* #,##0{dec_places}_);{neg_prefix}_($* (#,##0{dec_places});_($* "-"??_);_(@_)'
    xls_fmt_percent = '0{dec_places}%;{neg_prefix}-0{dec_places}%'

    def __init__(self, label, key_or_filter=None, key=None, can_sort=True, \
                reverse=False, xls_width=None, xls_style=None, xls_num_format=None,
                render_in=_None, format_as='general', places=2, curr='',
                sep=',', dp='.', pos='', neg='-', trailneg='',
                xls_neg_red=True, has_subtotal=False, **kwargs):
        Column.__init__(self, label, key_or_filter, key, can_sort, xls_width,
                        xls_style, xls_num_format, render_in,
                        has_subtotal, **kwargs)
        self.places = places
        self.curr = curr
        self.sep = sep
        self.dp = dp
        self.pos = pos
        self.neg = neg
        self.trailneg = trailneg
        self.xls_neg_red = xls_neg_red
        self.format_as = format_as

    def html_decimal_format_opts(self, data):
        return (
            2 if self.format_as == 'accounting' else self.places,
            '$' if self.format_as == 'accounting' else self.curr,
            self.sep,
            self.dp,
            self.pos,
            '(' if self.format_as == 'accounting' else self.neg,
            ')' if self.format_as == 'accounting' else self.trailneg,
        )

    def render_html(self, record, hah):
        data = self.extract_and_format_data(record)
        if not data and data != 0:
            return data

        if self.format_as == 'percent':
            data = data * 100

        formatted = decimalfmt(data, *self.html_decimal_format_opts(data))

        if self.format_as == 'percent':
            formatted += '%'

        if data < 0:
            hah.class_ += 'negative'

        return formatted

    def xls_construct_format(self, fmt_str):
        neg_prefix = '[RED]' if self.xls_neg_red else ''
        dec_places = '.'.ljust(self.places + 1, '0') if self.places else ''
        return fmt_str.format(dec_places=dec_places, neg_prefix=neg_prefix)

    def xlwt_stymat_init(self):
        num_format = None
        if self.format_as == 'general':
            num_format = self.xls_construct_format(self.xls_fmt_general)
        if self.format_as == 'percent':
            num_format = self.xls_construct_format(self.xls_fmt_percent)
        if self.format_as == 'accounting':
            num_format = self.xls_construct_format(self.xls_fmt_accounting)
        if num_format:
            return xlwt.easyxf(self.xls_style, num_format)
        return Column.xlwt_stymat_init(self)

class BaseGrid(object):
    __metaclass__ = _DeclarativeMeta
    # this value will rarely be used, it will always be overriden by the logic
    # in Column.__new__() which creates a new value on the Grid subclass
    # which will take precedence over this one.  Its really only hear to give
    # a default value for when a Grid is declared without columns when testing.
    __cls_cols__ = ()
    identifier = None
    sorter_on = True
    pager_on = True
    per_page = 50
    on_page = 1
    hide_controls_box = False
    hide_excel_link = False
    # enables keyed session store of grid arguments
    session_on = False
    # enables page/grand subtotals: none|page|grand|all
    subtotals = 'none'
    manager = None

    def __init__(self, ident=None, per_page=_None, on_page=_None, qs_prefix='', class_='datagrid', **kwargs):
        self._ident = ident
        self.hah = HTMLAttributes(kwargs)
        self.hah.id = self.ident
        self.hah.class_ += class_
        self.filtered_cols = OrderedDict()
        self.subtotal_cols = OrderedDict()
        self.order_by = []
        self.qs_prefix = qs_prefix
        self.user_warnings = []
        self._record_count = None
        self._records = None
        self._page_totals = None
        self._grand_totals = None
        self.set_renderers()
        self.export_to = None
        # when session feature is enabled, key is the unique string
        #   used to distinguish grids. Initially set to a random
        #   string, but will be set to the session key in args
        self.session_key = randchars(12)
        # at times, different grids may be made to share a session
        self.foreign_session_loaded = False

        self.per_page = per_page if per_page is not _None else self.__class__.per_page
        self.on_page = on_page if on_page is not _None else self.__class__.on_page

        self.columns = []
        self.key_column_map = {}
        def subtotal_function_map(v):
            if v == True or v == 'sum':
                return sum_
            elif v == 'avg':
                return avg_
            return None

        for col in self.__cls_cols__:
            new_col = col.new_instance(self)
            self.columns.append(new_col)
            self.key_column_map[new_col.key] = new_col
            if new_col.filter is not None:
                self.filtered_cols[new_col.key] = new_col
            if new_col.has_subtotal:
                self.subtotal_cols[new_col.key] = (
                    subtotal_function_map(new_col.has_subtotal),
                    new_col
                )

    def before_query_hook(self):
        """ Just a hook to give subclasses a chance to change things before executing the query """
        pass

    def build(self):
        self.apply_qs_args()
        self.before_query_hook()
        # this will force the query to execute.  We used to wait to evaluate this but it ended
        # up causing AttributeErrors to be hidden when the grid was used in Jinja.
        # Calling build is now preferred over calling .apply_qs_args() and then .html()
        self.record_count

    def column(self, ident):
        if isinstance(ident, basestring):
            return self.key_column_map[ident]
        return self.columns[ident]

    def iter_columns(self, render_type):
        for col in self.columns:
            if render_type in col.render_in:
                yield col

    def set_renderers(self):
        self.html = HTML(self)
        if xlwt is not None:
            self.xls = XLS(self)
        else:
            self.xls = None

    def set_filter(self, key, op, value):
        self.clear_record_cache()
        self.filtered_cols[key].filter.set(op, value)

    def set_sort(self, *args):
        self.clear_record_cache()
        self.order_by = []

        for key in args:
            if not key:
                continue
            flag_desc = False
            if key.startswith('-'):
                flag_desc = True
                key = key[1:]
            if key in self.key_column_map and self.key_column_map[key].can_sort:
                self.order_by.append((key, flag_desc))
            elif not self.foreign_session_loaded:
                self.user_warnings.append('can\'t sort on invalid key "{0}"'.format(key))

    def set_paging(self, per_page, on_page):
        self.clear_record_cache()
        self.per_page = per_page
        self.on_page = on_page

    def clear_record_cache(self):
        self._record_count = None
        self._records = None

    @property
    def ident(self):
        return self._ident \
            or self.identifier \
            or case_cw2us(self.__class__.__name__)

    @property
    def has_filters(self):
        for col in self.filtered_cols.itervalues():
            if col.filter.is_active:
                return True
        return False

    @property
    def has_sort(self):
        return bool(self.order_by)

    @property
    def record_count(self):
        if self._record_count is None:
            query = self.build_query(for_count=True)
            self._record_count = query.count()
        return self._record_count

    @property
    def records(self):
        if self._records is None:
            query = self.build_query()
            self._records = query.all()
        return self._records

    def _totals_col_results(self, page_totals_only):
        SUB = self.build_query(for_count=(not page_totals_only)).subquery()

        cols = []
        for colname, coltuple in self.subtotal_cols.iteritems():
            sa_aggregate_func, colobj = coltuple

            # column may have a label. If it does, use it
            if isinstance(colobj.expr, sasql.expression._Label):
                aggregate_this = sasql.text(colobj.key)
            elif colobj.expr is None:
                aggregate_this = sasql.literal_column(colobj.key)
            else:
                aggregate_this = colobj.expr

            labeled_aggregate_col = sa_aggregate_func(aggregate_this).label(colname)
            cols.append(labeled_aggregate_col)

        return self.manager.sa_query(*cols).select_entity_from(SUB).first()

    @property
    def page_totals(self):
        if self._page_totals is None:
            self._page_totals = self._totals_col_results(page_totals_only=True)
        return self._page_totals

    @property
    def grand_totals(self):
        if self._grand_totals is None:
            self._grand_totals = self._totals_col_results(page_totals_only=False)
        return self._grand_totals

    @property
    def page_count(self):
        if self.per_page is None:
            return 1
        return max(0, self.record_count - 1) // self.per_page + 1

    def build_query(self, for_count=False):
        has_filters = self.has_filters
        query = self.query_base(self.has_sort, has_filters)
        query = self.query_prep(query, self.has_sort or for_count, has_filters)

        if has_filters:
            query = self.query_filters(query)

        if for_count:
            return query

        query = self.query_sort(query)
        if self.pager_on:
            query = self.query_paging(query)

        return query

    def set_records(self, records):
        self._record_count = len(records)
        self._records = records

    def query_base(self, has_sort, has_filters):
        cols = [col.expr for col in self.columns if col.expr is not None]
        return self.manager.sa_query(*cols)

    def query_prep(self, query, has_sort, has_filters):
        return query

    def query_filters(self, query):
        for col in self.filtered_cols.itervalues():
            if col.filter.is_active:
                query = col.filter.apply(query)
        return query

    def query_paging(self, query):
        if self.on_page and self.per_page:
            offset = (self.on_page - 1) * self.per_page
            query = query.offset(offset).limit(self.per_page)
        return query

    def query_sort(self, query):
        redundant = []
        for key, flag_desc in self.order_by:
            if key in self.key_column_map:
                col = self.key_column_map[key]
                # remove any redundant names, whichever comes first is what we will keep
                if col.key in redundant:
                    continue
                else:
                    redundant.append(col.key)
                query = col.apply_sort(query, flag_desc)
        return query

    def apply_qs_args(self, add_user_warnings=True):
        def args_have_op(args):
            # any of the grid's query string args can be used to
            #   override the session behavior (except export_to)
            r = re.compile(
                self.qs_prefix+'(op\(.*\))'
            )
            return any(r.match(a) for a in args.keys())
        def args_have_page(args):
            r = re.compile(
                self.qs_prefix+'(onpage|perpage)'
            )
            return any(r.match(a) for a in args.keys())
        def args_have_sort(args):
            r = re.compile(
                self.qs_prefix+'(sort[1-3])'
            )
            return any(r.match(a) for a in args.keys())

        args = MultiDict(self.manager.request_args())
        # args are pulled first from the request. If the session feature
        #   is enabled and the request doesn't include grid-related args,
        #   check for either the session key or a default set in the
        #   session args store
        if self.session_on:
            # if session key is in request, set the unique key
            self.session_key = args.get(
                self.prefix_qs_arg_key('session_key'),
                self.session_key
            )
            if not args_have_op(args):
                session_args = self.get_session_store(args)
                # override paging if it exists in the query
                if args_have_page(args):
                    session_args['onpage'] = args.get('onpage')
                    session_args['perpage'] = args.get('perpage')
                # override sorting if it exists in the query
                if args_have_sort(args):
                    session_args['sort1'] = args.get('sort1')
                    session_args['sort2'] = args.get('sort2')
                    session_args['sort3'] = args.get('sort3')
                # flag a foreign session if loading from another grid's session
                grid_key = self.__class__.__name__
                if session_args.get('datagrid', grid_key) != grid_key:
                    self.foreign_session_loaded = True
                args = session_args

            req_args = self.manager.request_args()
            if req_args.has_key(self.prefix_qs_arg_key('export_to')):
                args[self.prefix_qs_arg_key('export_to')] = \
                    req_args[self.prefix_qs_arg_key('export_to')]
            self.save_session_store(args)

        ## filtering (make sure this is above paging otherwise self.page_count
        ## used in the paging section below won't work)
        for col in self.filtered_cols.itervalues():
            filter = col.filter
            filter_op_qsk = self.prefix_qs_arg_key('op({0})'.format(col.key))
            filter_v1_qsk = self.prefix_qs_arg_key('v1({0})'.format(col.key))
            filter_v2_qsk = self.prefix_qs_arg_key('v2({0})'.format(col.key))

            filter_op_value = args.get(filter_op_qsk, None)

            if filter.default_op:
                filter.set(None, None, None)

            if filter_op_value is not None:
                if filter.receives_list:
                    v1 = args.getlist(filter_v1_qsk)
                    v2 = args.getlist(filter_v2_qsk)
                else:
                    v1 = args.get(filter_v1_qsk, None)
                    v2 = args.get(filter_v2_qsk, None)

                try:
                    filter.set(
                        filter_op_value,
                        v1,
                        v2,
                    )
                except Invalid, e:
                    invalid_msg = filter.format_invalid(e, col)
                    self.user_warnings.append(invalid_msg)

        ## paging
        pp_qsk = self.prefix_qs_arg_key('perpage')
        if args.has_key(pp_qsk):
            per_page = self.apply_validator(fev.Int, args[pp_qsk], pp_qsk)
            if per_page is None or per_page < 1:
                per_page = 1
            self.per_page = per_page

        op_qsk = self.prefix_qs_arg_key('onpage')
        if args.has_key(op_qsk):
            on_page = self.apply_validator(fev.Int, args[op_qsk], op_qsk)
            if on_page is None or on_page < 1:
                on_page = 1
            if on_page > self.page_count:
                on_page = self.page_count
            self.on_page = on_page

        ## sorting
        sort_qs_keys = [
            self.prefix_qs_arg_key('sort1'),
            self.prefix_qs_arg_key('sort2'),
            self.prefix_qs_arg_key('sort3'),
        ]
        sort_qs_values = [args[sort_qsk] for sort_qsk in sort_qs_keys if sort_qsk in args]
        if sort_qs_values:
            self.set_sort(*sort_qs_values)

        # handle other file formats
        export_qsk = self.prefix_qs_arg_key('export_to')
        self.set_export_to(args.get(export_qsk, None))

        if add_user_warnings:
            for msg in self.user_warnings:
                self.manager.flash_message('warning', msg)

    def prefix_qs_arg_key(self, key):
        return '{0}{1}'.format(self.qs_prefix, key)

    def apply_validator(self, validator, value, qs_arg_key):
        try:
            return validator.to_python(value)
        except Invalid:
            invalid_msg = '"{0}" grid argument invalid, ignoring'.format(qs_arg_key)
            self.user_warnings.append(invalid_msg)
            return None

    def set_export_to(self, to):
        if to in ('xls',):
            self.export_to = to

    def get_session_store(self, args):
        # check args for a session key. If the key is present,
        #   look it up in the session and use the saved args
        #   (if they have been saved under that key). If not,
        #   look up the class name for a default arg store.
        web_session = self.manager.web_session()
        if 'dgsessions' not in web_session:
            return args
        dgsessions = web_session['dgsessions']
        stored_args = None
        # if dgreset is in args, store the session key if present
        #   and then pass back the incoming args
        reset = args.has_key(self.prefix_qs_arg_key('dgreset'))
        if args.get(self.prefix_qs_arg_key('session_key'), None):
            if dgsessions.get(self.session_key, None):
                stored_args = dgsessions[self.session_key]
        else:
            def_key = '_{0}'.format(self.__class__.__name__)
            stored_args = dgsessions.get(def_key, None)
        return stored_args if (stored_args and not reset) else args

    def save_session_store(self, args):
        # save the args in the session under the session key
        #   and also as the default args for this grid
        web_session = self.manager.web_session()
        if 'dgsessions' not in web_session:
            web_session['dgsessions'] = dict()
        dgsessions = web_session['dgsessions']
        # work with a copy here
        args = MultiDict(args)
        # remove keys that should not be stored
        args.pop(self.prefix_qs_arg_key('export_to'), None)
        args.pop(self.prefix_qs_arg_key('dgreset'), None)
        args['datagrid'] = self.__class__.__name__
        # save in store under grid default and session key
        dgsessions[self.session_key] = args
        dgsessions['_{0}'.format(self.__class__.__name__)] = args

    def __repr__(self):
        return '<Grid "{0}">'.format(self.__class__.__name__)

def row_styler(f):
    f.__grid_rowstyler__ = True
    return f

def col_styler(for_column):
    def decorator(f):
        f.__grid_colstyler__ = for_column
        return f
    return decorator

def col_filter(for_column):
    def decorator(f):
        f.__grid_colfilter__ = for_column
        return f
    return decorator
