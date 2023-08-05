from influxdb import InfluxDBClient

from .models import Content


class ContentClient(object):
    """a client object to interact with influxdb
    """

    def __init__(self, host, port, username, password, db, series):
        """creates a new instance


        :param host: the hostname or ip address to connect the influxdb client
        :type host: str

        :param port: the port number to connect over
        :type port: int

        :param username: a read/write user's username
        :type username: str

        :param password: a read/write user's password
        :type password: str

        :param db: the name of the database to connect to
        :type db: str
        """
        # store vars
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._db = db
        self.series = series

        # create client
        self.client = InfluxDBClient(self._host, self._port, self._username, self._password, self._db)

    def get_content(self, time_offset, limit=None):
        """gets trending content


        :param time_offset: the influxdb formatted time offset interval
        :type time_offset: str

        :param limit: a hard limit on the number of pieces of content returned
        :type limit: int or None
        :default limit: None

        :return: a list of content
        :rtype: [Content, ]
        """
        # construct query
        query = 'select sum(clicks) as clicks ' \
                'from {} ' \
                'where time > now() - {} ' \
                'group by content_id'\
            .format(self.series, time_offset)

        # execute query
        try:
            results = self.client.query(query)
        except:
            query = 'select * from {} where time > now() - {}'
            results = self.client.query(query)

        # make content objects
        content_objects = []
        for result in results:
            site = result.get('name', '').split('.')[0]
            columns = result.get('columns', [])
            points = result.get('points', [])
            for point in points:
                content = Content.from_query_result(columns, point)
                content.site = site
                content_objects.append(content)

        # sort content objects
        content_objects.sort(reverse=True)

        # return objects
        if limit:
            return content_objects[:limit]
        return content_objects
