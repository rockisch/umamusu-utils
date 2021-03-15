import enum


class Templates(enum.Enum):
    ITEM = 'Item'

    @property
    def name_field(self):
        return extra_data[self]['name_field']

    @property
    def cargo_table(self):
        return extra_data[self]['cargo_table']

    @property
    def before(self):
        return extra_data[self].get('before')

    @property
    def after(self):
        return extra_data[self].get('after')

    @property
    def keep_original(self):
        return extra_data[self].get('keep_original')


extra_data = {
    Templates.ITEM: {
        'name_field': 'name',
        'cargo_table': 'item',
        'keep_original': ['name']
    }
}
