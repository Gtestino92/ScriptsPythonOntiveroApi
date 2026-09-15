class SingularMatException(Exception):
     def __init__(self, code, message="Matriz singular, imposible calcular regresion"):
        self.message = message
        self.code = code
        super().__init__(self.message)
    