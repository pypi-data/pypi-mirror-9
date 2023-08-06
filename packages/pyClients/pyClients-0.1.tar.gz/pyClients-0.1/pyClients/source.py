import serial
import random
import time
from .protocol import (BaseClient, SUS_OP_FUENTE, RESP_TIPO_OK,
                       RESP_CODIGO_101, RESP_CODIGO_103)


class DataGeneratorMock():
    def __init__(self, num_data):
        self.num_data = num_data

    def get_data(self):
        data = ((str(random.random() * 10)) for _ in range(self.num_data))
        return ','.join(data).encode()


class DataGenerator():
    def __init__(self, port, baud):
        self.arduino = serial.Serial(port, baud)

    def get_data(self):
        return self.arduino.readline().strip()


class Source(BaseClient):
    def __init__(self, dataGenerator):
        super().__init__()
        self.dgenerator = dataGenerator

    def send_data(self):
        data = self.dgenerator.get_data()
        if data == b'fail':
            print("La fuente fallo")

        self.send_post(data)
        tipo, codigo, datos = self.recive_response()
        if (tipo == RESP_TIPO_OK and codigo == RESP_CODIGO_103):
            time.sleep(4)
            return True
        return False

    def send_suscription(self, datatype, description):
        self.send_sus(SUS_OP_FUENTE, datatype + ';' + description)
        tipo, codigo, datos = self.recive_response()
        if (tipo == RESP_TIPO_OK and codigo == RESP_CODIGO_101):
            self.id = int(datos)
            return True
        return False
