# -*- coding: utf-8 -*-
from math import ceil
from watson.common import imports


def _table_attr(obj, attr):
    return '{}.{}'.format(obj.__tablename__, attr)


class Pagination(object):
    """Provides simple pagination for query results.

    Attributes:
        query (Query): The SQLAlchemy query to be paginated
        page (int): The page to be displayed
        limit (int): The maximum number of results to be displayed on a page
        total (int): The total number of results
        items (list): The items returned from the query

    Example:

    .. code-block:: python

        # within controller
        query = session.query(Model)
        paginator = Pagination(query, limit=50)

        # within view
        {% for item in paginator %}
        {% endfor %}
        <div class="pagination">
        {% for page in paginator.iter_pages() %}
            {% if page == paginator.page %}
            <a href="#" class="current">{{ page }}</a>
            {% else %}
            <a href="#">{{ page }}</a>
            {% endif %}
        {% endfor %}
        </div>
    """
    query = None
    page = None
    limit = None
    total = None
    items = None

    def __init__(self, query, page=1, limit=20):
        """Initialize the paginator and set some default values.
        """
        self.query = query
        self.page = page
        self.limit = limit
        self.__prepare()

    @property
    def has_previous(self):
        """Return whether or not there are previous pages from the currently
        displayed page.

        Returns:
            boolean
        """
        return self.page > 1

    @property
    def has_next(self):
        """Return whether or not there are more pages from the currently
        displayed page.

        Returns:
            boolean
        """
        return self.page < self.pages

    @property
    def pages(self):
        """The total amount of pages to be displayed based on the number of
        results and the limit being displayed.

        Returns:
            int
        """
        if not self.limit:
            return 0  # pragma: no cover
        else:
            return int(ceil(self.total / float(self.limit)))

    def iter_pages(self):
        """An iterable containing the number of pages to be displayed.

        Example:

        .. code-block:: python

            {% for page in paginator.iter_pages() %}{% endfor %}
        """
        for num in range(1, self.pages + 1):
            yield num

    # Internals

    def __bool__(self):
        return True if self.items else False

    def __iter__(self):
        for result in self.items:
            yield result

    def __prepare(self):
        self.items = self.query.limit(self.limit).offset(
            (self.page - 1) * self.limit).all()
        self.total = 1
        if not self.items and self.page != 1:
            self.total = 0
        if self.page == 1 and len(self.items) < self.limit:
            self.total = len(self.items)
        else:
            self.total = self.query.order_by(None).count()

    def __repr__(self):
        return '<{0} page:{1} limit:{2} total:{3} pages:{4}>'.format(
            imports.get_qualified_name(self),
            self.page, self.limit, self.total, self.pages)
