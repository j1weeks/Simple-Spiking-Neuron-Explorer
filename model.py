# Updated 20251210
import numpy as np


def simple_spiking_neuron_model(a=0.02, b=0.2, c=-65, d=8,
                                I=10, T=500, dt=0.25,
                                T_pre=50):
    """
    All code is based on MATLAB code provided by Dr. Eugene Izhikevich in the following works:
    Izhikevich, E. M. Simple model of spiking neurons. IEEE Trans. Neural Netw. 14, 1569–1572 (2003). 
    Izhikevich, E. M. Dynamical Systems in Neuroscience: The Geometry of Excitability and Bursting. (MIT press, Cambridge, Mass, 2007). 

    Parameters
    ----------
    a : float
        Time scale of the recovery variable; large a = faster recovery
    b : float
        Sensitivity of u to the membrane potential v. Large b means u responds more strongly to changes in v;
        "v and u will be coupled more strongly resulting in possible subthreshold oscillations and low-threshold spiking dynamics."
    c : float
        Reset value of u after a spike (mV). When v crosses the threshold, it is set to c.
    d : float
        Reset increment of recovery variable u after a spike. Represents after-spike effect on u.
        
    I : float or ndarray
        Input current injected into the neuron. Controls the drive that can trigger spikes.
    T : float
        Main simulation time (ms). Constant excitation current I is applied for the duration of T.
    dt : float
        Time step (ms).
    T_pre : float
        Pre-run time (ms) for resting state. Note that excitation with the current I occurs at T=0, or
        in other words after T_pre.

    Returns
    -------
    t_total : ndarray
        Time vector (pre-run + main).
    v_total : ndarray
        Membrane potential over time (mV).
    u_total : ndarray
        Recovery variable over time.
    """
    # ------------------
    # Pre-run
    # ------------------
    t_pre = np.arange(0, T_pre, dt)
    I_pre = np.zeros_like(t_pre)

    v = -65 * np.ones_like(t_pre)
    u = b * v

    for i in range(len(t_pre)-1):
        dv = 0.04*v[i]**2 + 5*v[i] + 140 - u[i] + I_pre[i]
        du = a * (b*v[i] - u[i])
        v[i+1] = v[i] + dv*dt
        u[i+1] = u[i] + du*dt
        if v[i+1] >= 30:
            v[i] = 30
            v[i+1] = c
            u[i+1] += d

    v_pre_end = v[-1]
    u_pre_end = u[-1]

    # ------------------
    # Main simulation
    # ------------------
    t_main = np.arange(0, T, dt)
    I_main = I*np.ones_like(t_main) if np.isscalar(I) else I

    v2 = np.zeros_like(t_main)
    u2 = np.zeros_like(t_main)
    v2[0] = v_pre_end
    u2[0] = u_pre_end

    for i in range(len(t_main)-1):
        dv = 0.04*v2[i]**2 + 5*v2[i] + 140 - u2[i] + I_main[i] # Membrane potential dynamics
        du = a*(b*v2[i] - u2[i]) # Recovery dynamics; see citations above for derivations of dv and du
        v2[i+1] = v2[i] + dv*dt
        u2[i+1] = u2[i] + du*dt
        if v2[i+1] >= 30:
            v2[i] = 30
            v2[i+1] = c
            u2[i+1] += d

    # ------------------
    # Combine pre-run + main
    # ------------------
    t_total = np.concatenate([t_pre - T_pre, t_main])
    v_total = np.concatenate([v, v2])
    u_total = np.concatenate([u, u2])

   # --------------------
    # Compute nullclines - DELETE IF NOT NEEDED
    # --------------------
    v_vals = np.linspace(min(v) - 10, max(v) + 10, 300)

    # v-nullcline: dv/dt = 0 → u = 0.04v² + 5v + 140 + I
    u_v_nullcline = 0.04 * v_vals**2 + 5 * v_vals + 140 + I

    # u-nullcline: du/dt = 0 → u = b*v
    u_u_nullcline = b * v_vals

    return t_total, v_total, u_total, v_vals, u_v_nullcline, u_u_nullcline


 
