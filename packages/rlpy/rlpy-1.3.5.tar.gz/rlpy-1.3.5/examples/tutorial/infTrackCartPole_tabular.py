"""
Cart-pole balancing with tabular representation
"""
from rlpy.Domains import InfCartPoleBalance
from rlpy.Agents import Q_Learning
from rlpy.Representations import *
from rlpy.Policies import eGreedy
from rlpy.Experiments import Experiment
import numpy as np
from hyperopt import hp

param_space = {'discretization': hp.quniform("resolution", 4, 40, 1),
               'lambda_': hp.uniform("lambda_", 0., 1.),
               'boyan_N0': hp.loguniform("boyan_N0", np.log(1e1), np.log(1e5)),
               'initial_learn_rate': hp.loguniform("initial_learn_rate", np.log(5e-2), np.log(1))}


def make_experiment(
        exp_id=1, path="./Results/Temp/{domain}/{agent}/{representation}/",
        boyan_N0=753,
        initial_learn_rate=.7,
        discretization=20.,
        lambda_=0.75):
    opt = {}
    opt["path"] = path
    opt["exp_id"] = exp_id
    opt["max_steps"] = 5000
    opt["num_policy_checks"] = 10
    opt["checks_per_policy"] = 10

    domain = InfCartPoleBalance(episodeCap=1000)
    opt["domain"] = domain
    representation = Tabular(domain,
                             discretization=discretization)
    policy = eGreedy(representation, epsilon=0.1)
    opt["agent"] = Q_Learning(
        policy, representation, discount_factor=domain.discount_factor,
        lambda_=lambda_, initial_learn_rate=initial_learn_rate,
        learn_rate_decay_mode="boyan", boyan_N0=boyan_N0)
    experiment = Experiment(**opt)
    return experiment

if __name__ == '__main__':
    experiment = make_experiment(1)
    experiment.run_from_commandline()
    experiment.plot()
