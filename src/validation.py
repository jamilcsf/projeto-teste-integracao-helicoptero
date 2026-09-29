class FlightValidationModule:

    def __init__(self, db):
        self.db = db

    def validar_elegibilidade(
        self, helicoptero_id: str, horario: str, passageiros: int
    ):
        aeronave = self.db.obter_helicoptero(helicoptero_id)
        if not aeronave:
            raise ValueError(f"Helicóptero {helicoptero_id} não cadastrado.")

        _, _, status_manutencao = aeronave

        # Regra de negócio: Status de manutenção
        if status_manutencao != "LIBERADO":
            raise ValueError(
                f"Aeronave {helicoptero_id} em manutenção ({status_manutencao}). Agendamento recusado."
            )

        # Regra de negócio: Conflito de horário
        if self.db.verificar_conflito_horario(helicoptero_id, horario):
            raise ValueError(
                f"Aeronave {helicoptero_id} já possui agendamento para o horário {horario}."
            )

        return True