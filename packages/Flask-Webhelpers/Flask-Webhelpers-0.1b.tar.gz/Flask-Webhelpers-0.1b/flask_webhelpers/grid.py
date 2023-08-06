from webhelpers.html.grid import Grid
from webhelpers.html.builder import HTML
from webhelpers.html.builder import literal

from flask import url_for
from flask import current_app


class FlaskGrid(Grid):
    """
    Subclass of Grid that can handle header link generation for quick building
    of tables that support ordering of their contents, paginated results etc.
    """
    # We set this flag to false because of backward compatibility
    # Previous versions of Webhelpers did not wrap header and body
    # In containers
    use_header_and_body = False

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(FlaskGrid, self).__init__(*args, **kwargs)

    def use_header_body(self, use=False):
        """Whether or not to wrap the headers and body
           in containers
            Example, wrap heders in <thead>header content</thead>
            Example, wrap body in <tbody>body content</tbody>
        """
        self.use_header_and_body = use

    def default_header_column_format(
        self,
        column_number,
        column_name,
        header_label
    ):
        """We are overriding this method because we want to wrap
            header columns in <th> rather than <td>. <td> is used as
            default in webhelpers
        """
        if column_name == "_numbered":
            column_name = "numbered"
        if column_name in self.exclude_ordering:
            class_name = "c%s %s" % (column_number, column_name)
            return HTML.tag("th", header_label, class_=class_name)
        else:
            header_label = HTML(
                header_label,
                HTML.tag("span", class_="marker")
            )
            class_name = "c%s ordering %s" % (column_number, column_name)
            return HTML.tag("th", header_label, class_=class_name)

    def __html__(self):
        """ renders the grid """
        header_records = []
        body_records = []
        # first render headers record
        headers = self.make_headers()
        r = self.default_header_record_format(headers)
        header_records.append(r)
        # now lets render the actual item grid
        for i, record in enumerate(self.itemlist):
            columns = self.make_columns(i, record)
            if hasattr(self, 'custom_record_format'):
                r = self.custom_record_format(i + 1, record, columns)
            else:
                r = self.default_record_format(i + 1, record, columns)
            body_records.append(r)
        if self.use_header_and_body:
            header_records = HTML.tag(
                'thead',
                HTML(*header_records),
                class_='table-header'
            )
            body_records = HTML.tag(
                'tbody',
                HTML(*body_records),
                class_='table-body'
            )
        else:
            records = header_records + body_records
            return HTML(*records)
        return literal(header_records + body_records)

    def generate_header_link(self, column_number, column, label_text):
        """ This handles generation of link and then decides to call
        self.default_header_ordered_column_format
        or
        self.default_header_column_format
        based on if current column is the one that is used for sorting or not
        """

        # this will handle possible URL generation

        self.order_column = self.request.args.get("order_col", None)
        self.order_dir = self.request.args.get("order_dir", None)

        if column == self.order_column and self.order_dir == "asc":
            new_order_dir = "dsc"
        else:
            new_order_dir = "asc"

        args_items = self.request.args.items()
        args = dict(args_items + self.request.view_args.items())
        args.update(dict(order_col=column, order_dir=new_order_dir))

        url_href = url_for(self.request.endpoint, **args)
        label_text = HTML.tag("a", href=url_href, c=label_text)
        # Is the current column the one we're ordering on?
        if column == self.order_column:
            return self.default_header_ordered_column_format(
                column_number,
                column,
                label_text
            )
        else:
            return self.default_header_column_format(
                column_number,
                column,
                label_text
            )


class FlaskObjectGrid(FlaskGrid):
    """ This grid will work well with sqlalchemy row instances """
    def default_column_format(self, column_number, i, record, column_name):
        class_name = "c%s" % (column_number)
        return HTML.tag("td", getattr(record, column_name), class_=class_name)
