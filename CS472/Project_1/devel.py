import numpy as np
import scipy

from Wordle.main import Task

# example of testing a specific task
for i in range(0, 99) :
    # id = 5
    T = Task(i)                # initialize task
    T.plan_path()               # path planning
    T.visualize_path()          # path visualization
    print (T.check_path())      # the validity check of the generated path