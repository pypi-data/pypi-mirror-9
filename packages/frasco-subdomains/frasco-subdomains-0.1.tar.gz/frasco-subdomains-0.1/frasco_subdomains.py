from frasco import Feature, hook, current_context, g


class SubdomainsFeature(Feature):
    name = "subdomains"
    defaults = {"param_name": "subdomain"}
        
    @hook('url_value_preprocessor')
    def extract_subdomain_from_values(self, endpoint, values):
        if values:
            g.subdomain = values.pop(self.options["param_name"], None)
     
    @hook('url_defaults')
    def add_subdomain_to_url_params(self, endpoint, values):
        if self.options["param_name"] not in values:
            values[self.options["param_name"]] = g.subdomain

    @hook()
    def before_request(self, *args, **kwargs):
        current_context["subdomain"] = g.subdomain