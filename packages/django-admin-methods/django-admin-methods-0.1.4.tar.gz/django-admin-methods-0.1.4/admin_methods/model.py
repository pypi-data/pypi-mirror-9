from .exceptions import InvalidFunctionName


def image_thumb(field_name, name='', width=100, description=False, description_text='', if_no_image=''):
    """ 
        Returns a function that can be used as a field on a Django admin list view
        It tries to use an ImageField's url and render it as an image of specified width (defaults to 100)
        If no description is given, short description will be left empty.
        An additional if_no_image named argument can be passed which will be shown if the entry has no image or a url can't be determined
    """
    # Self will be the model instance
    def fn(self):
        try:
            url = getattr(self, field_name).url
        except:
            return if_no_image
        return '<img src="{url}" width="{width}" />'.format(url=url, width=width)
    fn.allow_tags = True

    if not name:
        name = '{}_preview'.format(field_name)
    # Name is needed by Django for unicity
    try:
        fn.__name__ = str(name)
    except UnicodeEncodeError:
        raise InvalidFunctionName('Name parameter is used as the function name. It must be a string (not unicode). For translations, use the description parameter instead')

    # Description is not
    if description:
        if not description_text:
            description_text = name
        fn.short_description = description_text
    else:
        fn.short_description = ''

    return fn