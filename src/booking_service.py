from src.validation import FlightValidationModule


class BookingService:

    def __init__(self, db):
        self.db = db
        self.validator = FlightValidationModule(db)

    def agendar_voo(self, helicoptero_id: str, horario: str, passageiros: int):
        self.validator.validar_elegibilidade(
            helicoptero_id, horario, passageiros
        )
        agendamento_id = self.db.salvar_agendamento(
            helicoptero_id, horario, passageiros
        )
        return agendamento_id