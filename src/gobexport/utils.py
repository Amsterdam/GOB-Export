
def resolve_config_filenames(config):
    """Replaces filenames in config with the resolved version for the filenames that are defined with functions.

    :param config:
    :return:
    """

    for product in config.products.values():
        product['filename'] = product['filename']() if callable(product['filename']) else product['filename']

        for file in product.get('extra_files', []):
            file['filename'] = file['filename']() if callable(file['filename']) else file['filename']
