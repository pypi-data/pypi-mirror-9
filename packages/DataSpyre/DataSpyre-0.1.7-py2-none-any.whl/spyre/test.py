import server

import numpy as np
from matplotlib import pyplot as plt
	
class SimpleApp(server.App):
	title = "Simple Sine App"
	inputs = [{ "input_type":"text",
            "variable_name":"freq",
            "value":5,
            "action_id":"plot_sine_wave"}]
	
	outputs = [{"output_type":"plot",
            "output_id":"plot_sine_wave",
            "on_page_load":True }]

	def getPlot(self,params):
		f = int(params['freq'])
		x = np.arange(1,6,0.01)
		y = np.sin(f*x)
		plt.plot(x,y)
		return plt.gcf()

app = SimpleApp()
app.launch()