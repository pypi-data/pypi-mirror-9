from rlpy.Domains import BlocksWorld
from rlpy.Agents import Q_Learning
from rlpy.Representations import *
from rlpy.Policies import eGreedy
from rlpy.Experiments import Experiment
import numpy as np
from hyperopt import hp

param_space = {'discover_threshold': hp.loguniform("discover_threshold",
                                                   np.log(1e-3), np.log(1e2)),
               #'lambda_': hp.uniform("lambda_", 0., 1.),
               'boyan_N0': hp.loguniform("boyan_N0", np.log(1e1), np.log(1e5)),
               'initial_learn_rate': hp.loguniform("initial_learn_rate", np.log(5e-2), np.log(1))}


def make_experiment(
        exp_id=1, path="./Results/Temp/{domain}/{agent}/{representation}/",
        discover_threshold=0.03104970,
        lambda_=0.,
        boyan_N0=1220.247254,
        initial_learn_rate=0.27986823):
    opt = {}
    opt["path"] = path
    opt["exp_id"] = exp_id
    opt["max_steps"] = 100000
    opt["num_policy_checks"] = 20
    opt["checks_per_policy"] = 1
    sparsify = 1
    ifddeps = 1e-7
    domain = BlocksWorld(blocks=6, noise=0.3, )
    opt["domain"] = domain
    initial_rep = IndependentDiscretization(domain)
    representation = iFDD(domain, discover_threshold, initial_rep,
                          sparsify=sparsify,
                          useCache=True,
                          iFDDPlus=1 - ifddeps)
    policy = eGreedy(representation, epsilon=0.1)
    opt["agent"] = Q_Learning(
        policy, representation,discount_factor=domain.discount_factor,
        lambda_=lambda_, initial_learn_rate=initial_learn_rate,
        learn_rate_decay_mode="boyan", boyan_N0=boyan_N0)
    experiment = Experiment(**opt)
    return experiment

if __name__ == '__main__':
    from rlpy.Tools.run import run_profiled
    # run_profiled(make_experiment)
    experiment = make_experiment(1)
    experiment.run()
    # experiment.plot()
    # experiment.save()
