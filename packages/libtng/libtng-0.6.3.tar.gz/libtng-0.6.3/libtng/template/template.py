from jinja2 import Template


def dict_from_context(context):
    """
    Converts context to native python dict.
    """

    if hasattr(context, 'dicts'):
        new_dict = {}
        for i in reversed(list(context)):
            new_dict.update(dict_from_context(i))
        return new_dict

    return dict(context)


class Template(Template):
    """
    Customized template class.
    Add correct handling django context objects.
    """

    def render(self, context={}):
        new_context = dict_from_context(context)
        return super(Template, self).render(new_context)

    def stream(self, context={}):
        new_context = dict_from_context(context)
        return super(Template, self).stream(new_context)