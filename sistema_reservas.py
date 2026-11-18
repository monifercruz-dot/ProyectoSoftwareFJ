import logging
from abc import ABC, abstractmethod
from datetime import datetime

# ==========================================
# 1. CONFIGURACIÓN DEL SISTEMA DE LOGS
# ==========================================
logging.basicConfig(
    filename='sistema_reservas.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] - %(message)s',
    encoding='utf-8'
)

# ==========================================
# 2. EXCEPCIONES PERSONALIZADAS
# ==========================================
class ErrorSistemaSoftwareFJ(Exception):
    """Excepción base para todos los errores personalizados del sistema."""
    pass

class ErrorClienteInvalido(ErrorSistemaSoftwareFJ):
    """Se lanza cuando los datos de un cliente son incorrectos o inválidos."""
    pass

class ErrorServicioInvalido(ErrorSistemaSoftwareFJ):
    """Se lanza cuando hay un error en la configuración o parámetros de un servicio."""
    pass

class ErrorReservaInvalido(ErrorSistemaSoftwareFJ):
    """Se lanza cuando se intenta procesar una reserva con datos incorrectos."""
    pass

class ErrorOperacionNoPermitida(ErrorSistemaSoftwareFJ):
    """Se lanza ante operaciones lógicas no autorizadas (ej. cancelar una reserva ya cancelada)."""
    pass


# ==========================================
# 3. CLASE ABSTRACTA GENERAL
# ==========================================
class EntidadSistema(ABC):
    """Clase abstracta que representa entidades generales del sistema Software FJ."""
    
    def __init__(self, identificador):
        self._identificador = identificador

    @property
    def identificador(self):
        return self._identificador

    @abstractmethod
    def obtener_detalles(self):
        pass


# ==========================================
# 4. CLASE CLIENTE (Con encapsulación y validación)
# ==========================================
class Cliente(EntidadSistema):
    """Clase que representa a un cliente de la empresa Software FJ."""
    
    def __init__(self, identificador, nombre, correo, telefono):
        super().__init__(identificador)
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not valor or not isinstance(valor, str) or len(valor.strip()) < 3:
            logging.error(f"Intento de registrar cliente con nombre inválido: {valor}")
            raise ErrorClienteInvalido("El nombre del cliente no puede estar vacío y debe tener al menos 3 caracteres.")
        self._nombre = valor.strip()

    @property
    def correo(self):
        return self._correo

    @correo.setter
    def correo(self, valor):
        if not valor or not isinstance(valor, str) or "@" not in valor or "." not in valor:
            logging.error(f"Intento de registrar cliente con correo inválido: {valor}")
            raise ErrorClienteInvalido("El formato del correo electrónico del cliente no es válido.")
        self._correo = valor.strip()

    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        if not valor or not str(valor).isdigit() or len(str(valor)) < 7:
            logging.error(f"Intento de registrar cliente con teléfono inválido: {valor}")
            raise ErrorClienteInvalido("El teléfono debe contener solo números y tener al menos 7 dígitos.")
        self._telefono = str(valor)

    def obtener_detalles(self):
        return f"Cliente [ID: {self.identificador}] - Nombre: {self.nombre}, Correo: {self.correo}, Teléfono: {self.telefono}"


# ==========================================
# 5. CLASE ABSTRACTA SERVICIO Y SERVICIOS ESPECIALIZADOS (Polimorfismo)
# ==========================================
class Servicio(EntidadSistema, ABC):
    """Clase abstracta que representa los servicios ofrecidos por Software FJ."""
    
    def __init__(self, identificador, nombre_servicio, tarifa_base):
        super().__init__(identificador)
        self.nombre_servicio = nombre_servicio
        self.tarifa_base = tarifa_base

    @abstractmethod
    def calcular_costo(self, *args, **kwargs):
        """Método abstracto para calcular el costo (aplicando polimorfismo y sobrecarga)."""
        pass


class ReservaSalas(Servicio):
    """Servicio especializado en reserva de salas de trabajo/conferencias."""
    
    def __init__(self, identificador, tarifa_base, capacidad_personas):
        super().__init__(identificador, "Reserva de Salas", tarifa_base)
        self.capacidad_personas = capacidad_personas

    # Sobrecarga simulada de calcular_costo usando argumentos opcionales
    def calcular_costo(self, horas=1, descuento_porcentaje=0):
        if horas <= 0:
            raise ErrorServicioInvalido("Las horas de reserva de sala deben ser mayores a cero.")
        subtotal = self.tarifa_base * horas
        descuento = subtotal * (descuento_porcentaje / 100)
        return max(0.0, subtotal - descuento)

    def obtener_detalles(self):
        return f"Servicio: {self.nombre_servicio} [ID: {self.identificador}] - Capacidad: {self.capacidad_personas} personas, Tarifa Base/Hora: ${self.tarifa_base}"


class AlquilerEquipos(Servicio):
    """Servicio especializado en alquiler de equipos tecnológicos."""
    
    def __init__(self, identificador, tarifa_base, tipo_equipo):
        super().__init__(identificador, "Alquiler de Equipos", tarifa_base)
        self.tipo_equipo = tipo_equipo

    def calcular_costo(self, dias=1, seguro_adicional=False):
        if dias <= 0:
            raise ErrorServicioInvalido("Los días de alquiler de equipo deben ser mayores a cero.")
        costo_seguro = 15.0 if seguro_adicional else 0.0
        return (self.tarifa_base * dias) + costo_seguro

    def obtener_detalles(self):
        return f"Servicio: {self.nombre_servicio} [ID: {self.identificador}] - Equipo: {self.tipo_equipo}, Tarifa Base/Día: ${self.tarifa_base}"


class AsesoriaEspecializada(Servicio):
    """Servicio especializado en asesorías técnicas profesionales."""
    
    def __init__(self, identificador, tarifa_base, area_especialidad):
        super().__init__(identificador, "Asesoría Especializada", tarifa_base)
        self.area_especialidad = area_especialidad

    def calcular_costo(self, sesiones=1, incluye_impuestos=True):
        if sesiones <= 0:
            raise ErrorServicioInvalido("El número de sesiones de asesoría debe ser mayor a cero.")
        subtotal = self.tarifa_base * sesiones
        impuestos = subtotal * 0.19 if incluye_impuestos else 0.0
        return subtotal + impuestos

    def obtener_detalles(self):
        return f"Servicio: {self.nombre_servicio} [ID: {self.identificador}] - Área: {self.area_especialidad}, Tarifa Base/Sesión: ${self.tarifa_base}"


# ==========================================
# 6. CLASE RESERVA
# ==========================================
class Reserva:
    """Clase que integra cliente, servicio, duración y estado con manejo de excepciones."""
    
    def __init__(self, id_reserva, cliente, servicio, cantidad):
        self.id_reserva = id_reserva
        self.cliente = cliente
        self.servicio = servicio
        self.cantidad = cantidad
        self.estado = "Pendiente" # Estados: Pendiente, Confirmada, Cancelada
        self.costo_total = 0.0

    def confirmar_reserva(self, *args, **kwargs):
        try:
            # Bloque try/except/else/finally requerido por la rúbrica
            self.costo_total = self.servicio.calcular_costo(*args, **kwargs)
            self.estado = "Confirmada"
            logging.info(f"Reserva {self.id_reserva} confirmada exitosamente para el cliente {self.cliente.nombre}.")
            print(f"Éxito: Reserva {self.id_reserva} confirmada. Costo total: ${self.costo_total:.2f}")
        except ErrorServicioInvalido as e:
            logging.error(f"Error de servicio al confirmar reserva {self.id_reserva}: {e}")
            raise ErrorReservaInvalido(f"No se pudo procesar la reserva debido a un error en el servicio: {e}") from e
        else:
            print(f"--> Transacción validada correctamente por el sistema para la reserva {self.id_reserva}.")
        finally:
            print(f"--> Estado actual de la reserva {self.id_reserva}: {self.estado}\n")

    def cancelar_reserva(self):
        if self.estado == "Cancelada":
            logging.warning(f"Intento fallido de cancelar la reserva {self.id_reserva} que ya estaba cancelada.")
            raise ErrorOperacionNoPermitida("La reserva ya se encuentra cancelada.")
        self.estado = "Cancelada"
        logging.info(f"Reserva {self.id_reserva} cancelada correctamente.")
        print(f"Aviso: La reserva {self.id_reserva} ha sido cancelada.\n")


# ==========================================
# 7. SIMULACIÓN DE 10 OPERACIONES (Válidas e Inválidas)
# ==========================================
if __name__ == "__main__":
    print("==================================================")
    print(" INICIANDO SIMULACIÓN DE OPERACIONES - SOFTWARE FJ")
    print("==================================================\n")

    # Lista para almacenar objetos en memoria (sin bases de datos)
    operaciones_sistema = []

    # Operación 1: Registro válido de Cliente
    try:
        print("[Op 1] Registrando cliente válido...")
        cli1 = Cliente("C01", "Carlos Pérez", "carlos.perez@mail.com", "3201234567")
        operaciones_sistema.append(cli1)
        print("->", cli1.obtener_detalles(), "\n")
    except Exception as e:
        print(f"Error: {e}\n")

    # Operación 2: Registro inválido de Cliente (Genera excepción personalizada)
    try:
        print("[Op 2] Intentando registrar cliente con correo inválido...")
        cli_malo = Cliente("C02", "Ana", "correo-sin-arroba", "123")
    except ErrorClienteInvalido as e:
        print(f"-> Excepción capturada correctamente: {e}\n")

    # Operación 3: Creación de Servicio de Salas
    try:
        print("[Op 3] Creando servicio de reserva de salas...")
        sala1 = ReservaSalas("S01", 50.0, 10)
        operaciones_sistema.append(sala1)
        print("->", sala1.obtener_detalles(), "\n")
    except Exception as e:
        print(f"Error: {e}\n")

    # Operación 4: Creación de Servicio de Equipos
    try:
        print("[Op 4] Creando servicio de alquiler de equipos...")
        eq1 = ReservaSalas("E01", 30.0, 5) # Instancia auxiliar válida
        equipo1 = AlquilerEquipos("E01", 40.0, "Laptop Core i7")
        operaciones_sistema.append(equipo1)
        print("->", equipo1.obtener_detalles(), "\n")
    except Exception as e:
        print(f"Error: {e}\n")

    # Operación 5: Creación de Servicio de Asesoría
    try:
        print("[Op 5] Creando servicio de asesoría especializada...")
        asesoria1 = AsesoriaEspecializada("A01", 100.0, "Arquitectura de Software")
        operaciones_sistema.append(asesoria1)
        print("->", asesoria1.obtener_detalles(), "\n")
    except Exception as e:
        print(f"Error: {e}\n")

    # Operación 6: Reserva exitosa (Sala con descuento y parámetros opcionales)
    try:
        print("[Op 6] Procesando reserva exitosa de Sala...")
        res1 = Reserva("R01", cli1, sala1, 3)
        res1.confirmar_reserva(horas=4, descuento_porcentaje=10)
        operaciones_sistema.append(res1)
    except Exception as e:
        print(f"Error: {e}\n")

    # Operación 7: Reserva exitosa (Alquiler de equipos con seguro adicional)
    try:
        print("[Op 7] Procesando reserva exitosa de Equipo...")
        res2 = Reserva("R02", cli1, equipo1, 2)
        res2.confirmar_reserva(dias=5, seguro_adicional=True)
        operaciones_sistema.append(res2)
    except Exception as e:
        print(f"Error: {e}\n")

    # Operación 8: Reserva fallida por parámetros de servicio incorrectos (horas negativas)
    try:
        print("[Op 8] Intentando reservar sala con horas negativas...")
        res3 = Reserva("R03", cli1, sala1, -1)
        res3.confirmar_reserva(horas=-2)
    except ErrorReservaInvalido as e:
        print(f"-> Excepción de reserva capturada exitosamente: {e}\n")

    # Operación 9: Cancelación correcta de una reserva existente
    try:
        print("[Op 9] Cancelando la reserva R01...")
        res1.cancelar_reserva()
    except Exception as e:
        print(f"Error: {e}\n")

    # Operación 10: Operación no permitida (Intentar cancelar una reserva ya cancelada)
    try:
        print("[Op 10] Intentando cancelar la misma reserva R01 nuevamente...")
        res1.cancelar_reserva()
    except ErrorOperacionNoPermitida as e:
        print(f"-> Excepción de operación no permitida capturada correctamente: {e}\n")

    print("==================================================")
    print(" SIMULACIÓN FINALIZADA CON ÉXITO Y ESTABILIDAD")
    print(" Revisa el archivo 'sistema_reservas.log' generado.")
    print("==================================================")
    