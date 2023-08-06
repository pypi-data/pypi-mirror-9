from frasco import Feature, action, hook, current_app, g, request, url_for


class MenuMissingError(Exception):
    pass


class Menu(object):
    def __init__(self, name=None, label=None, view=None, login_required=None, childs=None, separator=False, url=None, **options):
        self.name = name
        self.label = label or name.capitalize()
        self.view = view
        self.login_required = login_required
        self.childs = childs or []
        self.separator = separator
        self._url = url
        for k, v in options.iteritems():
            setattr(self, k, v)

    def url(self, **kwargs):
        if self._url:
            return self._url
        if self.view:
            return url_for(self.view, **kwargs)
        return "#"

    def add_child(self, *args, **kwargs):
        self.childs.append(Menu(*args, **kwargs))

    def is_current(self):
        current = getattr(g, "current_menu", None)
        if current is None:
            return request.endpoint == self.view
        return self.name == current

    def is_visible(self):
        if current_app.features.exists("users") and self.login_required is not None:
            if (self.login_required and not current_app.features.users.logged_in()) or \
               (not self.login_required and current_app.features.users.logged_in()):
                return False
        return True

    def __getattr__(self, name):
        return None

    def __iter__(self):
        return iter(self.childs)


class MenuFeature(Feature):
    name = "menu"
    defaults = {"default": None}

    def init_app(self, app):
        app.add_template_global(lambda n: current_app.features.menu[n], "get_menu")
        app.add_template_global(Menu, "menu")

        self.menus = {}
        for name, items in self.options.iteritems():
            if name in self.defaults.keys():
                continue
            self.menus[name] = Menu(name)
            for itemspec in items:
                if isinstance(itemspec, dict):
                    iname, options = itemspec.popitem()
                    if isinstance(options, str):
                        options = {"view": options}
                    elif isinstance(options, list):
                        options = {"childs": options}
                    item = Menu(iname, **options)
                elif itemspec == "--":
                    item = Menu(separator=True)
                else:
                    item = Menu(itemspec, view=iname)
                self.menus[name].childs.append(item)

    def __getitem__(self, name):
        if name not in self.menus:
            raise MenuMissingError("Menu '%s' not found" % name)
        return self.menus[name]

    def ensure(self, name):
        if name not in self.menus:
            self.menus[name] = Menu(name)
        return self.menus[name]

    @hook()
    def before_request(self):
        g.current_menu = self.options["default"]

    @action(default_option="name")
    def set_current_menu(self, name):
        g.current_menu = name