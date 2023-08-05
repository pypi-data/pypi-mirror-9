import numpy as np

import nengo
from nengo.spa.vocab import Vocabulary
from nengo.spa.module import Module
from nengo.spa.utils import enable_spa_params
from nengo.utils.compat import iteritems


class SPA(nengo.Network):
    """Base class for SPA models.

    This expands the standard Network system to support structured connections
    that use Semantic Pointers and associated vocabularies in their
    definitions.

    To build a SPA model, subclass this SPA class and in the make() method
    add in your objects.  Any spa.Module object that is assigned to a
    member variable will automatically be accessible by the SPA connection
    system.  For example, the following code will build three modules
    (two Buffers and a Memory) that can be referred to as a, b, and c,
    respectively:

    class Example(spa.SPA):
        def __init__(self):
            self.a = spa.Buffer(dimensions=8)
            self.b = spa.Buffer(dimensions=16)
            self.c = spa.Memory(dimensions=8)

    These names can be used by special Modules that are aware of these
    names.  For example, the Cortical module allows you to form connections
    between these modules in ways that are aware of semantic pointers:

    class Example(spa.SPA):
        def __init__(self):
            self.a = spa.Buffer(dimensions=8)
            self.b = spa.Buffer(dimensions=16)
            self.c = spa.Memory(dimensions=8)
            self.cortical = spa.Cortical(spa.Actions(
                'b=a*CAT', 'c=b*~CAT'))

    For complex cognitive control, the key modules are the BasalGangla
    and the Thalamus.  Together, these allow us to define complex actions
    using the Action syntax:

    class SequenceExample(spa.SPA):
        def __init__(self):
            self.state = spa.Memory(dimensions=32)

            actions = spa.Actions('dot(state, A) --> state=B',
                                  'dot(state, B) --> state=C',
                                  'dot(state, C) --> state=D',
                                  'dot(state, D) --> state=E',
                                  'dot(state, E) --> state=A',
                                  )

            self.bg = spa.BasalGanglia(actions=actions)
            self.thal = spa.Thalamus(self.bg)
    """

    def __init__(self, label=None, seed=None, add_to_container=None):
        super(SPA, self).__init__(label, seed, add_to_container)
        enable_spa_params(self)
        self._modules = {}
        self._default_vocabs = {}

    def __setattr__(self, key, value):
        """A setattr that handles Modules being added specially.

        This is so that we can use the variable name for the Module as
        the name that all of the SPA system will use to access that module.
        """
        super(SPA, self).__setattr__(key, value)
        if isinstance(value, Module):
            if value.label is None:
                value.label = key
            self._modules[key] = value
            for k, (obj, v) in iteritems(value.inputs):
                if type(v) == int:
                    value.inputs[k] = (obj, self.get_default_vocab(v))
                self.config[obj].vocab = value.inputs[k][1]
            for k, (obj, v) in iteritems(value.outputs):
                if type(v) == int:
                    value.outputs[k] = (obj, self.get_default_vocab(v))
                self.config[obj].vocab = value.outputs[k][1]

            value.on_add(self)

    def get_module(self, name):
        """Return the module for the given name."""
        return self._modules[name]

    def get_default_vocab(self, dimensions):
        """Return a Vocabulary with the desired dimensions.

        This will create a new default Vocabulary if one doesn't exist.
        """

        # If seed is set, create rng based off that seed.
        # Otherwise, just use the default NumPy rng.
        rng = None if self.seed is None else np.random.RandomState(self.seed)

        if dimensions not in self._default_vocabs:
            self._default_vocabs[dimensions] = Vocabulary(dimensions, rng=rng)
        return self._default_vocabs[dimensions]

    def get_module_input(self, name):
        """Return the object to connect into for the given name.

        The name will be either the same as a module, or of the form
        <module_name>_<input_name>.
        """
        if name in self._modules:
            return self._modules[name].inputs['default']
        elif '_' in name:
            module, name = name.rsplit('_', 1)
            return self._modules[module].inputs[name]

    def get_module_inputs(self):
        for name, module in iteritems(self._modules):
            for input in module.inputs:
                if input == 'default':
                    yield name
                else:
                    yield '%s_%s' % (name, input)

    def get_input_vocab(self, name):
        return self.get_module_input(name)[1]

    def get_module_output(self, name):
        """Return the object to connect into for the given name.

        The name will be either the same as a module, or of the form
        <module_name>_<output_name>.
        """
        if name in self._modules:
            return self._modules[name].outputs['default']
        elif '_' in name:
            module, name = name.rsplit('_', 1)
            return self._modules[module].outputs[name]

    def get_module_outputs(self):
        for name, module in iteritems(self._modules):
            for output in module.outputs:
                if output == 'default':
                    yield name
                else:
                    yield '%s_%s' % (name, output)

    def get_output_vocab(self, name):
        return self.get_module_output(name)[1]

    def similarity(self, data, probe, vocab=None):
        """Return the similarity between the probed data and corresponding
        vocabulary.

        Parameters
        ----------
        data: ProbeDict
            Collection of simulation data returned by sim.run() function call.
        probe: Probe
            Probe with desired data.
        """
        if vocab is None:
            vocab = self.config[probe.target].vocab
        return nengo.spa.similarity(data[probe], vocab)
