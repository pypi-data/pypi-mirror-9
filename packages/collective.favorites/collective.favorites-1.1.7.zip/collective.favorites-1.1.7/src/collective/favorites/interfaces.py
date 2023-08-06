from zope.interface import Interface


class IFavoriteStorage(Interface):
    """Adapts view, context and request to get
    """

    def add_favorite(self, user_id, id, type, date=None, view=None, **kwargs):
        """Add a favorite of a certain type
        """

    def remove_favorite(self, user_id, id, **kwargs):
        """Remove a favorite
        """

    def list_favorites(self, user_id):
        """List all favorites
        """

class IFavoritesLayer(Interface):
    """BrowserLayer for collective.favorites
    """

class IFavoritesPolicy(Interface):
    """A policy to display favorites
    """

    def get_favorites_infos(self, favorites_list):
        """Gets a list of favorites given by IFavoriteStorage,
        returns a list of dictionaries :
        {'url': url,
        'icon': icon url,
        'title': title,
        'description': description,
        'index': sort index}
        """