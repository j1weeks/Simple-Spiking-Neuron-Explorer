# Updated 20251210
import dearpygui.dearpygui as dpg
import numpy as np
from model import simple_spiking_neuron_model
from widgets import ParameterWidgets, PRESETS, PARAM_LABELS


class NeuronExplorer:
    def __init__(self):
        dpg.create_context()

        self.params = PRESETS["Regular Spiking"].copy() # Load Regular Spiking by default
        self.t, self.v, self.u, self.v_vals, self.u_v_nullcline, self.u_u_nullcline = simple_spiking_neuron_model(**self.params)

        self.animate = False
        self.anim_index = 0

        self.v_nc_line = None
        self.u_nc_line = None
        self.show_contours = False


        # Left hand GUI section
        with dpg.window(label="Simple Spiking Neuron Explorer", width=1200, height=850):
            with dpg.group(horizontal=True):
                with dpg.group(horizontal=False, width=200):
                    self.param_widget = ParameterWidgets(
                        callback=self.update_params,
                        param_labels=PARAM_LABELS
                    )
                    
                    # Checkboxes for animation and vector fields
                    dpg.add_checkbox(label="Animate", callback=self.toggle_animation)
                    
                    self.show_vectors=False
                    dpg.add_checkbox(label="Vector Fields", callback=self.toggle_vectors, default_value=False)
                    dpg.add_checkbox(label="Nullclines", callback=self.toggle_contours, default_value=False)


                # Right hand GUI section
                with dpg.group(horizontal=False):
                    # Membrane potential plot
                    with dpg.plot(label="Membrane Potential", height=380, width=850): # Dimensions of displayed plot
                        dpg.add_plot_legend()
                        dpg.add_plot_axis(dpg.mvXAxis, label="Time (ms)")
                        with dpg.plot_axis(dpg.mvYAxis, label="v (mV)", tag="v_axis"):
                            self.line_v = dpg.add_line_series(list(self.t), list(self.v), label="v(t)")
                            self.anim_v_dot = dpg.add_scatter_series([self.t[0]], [self.v[0]],
                                                                     label="Animation",
                                                                     parent="v_axis")

                    # Phase plane plot
                    with dpg.plot(label="Phase Plane", height=380, width=850): # Dimensions of displayed plot
                        dpg.add_plot_legend()
                        dpg.add_plot_axis(dpg.mvXAxis, label="v (mV)")
                        with dpg.plot_axis(dpg.mvYAxis, label="u", tag="u_axis"):
                            self.line_phase = dpg.add_line_series(list(self.v), list(self.u), label="Trajectory")
                            self.anim_phase_dot = dpg.add_scatter_series([self.v[0]], [self.u[0]],
                                                                         label="Animation",
                                                                         parent="u_axis")

                    

        dpg.create_viewport(title='Simple Spiking Neuron Explorer', width=1200, height=850, resizable=True)
        dpg.setup_dearpygui()
        dpg.show_viewport()

        # Frame loop
        while dpg.is_dearpygui_running():
            if self.animate:
                self.animate_step()
            dpg.render_dearpygui_frame()

        dpg.destroy_context()

    def update_params(self):
        (
            self.params_t,
            self.v,
            self.u,
            self.v_vals,
            self.u_v_nullcline,
            self.u_u_nullcline
        ) = simple_spiking_neuron_model(**self.param_widget.get_params())

        self.update_full_plot()
        self.update_contours()   # <-- refresh nullclines


    def update_full_plot(self):
        # Update line series
        dpg.set_value(self.line_v, [list(self.t), list(self.v)])
        dpg.set_value(self.line_phase, [list(self.v), list(self.u)])

        # Reset animation dot to the start of the new trajectory
        self.anim_index = 0
        dpg.set_value(self.anim_v_dot, [[self.t[0]], [self.v[0]]])
        dpg.set_value(self.anim_phase_dot, [[self.v[0]], [self.u[0]]])


    def toggle_animation(self, sender, app_data):
        self.animate = app_data
        self.anim_index = 0

    def animate_step(self):
        self.anim_index += 1
        if self.anim_index >= len(self.t):
            self.anim_index = 0

        # Update positions of scatter dots
        dpg.set_value(self.anim_v_dot, [[self.t[self.anim_index]], [self.v[self.anim_index]]])
        dpg.set_value(self.anim_phase_dot, [[self.v[self.anim_index]], [self.u[self.anim_index]]])

    def toggle_vectors(self, sender, app_data):
        self.show_vectors = app_data
        self.update_vector_field()
        
    import numpy as np

    def update_vector_field(self):
        # Clear previous arrows if any
        if hasattr(self, "vector_lines"):
            for line in self.vector_lines:
                dpg.delete_item(line)
            self.vector_lines = []

        if not self.show_vectors:
            return

        # Create grid
        v_min, v_max = min(self.v), max(self.v)
        u_min, u_max = min(self.u), max(self.u)
        v_vals = np.linspace(v_min, v_max, 15)
        u_vals = np.linspace(u_min, u_max, 15)
        self.vector_lines = []

        a, b, c, d, I = [self.params[k] for k in ["a","b","c","d","I"]]

        for v0 in v_vals:
            for u0 in u_vals:
                dv = 0.04*v0**2 + 5*v0 + 140 - u0 + I
                du = a*(b*v0 - u0)
                
                # Normalize for consistent arrow length
                norm = np.sqrt(dv**2 + du**2)
                scale = 3
                dv = dv / norm * scale
                du = du / norm * scale
                
                # Draw a tiny arrow line
                line = dpg.add_line_series([v0, v0 + dv], [u0, u0 + du],
                                            label="",   # empty label to avoid legend clutter
                                            parent="u_axis")
                self.vector_lines.append(line)

    def toggle_contours(self, sender, app_data):
        self.show_contours = app_data
        self.update_contours()

    def update_contours(self):
        # Remove old curves
        if self.v_nc_line is not None:
            dpg.delete_item(self.v_nc_line)
            self.v_nc_line = None

        if self.u_nc_line is not None:
            dpg.delete_item(self.u_nc_line)
            self.u_nc_line = None

        # If contours are not enabled, end here
        if not self.show_contours:
            return

        v_vals = self.v_vals
        u_v_nc = self.u_v_nullcline
        u_u_nc = self.u_u_nullcline

        # Add new curves to phase plot
        self.v_nc_line = dpg.add_line_series(
            v_vals, u_v_nc, label="v-nullcline", parent="u_axis"
        )
        self.u_nc_line = dpg.add_line_series(
            v_vals, u_u_nc, label="u-nullcline", parent="u_axis"
        )


def main():
    NeuronExplorer()


if __name__ == "__main__":
    main()
