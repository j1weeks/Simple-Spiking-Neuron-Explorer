# Simple-Spiking-Neuron-Explorer
A graphical user interface for plotting the membrane potential and phase portrait of neurons using the method described by Eugene Izhikevich in his paper, "Simple Model of Spiking Neurons" (2003).

This program simulates the dynamic behavior of a neuron with tunable parameters. Following a short period of rest, the user-defined input current I is applied. The membrane potential and the phase portrait are graphed with optional animations to show the relationship between the two plots over time. 

Installation
1. Download and unzip the .zip file via the Github page, or run "git clone https://github.com/j1weeks/Simple-Spiking-Neuron-Explorer.git".
2. Navigate to the newly created directory in the console.
3. Run "pip install -r requirements.txt".
4. Run "python main.py".

Known Issues
The animation can crash when reaching the end of the user-defined T if that T is greater than or less than 500ms. 
