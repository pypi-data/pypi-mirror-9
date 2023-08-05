import unittest
import _cubrid
from _cubrid import *
import time
import CUBRIDdb
from xml.dom import minidom

class TestCubridConnection(unittest.TestCase):
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

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_connect(self):
         con = self.driver.connect(self.conStr,'dba','')
         self.assertIsInstance(con, self.driver.connection)
         con.close()

    def test_connect_prop_autocommit(self):
         con = self.driver.connect(self.conStr,'dba','')
         
         self.assertTrue(con.autocommit)
         con.close()

    def test_connect_set_autocommit(self):
         con = self.driver.connect(self.conStr,'dba','')
         
         self.assertTrue(con.autocommit)
         con.set_autocommit(False)
         self.assertEqual(con.autocommit, False)
         con.close()
         
    def test_connect_prop_isolation_level(self):
         con = self.driver.connect(self.conStr,'dba','')
         
         self.assertEqual(con.isolation_level,"CUBRID_REP_CLASS_UNCOMMIT_INSTANCE")
         con.close()  

    def test_connect_client_version(self):
         con = self.driver.connect(self.conStr,'dba','')
         
         self.assertEqual(con.client_version(),"9.3.0.0089")
         con.close()  

    def test_connect_server_version(self):
         con = self.driver.connect(self.conStr,'dba','')
         
         self.assertIn("9.3.0",con.server_version())
         con.close() 

    def test_connection_ping(self):
         con = self.driver.connect(self.conStr,'dba','')
         self.assertEqual(con.ping(),1)
         con.close()

    def test_connection_insert_id(self):
         con = self.driver.connect(self.conStr,'dba','')
         cur = con.cursor()

         sqlDrop = "drop table if exists t1"
         cur.prepare(sqlDrop)
         cur.execute()
         
         sqlCreate = "create table t1(id NUMERIC AUTO_INCREMENT(300, 1),name varchar(50))"
         cur.prepare(sqlCreate)
         cur.execute()
         
         sqlInsert = "insert into t1 (name) values ('Lily')"
         cur.prepare(sqlInsert)
         cur.execute()
         self.assertEqual(con.insert_id(),300)
         
         sqlInsert = "insert into t1 (name) values ('Lucy')"
         cur.prepare(sqlInsert)
         cur.execute()
         self.assertEqual(con.insert_id(),301)
         
         sqlInsert = "insert into t1 (name) values ('Paul'),('Jonty')"
         cur.prepare(sqlInsert)
         cur.execute()
         self.assertEqual(con.insert_id(),302)
         con.close()

    def test_connection_cursor(self):
         con = self.driver.connect(self.conStr,'dba','')
         cur = con.cursor()
         self.assertIsInstance(cur, self.driver.cursor)
         con.close()

    def test_connection_prop_lock_timeout(self):  
         con = self.driver.connect(self.conStr,'dba','')
         self.assertEqual(con.lock_timeout,-1)
         con.close()
         
    def test_CUBRIDdb_connect(self):
         con=CUBRIDdb.connect(self.conStr,'dba','')
         self.assertIsInstance(con, CUBRIDdb.connections.Connection)
         con.close()
         
    def test_CUBRIDdb_autocommit(self):
         con=CUBRIDdb.connect(self.conStr,"dba","")
         
         self.assertTrue(con.autocommit);
         con.set_autocommit(False);
         self.assertFalse(con.autocommit);
         self.assertFalse(con.get_autocommit());
         
         con.set_autocommit(True);
         self.assertTrue(con.autocommit);
         self.assertTrue(con.get_autocommit());
         
         with self.assertRaises(Exception):
             con.set_autocommit("True");
         
         con.close()
         
         
if __name__ == '__main__':
    #unittest.main(defaultTest = 'suite')
    #unittest.main()
    log_file = 'test_connection.result'
    f = open(log_file, "w")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCubridConnection)
    unittest.TextTestRunner(verbosity=2, stream=f).run(suite)
    f.close()