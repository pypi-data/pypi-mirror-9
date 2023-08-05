class BaseContent(object):

    def __init__(self, content_id, site=None, **kwargs):
        """creates a new instance


        :param content_id: the content's unique id
        :type content_id: str or int

        :param site: the site's name
        :type site: str or None
        :default site: None

        :param kwargs: additional keyword arguments
        """
        self.site = site
        self.content_id = content_id
        for key, value in kwargs.items():
            setattr(self, '_{}'.format(key), value)

    def __str__(self):
        raise NotImplementedError

    def __lt__(self, other):
        raise NotImplementedError

    @classmethod
    def from_query_result(cls, columns, point_list):
        """creates an instance of Content from pieces of an influxdb query


        :param columns: the list of column names (keys)
        :type columns: [str, ]

        :param point_list: the list of associated instance values for the columns
        :type point_list: [type, ]

        :return: a new instance of Content
        :rtype: BaseContent
        """
        return BaseContent(**dict(zip(columns, point_list)))


class PopularContent(BaseContent):

    def __init__(self, content_id, clicks, site=None, **kwargs):
        """creates a new instance


        :param content_id: the content's unique id
        :type content_id: str or int

        :param clicks: the number of clicks recorded for a piece of content
        :type clicks: int

        :param site: the site's name
        :type site: str or None
        :default site: None

        :param kwargs: additional keyword arguments
        """
        self.clicks = clicks
        super(PopularContent, self).__init__(content_id=content_id, site=site, **kwargs)

    def __str__(self):
        return '[{}] {}: {}'.format(self.site, self.content_id, self.clicks)

    def __lt__(self, other):
        return self.clicks < other.clicks


class TrendingContent(BaseContent):

    def __init__(self, content_id, acceleration, site=None, **kwargs):
        """creates a new instance


        :param content_id: the content's unique id
        :type content_id: str or int

        :param acceleration: the number of clicks recorded for a piece of content between epochs
        :type clicks: int

        :param site: the site's name
        :type site: str or None
        :default site: None

        :param kwargs: additional keyword arguments
        """
        self.acceleration = acceleration
        super(TrendingContent, self).__init__(content_id=content_id, site=site, **kwargs)

    def __str__(self):
        return '[{}] {}: {}'.format(self.site, self.content_id, self.acceleration)

    def __lt__(self, other):
        return self.acceleration < other.acceleration
