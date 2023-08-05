class Content(object):

    def __init__(self, content_id, clicks, site=None, **kwargs):
        """creates a new instance


        :param content_id: the content's unique id
        :type content_id: str or int

        :param clicks: the number of clicks for the content
        :type clicks: int

        :param site: the site's name
        :type site: str or None
        :default site: None

        :param kwargs: additional keyword arguments that aren't really used, but whatever i'll keep them around
        """
        self.content_id = content_id
        self.clicks = clicks
        self.site = site
        for key, value in kwargs.items():
            setattr(self, '_{}'.format(key), value)

    def __str__(self):
        return '[{}] {}: {}'.format(self.site, self.content_id, self.clicks)

    def __lt__(self, other):
        return self.clicks < other.clicks

    @classmethod
    def from_query_result(cls, columns, point):
        """creates an instance of Content from pieces of an influxdb query


        :param columns: the list of column names (keys)
        :type columns: [str, ]

        :param point: the list of associated instance values for the columns
        :type point: [type, ]

        :return: a new instance of Content
        :rtype: Content
        """
        return Content(**dict(zip(columns, point)))
