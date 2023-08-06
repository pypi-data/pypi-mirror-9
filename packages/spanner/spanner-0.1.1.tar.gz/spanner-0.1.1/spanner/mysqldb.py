import mysql.connector
import atexit


active_connections = dict()


@atexit.register
def close_connections():
    for connection in active_connections.values():
        connection.close()


def db_connection(host, user, password, database):
    # check for cached connection
    key = (host, user, database)
    if key in active_connections:
        return active_connections[key]

    connection = mysql.connector.connect(host=host, user=user, password=password, database=database)
    active_connections[key] = connection
    return connection


def execute(statement, host, user, password, database, remove_duplicates=True, print_statement=False):
    assert len(statement.strip('\r\n ')) > 0, 'Please provide a valid statement'

    if print_statement:
        print statement

    db = db_connection(host, user, password, database)
    cursor = db.cursor()
    result = None
    try:
        cursor.execute(statement)
        if statement.lower().startswith('select'):
            result = cursor.fetchall()
            # if the result is all singleton tuples, de-tuplefy them
            for r in result:
                if len(r) > 1:
                    break
            else:
                result = [r for (r,) in result]

            if remove_duplicates:
                result = list(set(result))

    except mysql.connector.Error as e:
        print 'Failed statement: \n' + statement
        print e

    cursor.close()
    db.commit()
    db.close()

    return result
