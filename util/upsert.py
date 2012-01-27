def upsert(tbl_name, fields, keys, filename, tmp_tbl_name=None):
    if tmp_tbl_name is None:
        tmp_tbl_name = 'tmp_' + tbl_name

    update_fields = 
        ['%(tbl)s.%(field)s = %(tmp_tbl).%(field)s' %
         {'tbl' : tbl_name, 'tmp_tbl' : tmp_tbl_name, 'field' : field }
            for field in fields].join(', ')
    load_fields = fields.join(', ')
    insert_fields = '(%s)' % fields.join(', ')
    print update_fields
    """
    BEGIN TRANSACTION;
    LOCK TABLES %(tbl_name)s WRITE;
    
    -- Create temp table
    CREATE TEMPORARY TABLE %(tmp_tbl_name)s LIKE %(tbl_name)s;
    
    SET foreign_key_checks=0;
    -- Load all data into temp table
    LOAD DATA INFILE %(filename)s
    INTO TABLE $(tmp_tbl_name)s
    FIELDS TERMINATED BY '::'
    %(load_fields)s;
    """
    """
    -- Output all non overlapping rows back to a file
    SELECT %(fields)s FROM %(tmp_tbl_name)s
    INTO FILE %(tmp_filename)
    FIELDS TERMINATED BY '::';
    -- some join statement
    
    -- Load all non-overlapping rows into table
    LOAD DATA INFILE tmp_filename
    INTO TABLE tbl_name
    FIELDS TERMINATED BY '::'
    %(load_fields)s;
    
    -- Perform updates on all overlapping rows
    UPDATE tbl_name, tmp_tbl_name 
    VALUES tbl_name.flds = tmp_tbl_name.flds
    ON tbl_name.keys = tmp_tbl_name.keys;
    SET foreign_key_checks=1;
    
    UNLOCK TABLES;
    
    COMMIT TRANSACTION;
    """
