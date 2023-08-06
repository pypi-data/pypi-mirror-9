from pug.invest.util import clipped_area
# from scipy.optimize import minimize
import pandas as pd
from matplotlib import pyplot as plt
np = pd.np


t = ['2014-12-09T00:00', '2014-12-09T00:15', '2014-12-09T00:30', '2014-12-09T00:45', '2014-12-09T01:00', '2014-12-09T01:15', '2014-12-09T01:30', '2014-12-09T01:45']
ts = pd.Series([217, 234, 235, 231, 219, 219, 231, 232], index=pd.to_datetime(t))
thresh=234
capacity=562.5   # barely enough to do anything
bounds = (ts.min(), ts.max())
# thresh0 = 0.9*bounds[1] + 0.1*bounds[0]
# optimum = minimize(fun=cost_fun, x0=[thresh0], bounds=[bounds], args=(ts, capacity, bounds, costs))
# thresh = optimum.x[0]
# integral = clipped_area(ts, thresh=thresh)

rows = []
threshes = np.arange(bounds[0]*.9, 1.1*bounds[1], (1.1*bounds[1]-.9*bounds[0])/1000.)
for thresh in threshes:
    integral = clipped_area(ts, thresh=thresh)
    terms = np.array([(10. * (integral - capacity) / capacity) ** 2,
                        2. / 0.1**((bounds[0] - thresh) * capacity / bounds[0]),
                        2. / 0.1**((thresh - bounds[1]) * capacity / bounds[1]),
                        1.2 ** (integral / capacity)])
    row = [thresh, integral] + list(terms) + [np.sum(terms)]
    rows += [row]
labels = ['threshold', 'integral', 'capacity-error-term', 'lower-bound-term', 'upper-bound-term', 'exponential-capacity-term', 'total-cost']

df = pd.DataFrame(rows, columns=labels)
df2 = pd.DataFrame(df[[c for c in df.columns if c[-1] == 'm' or c[-1]=='t']])
df2.index = df['threshold']
df2.plot(logy=True)
plt.show()
