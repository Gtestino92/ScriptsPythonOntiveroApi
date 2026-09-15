class NoPedidosRegistradosException(Exception):
     def __init__(self, code, message="No se encontraron pedidos registrados con alguno de los modelos"):
        self.message = message
        self.code = code
        super().__init__(self.message)
    