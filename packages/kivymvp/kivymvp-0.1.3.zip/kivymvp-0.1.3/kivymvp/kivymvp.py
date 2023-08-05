from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager


class Model(object):
    def __init__(self, name):
        self.name = name
        self.presenters = []

    def get(self, id):
        raise Exception("not implemented")

    def set(self, id, data):
        for p in self.presenters:
            p.modelEvent(self, id)

class DictModel(Model):
    def __init__(self, name):
        super(DictModel, self).__init__(name)
        self.data = {}

    def get(self, id):
        if id in self.data.keys():
            return self.data[id]
        else:
            return None

    def set(self, id, data):
        self.data[id] = data
        super(DictModel, self).set(id, data)

# e.g. for HttpModel you can just subclass DictModel and overload get, set s.t. you call
# super on get, if no hit, then fallback to http and call set of DictModel with result


class View(Screen):
    def __init__(self, presenter, **kwargs):
        super(View, self).__init__(**kwargs)
        self.presenter = presenter

    def _update(self, data):
        raise Exception("not implemented")

    def set(self, data):
        self._update(data)
        self.canvas.ask_update()

    def emit(self, event):
        self.presenter.userEvent(event)

# a View is just a small wrapper around kivy screens; no need for lots of functionality here.


class Presenter(object):
    def __init__(self, ctrl, viewClass, models):
        self.bus = ctrl.bus
        self.view = viewClass(self, name=self._name())
        ctrl.sm.add_widget(self.view)
        self.models = {}
        for model in models:
            self.models[model.name] = model
            model.presenters.append(self)
            self.modelEvent(model)

    def _name(self):
        raise Exception("not implemented")

    def emit(self, event):
        self.bus.emit(event)

    # generic event from app controller or other presenter
    def receive(self, e):
        pass

    # associated view notifies us of user event, update model appropriately
    def userEvent(self, e):
        raise Exception("not implemented")

    # model notfies us of update, refresh the view
    def modelEvent(self, model, e=None):
        raise Exception("not implemented")


class AppController(object):
    def __init__(self):
        class EventBus(object):
            def __init__(self):
                self.listeners = []

            def register(self, obj):
                self.listeners.append(obj)

            def emit(self, event):
                for listener in self.listeners:
                    listener.receive(event)
        self.bus = EventBus()
        self.bus.register(self)
        self.sm = ScreenManager()
        self.presenters = {}
        sm = self.sm

        class KivyMVPApp(App):
            def build(self):
                return sm
            def on_pause(self):
                pass
            def on_resume(self):
                pass

        self.app = KivyMVPApp()

    def go(self, firstView):
        self.sm.current = firstView
        self.app.run()

    def receive(self, e):
        pass

    def add(self, pres):
        if pres._name() in self.presenters:
            raise Exception("presenter with name %s exists" % name)
        self.presenters[pres._name()] = pres
        self.bus.register(pres)


if __name__ == '__main__':
    import time
    from kivy.graphics import Color, Rectangle
    from kivy.uix.button import Button
    from kivy.uix.floatlayout import FloatLayout
    from kivy.uix.label import Label

    class TestAppController(AppController):
        def receive(self, e):
            if e == "switch":
                for p in self.presenters:
                    if self.sm.current != p:
                        self.sm.current = p
                        break

    ctrl = TestAppController()

    model = DictModel("aSingleNumber")
    model.set(0, 0)

    # This is a very basic example. Of course we should not duplicate code
    # for such a small difference in functionality. It is just to outlines
    # how the framework is intended to be used.
    class BlackPresenter(Presenter):
        def _name(self):
            return "black"

        def userEvent(self, e):
            if e == "done":
                self.emit("switch")
            elif e == "add":
                x = self.models["aSingleNumber"].get(0)
                self.models["aSingleNumber"].set(0, x+1)

        def modelEvent(self, m, e=None):
            self.view.set(str(m.get(0)))

    class WhitePresenter(Presenter):
        def _name(self):
            return "white"

        def userEvent(self, e):
            if e == "done":
                self.emit("switch")
            elif e == "subtract":
                x = self.models["aSingleNumber"].get(0)
                self.models["aSingleNumber"].set(0, x-1)

        def modelEvent(self, m, e=None):
            self.view.set(str(m.get(0)))

    class ColorLayout(FloatLayout):
        def __init__(self, color, **kwargs):
            super(ColorLayout, self).__init__(**kwargs)
            with self.canvas.before:
                Color(color[0], color[1], color[2], color[3])
                self.rect = Rectangle(size=self.size, pos=self.pos)
            self.bind(size=self._update_rect, pos=self._update_rect)

        def _update_rect(self, instance, value):
            self.rect.pos = instance.pos
            self.rect.size = instance.size

    class BlackView(View):
        def __init__(self, presenter, **kwargs):
            super(BlackView, self).__init__(presenter, **kwargs)
            with self.canvas:
                f = ColorLayout((0,0,0,1))
                self.l = Label(text="TEST", size_hint=(1, 0.25), pos_hint={ "x":0, "y":0.8 },
                     color=(0.75, 0.75, 0.75, 1), font_size=60)
                f.add_widget(self.l)
                b = Button(text='add', font_size=20, size_hint=(1, 0.25),
                    pos_hint={ "x":0, "y":0.25 })
                b.bind(on_press=lambda x: self.emit("add"))
                f.add_widget(b)
                b = Button(text='to white', font_size=20, size_hint=(1, 0.25))
                b.bind(on_press=lambda x: self.emit("done"))
                f.add_widget(b)
                self.add_widget(f)

        def _update(self, data):
            self.l.text = data

    class WhiteView(View):
        def __init__(self, presenter, **kwargs):
            super(WhiteView, self).__init__(presenter, **kwargs)
            with self.canvas:
                f = ColorLayout((1,1,1,1))
                self.l = Label(text="TEST", size_hint=(1, 0.25), pos_hint={ "x":0, "y":0.8 },
                    color=(0.75, 0.75, 0.75, 1), font_size=60)
                f.add_widget(self.l)
                b = Button(text='subtract', font_size=20, size_hint=(1, 0.25),
                    pos_hint={ "x":0, "y":0.25 })
                b.bind(on_press=lambda x: self.emit("subtract"))
                f.add_widget(b)
                b = Button(text='to black', font_size=20, size_hint=(1, 0.25))
                b.bind(on_press=lambda x: self.emit("done"))
                f.add_widget(b)
                self.add_widget(f)

        def _update(self, data):
            self.l.text = data

    black_pres = BlackPresenter(ctrl, BlackView, [model])
    white_pres = WhitePresenter(ctrl, WhiteView, [model])

    ctrl.add(white_pres)
    ctrl.add(black_pres)

    ctrl.go('black')