import time

from predictor import Predictor

today = 1578528000

menu = []
for i in range(5):
    menu.append(int(raw_input()))

time1 = time.time()
pd = Predictor(today, 20, menu)
pd.connectDB("localhost", "pi", "raspberry", "cafeteria")
print(pd.predict())
time2 = time.time()
print(str(time2-time1) + " seconds")
