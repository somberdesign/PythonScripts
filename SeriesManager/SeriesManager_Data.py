import sqlite3, easygui, contextlib, datetime, os

class SeriesManager_Data(object):
    """Interaction with datasource"""
    
    FILENAME_DB = os.path.join(os.path.dirname(__file__), "titles.db")
    SQL_GETINACTIVETITLES = """
        SELECT 
	        t.title
	        ,COALESCE(use_count.total_views, 0) total_views
	        ,COALESCE(use_date.last_date_viewed, DATE('1970-01-01')) last_date_viewed
	        ,t.multiplier title_multiplier
	        ,t.id title_id
        FROM
	        Titles t
	        LEFT JOIN (SELECT title_id, COUNT(*) total_views FROM uses GROUP BY title_id) use_count ON t.id = use_count.title_id
	        LEFT JOIN (SELECT title_id, MAX(datetime(date_used)) last_date_viewed FROM uses GROUP BY title_id) use_date ON t.id = use_date.title_id
        WHERE t.is_active = 0
    """
    SQL_GETTITLES = """
        SELECT 
	        t.title
	        ,COALESCE(use_count.total_views, 0) total_views
	        ,COALESCE(use_date.last_date_viewed, DATE('1970-01-01')) last_date_viewed
	        ,t.multiplier title_multiplier
	        ,t.id title_id
        FROM
	        Titles t
	        LEFT JOIN (SELECT title_id, COUNT(*) total_views FROM uses GROUP BY title_id) use_count ON t.id = use_count.title_id
	        LEFT JOIN (SELECT title_id, MAX(datetime(date_used)) last_date_viewed FROM uses GROUP BY title_id) use_date ON t.id = use_date.title_id
        WHERE t.is_active = 1
    """
    SQL_INSERTTITLE = "insert into Titles (title, is_active, multiplier) VALUES(?, 1, ?)"
    SQL_INSERTUSE = "INSERT INTO Uses (title_id, date_used) VALUES({0}, '{1}')"
    SQL_TITLEEXISTS = "SELECT CASE WHEN COUNT(*) = 1 THEN 1 ELSE 0 END titleExists FROM titles WHERE LOWER(title) = ?"
    SQL_UPDATETITLE_SETISACTIVE = "UPDATE Titles SET is_active = {1} WHERE LOWER(title) = '{0}'"

    def __enter__(self):
        print(f'Using database {SeriesManager_Data.FILENAME_DB}')
        self.conn = sqlite3.connect(SeriesManager_Data.FILENAME_DB)
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.conn.commit()
        self.conn.close()

    def GetActiveTitles(self):
        allRecordRows = []

        for row in self.conn.execute(SeriesManager_Data.SQL_GETTITLES + " ORDER BY LOWER(t.title)"):
            newItem = [row[0], row[1], row[2], row[3], 1, 0, row[4]]
            allRecordRows.append(newItem)

        return allRecordRows

    def GetDisplayTitles(self):
        allRecordRows = []

        for row in self.conn.execute(SeriesManager_Data.SQL_GETTITLES + " ORDER BY last_date_viewed DESC, total_views DESC"):
            newItem = [row[0], row[1], row[2], row[3], 1, 0, row[4]]
            allRecordRows.append(newItem)

        return allRecordRows

    def GetInactiveTitles(self):
        allRecordRows = []

        for row in self.conn.execute(SeriesManager_Data.SQL_GETINACTIVETITLES + " ORDER BY LOWER(t.title)"):
            newItem = [row[0], row[1], row[2], row[3], 1, 0, row[4]]
            allRecordRows.append(newItem)

        return allRecordRows

    def InsertUse(self, titleId):
        sql = SeriesManager_Data.SQL_INSERTUSE.format(titleId, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        with contextlib.closing(self.conn.cursor()) as cur:
            cur.execute(sql)
        return


    def InsertTitle(self, title, multiplier):
        with contextlib.closing(self.conn.cursor()) as cur:
            cur.execute(SeriesManager_Data.SQL_INSERTTITLE, [title, multiplier])
        return

    def SeriesExists(self, seriesTitle):
        with contextlib.closing(self.conn.cursor()) as cur:
            resultRow = cur.execute(SeriesManager_Data.SQL_TITLEEXISTS, [seriesTitle.lower()]).fetchone()

        return True if resultRow[0] == 1 else False

    def SetTitleIsActive(self, title, isActive):
        with contextlib.closing(self.conn.cursor()) as cur:
            cur.execute(SeriesManager_Data.SQL_UPDATETITLE_SETISACTIVE.format(title.lower(), isActive))
        return

        

