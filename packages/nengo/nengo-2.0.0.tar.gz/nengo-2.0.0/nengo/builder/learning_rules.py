import numpy as np

from nengo.builder.builder import Builder
from nengo.builder.operator import DotInc, ElementwiseInc, Operator, Reset
from nengo.builder.signal import Signal
from nengo.builder.synapses import filtered_signal
from nengo.connection import LearningRule
from nengo.ensemble import Ensemble, Neurons
from nengo.learning_rules import BCM, Oja, PES


class SimBCM(Operator):
    """Change the transform according to the BCM rule."""
    def __init__(self, pre_filtered, post_filtered, theta, delta,
                 learning_rate):
        self.post_filtered = post_filtered
        self.pre_filtered = pre_filtered
        self.theta = theta
        self.delta = delta
        self.learning_rate = learning_rate

        self.sets = []
        self.incs = []
        self.reads = [pre_filtered, post_filtered, theta]
        self.updates = [delta]

    def make_step(self, signals, dt, rng):
        pre_filtered = signals[self.pre_filtered]
        post_filtered = signals[self.post_filtered]
        theta = signals[self.theta]
        delta = signals[self.delta]
        alpha = self.learning_rate * dt

        def step():
            delta[...] = np.outer(
                alpha * post_filtered * (post_filtered - theta), pre_filtered)
        return step


class SimOja(Operator):
    """Change the transform according to the OJA rule."""
    def __init__(self, pre_filtered, post_filtered, transform, delta,
                 learning_rate, beta):
        self.post_filtered = post_filtered
        self.pre_filtered = pre_filtered
        self.transform = transform
        self.delta = delta
        self.learning_rate = learning_rate
        self.beta = beta

        self.sets = []
        self.incs = []
        self.reads = [pre_filtered, post_filtered, transform]
        self.updates = [delta]

    def make_step(self, signals, dt, rng):
        transform = signals[self.transform]
        pre_filtered = signals[self.pre_filtered]
        post_filtered = signals[self.post_filtered]
        delta = signals[self.delta]
        alpha = self.learning_rate * dt
        beta = self.beta

        def step():
            # perform forgetting
            post_squared = alpha * post_filtered * post_filtered
            delta[...] = -beta * transform * post_squared[:, None]

            # perform update
            delta[...] += np.outer(alpha * post_filtered, pre_filtered)

        return step


@Builder.register(LearningRule)
def build_learning_rule(model, rule):
    rule_type = rule.learning_rule_type
    model.build(rule_type, rule)


@Builder.register(BCM)
def build_bcm(model, bcm, rule):
    conn = rule.connection
    pre = (conn.pre_obj if isinstance(conn.pre_obj, Ensemble)
           else conn.pre_obj.ensemble)
    post = (conn.post_obj if isinstance(conn.post_obj, Ensemble)
            else conn.post_obj.ensemble)
    transform = model.sig[conn]['transform']
    pre_activities = model.sig[pre.neurons]['out']
    post_activities = model.sig[post.neurons]['out']
    pre_filtered = filtered_signal(model, bcm, pre_activities, bcm.pre_tau)
    post_filtered = filtered_signal(model, bcm, post_activities, bcm.post_tau)
    theta = filtered_signal(model, bcm, post_filtered, bcm.theta_tau)
    delta = Signal(np.zeros((post.n_neurons, pre.n_neurons)),
                   name='BCM: Delta')

    model.add_op(SimBCM(pre_filtered, post_filtered, theta, delta,
                        learning_rate=bcm.learning_rate))
    model.add_op(ElementwiseInc(
        model.sig['common'][1], delta, transform, tag="BCM: Inc Transform"))

    # expose these for probes
    model.sig[rule]['theta'] = theta
    model.sig[rule]['pre_filtered'] = pre_filtered
    model.sig[rule]['post_filtered'] = post_filtered

    model.params[rule] = None  # no build-time info to return


@Builder.register(Oja)
def build_oja(model, oja, rule):
    conn = rule.connection
    pre = (conn.pre_obj if isinstance(conn.pre_obj, Ensemble)
           else conn.pre_obj.ensemble)
    post = (conn.post_obj if isinstance(conn.post_obj, Ensemble)
            else conn.post_obj.ensemble)
    transform = model.sig[conn]['transform']
    pre_activities = model.sig[pre.neurons]['out']
    post_activities = model.sig[post.neurons]['out']
    pre_filtered = filtered_signal(model, oja, pre_activities, oja.pre_tau)
    post_filtered = filtered_signal(model, oja, post_activities, oja.post_tau)
    delta = Signal(np.zeros((post.n_neurons, pre.n_neurons)),
                   name='Oja: Delta')

    model.add_op(SimOja(pre_filtered, post_filtered, transform, delta,
                        learning_rate=oja.learning_rate, beta=oja.beta))
    model.add_op(ElementwiseInc(
        model.sig['common'][1], delta, transform, tag="Oja: Inc Transform"))

    # expose these for probes
    model.sig[rule]['pre_filtered'] = pre_filtered
    model.sig[rule]['post_filtered'] = post_filtered

    model.params[rule] = None  # no build-time info to return


@Builder.register(PES)
def build_pes(model, pes, rule):
    # TODO: Filter activities
    conn = rule.connection
    activities = model.sig[conn.pre_obj]['out']
    error = model.sig[pes.error_connection]['out']

    scaled_error = Signal(np.zeros(error.shape),
                          name="PES:error * learning_rate")
    scaled_error_view = scaled_error.reshape((error.size, 1))
    activities_view = activities.reshape((1, activities.size))
    lr_sig = Signal(pes.learning_rate * model.dt, name="PES:learning_rate")

    model.add_op(Reset(scaled_error))
    model.add_op(DotInc(lr_sig, error, scaled_error, tag="PES:scale error"))

    if conn.solver.weights or (
            isinstance(conn.pre_obj, Neurons) and
            isinstance(conn.post_obj, Neurons)):
        post = (conn.post_obj.ensemble if isinstance(conn.post_obj, Neurons)
                else conn.post_obj)
        transform = model.sig[conn]['transform']
        encoders = model.sig[post]['encoders']
        encoded_error = Signal(np.zeros(transform.shape[0]),
                               name="PES: encoded error")

        model.add_op(Reset(encoded_error))
        model.add_op(DotInc(
            encoders, scaled_error, encoded_error, tag="PES:Encode error"))

        encoded_error_view = encoded_error.reshape((encoded_error.size, 1))
        model.add_op(ElementwiseInc(
            encoded_error_view, activities_view, transform,
            tag="PES:Inc Transform"))
    elif isinstance(conn.pre_obj, Neurons):
        transform = model.sig[conn]['transform']
        model.add_op(ElementwiseInc(
            scaled_error_view, activities_view, transform,
            tag="PES:Inc Transform"))
    else:
        assert isinstance(conn.pre_obj, Ensemble)
        decoders = model.sig[conn]['decoders']
        model.add_op(ElementwiseInc(
            scaled_error_view, activities_view, decoders,
            tag="PES:Inc Decoder"))

    # expose these for probes
    model.sig[rule]['scaled_error'] = scaled_error
    model.sig[rule]['activities'] = activities

    model.params[rule] = None  # no build-time info to return
