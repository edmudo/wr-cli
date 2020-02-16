import sqlite3
import csv

class Database:
    def __init__(self, schema_path='schema.txt', db_path='wine.db',
                 data_path='data'):
        self.connection = sqlite3.connect(db_path)
        self.schema_path = schema_path
        self.data_path = data_path
        self.connection.row_factory = self.dict_factory
        self.close = self.connection.close

    def load_data(self):
        schemaFile = open(self.schema_path, "r")
        wineTable = ""
        reviewTable = ""
        reviewerTable = ""

        # Read in create statements for each table from schema.txt file
        for x in range(7):
            wineTable += schemaFile.readline()

        schemaFile.readline()
        for x in range(8):
            reviewTable += schemaFile.readline()

        schemaFile.readline()
        for x in range(4):
            reviewerTable += schemaFile.readline()

        # Create wine, review and reviewer tables
        self.connection.execute(wineTable)
        self.connection.execute(reviewTable)
        self.connection.execute(reviewerTable)

        # Read in data for each table from csv files
        wine_array = []
        with open(f'{self.data_path}/Wine.csv') as wine_file:
            csv_reader = csv.reader(wine_file)
            next(csv_reader)
            for row in csv_reader:
                wine_array.append(row)

        review_array = []
        with open(f'{self.data_path}/Review.csv') as review_file:
            csv_reader = csv.reader(review_file)
            next(csv_reader)
            for row in csv_reader:
                review_array.append(row)

        reviewer_array = []
        with open(f'{self.data_path}/Reviewer.csv') as reviewer_file:
            csv_reader = csv.reader(reviewer_file)
            next(csv_reader)
            for row in csv_reader:
                if row not in reviewer_array:
                    reviewer_array.append(row)

        # Insert data into wine, review and reviewer tables
        self.connection.executemany("INSERT INTO tblWine (country, price, province, variety, winery) "
                                    "values (?, ?, ?, ?, ?)", wine_array)

        self.connection.executemany(
            "INSERT INTO tblReview (review_id, description, points, taster_twitter_handle, title, "
            "variety, winery) values (?, ?, ?, ?, ?, ?, ?)", review_array)

        self.connection.executemany("INSERT INTO tblReviewer (taster_name, taster_twitter_handle) "
                                    "values (?, ?)", reviewer_array)

    def do_query(self, kw):
        try:
            if kw['_keyword'] == "wine":
                return self.query_wine(kw)

            if kw['_keyword'] == "review":
                return self.query_review(kw)

            if kw['_keyword'] == "reviewer":
                return self.query_reviewer(kw)
        except Exception as e:
            print("Cannot fetch data" + str(e))

    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def query_wine(self, kw):
        base_string = "SELECT * FROM tblWine"
        add_on_string = self.add_on(kw)
        wineSelect = self.connection.execute(base_string + add_on_string)
        wineResults = wineSelect.fetchall()

        return wineResults

    def query_review(self, kw):
        base_string = """
            SELECT review_id, description, points,
                   tblReviewer.taster_name as taster_name, 
                   tblReview.taster_twitter_handle as taster_twitter_handle, title,
                   tblReview.variety as variety, tblWine.winery as winery,
                   province, country, price
            FROM tblReview
            JOIN tblWine ON tblWine.variety = tblReview.variety AND tblReviewer.taster_twitter_handle = tblReview.taster_twitter_handle
            JOIN tblReviewer ON tblReviewer.taster_twitter_handle = tblReview.taster_twitter_handle
            """
        add_on_string = self.add_on(kw, default_table='tblReview')
        reviewSelect = self.connection.execute(base_string + add_on_string)
        reviewResults = reviewSelect.fetchall()

        return reviewResults

    def query_reviewer(self, kw):
        base_string = "SELECT * FROM tblReviewer"
        add_on_string = self.add_on(kw)
        reviewerSelect = self.connection.execute(base_string + add_on_string)
        reviewerResults = reviewerSelect.fetchall()

        return reviewerResults

    def add_on(self, kw, default_table=None):
        key_values = []
        for key, value in kw.items():
            if key == "_keyword":
                continue
            key_values.append(f"{key}='{value}'")
        if key_values:
            add_on_string = " WHERE " + " AND ".join(key_values)
        else:
            add_on_string = ""
        return add_on_string
