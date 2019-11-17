class ProcessorList(object):

    def __init__(self, **args):
        self._processors = []

        for idx, processor in enumerate(args):
            self._processors.append(processor)

    def add(self, processor):
        self.check_processor(processor)
        self._processors.append(processor)

    def insert(self, processor, index):
        self.check_processor(processor)
        self._processors.insert(index, processor)

    def swap(self, name_a, name_b):
        names = [processor.name for processor in self._processors]
        a = self._processors.get(name_a)
        b = self._processors.get(name_b)

        i = names.index(name_a)
        j = names.index(name_b)

        self._processors[i], self._processors[j] = b, a

    def remove(self, name):
        self._processors.remove(self.get(name))

    def get(self, name):
        names = [processor.name for processor in self._processors]
        return self._processors[names.index(name)]

    def get_all(self):
        return self._processors

    def check_processor(self, processor):
        if processor.name in [processor.name for processor in self._processors]:
            raise ValueError("Processor names must be unique!")

    def clear(self):
        self._processors = []