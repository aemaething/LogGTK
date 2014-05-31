import gtk
import gobject
import datetime
from peewee import *
from Models import database, LogEntry
import Fixtures


class LogGTKMainBox(gtk.VBox):
    """
        Specialized Box, implementing the main content stage.
    """
    def __init__(self, app):
        super(LogGTKMainBox, self).__init__()
        self.app = app
        self.pack_start(LogGTKMenuBar(app), 0)
        self.pack_start(LogGTKPaned(app), 1)
        self.pack_end(LogGTKStatusBar(app), 0)
        pass
    pass


class LogGTKMenuBar(gtk.MenuBar):
    """
        Specialized PyGTK MenuBar.
    """
    def __init__(self, app):
        super(LogGTKMenuBar, self).__init__()
        self.app = app
        self.__create_file_menu()
        pass

    def __create_file_menu(self):
        item_file = gtk.MenuItem('File')
        self.append(item_file)

        menu_file = gtk.Menu()
        item_file.set_submenu(menu_file)

        item_exit = gtk.MenuItem('Exit')
        item_exit.connect('activate', self.app.handle_exit)
        menu_file.append(item_exit)
        pass
    pass


class LogGTKStatusBar(gtk.Statusbar):
    """
        Specialized PyGTK Status bar with a move convenient push method.
    """
    def __init__(self, app):
        super(LogGTKStatusBar, self).__init__()
        self.app = app
        self.ctx_id = self.get_context_id('LogGTK')
        self.app.register_component(self.app.WIDGET_STATUS_BAR, self)
        pass

    def push(self, msg):
        super(LogGTKStatusBar, self).push(self.ctx_id, msg)
        pass


class LogGTKButtonBox(gtk.HButtonBox):
    """
        Specialized PyGTK ButtonBox widget.
    """
    def __init__(self, app):
        super(LogGTKButtonBox, self).__init__()
        self.app = app

        self.set_layout(gtk.BUTTONBOX_CENTER)
        self.set_spacing(20)

        self.button_new = gtk.Button(stock=gtk.STOCK_NEW)
        self.button_new.set_tooltip_text("Clears form")
        self.button_new.connect('released', self.app.handle_new)

        self.button_save = gtk.Button(stock=gtk.STOCK_SAVE)
        self.button_save.set_tooltip_text("Persists current entry")
        self.button_save.connect('released', self.app.handle_save)
        self.button_save.set_sensitive(False)

        self.button_delete = gtk.Button(stock=gtk.STOCK_DELETE)
        self.button_delete.set_tooltip_text("Load entry to delete it")
        self.button_delete.set_sensitive(False)
        self.button_delete.connect('released', self.app.handle_delete)

        self.add(self.button_new)
        self.add(self.button_delete)
        self.add(self.button_save)

        self.app.register_component(self.app.WIDGET_BUTTON_BOX, self)
        pass

    def toggle_save(self, state):
        self.button_save.set_sensitive(state)
        pass

    def toggle_delete(self, state):
        self.button_delete.set_sensitive(state)
        pass

    pass


class LogGTKForm(gtk.Table):
    """
        Specialized PyGTK Table widget,
        implements some kind of "form" here.
    """
    def __init__(self, app):
        super(LogGTKForm, self).__init__(2, 5, False)
        self.app = app
        self.set_row_spacings(2)
        self.set_col_spacings(2)
        self.set_border_width(2)

        # id - as 'hidden' form element. comfortable, because of signal usage
        self.id = gtk.Entry()
        self.id.connect('changed', self.check_content)

        # title
        l = gtk.Label('Title:')
        l.set_alignment(0.9, 0.5)
        self.attach(l, 0, 1, 0, 1)
        self.title = gtk.Entry(255)
        self.title.connect('changed', self.check_content)
        self.attach(self.title, 1, 2, 0, 1, gtk.EXPAND | gtk.FILL, gtk.FILL)

        # content
        l = gtk.Label('Content:')
        l.set_alignment(0.9, 0.5)
        self.attach(l, 0, 1, 1, 2)
        scroll = gtk.ScrolledWindow()
        scroll.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.content = gtk.TextView()
        self.buffer = self.content.get_buffer()
        self.content.set_border_width(2)
        self.content.set_wrap_mode(gtk.WRAP_WORD)
        self.content.set_size_request(300, 200)
        scroll.add(self.content)
        self.buffer.connect('changed', self.check_content)
        self.attach(scroll, 1, 2, 1, 2, gtk.EXPAND | gtk.FILL, gtk.EXPAND | gtk.FILL)

        # created_at
        l = gtk.Label('Created at:')
        l.set_alignment(0.9, 0.5)
        self.attach(l, 0, 1, 2, 3)
        self.created_at = gtk.Entry()
        self.created_at.set_editable(False)
        self.created_at.set_can_focus(False)
        self.created_at.set_tooltip_text('readonly')
        self.attach(self.created_at, 1, 2, 2, 3, gtk.EXPAND | gtk.FILL, gtk.FILL)

        # updated_at
        l = gtk.Label('Updated at:')
        l.set_alignment(0.9, 0.5)
        self.attach(l, 0, 1, 3, 4)
        self.updated_at = gtk.Entry()
        self.updated_at.set_editable(False)
        self.updated_at.set_can_focus(False)
        self.updated_at.set_tooltip_text('readonly')
        self.attach(self.updated_at, 1, 2, 3, 4, gtk.EXPAND | gtk.FILL, gtk.FILL)

        # buttons
        self.attach(LogGTKButtonBox(self.app), 1, 2, 4, 5, gtk.EXPAND | gtk.FILL, gtk.FILL)
        self.app.register_component(self.app.WIDGET_FORM, self)
        pass

    def set_entry(self, entry):
        self.id = entry.id
        self.title.set_text(entry.title)
        self.buffer.set_text(entry.content)     # first load has always no effect, here. I've no idea.
        self.created_at.set_text('n/a' if entry.created_at is None else entry.created_at.strftime("%Y-%m-%d %H:%M:%S"))
        self.updated_at.set_text('n/a' if entry.updated_at is None else entry.updated_at.strftime("%Y-%m-%d %H:%M:%S"))
        pass

    def set_selected_id(self, new_id):
        self.id = new_id
        pass

    def get_content(self):
        start, end = self.buffer.get_bounds()
        return self.id, self.title.get_text(), self.buffer.get_text(start, end, True)

    def set_new(self):
        self.id = None
        self.title.set_text('')
        self.buffer.set_text('')
        self.created_at.set_text('')
        self.updated_at.set_text('')
        pass

    def check_content(self, event):
        xid, title, content = self.get_content()
        self.app.components[self.app.WIDGET_BUTTON_BOX].toggle_save(len(title) > 0 and len(content) > 0)
        self.app.components[self.app.WIDGET_BUTTON_BOX].toggle_delete(xid is not None)
        pass

    pass


class LogGTKPaned(gtk.HPaned):
    """
        Specialized PyGTK Paned widget.
    """
    def __init__(self, app):
        super(LogGTKPaned, self).__init__()
        self.app = app

        self.__init_left()
        self.__init_right()
        pass

    def __init_left(self):
        scroll = gtk.ScrolledWindow()
        scroll.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroll.add(LogGTKTreeView(self.app))
        self.add1(scroll)
        pass

    def __init_right(self):
        self.add2(LogGTKForm(self.app))
        pass
    pass


class LogGTKTreeView(gtk.TreeView):
    """
        Specialized PyGTK TreeView widget.
    """
    def __init__(self, app):
        super(LogGTKTreeView, self).__init__()
        self.app = app
        self.data_store = gtk.ListStore(gobject.TYPE_INT, gobject.TYPE_STRING)
        self.__init_data_store()
        self.set_tooltip_text('double-click to load entry')
        self.set_rules_hint(True)
        self.get_selection().set_mode(gtk.SELECTION_SINGLE)
        self.set_enable_search(False)
        self.append_column(self.__create_column_id())
        self.append_column(self.__create_column_created_at())
        self.connect('row-activated', self.app.handle_load)
        self.get_selection().unselect_all()
        self.app.register_component(self.app.WIDGET_TREE_VIEW, self)
        pass

    @staticmethod
    def __create_column_id():
        cell_renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn('ID', cell_renderer, text=1)
        column.set_visible(False)
        return column

    @staticmethod
    def __create_column_created_at():
        cell_renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn('Created at', cell_renderer, text=1)
        column.set_sort_column_id(1)
        return column

    def __init_data_store(self):
        query = self.app.model.select()
        for entry in query:
            self.data_store.append([entry.id, entry.created_at.strftime("%Y-%m-%d %H:%M:%S")])
        self.set_model(self.data_store)
        pass

    def add_entry(self, entry):
        self.data_store.append([entry.id, entry.created_at.strftime("%Y-%m-%d %H:%M:%S")])
        pass

    def delete_entry(self, entry):
        for row in self.data_store:
            if row[0] == entry.id:
                self.data_store.remove(row.iter)
                return
        pass
    pass


class LogGTKWindow(gtk.Window):
    """
        Specialized PyGTK Window.
    """
    def __init__(self, app):
        super(LogGTKWindow, self).__init__(gtk.WINDOW_TOPLEVEL)
        self.app = app

        self.set_title("LogGTK")
        self.set_resizable(True)
        self.set_default_size(640, 480)
        self.set_border_width(4)

        self.add(LogGTKMainBox(app))

        self.connect('destroy', app.handle_exit)

        self.app.components[self.app.WIDGET_STATUS_BAR].push('Application ready')
        self.show_all()
        pass
    pass


class LogGTKApp(object):
    """
        Implementation of OOS EA2
    """
    WIDGET_STATUS_BAR = 'status-bar'
    WIDGET_FORM = 'form'
    WIDGET_BUTTON_BOX = 'button-box'
    WIDGET_TREE_VIEW = 'tree-view'

    def __init__(self, model):
        self.model = model
        self.components = {}    # little tiny dependency injection container
        LogGTKWindow(self)
        pass

    def register_component(self, handle, component):
        self.components[handle] = component
        pass

    @staticmethod
    def handle_exit(_):
        gtk.main_quit()
        pass

    def handle_load(self, tree, foo, bar):
        (store, iter) = tree.get_selection().get_selected()
        selected_id = store.get_value(iter, 0)

        entry = self.model.get(LogEntry.id == selected_id)
        if entry is not None:
            self.components[self.WIDGET_STATUS_BAR].push('Loaded entry ID [%d]' % selected_id)
            self.components[self.WIDGET_FORM].set_entry(self.model.get(LogEntry.id == selected_id))
        else:
            self.components[self.WIDGET_STATUS_BAR].push('Unable to load entry ID [%d]' % selected_id)
        pass

    def handle_save(self, foo):
        selected_id, title, content = self.components[self.WIDGET_FORM].get_content()

        if selected_id is None:
            entry = self.model(title=title, content=content)
            entry.save()
            msg = 'Created new entry ID [%d] on [%s]' % (entry.id, entry.created_at.strftime("%Y-%m-%d %H:%M:%S"))
            self.components[self.WIDGET_TREE_VIEW].add_entry(entry)
        else:
            entry = self.model.get(LogEntry.id == selected_id)
            entry.title = title
            entry.content = content
            entry.updated_at = datetime.datetime.now()
            entry.save()
            msg = 'Updated entry ID [%d] on [%s]' % (selected_id, entry.updated_at.strftime("%Y-%m-%d %H:%M:%S"))
        self.components[self.WIDGET_FORM].set_entry(entry)
        self.components[self.WIDGET_STATUS_BAR].push(msg)
        pass

    def handle_delete(self, event):
        selected_id, title, content = self.components[self.WIDGET_FORM].get_content()
        entry = self.model.get(LogEntry.id == selected_id)
        entry.delete_instance()
        self.components[self.WIDGET_TREE_VIEW].delete_entry(entry)
        self.components[self.WIDGET_FORM].set_new()
        self.components[self.WIDGET_STATUS_BAR].push('Deleted entry ID [%d]' % entry.id)
        pass

    def handle_new(self, event):
        self.components[self.WIDGET_FORM].set_new()
        self.components[self.WIDGET_STATUS_BAR].push('Ready for new input')
        pass

    @staticmethod
    def handle_button_state(event):
        print(event)
        pass

    pass


if __name__ == '__main__':
    database.connect()
    try:
        LogEntry.create_table()
        Fixtures.add_fake_content()
    except OperationalError:
        pass

    LogGTKApp(LogEntry)
    gtk.main()
