from sqlalchemy import create_engine, MetaData
import config.db_account as account

# engine = create_engine("mysql+pymysql://root:123456@localhost:3306/fahasadb")
# engine = create_engine("mysql+mysqlconnector://root:phamvandong@localhost:3306/fahasadb")
string_connect = "mysql+mysqlconnector://" + account.db_username + ":" + account.db_password + "@localhost:3306/" + account.db_name
engine = create_engine(string_connect)

meta = MetaData()

conn = engine.connect()