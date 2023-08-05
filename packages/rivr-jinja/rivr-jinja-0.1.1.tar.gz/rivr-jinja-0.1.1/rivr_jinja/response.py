from rivr.http import Response


class JinjaResponse(Response):
    def __init__(self, request, template_names, context, environment=None,
            *args, **kwargs):
        super(JinjaResponse, self).__init__(*args, **kwargs)
        self.request = request
        self.template_names = template_names
        self.context = context
        self._content = None
        self.environment = environment

        if 'request' not in self.context:
            self.context['request'] = request

    def get_environment(self):
        if self.environment:
            return self.environment

        raise Exception('JinjaResponse is improperly configured'
                        'and requires a jinja environment')

    def render(self):
        environment = self.get_environment()
        template = environment.select_template(self.template_names)
        return template.render(self.context)

    def get_content(self):
        if not self._content:
            self._content = self.render()

        return self._content

    def set_content(self, value):
        pass
    content = property(get_content, set_content)

