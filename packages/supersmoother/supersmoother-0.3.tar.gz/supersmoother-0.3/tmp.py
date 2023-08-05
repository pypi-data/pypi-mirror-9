import numpy as np
import matplotlib.pyplot as plt
from supersmoother import MovingAverageSmoother, LinearSmoother, SuperSmoother

rng = np.random.RandomState(0)
N = 10
period = 1
t = np.linspace(0, period, N, endpoint=False)
y = rng.rand(N)
y = np.arange(N)

t_folded = np.concatenate([-period + t, t, t + period])
y_folded = np.concatenate([y, y, y])

model1 = SuperSmoother(primary_spans=[0.05/3, 0.2/3, 0.5/3],
                       middle_span=0.2/3, final_span=0.5/3, period=None)
model2 = SuperSmoother(period=period)

model1.fit(t_folded, y_folded)
model2.fit(t, y)

print(model1.span_int())
print(model2.span_int())

plt.plot(t_folded, y_folded, '.k')
#plt.plot(model1.t, model1.cv_values())
#plt.plot(model2.t, model2.cv_values())

plt.plot(t, model1.predict(t))
plt.plot(t, model2.predict(t))

plt.show()
exit()

rng = np.random.RandomState(0)
N = 10
period = 1
t = np.linspace(0, period, N, endpoint=False)
y = rng.rand(N)

t_folded = np.concatenate([-period + t[N / 2:], t, t[:N / 2] + period])
y_folded = np.concatenate([y[N / 2:], y, y[:N / 2]])


fig, ax = plt.subplots(3, 2, figsize=(8, 8))

for j, Model in enumerate([MovingAverageSmoother, LinearSmoother]):
    for i, span in enumerate([3, 4, 5]):
        model1 = Model(span / len(t_folded), period=None)
        model2 = Model(span / len(t), period=period)
        ax[i, j].plot(t, model1.fit(t_folded, y_folded).predict(t))
        ax[i, j].plot(t, model2.fit(t, y). predict(t))

plt.show()
