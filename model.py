# Updated 20251210
import numpy as np


def simple_spiking_neuron_model(a=0.02, b=0.2, c=-65, d=8,
                                I=10, T=500, dt=0.25, T_pre=50):
                                    
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
    n_pre = int(T_pre / dt)
    v = -65.0
    u = b * v

    v_pre = np.zeros(n_pre)
    u_pre = np.zeros(n_pre)

    for i in range(n_pre):
        dv = 0.04*v*v + 5*v + 140 - u
        v += 0.5*dv*dt
        dv = 0.04*v*v + 5*v + 140 - u
        v += 0.5*dv*dt
        u += a*(b*v - u)*dt

        if v >= 30:
            v = c
            u += d

        v_pre[i] = v
        u_pre[i] = u

    # Main simulation
    n_main = int(T / dt)
    v_main = np.zeros(n_main)
    u_main = np.zeros(n_main)

    # start from pre-end
    v = v_pre[-1]
    u = u_pre[-1]

    for i in range(n_main):
        dv = 0.04*v*v + 5*v + 140 - u + I
        v += 0.5*dv*dt
        dv = 0.04*v*v + 5*v + 140 - u + I
        v += 0.5*dv*dt
        u += a*(b*v - u)*dt

        if v >= 30:
            v = c
            u += d

        v_main[i] = v
        u_main[i] = u

    # -----------------------
    # Combine pre + main time arrays
    # -----------------------
    t_pre = np.arange(-T_pre, 0, dt)
    t_main = np.arange(0, T, dt)

    t_total = np.concatenate((t_pre, t_main))
    v_total = np.concatenate((v_pre, v_main))
    u_total = np.concatenate((u_pre, u_main))

    # -----------------------
    # Nullclines
    # -----------------------
    v_vals = np.linspace(min(v_total) - 10, max(v_total) + 10, 300)
    u_v_nullcline = 0.04*v_vals**2 + 5*v_vals + 140 + I
    u_u_nullcline = b * v_vals

    return t_total, v_total, u_total, v_vals, u_v_nullcline, u_u_nullcline

