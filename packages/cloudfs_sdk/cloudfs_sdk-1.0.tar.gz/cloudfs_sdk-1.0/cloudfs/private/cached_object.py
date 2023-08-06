import time

class CachedObject(object):
    # no caching by default
    CACHE_EXPIRE = 0

    def __init__(self, rest_interface, data):
        self.rest_interface = rest_interface
        self.changed_meta = set()
        headers = {}
        if rest_interface:
            headers = self.rest_interface.get_latest_header_info()
        self._initialize_self(data, headers)
        self.last_update = time.time()
        self.dirty = False

    def _get(self, property_name, default_value=None):
        if property_name in self.data:
            return self.data[property_name]
        else:
            return default_value

    def _set(self, property_name, new_value, save=True):
        self.changed_meta.add(property_name)
        self.data[property_name] = new_value
        if save:
            self._save()

    def _save(self):
        pass
    # to be overidden by sub-classes
    def _initialize_self(self, request, x_headers={}):
        self.data = request

    def _refresh_request(self, debug=False):
        pass

    def _update_self(self, debug=False):
        result = self._refresh_request(debug)
        x_headers =  self.rest_interface.get_latest_header_info()
        self._initialize_self(result, x_headers)
        self.dirty = False
        self.last_update = time.time()
        return True

    def _prepare_to_read(self):
        if self.CACHE_EXPIRE != None and\
            (self.dirty or (time.time() - self.last_update) > self.CACHE_EXPIRE):
            self._update_self()

    def last_updated(self):
        return self.last_update

    def age(self):
        return time.time() - self.last_update

    def refresh(self, debug=False):
        return self._update_self(debug)

    def _mark_dirty(self):
        self.dirty = True