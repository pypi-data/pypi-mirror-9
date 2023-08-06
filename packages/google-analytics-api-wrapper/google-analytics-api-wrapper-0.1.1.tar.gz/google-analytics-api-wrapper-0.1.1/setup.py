from distutils.core import setup

setup(
    name='google-analytics-api-wrapper',
    version='0.1.1',
    packages=['analytics_query'],
    url='https://github.com/tikazyq/google-analytics-api-wrapper',
    download_url='https://github.com/tikazyq/google-analytics-api-wrapper/0.1.1',
    license=open('LICENSE').read(),
    author='Yeqing Zhang',
    author_email='tikazyq@gmail.com',
    description='The Goolge Analytics wrapper is a convenient tool to extract data from GA via API. It is especially '
                'useful when the user has many GA profiles / web properties.',
    keywords=['google-analytics', 'ga', 'pandas', 'dataframe', 'api']
)
