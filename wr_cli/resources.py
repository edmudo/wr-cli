import os

class ResourceQuery:
    INSERT_WINE = """REPLACE INTO tblWine (country, price, province, variety, winery) values (?, ?, ?, ?, ?)"""
    INSERT_REVIEW = """REPLACE INTO tblReview (review_id, description, points, taster_twitter_handle, title, variety, winery) values (?, ?, ?, ?, ?, ?, ?)"""
    INSERT_REVIEWER = """REPLACE INTO tblReviewer (taster_name, taster_twitter_handle) values (?, ?)"""

    SELECT_WINE = """Select * From tblWine"""
    SELECT_REVIEWER = """SELECT * FROM tblReviewer"""
    SELECT_REVIEW = """
                    SELECT *
                    FROM (
                        SELECT review_id, description, points,
                            tblReviewer.taster_name as taster_name, 
                            tblReview.taster_twitter_handle as taster_twitter_handle, title,
                            tblReview.variety as variety, tblWine.winery as winery,
                            province, country, price
                        FROM tblReview
                        JOIN tblWine ON tblWine.variety = tblReview.variety AND tblReviewer.taster_twitter_handle = tblReview.taster_twitter_handle
                        JOIN tblReviewer ON tblReviewer.taster_twitter_handle = tblReview.taster_twitter_handle
                    )
                    """

    ADDON_LIMIT = """ LIMIT {0:d} OFFSET {1:d} """

class ResourcePath:
    DIRECTORY = os.path.dirname(__file__)
    FORMAT_PATH = f'{DIRECTORY}/format'

    WINEF_PATH = f'{FORMAT_PATH}/format_wine.txt'
    REVIEWF_PATH = f'{FORMAT_PATH}/format_review.txt'
    REVIEWERF_PATH = f'{FORMAT_PATH}/format_reviewer.txt'
