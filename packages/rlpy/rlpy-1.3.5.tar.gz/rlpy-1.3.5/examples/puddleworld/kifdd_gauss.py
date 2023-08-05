"""
Cart-pole balancing with continuous / Kernelized iFDD
"""

from rlpy.Domains import PuddleWorld
from rlpy.Agents import SARSA, Q_LEARNING
from rlpy.Representations import *
from rlpy.Policies import eGreedy
from rlpy.Experiments import Experiment
import numpy as np
from hyperopt import hp
from rlpy.Representations import KernelizediFDD

param_space = {
    'kernel_resolution':
    hp.loguniform("kernel_resolution", np.log(3), np.log(100)),
    'discover_threshold':
    hp.loguniform(
        "discover_threshold",
        np.log(1e-2),
        np.log(1e1)),
    'lambda_': hp.uniform("lambda_", 0., 1.),
    'boyan_N0': hp.loguniform("boyan_N0", np.log(1e1), np.log(1e5)),
    'initial_learn_rate': hp.loguniform("initial_learn_rate", np.log(1e-3), np.log(1))}


def make_experiment(
        exp_id=1, path="./Results/Temp/{domain}/{agent}/{representation}/",
        discover_threshold=.0807,
        boyan_N0=389.56,
        lambda_=0.52738,
        initial_learn_rate=.424409,
        kernel_resolution=8.567677):
    opt = {}
    opt["path"] = path
    opt["exp_id"] = exp_id
    opt["max_steps"] = 40000
    opt["num_policy_checks"] = 20
    opt["checks_per_policy"] = 100
    active_threshold = 0.01
    max_base_feat_sim = 0.5
    sparsify = 1

    domain = PuddleWorld()
    opt["domain"] = domain
    kernel_width = (
        domain.statespace_limits[:,
                                 1] - domain.statespace_limits[:,
                                                               0]) / kernel_resolution
    representation = KernelizediFDD(domain, sparsify=sparsify,
                               kernel=gaussian_kernel,
                               kernel_args=[kernel_width],
                               active_threshold=active_threshold,
                               discover_threshold=discover_threshold,
                               normalization=True,
                               max_active_base_feat=10, max_base_feat_sim=max_base_feat_sim)
    policy = eGreedy(representation, epsilon=0.1)
    opt["agent"] = Q_LEARNING(policy, representation, discount_factor=domain.discount_factor,
                       lambda_=lambda_, initial_learn_rate=initial_learn_rate,
                       learn_rate_decay_mode="boyan", boyan_N0=boyan_N0)
    experiment = Experiment(**opt)
    return experiment

if __name__ == '__main__':
    experiment = make_experiment(1)
    experiment.run()
    experiment.save()
