# coding: utf-8
u"""
Пользовательский интерфейс (окошки).
"""
#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

# 3rdparty
from django.db import models
from m3_ext.ui.windows.edit_window import ExtEditWindow
from m3_ext.ui.controls.buttons import ExtButton
from m3_ext.ui.containers.containers import ExtToolBar
from m3_ext.ui.windows.window import ExtWindow
from m3_ext.ui.panels.grids import ExtMultiGroupinGrid
from m3_ext.ui.containers.forms import ExtForm
from m3_ext.ui.fields import simple as fields
from m3_ext.ui.misc import store as stores

#------------------------------------------------------------------------------
# Windows
#------------------------------------------------------------------------------

class PersonEditWindow(ExtEditWindow):
    def __init__(self, create_new=True, *args, **kwargs):
        super(PersonEditWindow, self).__init__(*args, **kwargs)
        self.icon_cls = 'icon-application-edit'
        self.min_width, self.min_height = self.width, self.height = 400, 200
        self.modal = True
        self.form = ExtForm()

        self.button_align = self.align_left
        self.save_button = ExtButton(
            text=u'Сохранить',
            handler='submitForm')
        self.cancel_button = ExtButton(
            text=u'Закрыть',
            handler='function(){win.close();}')

        self.footer_bar = ExtToolBar()
        self.footer_bar.items.extend([
            self.save_button,
            self.cancel_button,
        ])

        self.init_component(*args, **kwargs)
        self.init_main_form()

    def init_main_form(self):

        # Имя
        # -------------------------------------------------------------
        fname_field = fields.ExtStringField()
        fname_field.label = u'Имя'
        fname_field.name = 'fname'
        fname_field.max_length = 255
        fname_field.anchor = '100%'
        fname_field.allow_blank = False

        self.fname_field = fname_field
        self.form.items.append(fname_field)

        # Фамилия
        # -------------------------------------------------------------
        sname_field = fields.ExtStringField()
        sname_field.label = u'Фамилия'
        sname_field.name = 'sname'
        sname_field.max_length = 255
        sname_field.anchor = '100%'
        sname_field.allow_blank = False

        self.sname_field = sname_field
        self.form.items.append(sname_field)

        # Отчество
        # -------------------------------------------------------------
        mname_field = fields.ExtStringField()
        mname_field.label = u'Фамилия'
        mname_field.name = 'mname'
        mname_field.max_length = 255
        mname_field.anchor = '100%'
        mname_field.allow_blank = False

        self.mname_field = mname_field
        self.form.items.append(mname_field)

        # Дата рождения
        # -------------------------------------------------------------
        birthday_field = fields.ExtDateField()
        birthday_field.label = u'Дата рождения'
        birthday_field.name = 'birthday'
        birthday_field.anchor = '100%'
        birthday_field.allow_blank = False

        self.birthday_field = birthday_field
        self.form.items.append(birthday_field)

        # Пол
        # -------------------------------------------------------------
        gender_field = fields.ExtComboBox()
        gender_field.editable = False
        gender_field.mode = 'local'
        gender_field.display_field = 'name'
        gender_field.value_field = 'id'
        gender_field.label = u'Пол'
        gender_field.name = 'gender'
        gender_field.anchor = '100%'
        gender_field.allow_blank = False
        gender_field.trigger_action = 'all'

        person_model = models.get_model('demo', 'Person')
        gender_field.set_store(
            stores.ExtDataStore(data=person_model.GENDERS_LIST))

        self.gender_field = gender_field
        self.form.items.append(gender_field)


class PersonListWindow(ExtWindow):

    columns = {
        'header': u'Имя',
        'data_index': 'fname',
        'sortable': True,
    }, {
        'header': u'Фамилия',
        'data_index': 'sname',
        'sortable': True,
    }, {
        'header': u'Отчество',
        'data_index': 'mname',
        'sortable': True,
    }, {
        'header': u'Пол',
        'data_index': 'gender',
        'sortable': True,
    }, {
        'header': u'Дата рождения',
        'data_index': 'birthday',
        'sortable': True,
    }

    def __init__(self, *args, **kwargs):
        ExtWindow.__init__(self, *args, **kwargs)
        self.icon_cls = 'icon-application-view-list'
        self.modal = False
        self.layout = 'border'
        self.width, self.height = 800, 600
        self.maximized = True
        self.maximizable = True
        self.minimizable = True
        self.grid = self._create_grid()
        self.items.append(self.grid)
        self.init_component(*args, **kwargs)

    def _create_grid(self):
        grid = ExtMultiGroupinGrid(region='center')
        grid.groupable = False
        grid.plugins.append('new Ext.ux.grid.GridHeaderFilters()')
        grid.plugins.append('new Ext.ux.grid.MultiGroupingSummary()')
        grid.plugins.append('new Ext.ux.grid.MultiSorting()')
        for column in self.columns:
            grid.add_column(**column)
        return grid

    def _add_clear_filters(self):
        self.cancel_button = ExtButton(
            text=u'Закрыть',
            handler='function(){win.close();}')