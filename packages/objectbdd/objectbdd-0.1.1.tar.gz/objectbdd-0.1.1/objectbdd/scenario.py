class Scenario(object):
    def __init__(self, test):
        self.test = test

    def transform(self, message):
        messages = message.split('\n')
        messages = map(lambda s: s.strip(), messages)
        messages = map(lambda s: s.replace(' ', '_'), messages)
        messages = map(lambda s: s.lower(), messages)
        messages = filter(lambda s: s is not '', messages)
        messages = map(lambda s: s.replace('given_', '', 1), messages)
        messages = map(lambda s: s.replace('when_', '', 1), messages)
        messages = map(lambda s: s.replace('then_', '', 1), messages)
        messages = map(lambda s: s.replace('and_', '', 1), messages)
        return messages

    def describe(self, message):
        methods = self.transform(message)
        print methods

        for method in methods:
            function = getattr(self.test, method)
            function.__call__()
