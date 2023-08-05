import unittest
import _cubrid
from _cubrid import *
import time
import CUBRIDdb
from xml.dom import minidom

class TestCubridCursor(unittest.TestCase):
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
         cur.close()
         con.close()
         
    def setUp(self):
        pass
    def tearDown(self):
        pass 
    
    def test_cursor_affected_rows(self):
         self.init_table()
         con = self.driver.connect(self.conStr,"dba","")
         
         cur = con.cursor();
         cur.prepare("insert into t1 values (1,'Lily')")
         cur.execute()
         self.assertEqual(cur.affected_rows(), 1)
         
         cur.prepare("insert into t1 values (2,'Lucy'),(3,'Paul')")
         cur.execute()
         self.assertEqual(cur.affected_rows(), 2)
         
         cur.prepare("update t1 set name = 'Jessica' where id = 3")
         cur.execute()
         self.assertEqual(cur.affected_rows(), 1)
         
         cur.prepare("select * from t1")
         cur.execute()
         self.assertEqual(cur.affected_rows(), -1)
         
         cur.prepare("delete from t1 where id = 4")
         cur.execute()
         self.assertEqual(cur.affected_rows(), 0)
         
         cur.prepare("delete from t1")
         cur.execute()
         self.assertEqual(cur.affected_rows(), 3)
         
         cur.close()
         con.close()

    def test_cursor_close(self):
         self.init_table()
         con = self.driver.connect(self.conStr,"dba","")

         cur = con.cursor();
         cur.prepare("insert into t1 values (1,'Lily')")
         cur.execute()
         cur.close();
         
         with self.assertRaises(Exception):
             cur.prepare("insert into t1 values (2,'Lucy'),(3,'Paul')")
         #cur.execute()
         #self.assertEqual(cur.affected_rows(), 0)
         with self.assertRaises(Exception):
             cur.close()
         con.close()

    def test_cursor_bind_param(self):
         self.init_table()
         con = self.driver.connect(self.conStr,"dba","")
         
         cur = con.cursor();
         cur.prepare("insert into t1 values (?,?)")
         cur.bind_param(1,'1')
         cur.bind_param(2,'Lily')
         cur.execute()
         self.assertEqual(cur.affected_rows(), 1)
         
         cur.close();
         con.close()
         
    def test_cursor_fetch_row(self):
         self.init_table()
         con = self.driver.connect(self.conStr,"dba","")
         
         dataCheck = [[1,'Lily'],[2,'Lucy'],[3,'Paul'],[4,'Jessica']]
         dataResult = []
         
         cur = con.cursor();
         cur.prepare("insert into t1 values (1,'Lily'),(2,'Lucy'),(3,'Paul'),(4,'Jessica')")
         cur.execute()
         
         cur.prepare('select * from t1')
         cur.execute()
         row = cur.fetch_row()
         
         self.assertEqual(row[0], 1)
         self.assertEqual(row[1], 'Lily')
         
         while row:
           dataResult.append(row)
           row = cur.fetch_row()
         
         self.assertEqual(dataCheck, dataResult)
         cur.close();
         con.close()

    def test_cursor_next_result(self):
         self.init_table()
         con = self.driver.connect(self.conStr,"dba","")
         
         dataCheck = [[1,'Lily']]
         dataResult = []
         
         cur = con.cursor();
         cur.prepare("insert into t1 values (1,'Lily'),(2,'Lucy'),(3,'Paul'),(4,'Jessica')")
         cur.execute()
         
         cur.prepare('select * from t1;select * from t1 where id = 1')
         cur.execute(CUBRID_EXEC_QUERY_ALL)

         cur.next_result()
         
         row = cur.fetch_row()
         
         while row:
           dataResult.append(row)
           row = cur.fetch_row()
         
         self.assertEqual(dataCheck, dataResult)
         cur.close()
         con.close()

    def test_cursor_num_fields(self):
         self.init_table()
         con = self.driver.connect(self.conStr,"dba","")
         
         cur = con.cursor();
         cur.prepare("insert into t1 values (1,'Lily'),(2,'Lucy'),(3,'Paul'),(4,'Jessica')")
         cur.execute()
         
         cur.prepare('select * from t1;')
         cur.execute()
         
         self.assertEqual(cur.num_fields(), 2)
         cur.close()
         con.close()

    def test_cursor_num_rows(self):
         self.init_table()
         con = self.driver.connect(self.conStr,"dba","")
         
         cur = con.cursor();
         cur.prepare("insert into t1 values (1,'Lily'),(2,'Lucy'),(3,'Paul'),(4,'Jessica')")
         cur.execute()
         
         cur.prepare('select * from t1;')
         cur.execute()
         self.assertEqual(cur.num_rows(), 4)
         
         cur.prepare('select * from t1 where id > 2;')
         cur.execute()
         self.assertEqual(cur.num_rows(), 2)
         
         cur.close()
         con.close()

    def test_cursor_result_info(self):
         self.init_table()
         con = self.driver.connect(self.conStr,"dba","")
         
         cur = con.cursor();
         cur.prepare("insert into t1 values (1,'Lily'),(2,'Lucy'),(3,'Paul'),(4,'Jessica')")
         cur.execute()
         
         cur.prepare('select * from t1;')
         cur.execute()
        
         infos = cur.result_info()
         
         self.assertEqual(cur.result_info(1), ((8, 0, 0, 10, 'id', '', 't1', 'NULL', 0, 0, 0, 0, 0, 0, 0),))
         self.assertEqual(cur.result_info(2), ((2, 0, 0, 50, 'name', '', 't1', 'NULL', 0, 0, 0, 0, 0, 0, 0),))
         
         cur.close()
         con.close()
         
    def test_cursor_CUBRIDdb_close(self):
         self.init_table()
         con = CUBRIDdb.connect(self.conStr,"dba","")
         
         cur = con.cursor();
         cur.execute("insert into t1 values (1,'Lily')")
         cur.close()
         
         with self.assertRaises(Exception):
             cur.execute("insert into t1 values (2,'Lucy'),(3,'Paul')")

         con.close()

    def test_cursor_CUBRIDdb_fetchall(self):
         self.init_table()
         con = CUBRIDdb.connect(self.conStr,"dba","")
         
         cur = con.cursor();
         cur.execute("insert into t1 values (1,'Lily'),(2,'Lucy'),(3,'Paul')")
         
         cur.execute("select * from t1")
         
         results = cur.fetchall()

         self.assertEquals(3,len(results))
         
         cur.close()
         con.close()

    def test_cursor_CUBRIDdb_fetchone(self):
         self.init_table()
         con = CUBRIDdb.connect(self.conStr,"dba","")
         
         dataCheck = [[1,'Lily'],[2,'Lucy'],[3,'Paul']]
         dataResult = []
         
         cur = con.cursor();
         cur.execute("insert into t1 values (1,'Lily'),(2,'Lucy'),(3,'Paul')")
         
         cur.execute("select * from t1")
         
         row = cur.fetchone()

         while row:
           dataResult.append(row)
           row = cur.fetchone()
         
         self.assertEqual(dataCheck, dataResult)
         cur.close()
         con.close()

    def test_cursor_CUBRIDdb_fetchmany(self):
         self.init_table()
         con = CUBRIDdb.connect(self.conStr,"dba","")
         
         dataCheck = [[1,'Lily'],[2,'Lucy'],[3,'Paul']]
         dataResult = []
         
         cur = con.cursor();
         cur.execute("insert into t1 values (1,'Lily'),(2,'Lucy'),(3,'Paul')")
         
         cur.execute("select * from t1")
         
         row = cur.fetchone()

         while row:
           dataResult.append(row)
           row = cur.fetchone()
         
         self.assertEqual(dataCheck, dataResult)
         cur.close()
         con.close()
         
if __name__ == '__main__':
    #unittest.main(defaultTest = 'suite')
    #unittest.main()
    log_file = 'test_cursor.result'
    f = open(log_file, "w")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCubridCursor)
    unittest.TextTestRunner(verbosity=2, stream=f).run(suite)
    f.close()