from flask.ext.classy import FlaskView
from flask import g, url_for, request, current_app

class MenuManager(object):
    def __init__(self):
        self._menus = {}

    def register_menu(self, menu_id):
        self._menus[menu_id] = Menu(identifier=menu_id)

    def get_menu(self, menu_id):
        return self._menus[menu_id]

    @property
    def menus(self):
        return self._menus


class Menu(object):
    def __init__(self, identifier):
        self.identifier = identifier
        self.items = []

    def register_item(self, item):
        if type(item) != MenuItem:
            raise Exception("Expected item to be of type 'MenuItem'. Got '{}'.".format(type(item)))

        self.items.append(item)
        self.items.sort(key=lambda x: x.position)

    def __iter__(self):
        return self.items.__iter__()

class MenuItem(object):
    def __init__(self, title=None, identifier=None, position=0, href=None,
     menu_id=None, _root_item=False, always_expanded=False):
        self.title = title
        self.identifier = identifier
        self.position = position
        self.href = href
        self.menu_id = menu_id
        self.children = []
        self._root_item = _root_item
        self.always_expanded = always_expanded

    def is_active(self):
        """
        Helper method for determining whether or not a menui tem is currently active
        """
        return self.url() == request.path

    def child_is_active(self):
        return any([x.is_active() for x in self.children]) 

    def should_show_children(self):
        return self.always_expanded or self.child_is_active() or self.is_active()

    def url(self, **kwargs):
        kw = {}
        if hasattr(g, '_menu_kwargs'):
            kw = g._menu_kwargs
        return url_for(self.href, **kw)

    def register_child(self, item):
        if type(item) != MenuItem:
            raise Exception("Expected item to be of type 'MenuItem'. Got '{}'.".format(type(item)))

        self.children.append(item)
        self.children.sort(key=lambda x: x.position)

    def has_children(self):
        return bool(len(self.children)) 

class MenuFlaskView(FlaskView):
    @classmethod
    def register(cls, app):
        """
        Take the cached attributes from the methods that were
        created using the menu_item decorator. 

        Turn them into a list and sort it.
        """

        super(__class__, cls).register(app)
        has_root = False
        if hasattr(cls, '_menu_items'):
            # The class was wrapped, as a root element.
            # Add children
            cls._root_item = cls._menu_items[0]
            has_root = True

        found_root_view = False
        cls._menu_items = []
        for meth_str in dir(cls):
            meth = getattr(cls, meth_str)
            if hasattr(meth, '_menu_items'):
                href = '{}:{}'.format(cls.__name__, meth.__name__)
                for menu_item in meth._menu_items:
                    menu_item.href = href

                    if has_root and menu_item._root_item:
                        found_root_view = True
                        menu_item.menu_id = cls._root_item.menu_id
                        menu_item.position = cls._root_item.position
                        menu_item.children = cls._root_item.children
                        menu_item.always_expanded = cls._root_item.always_expanded
                        cls._root_item = menu_item
                    else:
                        cls._menu_items.append(menu_item)
                        if has_root:
                            cls._root_item.register_child(menu_item)
                        elif menu_item.menu_id:
                            menu = app.menu_manager.get_menu(menu_item.menu_id)
                            menu.register_item(menu_item)

        if has_root and not found_root_view:
            raise Exception('Could not find a root item for {}\' upper menu'\
                ' item.'.format(cls))

        cls._menu_items.sort(key=lambda x: x.position)

        if has_root and hasattr(app, 'menu_manager'):
            menu = app.menu_manager.get_menu(cls._root_item.menu_id)
            menu.register_item(cls._root_item)


    def before_request(self, name, **kwargs):
        """
        Make the menu items accessible to the template renderer.
        Currently there is no context_preprocessor available for 
        FlaskView's, so this is as good as it gets.
        """
        g._menu_kwargs = kwargs
        current_app.jinja_env.globals['menu_items'] = self._menu_items
        current_app.jinja_env.globals['section_menu_items'] = self._root_item.children

def menu_item(title='', identifier=None, position=10, menu_id=None, root_item=False, always_expanded=False):
    def decorator(f):
        item = MenuItem(
            title=title,
            identifier=identifier,
            position=position,
            menu_id=menu_id,
            _root_item=root_item,
            always_expanded=always_expanded
        )
        if not hasattr(f, '_menu_items') or f._menu_items is None:
            f._menu_items = [item]
        else:
            f._menu_items.append(item)
        return f
    return decorator
