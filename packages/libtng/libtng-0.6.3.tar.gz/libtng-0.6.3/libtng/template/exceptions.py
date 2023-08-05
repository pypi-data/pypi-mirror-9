

class TemplateDoesNotExist(Exception):

    def __init__(self, template_name, tried=None):
        Exception.__init__(self, template_name, tried)
        self.template_name = template_name
        self.tried = tried or []