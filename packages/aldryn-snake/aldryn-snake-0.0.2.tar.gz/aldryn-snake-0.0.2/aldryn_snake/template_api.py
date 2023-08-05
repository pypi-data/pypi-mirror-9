from django.utils.safestring import mark_safe


class Registry(object):
    def __init__(self):
        self.head = []
        self.tail = []
        
    def add_to_head(self, content):
        self.head.append(content)
    
    def add_to_tail(self, content):
        self.tail.append(content)
        
    def template_processor(self, request):
        obj = TemplateContextProcessor(registry=self, request=request)
        return {
            'TEMPLATE_API_REGISTRY': obj,  # for backwards compatibility
            'ALDRYN_SNAKE': obj,
        }


class TemplateContextProcessor(object):
    def __init__(self, registry, request=None):
        self.registry = registry
        self.request = request

    def render_head(self):
        return self._render(self.registry.head)

    def render_tail(self):
        return self._render(self.registry.tail)

    def _render(self, data):
        result = []
        for item in data:
            if callable(item):
                result.append(item(request=self.request))
            else:
                result.append(item)
        return mark_safe('\n'.join(result))


registry = Registry()
template_processor = registry.template_processor
