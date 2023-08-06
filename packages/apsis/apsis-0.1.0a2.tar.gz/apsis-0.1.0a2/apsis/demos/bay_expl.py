__author__ = 'Frederik Diehl'

import matplotlib.pyplot as plt
import math
from apsis.assistants.lab_assistant import PrettyLabAssistant
from apsis.models.parameter_definition import MinMaxNumericParamDef
import numpy as np

def obj_func(x):
    return math.sin(x) + ((x/10.)**3 + 50**2 -50*x +x**2)/100.

def obj_der(x):
    return math.cos(x) + (3*(x/10.)**2 -50 + 2*x)/100.

def eval_exp():
    LAss = PrettyLabAssistant()

    param_defs = {
        "x": MinMaxNumericParamDef(0, 100)
    }

    LAss.init_experiment("eval", "BayOpt", param_defs, minimization=False)
    for i in range(10):
        to_eval = LAss.get_next_candidate("eval")
        x = to_eval.params["x"]
        to_eval.result = x
        LAss.update("eval", to_eval)
    for i in range(10):
        to_eval = LAss.get_next_candidate("eval")
        x = to_eval.params["x"]
        to_eval.result = x
        LAss.update("eval", to_eval)
        plot_exp(0, 100, 100, LAss.exp_assistants["eval"])

def plot_exp(min_, max_, steps, EA):
    x = []
    for i in range(steps):
        x.append(min_ + max_/steps * i)

    obj_plt = []
    obj_dplt = []
    predict = []
    for i in range(steps):
        obj_plt.append(obj_func(i))
        obj_dplt.append(obj_der(i))
        predict.append(EA.optimizer.gp.predict(np.matrix(i)))
    plt.plot(obj_plt)
    plt.plot(obj_dplt)
    plt.plot(predict)
    plt.show()

if __name__ == '__main__':
    eval_exp()