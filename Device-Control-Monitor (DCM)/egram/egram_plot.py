# -----------------------------------------------------------------------------
# EGRAM PLOT HANDLER (DARK THEME)
# Handles creation, updating, and formatting of electrogram plots
# Uses matplotlib + helper/egram_utils
# -----------------------------------------------------------------------------

from matplotlib.figure import Figure
from egram.egram_utils import apply_gain, append_and_trim, format_marker_label

# color scheme
BG_COLOR = "#1e1e1e"
AXIS_LABEL_COLOR = "#ffffff"
GRID_COLOR = "#444444"

class EgramPlot:
    def __init__(self, window_seconds):
        # window size in milliseconds
        self.window_ms = window_seconds * 1000

        # buffers
        self.atrial_buf = []
        self.vent_buf = []
        self.surface_buf = []

        # markers
        self.markers = []

        # create figure with dark background
        self.fig = Figure(figsize=(7, 5), dpi=100, facecolor=BG_COLOR)

        self.ax_atrial = self.fig.add_subplot(311, facecolor=BG_COLOR)
        self.ax_vent = self.fig.add_subplot(312, facecolor=BG_COLOR)
        self.ax_surface = self.fig.add_subplot(313, facecolor=BG_COLOR)

        self.line_atrial = None
        self.line_vent = None
        self.line_surface = None

        self.init_axes()

    def init_axes(self):
        for ax, title in zip(
            [self.ax_atrial, self.ax_vent, self.ax_surface],
            ["Atrial EGM", "Ventricular EGM", "Surface ECG"]
        ):
            ax.set_title(title, color=AXIS_LABEL_COLOR)
            ax.set_xlabel("Time (ms)", color=AXIS_LABEL_COLOR)
            ax.set_ylabel("mV", color=AXIS_LABEL_COLOR)
            ax.tick_params(colors=AXIS_LABEL_COLOR)
            ax.grid(True, color=GRID_COLOR)

    def reset(self):
        self.atrial_buf = []
        self.vent_buf = []
        self.surface_buf = []
        self.markers = []

        for ax in [self.ax_atrial, self.ax_vent, self.ax_surface]:
            ax.cla()
            ax.set_facecolor(BG_COLOR)

        self.init_axes()
        self.line_atrial = None
        self.line_vent = None
        self.line_surface = None

    def update_samples(self, channel, samples, gain_str):
        gain_samples = apply_gain(samples, gain_str)
        if channel == "atrial":
            self.atrial_buf = append_and_trim(self.atrial_buf, gain_samples, self.window_ms)
        elif channel == "ventricular":
            self.vent_buf = append_and_trim(self.vent_buf, gain_samples, self.window_ms)
        elif channel == "surface":
            self.surface_buf = append_and_trim(self.surface_buf, gain_samples, self.window_ms)

    def add_marker(self, marker):
        self.markers.append(marker)

    def draw_markers(self, ax, channel_name):
        for marker in self.markers:
            if marker.get("channel") != channel_name:
                continue
            t = marker.get("timestamp_ms", 0)
            label = format_marker_label(marker)
            ax.text(t, 0, label, fontsize=8, color="red")

    def buffer_to_xy(self, buf):
        xs, ys = [], []
        for sample in buf:
            xs.append(sample.get("t", 0))
            ys.append(sample.get("value", 0))
        return xs, ys

    def redraw(self, channels_selected):
        
        """Redraw plots based on selected channels; only show relevant axes with gap."""
        # Clear all axes first
        for ax in [self.ax_atrial, self.ax_vent, self.ax_surface]:
            ax.cla()
            ax.set_facecolor(BG_COLOR)
            ax.set_visible(False)  # hide by default

        self.init_axes()

        fig_height_px = self.fig.get_figheight() * self.fig.get_dpi()
        gap_px = 10
        gap_frac = gap_px / fig_height_px  # convert 10px to figure fraction

        if channels_selected == "both":
            height = ((1.0 - gap_frac) / 2) * 0.75

            # Atrial on top
            self.ax_atrial.set_visible(True)
            self.ax_atrial.set_position([0.1, 0.5 + gap_frac/2 + 0.075, 0.85, height])
            xs, ys = self.buffer_to_xy(self.atrial_buf)
            self.ax_atrial.plot(xs, ys, color="cyan")

            # Ventricular below
            self.ax_vent.set_visible(True)
            self.ax_vent.set_position([0.1, 0.05, 0.85, height])
            xs, ys = self.buffer_to_xy(self.vent_buf)
            self.ax_vent.plot(xs, ys, color="lime")
        else:
            # Single plot fills top
            if channels_selected == "atrial":
                self.ax_atrial.set_visible(True)
                self.ax_atrial.set_position([0.1, 0.05, 0.85, 0.9])
                xs, ys = self.buffer_to_xy(self.atrial_buf)
                self.ax_atrial.plot(xs, ys, color="cyan")
            elif channels_selected == "ventricular":
                self.ax_vent.set_visible(True)
                self.ax_vent.set_position([0.1, 0.05, 0.85, 0.9])
                xs, ys = self.buffer_to_xy(self.vent_buf)
                self.ax_vent.plot(xs, ys, color="lime")
            elif channels_selected == "surface":
                self.ax_surface.set_visible(True)
                self.ax_surface.set_position([0.1, 0.05, 0.85, 0.9])
                xs, ys = self.buffer_to_xy(self.surface_buf)
                self.ax_surface.plot(xs, ys, color="magenta")

        self.adjust_xlim()
        return self.fig






    def adjust_xlim(self):
        latest = 0
        for buf in [self.atrial_buf, self.vent_buf, self.surface_buf]:
            for sample in buf:
                t = sample.get("t", 0)
                if t > latest:
                    latest = t

        left = max(latest - self.window_ms, 0)
        for ax in [self.ax_atrial, self.ax_vent, self.ax_surface]:
            ax.set_xlim(left, latest)
