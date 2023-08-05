import numpy as np

from nengo.builder.builder import Builder
from nengo.builder.signal import Signal
from nengo.builder.operator import DotInc, Operator, Reset
from nengo.node import Node


class SimPyFunc(Operator):
    """Set signal `output` by some non-linear function of x, possibly t"""

    def __init__(self, output, fn, t_in, x):
        self.output = output
        self.fn = fn
        self.t_in = t_in
        self.x = x

        self.sets = [] if output is None else [output]
        self.incs = []
        self.reads = [] if x is None else [x]
        self.updates = []

    def __str__(self):
        return "SimPyFunc(%s -> %s '%s')" % (self.x, self.output, self.fn)

    def make_step(self, signals, dt, rng):
        output = signals[self.output] if self.output is not None else None
        fn = self.fn
        t_in = self.t_in
        t_sig = signals['__time__']

        args = []
        if self.x is not None:
            x_sig = signals[self.x].view()
            x_sig.flags.writeable = False
            args += [x_sig]

        def step():
            y = fn(t_sig.item(), *args) if t_in else fn(*args)
            if output is not None:
                if y is None:
                    raise ValueError(
                        "Function '%s' returned invalid value" % fn.__name__)
                output[...] = y

        return step


def build_pyfunc(model, fn, t_in, n_in, n_out, label):
    if n_in:
        sig_in = Signal(np.zeros(n_in), name="%s.input" % label)
        model.add_op(Reset(sig_in))
    else:
        sig_in = None

    if n_out > 0:
        sig_out = Signal(np.zeros(n_out), name="%s.output" % label)
    else:
        sig_out = None

    model.add_op(SimPyFunc(output=sig_out, fn=fn, t_in=t_in, x=sig_in))

    return sig_in, sig_out


@Builder.register(Node)
def build_node(model, node):
    # Get input
    if node.output is None or callable(node.output):
        if node.size_in > 0:
            model.sig[node]['in'] = Signal(
                np.zeros(node.size_in), name="%s.signal" % node)
            # Reset input signal to 0 each timestep
            model.add_op(Reset(model.sig[node]['in']))

    # Provide output
    if node.output is None:
        model.sig[node]['out'] = model.sig[node]['in']
    elif not callable(node.output):
        model.sig[node]['out'] = Signal(node.output, name=str(node))
    else:
        sig_in, sig_out = build_pyfunc(model=model,
                                       fn=node.output,
                                       t_in=True,
                                       n_in=node.size_in,
                                       n_out=node.size_out,
                                       label="%s.pyfn" % node)
        if sig_in is not None:
            model.add_op(DotInc(model.sig[node]['in'],
                                model.sig['common'][1],
                                sig_in,
                                tag="%s input" % node))
        if sig_out is not None:
            model.sig[node]['out'] = sig_out

    model.params[node] = None
