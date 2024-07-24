## 简介
在这个模块里，我们提供了动态测试不同数据库的框架。你可以用python 脚本文件(random_do_list.py、 mda_detect.py、mda_generate.py)自行生成输入测试文件。动态测试具体实现在（3TS/src/​dbtest/​src）下的case_cntl_v2.cc、sqltest_v2.cc、sql_cntl_v2.cc。

## 测试文件生成
运行random_do_list.py
```shell
python random_do_list.py data_num target_num
```
脚本会生成do_test_list.txt文件，里面内容形如
```
PW0-PW1
```
指示了操作类型

接下来运行mda_generate.py
```shell
python mda_generate.py db_type test_type
```
db_type有tdsql,crdb等，test_type有single,dist

运行mad_detect.py进行错误检测
```shell
python mad_detect.py
```
## 测试文件格式
静态测试首先声明ParamNum，即结果集有多少列
下面输入testSequence，格式为：执行顺序ID-事务ID-SQL语句
接下来输入隔离级别，例如serializable{...}
括号里面是像"9-0,1 1,1"的对，其中 9 是 SQL ID，"(0,1) (1,1)" 是结果。
文件可以在#后添加注释。
动态测试声明Parameters和testSequence，但是没有期望结果序列。
Parameters格式类似如下：

```
#Parameters: #column=2 #txn=2 #operations=2 #variable=2
```

## case_cntl_v2.cc 
实现了测试用例控制功能，包含从测试文件中读取数据库配置、sql 语句和预期结果，验证处理实际结果和预期结果的区别，输出比对结果到指定文件夹等功能。
代码首先通过TestSequenceAndTestResultSetFromFile函数读取指定的测试文件。这个函数解析测试文件的内容，提取测试序列和结果集信息。在读取测试文件的过程中，对每一行进行解析。根据行的内容，执行不同的操作：
如果行包含"Parameters"，则提取参数数量，并设置到测试序列对象中。<br> 
如果行以"#"开头，表示这是一条注释，跳过这行。<br> 
其他情况下，假设行包含事务ID和SQL语句，使用TxnIdAndSql函数解析这行，提取事务ID、SQL ID和SQL语句，然后创建一个TxnSql对象，并添加到测试序列中。<br> 
初始化测试序列和结果集列表：InitTestSequenceAndTestResultSetList函数读取"do_test_list.txt"文件，该文件包含要执行的测试案例列表。对于列表中的每个测试案例，函数会读取相应的测试文件，并将解析得到的测试序列和结果集添加到内部存储结构中。<br> 
最后调用IsSqlExpectedResult比较SQL查询的当前结果和预期结果。这个比较是逐项进行的。如果当前结果和预期结果的大小不同，或者任何一项不匹配，函数返回false，表示结果不符合预期。否则，返回true，表示测试通过。

数据结构：
1.Outputter：提供将测试用例和结果数据写入文件的函数
2.ResultHandler：处理和验证期望的测试结果

函数：<br> 
和v1静态测试相同的有：<br> 
CaseReader::TxnIdAndSql:解析给定的行以提取执行顺序ID、事务ID和SQL语句。 <br> 
CaseReader::SqlIdAndResult：解析给定的行以提取SQL ID及其预期结果。<br>
CaseReader::Isolation：解析隔离级别。<br>
CaseReader::InitTestSequenceAndTestResultSetList：同v1,基于提供的测试路径和数据库类型初始化 TestSequence 和 TestResultSet 列表。<br>
ResultHandler::IsSqlExpectedResult，ResultHandler::IsTestExpectedResult：比较测试结果和期望结果<br>
Outputter::WriteResultTotal，Outputter::WriteTestCaseTypeToFile，Outputter::WriteResultType：将测试结果写入文件<br>
不同：<br>
CaseReader::TestSequenceAndTestResultSetFromFile:读取文件并输出testSequence，和v1不同的是没有解析隔离级别和预期结果。<br>
Outputter::PrintAndWriteTxnSqlResult:输出事物结果，和v1不同的是只输出当前结果，没有和预期结果集的比对<br>

## sql_cntl_v2.cc
SQL控制或操作的代码。实现了与 ODBC 数据库的接口功能。包含设置数据库隔离级别、开始事务、执行增删改查等功能、处理 SQL 返回值并获取错 误信息、结束事务或回滚事务等功能。

这段代码首先使用DBConnector从连接池中获取对应会话ID的数据库连接，然后分配一个新的语句句柄。如果句柄分配失败，函数会调用DBConnector::SqlExecuteErr来获取错误信息，并输出错误提示。sql_id为1024会跳过打印输出功能然后，它会释放语句句柄并返回false，表示SQL执行失败。最终返回一个布尔值，表示SQL语句的执行是否成功。

数据结构：<br> 
DBConnector:管理所有和数据库连接相关功能，持有ODBC中的数据库连接句柄(Database Connection Handle)

和v1静态测试相同的有：<br> 
DBConnector::ErrInfoWithStmt：从ODBC句柄提取错误信息<br>
DBConnector::ExecReadSql2Int：执行SQL读语句并处理错误<br>
DBConnector::SQLStartTxn：启动事务并处理错误<br>
DBConnector::SetAutoCommit：数据库连接设为自动提交模式<br>
DBConnector::SetTimeout：设置连接timeout<br>
DBConnector::SetIsolationLevel:设置隔离级别<br>
不同：<br>
DBConnector::SqlExecuteErr：处理和记录执行错误，和v1不同的是输出了session id,如果因为莫名原因失败就返回空而没有信息<br>
DBConnector::ExecWriteSql：执行SQL写语句并处理错误，和v1不同的是使用SQLRowCount函数获取受影响的行数，如果没有受影响的行就输出错误<br>
DBConnector::SQLEndTnx：通过提交或回滚结束事务，和v1不同的是在SQL语句执行成功后会输出执行时间信息

## sqltest_v2.cc 
SQL测试的代码，包含项目的主函数。
首先利用gflags库来实现命令行参数解析。
初始化测试环境：
设置数据库连接池大小、事务超时时间等配置参数。
初始化数据库连接器（DBConnector）以连接到指定的数据库。
准备测试用的SQL语句和事务序列，这些可能包括读（SELECT）、写（INSERT, UPDATE, DELETE）、事务开始（BEGIN）和结束（COMMIT, ROLLBACK）等操作。采用多线程编程，每个线程负责一组数据库语句的执行，并且通过子线程不同的休眠时间实现程序代码按指定顺序运行。<br>
在执行过程中，将测试过程和结果记录到指定的日志文件中，以便后续分析和审计。完成所有SQL语句的执行后，释放相关资源，如关闭数据库连接、释放互斥锁等。汇总测试结果，包括成功执行的语句数量、失败的语句及其原因等。<br>
和v1不同的是不支持cassandra和yugabyte，也不支持它们的隔离级别定义
函数：
MultiThreadExecution：多线程执行SQL查询并返回结果，和v1不同的是没有对yugabyte和myrocks支持


## Introduction
In this module, we provide a framework for dynamically testing different databases. You can use Python scripts (random_do_list.py, mda_detect.py, mda_generate.py) to generate input test files yourself. Dynamic testing is specifically implemented in (3TS/src/dbtest/src) under case_cntl_v2.cc, sqltest_v2.cc, sql_cntl_v2.cc.

## Test File Generation
Run random_do_list.py
```shell
python random_do_list.py data_num target_num
```
The script will generate a do_test_list.txt file with contents like
```
PW0-PW1
```
indicating the type of operation.

Next, run mda_generate.py
```shell
python mda_generate.py db_type test_type
```
db_type includes tdsql, crdb, etc., and test_type includes single, dist.

Run mad_detect.py for error detection
```shell
python mad_detect.py
```

## Test File Format
Static testing first declares ParamNum, which means how many columns the result set has.
Then input testSequence in the format: execution order ID-transaction ID-SQL statement
Next, input the isolation level, such as serializable{...}
Inside the brackets are pairs like "9-0,1 1,1", where 9 is the SQL ID and "(0,1) (1,1)" is the result.
Comments can be added after # in the file.
Dynamic testing declares Parameters and testSequence but does not have an expected result sequence.
Parameters format is similar to the following:
```
#Parameters: #column=2 #txn=2 #operations=2 #variable=2
```

## case_cntl_v2.cc 
Implements the test case control function, including reading database configuration, SQL statements, and expected results from the test file, verifying the difference between actual results and expected results, and outputting comparison results to the specified folder.
The code first reads the specified test file using the TestSequenceAndTestResultSetFromFile function. This function parses the content of the test file and extracts the test sequence and result set information. During the process of reading the test file, each line is parsed. Depending on the content of the line, different operations are performed:
If the line contains "Parameters", the number of parameters is extracted and set to the test sequence object.
If the line starts with "#", it indicates a comment and is skipped.
In other cases, it is assumed that the line contains transaction ID and SQL statement. The TxnIdAndSql function is used to parse this line, extract the transaction ID, SQL ID, and SQL statement, then create a TxnSql object and add it to the test sequence.
Initialize the test sequence and result set list: The InitTestSequenceAndTestResultSetList function reads the "do_test_list.txt" file, which contains the list of test cases to be executed. For each test case in the list, the function reads the corresponding test file and adds the parsed test sequence and result set to the internal storage structure.
Finally, the IsSqlExpectedResult function is called to compare the current result of the SQL query with the expected result. This comparison is done item by item. If the current result and the expected result differ in size or any item does not match, the function returns false, indicating that the result does not meet expectations. Otherwise, it returns true, indicating that the test passed.

Data structures:

Outputter: Provides functions to write test cases and result data to a file
ResultHandler: Handles and verifies expected test results

Functions:
Same as v1 static testing:
CaseReader::TxnIdAndSql: Parses a given line to extract the execution order ID, transaction ID, and SQL statement.
CaseReader::SqlIdAndResult: Parses a given line to extract the SQL ID and its expected result.
CaseReader::Isolation: Parses the isolation level.
CaseReader::InitTestSequenceAndTestResultSetList: Same as v1, initializes the TestSequence and TestResultSet lists based on the provided test path and database type.
ResultHandler::IsSqlExpectedResult, ResultHandler::IsTestExpectedResult: Compares the test result with the expected result.
Outputter::WriteResultTotal, Outputter::WriteTestCaseTypeToFile, Outputter::WriteResultType: Writes test results to a file.

Different:
CaseReader::TestSequenceAndTestResultSetFromFile: Reads the file and outputs the testSequence. Unlike v1, it does not parse the isolation level and expected results.
Outputter::PrintAndWriteTxnSqlResult: Outputs transaction results. Unlike v1, it only outputs the current result without comparing it with the expected result set.

## sql_cntl_v2.cc
Code for SQL control or operations. Implements interface functions with ODBC databases, including setting database isolation levels, starting transactions, performing CRUD operations, handling SQL return values and retrieving error messages, ending transactions or rolling back transactions.

The code first uses DBConnector to get the database connection for the corresponding session ID from the connection pool, then allocates a new statement handle. If the handle allocation fails, the function calls DBConnector::SqlExecuteErr to get error information and outputs an error message. If sql_id is 1024, it skips the print output function. Then, it releases the statement handle and returns false, indicating that the SQL execution failed. Finally, it returns a boolean value indicating whether the SQL statement execution was successful.

Data structures:
DBConnector: Manages all database connection-related functions and holds the ODBC database connection handle (Database Connection Handle).

Same as v1 static testing:
DBConnector::ErrInfoWithStmt: Extracts error information from the ODBC handle.
DBConnector::ExecReadSql2Int: Executes SQL read statements and handles errors.
DBConnector::SQLStartTxn: Starts a transaction and handles errors.
DBConnector::SetAutoCommit: Sets the database connection to auto-commit mode.
DBConnector::SetTimeout: Sets the connection timeout.
DBConnector::SetIsolationLevel: Sets the isolation level.

Different:
DBConnector::SqlExecuteErr: Handles and records execution errors. Unlike v1, it outputs the session id and returns empty if it fails for some unknown reason without providing information.
DBConnector::ExecWriteSql: Executes SQL write statements and handles errors. Unlike v1, it uses the SQLRowCount function to get the number of affected rows. If no rows are affected, it outputs an error.
DBConnector::SQLEndTnx: Ends the transaction by committing or rolling back. Unlike v1, it outputs the execution time information after the SQL statement is successfully executed.

sqltest_v2.cc
Code for SQL testing, containing the main function of the project.
First, the gflags library is used to implement command-line argument parsing.
Initialize the test environment:
Set configuration parameters such as database connection pool size and transaction timeout.
Initialize the database connector (DBConnector) to connect to the specified database.
Prepare SQL statements and transaction sequences for testing, which may include read (SELECT), write (INSERT, UPDATE, DELETE), transaction start (BEGIN), and end (COMMIT, ROLLBACK) operations. Use multi-threaded programming, where each thread is responsible for executing a group of database statements, and the program code is executed in a specified order by setting different sleep times for the sub-threads.
During execution, record the test process and results in the specified log file for subsequent analysis and audit. After completing the execution of all SQL statements, release related resources, such as closing database connections and releasing mutex locks. Summarize test results, including the number of successfully executed statements, failed statements, and their reasons.
Unlike v1, it does not support Cassandra and Yugabyte, nor their isolation level definitions.

Functions:
MultiThreadExecution: Executes SQL queries in multiple threads and returns results. Unlike v1, it does not support Yugabyte and MyRocks.

