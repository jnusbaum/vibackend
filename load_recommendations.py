import os
import csv
from models import *

dbhost = os.getenv('DBHOST')
database = os.getenv('DATABASE')
dbuser = os.getenv('DBUSER')
dbsslmode = os.getenv('DBSSLMODE')
dbpwd = os.getenv('DBPWD')

db.bind(provider='postgres', host=dbhost,
        database=database,
        user=dbuser,
        password=dbpwd,
        sslmode=dbsslmode)

db.generate_mapping()

with open('./recommendations.tsv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t')
        # skip header
        next(csv_reader)
        for row in csv_reader:
                with db_session:
                        component_id = row[0]
                        recommendation = row[1]
                        if recommendation == "Recommendation coming soon!":
                                recommendation = ""
                        print('%s -> "%s"' % (component_id, recommendation))
                        isc = IndexSubComponent[component_id]
                        isc.recommendation = recommendation
