import mysql.connector
class DBConnection:
    @staticmethod
    def getConnection():
        database = mysql.connector.connect(host="driveralertsystem.cuhoq4docfp1.us-east-1.rds.amazonaws.com", user="admin", passwd="Das#2022", db='drowsy_detection')
        return database
if __name__=="__main__":
    print(DBConnection.getConnection())