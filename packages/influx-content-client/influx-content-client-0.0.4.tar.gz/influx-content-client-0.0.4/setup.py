from distutils.core import setup


setup(
    name='influx-content-client',
    version='0.0.4',

    packages=['influx_content_client'],

    install_requires=[
        'influxdb==0.1.13'
    ],

    author='Vince Forgione',
    author_email='vforgione@theonion.com',
    description='a thin wrapper around the influxdb client to work with content series '
                '-- see https://github.com/theonion/influx-trending',

    url='https://github.com/theonion/influx-content-client'
)
