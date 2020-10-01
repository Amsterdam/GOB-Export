from flask import Flask
from flask_cors import CORS
from gobexport.config import API_BASE_PATH
from gobexport.exporter import CONFIG_MAPPING


def _health():
    """

    :return: Message telling the API is OK
    """
    return 'Connectivity OK'


def _products():
    """Returns an overview of all generated products with their filenames.

    For example:

    "bag": {
        "woonplaatsen": {
             "esri_actueel": [
                "SHP/BAG_woonplaats.shp",
                "SHP/BAG_woonplaats.dbf",
                "SHP/BAG_woonplaats.shx",
                "SHP/BAG_woonplaats.prj"
            ],
            "uva2": [
                "UVA2_Actueel/WPL_20201001_N_20201001_20201001.UVA2"
            ],
            ...
        },
        ...
    },
    ...,
    "brk": ...

    :return:
    """
    result = {}

    for catalog_name, catalog in CONFIG_MAPPING.items():
        result[catalog_name] = {}
        for collection_name, config in catalog.items():
            result[catalog_name][collection_name] = {}

            for product_name, product in config.products.items():
                filenames = [
                    filename() if callable(filename) else filename for filename in
                    ([product['filename']] + [extra_file['filename'] for extra_file in product.get('extra_files', [])])
                ]

                result[catalog_name][collection_name][product_name] = filenames

    return result


def get_flask_app():
    """
    Initializes the Flask App

    :return: Flask App
    """

    ROUTES = [
        # Health check URL
        ('/status/health/', _health, ['GET']),
        (f'{API_BASE_PATH}/products', _products, ['GET']),
    ]

    app = Flask(__name__)
    CORS(app)

    for route, view_func, methods in ROUTES:
        app.route(rule=route, methods=methods)(view_func)

    return app
