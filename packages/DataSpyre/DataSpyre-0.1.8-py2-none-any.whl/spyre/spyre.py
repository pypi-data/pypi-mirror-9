import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import cherrypy

import server

class App:

	title = None
	inputs = [{		"input_type":'text',
					"label": 'Variable', 
					"value" : "Value Here",
					"variable_name": 'var1'}]

	controls = None

	outputs = [{	"output_type" : "plot",
					"output_id" : "plot",
					"control_id" : "button1",
					"on_page_load" : "true"}]
	outputs = None
	inputs = None
	tabs = None
	templateVars = None
				
	def getJsonData(self, params):
		"""turns the DataFrame returned by getData into a dictionary

		arguments:
		the params passed used for table or d3 outputs are forwarded on to getData
		"""
		df = self.getData(params)
		return df.to_dict(outtype='records')

	def getData(self, params):
		"""Override this function

		arguments:
		params (dict)

		returns:
		DataFrame
		"""
		count = [1,4,3]
		name = ['Override','getData() method','to generate tables']
		df = pd.DataFrame({'name':name, 'count':count})
		return df

	def getPlot(self, params):
		"""Override this function

		arguments:
		params (dict)

		returns:
		matplotlib.pyplot figure
		"""
		plt.title("Override getPlot() method to generate figures")
		return plt.gcf()

	def getImage(self, params):
		"""Override this function

		arguments:
		params (dict)

		returns:
		matplotlib.image figure
		"""
		return np.array([[0,0,0]])

	def getHTML(self, params):
		"""Override this function

		arguments:
		params (dict)

		returns:
		html string
		"""
		return "<b>Override</b> the getHTML method to insert your own HTML <i>here</i>"

	def noOutput(self, params):
		"""Override this function
		A method for doing stuff that doesn't reququire an output (refreshing data,
			updating variables, etc.)

		arguments:
		params (dict)
		"""
		pass

	def getD3(self):
		d3 = {}
		d3['css'] = ""
		d3['js'] = ""
		return d3

	def getCustomJS(self):
		"""Override this function

		returns:
		string of javascript to insert on page load
		"""
		return ""

	def getCustomCSS(self):
		"""Override this function

		returns:
		string of css to insert on page load
		"""
		return ""

	def launch(self,host="local",port=8080):
		webapp = server.Root(templateVars=self.templateVars, title=self.title, inputs=self.inputs, outputs=self.outputs, controls=self.controls, tabs=self.tabs, getJsonDataFunction=self.getJsonData, getDataFunction=self.getData, getPlotFunction=self.getPlot, getImageFunction=self.getImage, getD3Function=self.getD3, getCustomJSFunction=self.getCustomJS, getCustomCSSFunction=self.getCustomCSS, getHTMLFunction=self.getHTML, noOutputFunction=self.noOutput)
		if host!="local":
			cherrypy.server.socket_host = '0.0.0.0'
		cherrypy.server.socket_port = port
		cherrypy.quickstart(webapp)

	def launch_in_notebook(self, port=9095, width=900, height=600):
		"""launch the app within an iframe in ipython notebook"""
		from IPython.lib import backgroundjobs as bg
		from IPython.display import HTML

		jobs = bg.BackgroundJobManager()
		jobs.new(self.launch, kw=dict(port=port))
		return HTML('<iframe src=http://localhost:{} width={} height={}></iframe>'.format(port,width,height))


if __name__=='__main__':
	app = App()
	app.launch()
