import requests
import psycopg2
from psycopg2.extras import execute_batch
from game_gbfs import settings
import environ


class GBFSImporter(object):
    def __getattr(self, item,attribute,default):
        value = getattr(item,attribute,default)
        if not value:
            value = default
        return value

    def __init__(self):
        self.conn = psycopg2.connect(
            host=settings.DATABASES['default']['HOST'],
            database=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD']
        )
        self.gbfs_urls = settings.GBFS_FEEDS

    # Function to fetch GBFS data
    def fetch_gbfs_data(self,gbfs_url):
        # gbfs_url = "https://api.delijn.be/gbfs/gbfs.json"
        # gbfs_url = "https://stables.donkey.bike/api/public/gbfs/2/donkey_antwerp/gbfs.json"
        # gbfs_url = "https://gbfs.smartbike.com/antwerp/1.0/gbfs.json"
        response = requests.get(gbfs_url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching GBFS data. Status code: {response.status_code}")
            return None

    # Function to insert data into PostgreSQL
    def import_gbfs_data(self, data):
        # Extract relevant information from GBFS data
        data = data.get('data',{})
        feeds = data.get('nl', {})
        feeds = feeds.get('feeds', {})

        station_url = ''
        station_status_url = ''
        system_info_url = ''
        for feed in feeds:
            if feed.get('name') == 'station_information':
                station_url = feed.get('url')
            elif feed.get('name') == 'station_status':
                station_status_url = feed.get('url')
            elif feed.get('name') == 'system_information':
                system_info_url = feed.get('url')
            else:
                pass

        stations = {}
        stations_status = {}
        sys_info = {}
        updated_availabilites = []
        operator_name = ''

        if station_url:
            response_stations = requests.get(station_url)
            if response_stations.status_code == 200:
                stations = response_stations.json().get('data')
        if station_status_url:
            response_stations_status = requests.get(station_status_url)
            if response_stations_status.status_code == 200:
                stations_status = response_stations_status.json().get('data')
        if system_info_url:
            response_sys_info = requests.get(system_info_url)
            if response_sys_info.status_code == 200:
                sys_info = response_sys_info.json().get('data')

            operator_name = sys_info.get('name')
            print (operator_name + " import started" )

            updated_availabilites = []
            for station in stations.get('stations'):
                for station_status in stations_status.get('stations'):
                    if station.get('station_id') == station_status.get('station_id'):
                        updated_availabilites.append((operator_name, station.get('station_id'),station.get('name'),station.get('lat'), station.get('lon'), station_status.get('num_bikes_available'),station_status.get('num_docks_available') ))

        upsert_query = """INSERT INTO gbfs_stations (operator_name, station_id, station_name, station_lat, station_lon, num_bikes, num_docks)
                            VALUES (%s,  %s,  %s,  %s,  %s,  %s,  %s)
                            ON CONFLICT (operator_name, station_id) DO UPDATE
                            SET (num_bikes, num_docks) = (EXCLUDED.num_bikes, EXCLUDED.num_docks)"""

        cursor = self.conn.cursor()
        try:
            execute_batch(cursor, upsert_query, updated_availabilites)
        finally:
            print (operator_name + " import successfully finished" )
            self.close_connection()
        return True

    def close_connection(self):
        self.conn.commit()


def gbfs_import():
    importer = GBFSImporter()
    print (importer.gbfs_urls)
    for gbfs_url in importer.gbfs_urls:
        data = importer.fetch_gbfs_data(gbfs_url=gbfs_url)
        importer.import_gbfs_data(data=data)
    importer.close_connection()

