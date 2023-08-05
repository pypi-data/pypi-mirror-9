class MaatException(Exception): pass

class ManagerDoesNotExist(MaatException): pass
class ModelAlreadyRegistered(MaatException): pass
class ModelNotRegistered(MaatException): pass
class TypologyNotImplemented(MaatException): pass