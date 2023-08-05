from collections import OrderedDict
import pandas as pd
import numpy as np
from bokeh.charts import Dot

# create some example data
xyvalues = OrderedDict(
    python=[2, 3, 7, 5, 26],
    pypy=[12, 33, 47, 15, 126],
    jython=[22, 43, 10, 25, 26],
)

# any of the following commented are valid Dot inputs
#xyvalues = pd.DataFrame(xyvalues)
#xyvalues = list(xyvalues.values())
#xyvalues = np.array(list(xyvalues.values()))

dots = Dot(xyvalues, cat=['lists','loops','dicts', 'gen exp', 'exceptions'],
         title="Dots Example", ylabel='Performance', filename="dots.html")
dots.legend("top_left").show()
