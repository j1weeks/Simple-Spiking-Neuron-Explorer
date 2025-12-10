# Updated 20251210
import dearpygui.dearpygui as dpg


# Based on the suggestions in the 2003 paper
PRESETS = {
    "Regular Spiking": {"a": 0.02, "b": 0.2, "c": -65, "d": 8, "I": 10},
    "Fast Spiking": {"a": 0.1, "b": 0.2, "c": -65, "d": 2, "I": 10},
    "Intrinsically Bursting": {"a": 0.02, "b": 0.2, "c": -55, "d": 4, "I": 10},
    "Chattering": {"a": 0.02, "b": 0.2, "c": -50, "d": 2, "I": 10},
    "Low-Threshold Spiking": {"a": 0.02, "b": 0.25, "c": -65, "d": 2, "I": 10},
    "Thalamo-cortical": {"a": 0.02, "b": 0.25, "c": -65, "d": 0.05, "I": 1},
    "Resonator": {"a": 0.1, "b": 0.25, "c": -65, "d": 2, "I": 10},
}

# Justification for these values can be found in Dynamical Systems in Neuroscience
SLIDER_RANGES = {
    "a": (0.0, 1.0),
    "b": (0.0, 1.0),
    "c": (-100, 0), # in mV
    "d": (0.0, 10.0),
    "I": (0.0, 20.0),
}

PARAM_LABELS = {
    "a": "Time scale a",
    "b": "Sensitivity b",
    "c": "Reset value c (mV)",
    "d": "Reset Increment d",
    "I": "Input Current I",
}

class ParameterWidgets:
    """
    Creates sliders and preset buttons for neuron parameters.
    """
    def __init__(self, callback, param_labels=None):
        self.callback = callback  # function to call when params change
        self.sliders = {}
        self.param_labels = param_labels if param_labels else {key: key for key in SLIDER_RANGES}
        self.create_widgets()

    def create_widgets(self):
        with dpg.group(horizontal=False):
            # Sliders with labels on top
            for key in ["a", "b", "c", "d", "I"]:
                label = self.param_labels.get(key, key)
                with dpg.group(horizontal=False):
                    dpg.add_text(label)
                    self.sliders[key] = dpg.add_slider_float(
                        min_value=SLIDER_RANGES[key][0],
                        max_value=SLIDER_RANGES[key][1],
                        default_value=PRESETS["Regular Spiking"][key],
                        width=250,
                        format="%.3f",
                        callback=self.slider_callback,
                        tag=key
                    )
                    dpg.add_spacer(height=5)

            # Presets section
            dpg.add_spacer(height=20)
            dpg.add_text("Presets")
            dpg.add_spacer(height=5)

            for preset_name, preset_vals in PRESETS.items():
                # Factory function ensures correct binding
                def make_callback(preset):
                    def callback(sender, app_data):
                        self.apply_preset(preset)
                    return callback
                dpg.add_button(label=preset_name, callback=make_callback(preset_vals))

    def slider_callback(self, sender, app_data, user_data):
        if self.callback:
            self.callback()

    def apply_preset(self, preset_vals):
        # Update slider values
        for key, val in preset_vals.items():
            dpg.set_value(key, val)
        # Notify main program to update plots
        if self.callback:
            self.callback()

    def get_params(self):
        return {key: dpg.get_value(key) for key in self.sliders}
