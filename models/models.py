# models.py
from flask_login import UserMixin

class Usuario(UserMixin):
    def __init__(self, id, nombre, mail, password):
        self.id = id
        self.nombre = nombre
        self.mail = mail
        self.password = password
