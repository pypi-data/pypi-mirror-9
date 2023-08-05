from rivr.views import View
from rivr_jinja.response import JinjaResponse


class JinjaMixin(object):
    template_name = None
    response_class = JinjaResponse

    def get_template_names(self):
        """
        This method will be called to get the template to be rendered, by
        default we will try self.template_name.

        `get_template_names` should return a string or list of template names
        to render.
        """

        if self.template_name is None:
            raise Exception("TemplateResponseMixin requires either a"
                            "definition of 'template_name' or a"
                            "implementation of 'get_template_names()'")
        return [self.template_name]

    def render_to_response(self, context):
        return self.response_class(self.request, self.get_template_names(),
                                   context)


class JinjaView(View, JinjaMixin):
    def get_context_data(self, **kwargs):
        """
        This method will be called to get the context data for the template.
        """

        return {'params': kwargs}

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

