
def resolve_config(config, key):
    """Replaces a key (like "filename") in config with the resolved versions that are defined with functions.

    :param config:
    :return:
    """

    def get_resolver(key):
        """
        Return resolve key method
        or generate a resolver that resolves to the literal key value
        :param key:
        :return:
        """
        return key if callable(key) else lambda: key

    resolve_key = f"resolve_{key}"
    for product in config.products.values():
        if not product.get(resolve_key):
            # Set resolver methods only once
            product[resolve_key] = get_resolver(product.get(key))
            for file in product.get('extra_files', []):
                file[resolve_key] = get_resolver(file.get(key))

        # Resolve keys by calling the resolver methods
        product[key] = product[resolve_key]()
        for file in product.get('extra_files', []):
            file[key] = file[resolve_key]()
