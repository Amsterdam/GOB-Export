import json


def resolve_config_filenames(config):
    """Replaces filenames in config with the resolved version for the filenames that are defined with functions.

    :param config:
    :return:
    """

    def get_resolver(filename):
        """
        Return resolve filename method
        or generate a resolver that resolves to the literal filename value
        :param filename:
        :return:
        """
        return filename if callable(filename) else lambda: filename

    filename = "filename"
    resolve_filename = "resolve_filename"
    for product in config.products.values():
        if not product.get(resolve_filename):
            # Set resolver methods only once
            product[resolve_filename] = get_resolver(product[filename])
            for file in product.get('extra_files', []):
                file[resolve_filename] = get_resolver(file[filename])

        # Resolve filenames by calling the resolver methods
        product[filename] = product[resolve_filename]()
        for file in product.get('extra_files', []):
            file[filename] = file[resolve_filename]()


def json_loads(item):
    try:
        return json.loads(item)
    except Exception as e:
        print(f"ERROR: Deserialization failed for item {item}.")
        raise e
