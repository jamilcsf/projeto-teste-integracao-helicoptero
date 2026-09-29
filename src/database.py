import sqlite3


class Database:

    def __init__(self, db_name=":memory:"):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS helicopteros (
                id TEXT PRIMARY KEY,
                modelo TEXT NOT NULL,
                status_manutencao TEXT NOT NULL
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS agendamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                helicoptero_id TEXT NOT NULL,
                horario TEXT NOT NULL,
                passageiros INTEGER NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY (helicoptero_id) REFERENCES helicopteros (id)
            )
        """
        )
        self.conn.commit()

    def inserir_helicoptero(
        self, helicoptero_id: str, modelo: str, status_manutencao: str
    ):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO helicopteros (id, modelo, status_manutencao)
            VALUES (?, ?, ?)
        """,
            (helicoptero_id, modelo, status_manutencao),
        )
        self.conn.commit()

    def obter_helicoptero(self, helicoptero_id: str):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, modelo, status_manutencao FROM helicopteros WHERE id = ?",
            (helicoptero_id,),
        )
        return cursor.fetchone()

    def verificar_conflito_horario(self, helicoptero_id: str, horario: str):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT COUNT(*) FROM agendamentos
            WHERE helicoptero_id = ? AND horario = ? AND status = 'AGENDADO'
        """,
            (helicoptero_id, horario),
        )
        count = cursor.fetchone()[0]
        return count > 0

    def salvar_agendamento(
        self, helicoptero_id: str, horario: str, passageiros: int
    ):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO agendamentos (helicoptero_id, horario, passageiros, status)
            VALUES (?, ?, ?, 'AGENDADO')
        """,
            (helicoptero_id, horario, passageiros),
        )
        self.conn.commit()
        return cursor.lastrowid

    def obter_agendamento(self, agendamento_id: int):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT id, helicoptero_id, horario, passageiros, status
            FROM agendamentos WHERE id = ?
        """,
            (agendamento_id,),
        )
        return cursor.fetchone()

    def close(self):
        self.conn.close()