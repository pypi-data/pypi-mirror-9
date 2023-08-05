procedures = {}

procedures['SIC_FAEXIST_ARTICULO_AT'] = '''
    CREATE OR ALTER PROCEDURE SIC_FAEXIST_ARTICULO_AT
    as
    BEGIN
        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'ARTICULOS' and rf.RDB$FIELD_NAME = 'SIC_FAEXIST_IGNORAR')) then
            execute statement 'ALTER TABLE ARTICULOS ADD SIC_FAEXIST_IGNORAR SMALLINT';
    END  
    '''