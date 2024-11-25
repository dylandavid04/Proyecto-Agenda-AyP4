class Nodo:
    def __init__(self, contacto):
        self.contacto = contacto
        self.siguiente = None

class ListaLigada:
    def __init__(self):
        self.cabeza = None

    def agregar(self, contacto):
        nuevo_nodo = Nodo(contacto)
        if not self.cabeza:
            self.cabeza = nuevo_nodo
        else:
            actual = self.cabeza
            while actual.siguiente:
                actual = actual.siguiente
            actual.siguiente = nuevo_nodo

    def eliminar_por_usuario(self, usuario, password):
        actual = self.cabeza
        anterior = None
        while actual:
            if actual.contacto['usuario'] == usuario and actual.contacto['password'] == password:
                if anterior:
                    anterior.siguiente = actual.siguiente
                else:
                    self.cabeza = actual.siguiente
                return True
            anterior = actual
            actual = actual.siguiente
        return False

    def obtener_todos_ordenados(self):
        contactos = []
        actual = self.cabeza
        while actual:
            contactos.append(actual.contacto)
            actual = actual.siguiente
        return sorted(contactos, key=lambda x: x['nombre'].lower())
