import unittest
import _cubrid
from _cubrid import *
import time
import CUBRIDdb
from xml.dom import minidom

class TestCubridTransaction(unittest.TestCase):
    driver = _cubrid
    
    xmlt = minidom.parse('python_config.xml')
    ips = xmlt.childNodes[0].getElementsByTagName('ip')
    ip = ips[0].childNodes[0].toxml()
    ports = xmlt.childNodes[0].getElementsByTagName('port')
    port = ports[0].childNodes[0].toxml()
    dbnames = xmlt.childNodes[0].getElementsByTagName('dbname')
    dbname = dbnames[0].childNodes[0].toxml()
    conStr = "CUBRID:"+ip+":"+port+":"+dbname+":::"
    
    connect_args = (conStr, 'dba', '')
    connect_kw_args = {}

    def init_table(self):
         con = self.driver.connect(self.conStr,'dba','')
         cur = con.cursor();
         
         cur.prepare("drop table if exists t1")
         cur.execute()
         
         cur.prepare("create table t1(id int,name varchar(50))")
         cur.execute()
         con.close()
         
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_connection_set_isolation_level(self):         
         con = self.driver.connect(self.conStr,'dba','')
         con.set_isolation_level(CUBRID_COMMIT_CLASS_UNCOMMIT_INSTANCE)
         self.assertEqual(con.isolation_level,'CUBRID_COMMIT_CLASS_UNCOMMIT_INSTANCE')
         
         con.set_isolation_level(CUBRID_COMMIT_CLASS_COMMIT_INSTANCE)
         self.assertEqual(con.isolation_level,'CUBRID_COMMIT_CLASS_COMMIT_INSTANCE')
         
         con.set_isolation_level(CUBRID_REP_CLASS_UNCOMMIT_INSTANCE)
         self.assertEqual(con.isolation_level,'CUBRID_REP_CLASS_UNCOMMIT_INSTANCE')
         
         con.set_isolation_level(CUBRID_REP_CLASS_COMMIT_INSTANCE)
         self.assertEqual(con.isolation_level,'CUBRID_REP_CLASS_COMMIT_INSTANCE')
         
         con.set_isolation_level(CUBRID_REP_CLASS_REP_INSTANCE)
         self.assertEqual(con.isolation_level,'CUBRID_REP_CLASS_REP_INSTANCE')

         con.set_isolation_level(CUBRID_SERIALIZABLE)
         self.assertEqual(con.isolation_level,'CUBRID_SERIALIZABLE')
         con.close()

    def test_connection_commit(self):
         self.init_table()
         con = self.driver.connect(self.conStr,'dba','')
         
         con.set_autocommit(False)
         cur = con.cursor()
         cur.prepare("insert into t1 values (1,'Lily')")
         cur.execute()
         
         con.commit();
         
         cur2 = con.cursor()
         cur2.prepare('select * from t1')
         cur2.execute()
         self.assertEqual(cur2.num_rows(), 1)
         
         con.close()

    def test_connection_rollback(self):
         self.init_table()
         con = self.driver.connect(self.conStr,'dba','')
         con.set_autocommit(False)
         
         cur = con.cursor()
         cur.prepare("insert into t1 values (1,'Lily')")
         cur.execute()
         
         con.rollback();
         
         cur2 = con.cursor()
         cur2.prepare('select * from t1')
         cur2.execute()
         self.assertEqual(cur2.num_rows(), 0)
         
         con.close()

    def test_CUBRIDdb_commit(self):
         self.init_table()
         con = CUBRIDdb.connect(self.conStr,'dba','')
         
         con.set_autocommit(False)
         cur = con.cursor()
         cur.execute("insert into t1 values (1,'Lily')")
         
         con.commit();
         
         cur2 = con.cursor()
         cur2.execute('select * from t1')
         results=cur2.fetchall()
         
         self.assertEqual(len(results),1)
         con.close()

    def test_CUBRIDdb_rollback(self):
         self.init_table()
         con = CUBRIDdb.connect(self.conStr,'dba','')
         
         con.set_autocommit(False)
         cur = con.cursor()
         cur.execute("insert into t1 values (1,'Lily')")
         
         con.rollback();
         
         cur2 = con.cursor()
         cur2.execute('select * from t1')
         results=cur2.fetchall()
         
         self.assertEqual(len(results),0)
         
         con.close()
         
if __name__ == '__main__':
    #unittest.main(defaultTest = 'suite')
    #unittest.main()
    log_file = 'test_transaction.result'
    f = open(log_file, "w")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCubridTransaction)
    unittest.TextTestRunner(verbosity=2, stream=f).run(suite)
    f.close()