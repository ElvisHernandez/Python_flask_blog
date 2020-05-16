import psycopg2 

def getDbConnection():
    #code to get database connection 
    try: 
        connection = psycopg2.connect(user = 'elvis', database = 'mydb')
        return connection
    except (Exception, psycopg2.Error) as error:
        print ('There was an error connecting')

def closeDbConnection(connection):
    # code to close database connection
    if (connection):
        connection.close()
        print('The connection is now closed \n')

def readDbVersion():
    connection = getDbConnection()
    cursor = connection.cursor()
    #Execute SQL query to print database server version
    sql_query_version = 'SELECT version();'
    cursor.execute(sql_query_version)
    sql_version = cursor.fetchone()
    print('Current PostgreSQL version: ', sql_version)
    closeDbConnection(connection)

def readHospitalDetails(hospital_id):
    # Read data from hospital table 
    connection = getDbConnection()
    cursor = connection.cursor()
    sql_query = 'SELECT * FROM hospital WHERE hospital_id = %s;'

    cursor.execute(sql_query,(hospital_id,))
    hospitals = cursor.fetchall()

    for row in hospitals:
        print ('ID = ', row[0])
        print ('Name = ', row[1])
        print ('Beds = ', row[2], '\n')

    closeDbConnection(connection)

def readDoctorDetails(doctor_id): 
    connection = getDbConnection() 
    cursor = connection.cursor()
    sql_query = 'SELECT * FROM doctor WHERE doctor_id = %s;'

    cursor.execute(sql_query,(doctor_id,))
    doctors = cursor.fetchall()

    for row in doctors:
        print ('ID = ', row[0])
        print ('NAME = ', row[1])
        print ('HOSPITAL_ID = ', row[2])
        print ('JOINING DATE = ', row[3])
        print ('SPECIALTY  = ', row[4])
        print ('SALARY  = ', row[5])
        print ('EXPERIENCE = ', row[6], '\n')

readDoctorDetails(101)