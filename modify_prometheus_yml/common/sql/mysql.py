import pymysql

class MySQL():
    def __init__(self, ip, port, user, password, dbname):

        self.__conn = None
        self.__cursor = None
        self.lastrowid = None
        self.ip = ip
        self.port = port
        self.user = user
        self.password = password
        self.db = dbname
        self.rows_affected = 0

    def __init_conn(self):

        try:
            conn = pymysql.connect(
                host=self.ip,
                port=int(self.port),
                user=self.user,
                password=self.password,
                db=self.db,
                charset='utf8')

        except pymysql.Error as e:
            raise e

        self.__conn = conn

    def __init_cursor(self):
        if self.__conn:
            self.__cursor = self.__conn.cursor(pymysql.cursors.DictCursor)

    def close(self):
        if self.__conn:
            self.__conn.close()
            self.__conn = None

    def select(self, sql, args=None):
        try:
            if self.__conn is None:
                self.__init_conn()
                self.__init_cursor()

            self.__conn.autocommit = True
            self.__cursor.execute(sql, args)
            self.rows_affected = self.__cursor.rowcount
            results = self.__cursor.fetchall()
            return results

        except pymysql.Error as e:
            raise pymysql.Error(e)

        finally:
            if self.__conn:
                self.close()

    def excuted(self, sql, args=None):
        try:
            if self.__conn is None:
                self.__init_conn()
                self.__init_cursor()

            if self.__cursor is None:
                self.__init_cursor()

            self.rows_affected = self.__cursor.execute(sql, args)
            self.lastrowid = self.__cursor.lastrowid
            return self.rows_affected

        except pymysql.Error as e:
            raise pymysql.Error(e)

        finally:
            if self.__cursor:
                self.__cursor.close()
                self.__cursor = None

    def commit(self):
        try:
            if self.__conn:
                self.__conn.commit()

        except pymysql.Error as e:
            raise pymysql.Error(e)

        finally:
            if self.__conn:
                self.close()

    def rollback(self):
        try:
            if self.__conn:
                self.__conn.rollback()
        except pymysql.Error as e:
            raise pymysql.Error(e)

        finally:
            if self.__conn:
                self.close()

    def get_lastrowid(self):
        return self.lastrowid

    def get_affectrows(self):
        return self.rows_affected

    def __del__(self):
        self.commit()
