import argparse
import subprocess
import time

from helpers import fake2db_logger

logger, extra_information = fake2db_logger()


class InstantiateDBHandlerException(Exception):
    '''An Exception at the instantiation of the handler '''

    
class MissingDependencyException(Exception):
    '''An Exception to be thrown if the dependencies are missing'''

def _postgresql_process_checkpoint():
    '''this helper method checks if
    postgresql server is available in the sys
    if not fires up one
    '''
    try:
        subprocess.check_output("pgrep postgres", shell=True)
    except Exception:
        logger.warning('Your postgresql server is offline, fake2db will try to launch it now!', extra=extra_information)
        # close_fds = True argument is the flag that is responsible
        # for Popen to launch the process completely independent
        subprocess.Popen("postgres -D /usr/local/pgsql/data", close_fds=True, shell=True)
        time.sleep(3)


def _mysqld_process_checkpoint():
    '''this helper method checks if 
    mysql server is available in the sys
    if not fires up one
    '''
    try:
        subprocess.check_output("pgrep mysqld", shell=True)
    except Exception:
        logger.warning('Your mysql server is offline, fake2db will try to launch it now!', extra=extra_information)
        # close_fds = True argument is the flag that is responsible
        # for Popen to launch the process completely independent
        subprocess.Popen("mysqld", close_fds=True, shell=True)
        time.sleep(3)


def _mongodb_process_checkpoint():
    '''this helper method checks if 
    mongodb server is available in the sys
    if not fires up one
    '''
    try:
        subprocess.check_output("pgrep mongod", shell=True)
    except Exception:
        logger.warning('Your mongodb server is offline, fake2db will try to launch it now!', extra=extra_information)
        # close_fds = True argument is the flag that is responsible
        # for Popen to launch the process completely independent
        subprocess.Popen("mongod", close_fds=True, shell=True)
        time.sleep(3)


def _redis_process_checkpoint(host, port):
    '''this helper method checks if
    redis server is available in the sys
    if not fires up one
    '''
    try:
        subprocess.check_output("pgrep redis", shell=True)
    except Exception:
        logger.warning('Your redis server is offline, fake2db will try to launch it now!', extra=extra_information)
        # close_fds = True argument is the flag that is responsible
        # for Popen to launch the process completely independent
        subprocess.Popen("redis-server --bind %s --port %s" % (host, port), close_fds=True, shell=True)
        time.sleep(3)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", help="Amount of rows desired per table")
    parser.add_argument("--db",
                        help="Db type for creation: sqlite, mysql, postgresql, mongodb, redis, couchdb, to be expanded")
    parser.add_argument("--name", help="OPTIONAL : Give a name to the db to be generated. ")
    parser.add_argument("--host", help="OPTIONAL : Hostname of db. ")
    parser.add_argument("--port", help="OPTIONAL : Port of db. ")
    parser.add_argument("--password", help="OPTIONAL : Password for root. ")

    args = parser.parse_args()

    if not args.rows or not args.db:
        logger.error('Please use with --help argument for usage information!', extra=extra_information)

    else:
        logger.info('arguments found(rows and db), starting faking!!', extra=extra_information)
        logger.warning('Rows argument : %s', args.rows, extra=extra_information)
        logger.info('DB argument : %s', args.db, extra=extra_information)

        if args.db == 'sqlite':
            try:
                from sqlite_handler import Fake2dbSqliteHandler
                fake_sqlite_handler = Fake2dbSqliteHandler()
            except Exception:
                raise InstantiateDBHandlerException
            if args.name:
                fake_sqlite_handler.fake2db_sqlite_initiator(int(args.rows), str(args.name))
            else:
                fake_sqlite_handler.fake2db_sqlite_initiator(int(args.rows))

        elif args.db == 'mysql':
            try:
                from mysql_handler import Fake2dbMySqlHandler
                fake_mysql_handler = Fake2dbMySqlHandler()
            except Exception:
                raise InstantiateDBHandlerException
            _mysqld_process_checkpoint()
            host = args.host or "127.0.0.1"
            port = args.port or "3306"
            if args.name:
                fake_mysql_handler.fake2db_mysql_initiator(host, port, args.password, int(args.rows), str(args.name))
            else:
                fake_mysql_handler.fake2db_mysql_initiator(host, port, args.password, int(args.rows))

        elif args.db == 'postgresql':
            try:
                import psycopg2
            except ImportError:
                raise MissingDependencyException('psycopg2 package not found on the python packages, please run: pip install psycopg2')
                
            try:
                from postgresql_handler import Fake2dbPostgresqlHandler
                fake_postgresql_handler = Fake2dbPostgresqlHandler()
            except Exception:
                raise InstantiateDBHandlerException
            _postgresql_process_checkpoint()
            host = args.host or "localhost"
            port = args.port or "5432"
            if args.name:
                fake_postgresql_handler.fake2db_postgresql_initiator(host, port, int(args.rows), str(args.name))
            else:
                fake_postgresql_handler.fake2db_postgresql_initiator(host, port, int(args.rows))

        elif args.db == 'mongodb':
            try:
                import pymongo
            except ImportError:
                raise MissingDependencyException('pymongo package not found on the python packages, please run: pip install pymongo')
                                
            try:
                from mongodb_handler import Fake2dbMongodbHandler
                fake_mongodb_handler = Fake2dbMongodbHandler()
            except Exception:
                raise InstantiateDBHandlerException
            _mongodb_process_checkpoint()
            host = args.host or "localhost"
            port = args.port or 27017
            if args.name:
                fake_mongodb_handler.fake2db_mongodb_initiator(host, int(port), int(args.rows), str(args.name))
            else:
                fake_mongodb_handler.fake2db_mongodb_initiator(host, int(port), int(args.rows))

        elif args.db == 'redis':
            if args.name and (not args.name.isdigit() or int(args.name) < 0):
                logger.error('redis db name must be a non-negative integer', extra=extra_information)
                return

            try:
                import redis
            except ImportError:
                raise MissingDependencyException('redis package not found on the python packages, please run: pip install redis')

            try:
                from redis_handler import Fake2dbRedisHandler
                fake_redis_handler = Fake2dbRedisHandler()
            except Exception:
                raise InstantiateDBHandlerException
            host = args.host or "localhost"
            port = args.port or "6379"
            _redis_process_checkpoint(host, port)
            if args.name:
                fake_redis_handler.fake2db_redis_initiator(host, int(port), int(args.rows), str(args.name))
            else:
                fake_redis_handler.fake2db_redis_initiator(host, int(port), int(args.rows))

        else:
            logger.error('Wrong arg for db parameter. Valid ones : sqlite - mysql - postgresql - mongodb - redis',
                         extra=extra_information)


if __name__ == '__main__':
    main()
