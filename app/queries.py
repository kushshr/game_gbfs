import psycopg2
from psycopg2.extras import execute_batch
from app.models import *
from game_gbfs import settings
import psycopg2

class AnswerQueries:
    def __init__(self, database_url):
        self.queries = []
        self.conn = psycopg2.connect(
            host=settings.DATABASES['default']['HOST'],
            database=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD']
        )
        self.cursor = self.conn.cursor()

    def get_total_number_of_bikes(self, query_text):
        query = "SELECT count(*) from gbfs_stations"
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        return result

    def get_biggest_provider_in_city_bikes(self, query_text):
        query = """SELECT operator_name, SUM(num_bikes) as nb
                    FROM gbfs_stations
                    GROUP BY operator_name order by nb desc """
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        return result

    def get_biggest_provider_in_city_docks(self, query_text):
        query = """SELECT operator_name, SUM(num_docks) as nd
                    FROM gbfs_stations
                    GROUP BY operator_name order by nd desc """
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        return result

    def close_connection(self):
        self.conn.close()

    def get_farthest_bikes(self, query_text):
        query = """SELECT operator_name, SUM(num_bikes) as nb
                            FROM gbfs_stations
                            GROUP BY operator_name order by nb desc """
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        return result

    def run_all_answerqueries(self):
        questions = GameQuestions.objects.filter()
        # for question in questions:
        #     if question.query_type == "num_bikes_in_city":


