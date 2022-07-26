# Database 

To build the database tables, please ensure run the below:

```
cat CREATE-MUSIC-TABLES-ERD-SQL.sql | mysql -u root -p
```

For convenience, can run the script to do this, see below. Note the database name we are using:

```
(base) ➜  datamining_itc git:(cli) ✗ head  -1 sql/*sql
CREATE DATABASE IF NOT EXISTS datamining_itc_music ;

(base) ➜  datamining_itc git:(cli) ✗ cat sql/create-db.sh
cat *SQL | mysql -u root -p
```
