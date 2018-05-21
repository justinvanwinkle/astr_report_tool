class Product:
    name = None
    icon = None
    url = None
    title = None


class HomeProduct:
    name = 'home'
    icon = 'home'
    url = '/'
    title = 'Tool List'


class NEOLookup:
    name = 'neo_lookup'
    icon = 'minimize'
    url = '/NEOLookup'
    title = 'NEO Lookup'


class ProductList:
    _product_list = [
        HomeProduct(),
        NEOLookup()]

    def __iter__(self):
        return self.products()

    def products(self):
        for product in self._product_list:
            yield product
