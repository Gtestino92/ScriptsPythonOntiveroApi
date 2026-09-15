class Pedido:    
    def __init__(self,listadoMacetas,fechaEntrega):
        self.listadoMacetas = listadoMacetas
        self.fechaEntrega = fechaEntrega
        
    def setListadoMacetas(self, listadoMacetas):
        self.listadoMacetas = listadoMacetas
    
    def setFechaEntrega(self, fechaEntrega):
        self.fechaEntrega = fechaEntrega
    
