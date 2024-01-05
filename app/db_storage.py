import settings
import psycopg2



class DB_storage():

    def __init__(self, postresql_table_name, postresql_host, postresql_db_name, postresql_user, postresql_password):

        self.postresql_table_name = postresql_table_name
        self.postresql_host = postresql_host
        self.postresql_db_name = postresql_db_name
        self.postresql_user = postresql_user
        self.postresql_password = postresql_password


        self.conn = psycopg2.connect(
            host=self.postresql_host,
            database=self.postresql_db_name,
            user=self.postresql_user,
            password=self.postresql_password)

        self.cur = self.conn.cursor()
        self.cur.execute(
                """CREATE TABLE IF NOT EXISTS {} (
                        user_telegram_id bigint NOT NULL,
                        author varchar(4) NOT NULL,
                        message text NOT NULL
                )""".format(self.postresql_table_name)
                )     



    def push_to_history(self, user_message, author, user_id):
        user_message = '"'.join(user_message.split("'"))
        self.cur.execute('''INSERT INTO {} (user_telegram_id, author, message) VALUES ({}, '{}', '{}')'''.format(self.postresql_table_name, int(user_id), author, user_message))
        self.conn.commit()


    def get_user_history(self, user_id):
        self.cur.execute(
                        """SELECT * FROM {} WHERE user_telegram_id={}""".format(self.postresql_table_name, user_id)
                    )   

        data = self.cur.fetchall()
        history = []
        for row in data:
            if row[1] == 'USER':
                history += [[row[2]]]
            else:
                history[-1] += [row[2]]

        return history[:10]


    def delete_history(self):

        self.cur.execute("DROP TABLE {} ".format(self.postresql_table_name))
            
        # Commit your changes in the database 
        self.conn.commit()

        self.cur.execute(
                    """CREATE TABLE IF NOT EXISTS {} (
                            user_telegram_id bigint NOT NULL,
                            author varchar(4) NOT NULL,
                            message text NOT NULL
                    )""".format(self.postresql_table_name)
                    )    

















