import math
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider, TextBox
from matplotlib.animation import FuncAnimation

class ProjectileSimulation:
    def __init__(self):
        # Parametry symulacji – wartości domyślne
        self.default_params = {
            'k1': 1.0,       # opór powietrza [kg/s]
            'm': 10.0,       # masa [kg]
            'g': 9.81,       # grawitacja [m/s²]
            'angle': 45.0,   # kąt [°]
            'v0': 500.0,     # prędkość [m/s]
            'dt': 0.005,     # krok czasowy [s]
            'speed_factor': 1.0  # mnożnik przyspieszenia symulacji
        }
        self.k1 = self.default_params['k1']
        self.m = self.default_params['m']
        self.g = self.default_params['g']
        self.angle = self.default_params['angle']
        self.v0 = self.default_params['v0']
        self.dt = self.default_params['dt']
        self.speed_factor = self.default_params['speed_factor']
        self.t = 0

        # Listy przechowujące punkty trajektorii
        self.x_points = []
        self.y_points = []

        self.simulation_running = False

        # Konfiguracja wykresu
        self.fig, self.ax = plt.subplots()
        plt.subplots_adjust(left=0.1, bottom=0.55)
        self.ax.grid(True)
        self.ax.set_title("Symulacja rzutu ukośnego z oporem powietrza")
        self.ax.set_xlabel("Pozycja X [m]")
        self.ax.set_ylabel("Pozycja Y [m]")
        self.ax.plot(0, 0, 'ro', label="Punkt startowy")
        self.ax.legend()

        # Przyciski Start, Stop i Reset
        self.start_ax = plt.axes([0.75, 0.05, 0.1, 0.075])
        self.stop_ax = plt.axes([0.87, 0.05, 0.1, 0.075])
        self.reset_ax = plt.axes([0.75, 0.15, 0.22, 0.075])
        self.start_button = Button(self.start_ax, 'Start')
        self.stop_button = Button(self.stop_ax, 'Stop')
        self.reset_button = Button(self.reset_ax, 'Reset Parametrów')
        self.start_button.on_clicked(self.start_simulation)
        self.stop_button.on_clicked(self.stop_simulation)
        self.reset_button.on_clicked(self.reset_parameters)

        # Suwaki do dynamicznej zmiany parametrów (działają tylko, gdy symulacja jest zatrzymana, poza speed_factor)
        axcolor = 'lightgoldenrodyellow'
        self.ax_angle = plt.axes([0.1, 0.45, 0.3, 0.03], facecolor=axcolor)
        self.ax_v0 = plt.axes([0.1, 0.40, 0.3, 0.03], facecolor=axcolor)
        self.ax_k1 = plt.axes([0.1, 0.35, 0.3, 0.03], facecolor=axcolor)
        self.ax_g = plt.axes([0.5, 0.45, 0.3, 0.03], facecolor=axcolor)
        self.ax_mass = plt.axes([0.5, 0.40, 0.3, 0.03], facecolor=axcolor)
        self.ax_speed = plt.axes([0.5, 0.35, 0.3, 0.03], facecolor=axcolor)

        self.slider_angle = Slider(self.ax_angle, 'Kąt [°]', 0, 90, valinit=self.angle)
        self.slider_v0 = Slider(self.ax_v0, 'Prędkość [m/s]', 10, 1000, valinit=self.v0)
        self.slider_k1 = Slider(self.ax_k1, 'Opór [kg/s]', 0.1, 10, valinit=self.k1)
        self.slider_g = Slider(self.ax_g, 'Grawitacja [m/s²]', 0, 20, valinit=self.g)
        self.slider_mass = Slider(self.ax_mass, 'Masa [kg]', 1, 100, valinit=self.m)
        self.slider_speed = Slider(self.ax_speed, 'Przyspieszenie', 1, 100, valinit=self.speed_factor)

        self.slider_angle.on_changed(self.update_angle_slider)
        self.slider_v0.on_changed(self.update_v0_slider)
        self.slider_k1.on_changed(self.update_k1_slider)
        self.slider_g.on_changed(self.update_g_slider)
        self.slider_mass.on_changed(self.update_mass_slider)
        self.slider_speed.on_changed(self.update_speed_slider)  # speed_factor działa zawsze

        # Pola tekstowe do ręcznego wprowadzania parametrów (umieszczone poniżej etykiet)
        self.ax_text_angle = plt.axes([0.1, 0.27, 0.15, 0.04])
        self.ax_text_v0 = plt.axes([0.27, 0.27, 0.15, 0.04])
        self.ax_text_k1 = plt.axes([0.44, 0.27, 0.15, 0.04])
        self.ax_text_g = plt.axes([0.61, 0.27, 0.15, 0.04])
        self.ax_text_mass = plt.axes([0.78, 0.27, 0.15, 0.04])
        self.ax_text_speed = plt.axes([0.1, 0.20, 0.15, 0.04])

        # Etykiety tekstowe (przeniesione nad pola)
        self.fig.text(0.1, 0.32, "Kąt [°]")
        self.fig.text(0.27, 0.32, "Prędkość [m/s]")
        self.fig.text(0.44, 0.32, "Opór [kg/s]")
        self.fig.text(0.61, 0.32, "Grawitacja [m/s²]")
        self.fig.text(0.78, 0.32, "Masa [kg]")
        self.fig.text(0.1, 0.25, "Przyspieszenie symulacji")

        self.text_angle = TextBox(self.ax_text_angle, '', initial=str(self.angle))
        self.text_v0 = TextBox(self.ax_text_v0, '', initial=str(self.v0))
        self.text_k1 = TextBox(self.ax_text_k1, '', initial=str(self.k1))
        self.text_g = TextBox(self.ax_text_g, '', initial=str(self.g))
        self.text_mass = TextBox(self.ax_text_mass, '', initial=str(self.m))
        self.text_speed = TextBox(self.ax_text_speed, '', initial=str(self.speed_factor))

        self.text_angle.on_submit(self.update_angle_text)
        self.text_v0.on_submit(self.update_v0_text)
        self.text_k1.on_submit(self.update_k1_text)
        self.text_g.on_submit(self.update_g_text)
        self.text_mass.on_submit(self.update_mass_text)
        self.text_speed.on_submit(self.update_speed_text)

        # Inicjalizacja animacji (na początku nieuruchomiona)
        self.anim = None

    def wspx(self, t):
        angle_rad = math.radians(self.angle)
        return ((self.v0 * self.m / self.k1) * math.cos(angle_rad)) * (1 - math.exp(-self.k1 * t / self.m))

    def wspy(self, t):
        angle_rad = math.radians(self.angle)
        return (((self.v0 * self.m / self.k1) * math.sin(angle_rad)) + (self.m * self.g / self.k1)) * (1 - math.exp(-self.k1 * t / self.m)) - (self.m * self.g * t / self.k1)

    def start_simulation(self, event):
        # Uruchomienie symulacji z aktualnymi parametrami
        self.simulation_running = True
        self.t = 0
        self.x_points.clear()
        self.y_points.clear()
        self.ax.clear()
        self.ax.grid(True)
        self.ax.plot(0, 0, 'ro', label="Punkt startowy")
        self.ax.set_title("Symulacja rzutu ukośnego z oporem powietrza")
        self.ax.set_xlabel("Pozycja X [m]")
        self.ax.set_ylabel("Pozycja Y [m]")
        self.ax.legend()

        if self.anim:
            self.anim.event_source.stop()
        self.anim = FuncAnimation(self.fig, self.update_frame, interval=10, cache_frame_data=False)
        plt.draw()

    def stop_simulation(self, event):
        self.simulation_running = False
        if self.anim:
            self.anim.event_source.stop()

    def reset_parameters(self, event):
        # Przywracanie wartości domyślnych oraz aktualizacja suwaków i pól tekstowych
        self.k1 = self.default_params['k1']
        self.m = self.default_params['m']
        self.g = self.default_params['g']
        self.angle = self.default_params['angle']
        self.v0 = self.default_params['v0']
        self.dt = self.default_params['dt']
        self.speed_factor = self.default_params['speed_factor']
        self.t = 0

        self.slider_angle.set_val(self.angle)
        self.slider_v0.set_val(self.v0)
        self.slider_k1.set_val(self.k1)
        self.slider_g.set_val(self.g)
        self.slider_mass.set_val(self.m)
        self.slider_speed.set_val(self.speed_factor)

        self.text_angle.set_val(str(self.angle))
        self.text_v0.set_val(str(self.v0))
        self.text_k1.set_val(str(self.k1))
        self.text_g.set_val(str(self.g))
        self.text_mass.set_val(str(self.m))
        self.text_speed.set_val(str(self.speed_factor))
        print("Przywrócono parametry do wartości domyślnych.")

    def update_frame(self, frame):
        if not self.simulation_running:
            if self.anim:
                self.anim.event_source.stop()
            return

        x = self.wspx(self.t)
        y = self.wspy(self.t)
        if y < 0 and self.t > 0:
            y = 0
            self.x_points.append(x)
            self.y_points.append(y)
            self.redraw_plot()
            self.simulation_running = False
            if self.anim:
                self.anim.event_source.stop()
            return

        self.x_points.append(x)
        self.y_points.append(y)
        self.redraw_plot()
        self.t += self.dt * self.speed_factor

    def redraw_plot(self):
        self.ax.clear()
        self.ax.grid(True)
        self.ax.plot(0, 0, 'ro', label="Punkt startowy")
        self.ax.plot(self.x_points, self.y_points, label="Trajektoria", color="blue")
        self.ax.legend()
        self.ax.set_title("Symulacja rzutu ukośnego z oporem powietrza")
        self.ax.set_xlabel("Pozycja X [m]")
        self.ax.set_ylabel("Pozycja Y [m]")
        self.ax.relim()
        self.ax.autoscale_view()

    # Callbacki dla suwaków (poza speed_factor, które można zmieniać w trakcie)
    def update_angle_slider(self, val):
        if self.simulation_running:
            print("Zatrzymaj symulację, aby zmienić kąt.")
            return
        self.angle = self.slider_angle.val
        print(f"Zaktualizowano kąt: {self.angle}")

    def update_v0_slider(self, val):
        if self.simulation_running:
            print("Zatrzymaj symulację, aby zmienić prędkość.")
            return
        self.v0 = self.slider_v0.val
        print(f"Zaktualizowano prędkość: {self.v0}")

    def update_k1_slider(self, val):
        if self.simulation_running:
            print("Zatrzymaj symulację, aby zmienić opór.")
            return
        self.k1 = self.slider_k1.val
        print(f"Zaktualizowano opór: {self.k1}")

    def update_g_slider(self, val):
        if self.simulation_running:
            print("Zatrzymaj symulację, aby zmienić grawitację.")
            return
        self.g = self.slider_g.val
        print(f"Zaktualizowano grawitację: {self.g}")

    def update_mass_slider(self, val):
        if self.simulation_running:
            print("Zatrzymaj symulację, aby zmienić masę.")
            return
        self.m = self.slider_mass.val
        print(f"Zaktualizowano masę: {self.m}")

    # Speed factor można zmieniać w trakcie symulacji
    def update_speed_slider(self, val):
        self.speed_factor = self.slider_speed.val
        print(f"Zaktualizowano przyspieszenie symulacji: {self.speed_factor}")

    # Callbacki dla pól tekstowych
    def update_angle_text(self, text):
        if self.simulation_running:
            print("Zatrzymaj symulację, aby zmienić kąt.")
            return
        try:
            self.angle = float(text)
            self.slider_angle.set_val(self.angle)
            print(f"Ręcznie ustawiono kąt: {self.angle}")
        except ValueError:
            print("Nieprawidłowa wartość kąta!")

    def update_v0_text(self, text):
        if self.simulation_running:
            print("Zatrzymaj symulację, aby zmienić prędkość.")
            return
        try:
            self.v0 = float(text)
            self.slider_v0.set_val(self.v0)
            print(f"Ręcznie ustawiono prędkość: {self.v0}")
        except ValueError:
            print("Nieprawidłowa wartość prędkości!")

    def update_k1_text(self, text):
        if self.simulation_running:
            print("Zatrzymaj symulację, aby zmienić opór.")
            return
        try:
            self.k1 = float(text)
            if self.k1 == 0:
                print("Opór nie może być równy 0!")
                return
            self.slider_k1.set_val(self.k1)
            print(f"Ręcznie ustawiono opór: {self.k1}")
        except ValueError:
            print("Nieprawidłowa wartość oporu!")

    def update_g_text(self, text):
        if self.simulation_running:
            print("Zatrzymaj symulację, aby zmienić grawitację.")
            return
        try:
            self.g = float(text)
            self.slider_g.set_val(self.g)
            print(f"Ręcznie ustawiono grawitację: {self.g}")
        except ValueError:
            print("Nieprawidłowa wartość grawitacji!")

    def update_mass_text(self, text):
        if self.simulation_running:
            print("Zatrzymaj symulację, aby zmienić masę.")
            return
        try:
            self.m = float(text)
            self.slider_mass.set_val(self.m)
            print(f"Ręcznie ustawiono masę: {self.m}")
        except ValueError:
            print("Nieprawidłowa wartość masy!")

    def update_speed_text(self, text):
        # Speed factor można zmieniać w trakcie symulacji – brak blokady
        try:
            self.speed_factor = float(text)
            self.slider_speed.set_val(self.speed_factor)
            print(f"Ręcznie ustawiono przyspieszenie: {self.speed_factor}")
        except ValueError:
            print("Nieprawidłowa wartość przyspieszenia!")

if __name__ == '__main__':
    sim = ProjectileSimulation()
    plt.show()
