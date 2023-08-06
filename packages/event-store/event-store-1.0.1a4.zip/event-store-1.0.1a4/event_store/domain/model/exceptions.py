__author__ = 'Andriy Drozdyuk'


class ConcurrencyProblem(Exception):
    """Occurs when version on the aggregate does not match the version
    supplied by the client"""
    pass