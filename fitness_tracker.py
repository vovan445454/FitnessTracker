import json
import os
from datetime import datetime, timedelta
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle

class DateInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_year = datetime.now().year

    def insert_text(self, substring, from_undo=False):
        if len(self.text) + len(substring) > 10:
            return
        if substring.isdigit() or substring == '.':
            super(DateInput, self).insert_text(substring, from_undo=from_undo)
        self._update_format()

    def _update_format(self):
        text = self.text
        if len(text) == 2 or len(text) == 5:
            self.text += '.'
        elif len(text) == 10:
            try:
                year = int(text[6:])
                if year > self.current_year + 10:
                    self.text = text[:6] + str(self.current_year + 10)
            except ValueError:
                pass

class ExerciseManagerPopup(Popup):
    def __init__(self, exercises, update_spinner, **kwargs):
        super().__init__(**kwargs)
        self.exercises = exercises
        self.update_spinner = update_spinner
        self.title = 'Управление упражнениями'
        self.size_hint = (0.8, 0.8)
        self.content = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.exercise_layout = GridLayout(cols=2, spacing=10, size_hint_y=None, row_default_height=dp(40))
        self.exercise_layout.bind(minimum_height=self.exercise_layout.setter('height'))
        scroll_view = ScrollView()
        scroll_view.add_widget(self.exercise_layout)
        self.content.add_widget(scroll_view)

        input_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.1))
        self.new_exercise_input = TextInput(hint_text='Новое упражнение', multiline=False, font_size='20sp')
        add_button = Button(text='Добавить', size_hint=(0.3, 1), font_size='20sp')
        add_button.bind(on_press=self.add_exercise)
        input_layout.add_widget(self.new_exercise_input)
        input_layout.add_widget(add_button)
        self.content.add_widget(input_layout)

        close_button = Button(text='Закрыть', size_hint=(1, 0.1), font_size='20sp')
        close_button.bind(on_press=self.dismiss)
        self.content.add_widget(close_button)

        self.update_exercise_list()

    def update_exercise_list(self):
        self.exercise_layout.clear_widgets()
        for exercise in self.exercises:
            if exercise != 'Другое':
                exercise_label = Label(text=exercise, size_hint_y=None, height=dp(40), font_size='16sp')
                delete_button = Button(text='Удалить', size_hint_y=None, height=dp(40), size_hint_x=0.25, background_color=(0.9, 0.1, 0.1, 1), font_size='16sp')
                delete_button.bind(on_press=lambda instance, ex=exercise: self.delete_exercise(ex))
                self.exercise_layout.add_widget(exercise_label)
                self.exercise_layout.add_widget(delete_button)

    def add_exercise(self, instance):
        new_exercise = self.new_exercise_input.text.strip()
        if new_exercise.lower() == 'другое':
            print("Нельзя добавить упражнение с именем 'другое'")
            return
        if new_exercise and new_exercise not in self.exercises:
            if 'Другое' in self.exercises:
                self.exercises.remove('Другое')
            self.exercises.append(new_exercise)
            self.exercises.append('Другое')
            self.new_exercise_input.text = ''
            self.update_exercise_list()
            self.update_spinner()

    def delete_exercise(self, exercise):
        if exercise in self.exercises:
            self.exercises.remove(exercise)
            self.update_exercise_list()
            self.update_spinner()

class FitnessTrackerApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.workouts = []
        self.exercises = ['Приседания', 'Отжимания', 'Бег', 'Другое']
        self.data_file = os.path.join(self.user_data_dir, 'workouts.json')
        self.exercises_file = os.path.join(self.user_data_dir, 'exercises.json')
        self.sort_order = 'asc'
        self.load_workouts()
        self.load_exercises()

    def load_workouts(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                self.workouts = json.load(f)

    def save_workouts(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.workouts, f, indent=2)

    def load_exercises(self):
        if os.path.exists(self.exercises_file):
            with open(self.exercises_file, 'r') as f:
                self.exercises = json.load(f)
        else:
            self.exercises = ['Приседания', 'Отжимания', 'Бег', 'Другое']
        if 'Другое' in self.exercises:
            self.exercises.remove('Другое')
        self.exercises.append('Другое')

    def save_exercises(self):
        with open(self.exercises_file, 'w') as f:
            json.dump(self.exercises, f, indent=2)

    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        clock_layout = BoxLayout(size_hint=(1, 0.1))
        with clock_layout.canvas.before:
            Color(0.1, 0.1, 0.1, 1)
            self.clock_bg = Rectangle(size=clock_layout.size, pos=clock_layout.pos)
        clock_layout.bind(size=self._update_bg, pos=self._update_bg)
        self.time_label = Label(text=self.get_moscow_time(), font_size='24sp', color=(1, 1, 1, 1))
        clock_layout.add_widget(self.time_label)
        Clock.schedule_interval(self.update_time, 1)
        self.layout.add_widget(clock_layout)

        input_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.15), padding=10)
        today_button = Button(text='Сегодня', size_hint=(0.15, 1), font_size='20sp')
        today_button.bind(on_press=self.set_today_date)
        input_layout.add_widget(today_button)
        self.date_input = DateInput(hint_text='Дата', multiline=False, font_size='20sp', size_hint_x=0.2)
        input_layout.add_widget(self.date_input)
        self.exercise_spinner = Spinner(text='Тип упражнения', values=self.exercises, font_size='20sp', size_hint_x=0.25)
        self.exercise_spinner.bind(text=self.on_exercise_select)
        input_layout.add_widget(self.exercise_spinner)
        self.reps_input = TextInput(hint_text='Повторения', multiline=False, font_size='20sp', size_hint_x=0.2)
        input_layout.add_widget(self.reps_input)
        self.goal_input = TextInput(hint_text='Подходы', multiline=False, font_size='20sp', size_hint_x=0.2)
        input_layout.add_widget(self.goal_input)
        self.layout.add_widget(input_layout)

        add_button = Button(text='Добавить тренировку', size_hint=(1, 0.1), font_size='20sp')
        with add_button.canvas.before:
            Color(0.1, 0.7, 0.3, 1)
            add_button.bg_rect = Rectangle(size=add_button.size, pos=add_button.pos)
        add_button.bind(size=lambda instance, value: setattr(add_button.bg_rect, 'size', value))
        add_button.bind(pos=lambda instance, value: setattr(add_button.bg_rect, 'pos', value))
        add_button.bind(on_press=self.add_workout)
        self.layout.add_widget(add_button)

        filter_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.1))
        self.date_filter = DateInput(hint_text='Фильтр по дате (дд.мм.гггг)', multiline=False, font_size='20sp')
        self.date_filter.bind(text=self.update_workout_list)  # Привязка события для фильтра по дате
        self.type_filter = Spinner(text='Фильтр по типу', values=self.exercises, font_size='20sp')
        self.type_filter.bind(text=self.update_workout_list)
        filter_layout.add_widget(self.date_filter)
        filter_layout.add_widget(self.type_filter)
        self.layout.add_widget(filter_layout)

        self.sort_button = Button(text='Сортировать по дате (возрастание)', size_hint=(1, 0.1), background_color=(0.1, 0.7, 0.3, 1), font_size='20sp')
        self.sort_button.bind(on_press=self.sort_workouts)
        self.layout.add_widget(self.sort_button)

        reset_button = Button(text='Вернуть весь список', size_hint=(1, 0.1), background_color=(0.1, 0.7, 0.3, 1), font_size='20sp')
        reset_button.bind(on_press=self.reset_filters)
        self.layout.add_widget(reset_button)

        self.workout_layout = GridLayout(cols=5, spacing=10, size_hint_y=None, row_default_height=dp(40))
        self.workout_layout.bind(minimum_height=self.workout_layout.setter('height'))
        self.workout_layout.add_widget(Label(text='Дата', size_hint_y=None, height=dp(40), font_size='18sp'))
        self.workout_layout.add_widget(Label(text='Упражнение', size_hint_y=None, height=dp(40), font_size='18sp'))
        self.workout_layout.add_widget(Label(text='Повторения', size_hint_y=None, height=dp(40), font_size='18sp'))
        self.workout_layout.add_widget(Label(text='Подходы', size_hint_y=None, height=dp(40), font_size='18sp'))
        self.workout_layout.add_widget(Label(text='Действие', size_hint_y=None, height=dp(40), font_size='18sp'))
        scroll_view = ScrollView()
        scroll_view.add_widget(self.workout_layout)
        self.layout.add_widget(scroll_view)

        self.update_workout_list()
        return self.layout

    def _update_bg(self, instance, value):
        self.clock_bg.size = instance.size
        self.clock_bg.pos = instance.pos

    def get_moscow_time(self):
        moscow_time = datetime.utcnow() + timedelta(hours=3)
        return moscow_time.strftime('%H:%M:%S')

    def update_time(self, dt):
        self.time_label.text = self.get_moscow_time()

    def set_today_date(self, instance):
        today = datetime.now().strftime('%d.%m.%Y')
        self.date_input.text = today

    def on_exercise_select(self, spinner, text):
        if text == 'Другое':
            self.open_exercise_manager()

    def open_exercise_manager(self):
        popup = ExerciseManagerPopup(self.exercises, self.update_exercise_spinner)
        popup.open()

    def update_exercise_spinner(self, *args):
        if 'Другое' in self.exercises:
            self.exercises.remove('Другое')
        self.exercises.append('Другое')
        self.exercise_spinner.values = list(self.exercises)  # Обновляем значения явно
        self.type_filter.values = list(self.exercises)      # Обновляем значения явно
        self.save_exercises()

    def add_workout(self, instance):
        date = self.date_input.text.strip()
        exercise = self.exercise_spinner.text
        reps = self.reps_input.text.strip()
        goal = self.goal_input.text.strip()
        if date and exercise != 'Тип упражнения' and reps:
            try:
                datetime.strptime(date, '%d.%m.%Y')
                workout = {
                    'date': date,
                    'exercise': exercise,
                    'reps': reps,
                    'goal': goal
                }
                self.workouts.append(workout)
                self.save_workouts()
                self.date_input.text = ''
                self.reps_input.text = ''
                self.goal_input.text = ''
                self.update_workout_list()
            except ValueError:
                print("Неверный формат даты. Используйте дд.мм.гггг")

    def sort_workouts(self, instance):
        if self.sort_order == 'asc':
            self.workouts.sort(key=lambda w: datetime.strptime(w['date'], '%d.%m.%Y'))
            self.sort_order = 'desc'
            instance.text = 'Сортировать по дате (убывание)'
        else:
            self.workouts.sort(key=lambda w: datetime.strptime(w['date'], '%d.%m.%Y'), reverse=True)
            self.sort_order = 'asc'
            instance.text = 'Сортировать по дате (возрастание)'
        self.update_workout_list()

    def update_workout_list(self, *args):
        while len(self.workout_layout.children) > 5:
            self.workout_layout.remove_widget(self.workout_layout.children[0])
        date_filter = self.date_filter.text.strip()
        type_filter = self.type_filter.text if self.type_filter.text != 'Фильтр по типу' else None

        filtered_workouts = self.workouts[:]
        if date_filter:
            try:
                filter_date = datetime.strptime(date_filter, '%d.%m.%Y').strftime('%d.%m.%Y')
                filtered_workouts = [w for w in filtered_workouts if w['date'] == filter_date]
            except ValueError:
                pass
        if type_filter:
            filtered_workouts = [w for w in filtered_workouts if w['exercise'].lower() == type_filter.lower()]

        for workout in filtered_workouts:
            date_label = Label(text=workout['date'], size_hint_y=None, height=dp(40), font_size='16sp')
            exercise_label = Label(text=workout['exercise'], size_hint_y=None, height=dp(40), font_size='16sp')
            reps_label = Label(text=workout['reps'], size_hint_y=None, height=dp(40), font_size='16sp')
            goal_label = Label(text=workout.get('goal', ''), size_hint_y=None, height=dp(40), font_size='16sp')
            delete_button = Button(text='Удалить', size_hint_y=None, height=dp(40), size_hint_x=0.25, background_color=(0.9, 0.1, 0.1, 1), font_size='16sp')
            delete_button.bind(on_press=lambda instance, w=workout: self.delete_workout(w))
            self.workout_layout.add_widget(date_label)
            self.workout_layout.add_widget(exercise_label)
            self.workout_layout.add_widget(reps_label)
            self.workout_layout.add_widget(goal_label)
            self.workout_layout.add_widget(delete_button)

    def reset_filters(self, instance):
        self.date_filter.text = ''
        self.type_filter.text = 'Фильтр по типу'
        self.update_workout_list()

    def delete_workout(self, workout):
        self.workouts.remove(workout)
        self.save_workouts()
        self.update_workout_list()

if __name__ == '__main__':
    FitnessTrackerApp().run()
