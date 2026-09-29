import pytest
from src.booking_service import BookingService


def test_cenario_1_agendamento_valido(db_session):
    """
    Cenário 1 (Caminho Feliz - Agendamento Válido):
    Garante que uma aeronave liberada e com horário disponível seja agendada
    e persista com o status AGENDADO na base SQLite.
    """
    db_session.inserir_helicoptero("PR-AER", "EC135", "LIBERADO")
    service = BookingService(db_session)

    agendamento_id = service.agendar_voo(
        "PR-AER", "2026-09-30T10:00:00", passageiros=4
    )

    agendamento = db_session.obter_agendamento(agendamento_id)
    assert agendamento is not None
    assert agendamento[1] == "PR-AER"
    assert agendamento[2] == "2026-09-30T10:00:00"
    assert agendamento[3] == 4
    assert agendamento[4] == "AGENDADO"


def test_cenario_2_conflito_horario_aeronave(db_session):
    """
    Cenário 2 (Conflito de Horário da Aeronave):
    Garante a emissão de exceção e impede a duplicidade de registro no banco.
    """
    db_session.inserir_helicoptero("PR-AER", "EC135", "LIBERADO")
    service = BookingService(db_session)

    horario = "2026-09-30T14:00:00"
    service.agendar_voo("PR-AER", horario, passageiros=3)

    with pytest.raises(
        ValueError, match="já possui agendamento para o horário"
    ):
        service.agendar_voo("PR-AER", horario, passageiros=2)

    cursor = db_session.conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM agendamentos WHERE helicoptero_id = ? AND horario = ?",
        ("PR-AER", horario),
    )
    count = cursor.fetchone()[0]
    assert count == 1


def test_cenario_3_aeronave_em_manutencao(db_session):
    """
    Cenário 3 (Aeronave em Manutenção Preventiva/Corretiva):
    Garante a rejeição pela classe de validação se status for EM_INSPECAO
    e assegura que nenhuma alteração persista na base.
    """
    db_session.inserir_helicoptero("PR-MNT", "AW139", "EM_INSPECAO")
    service = BookingService(db_session)

    with pytest.raises(ValueError, match="em manutenção"):
        service.agendar_voo(
            "PR-MNT", "2026-09-30T16:00:00", passageiros=5
        )

    cursor = db_session.conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM agendamentos WHERE helicoptero_id = ?",
        ("PR-MNT",),
    )
    count = cursor.fetchone()[0]
    assert count == 0


def test_cenario_4_consistencia_isolamento_banco(db_session):
    """
    Cenário 4 (Consistência do Banco com Fixtures/Rollback):
    Garante que o estado inicial das tabelas seja completamente limpo,
    demonstrando o isolamento total entre suítes de teste.
    """
    cursor = db_session.conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM agendamentos")
    count_agendamentos = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM helicopteros")
    count_helicopteros = cursor.fetchone()[0]

    assert count_agendamentos == 0
    assert count_helicopteros == 0


def test_cenario_5_helicoptero_nao_cadastrado(db_session):
    """
    Cenário 5 (Validação de Aeronave Inexistente):
    Garante a cobertura do fluxo de exceção quando o helicóptero
    solicitado não existe no banco de dados.
    """
    service = BookingService(db_session)

    with pytest.raises(ValueError, match="não cadastrado"):
        service.agendar_voo("PR-INEXISTENTE", "2026-09-30T10:00:00", passageiros=2)