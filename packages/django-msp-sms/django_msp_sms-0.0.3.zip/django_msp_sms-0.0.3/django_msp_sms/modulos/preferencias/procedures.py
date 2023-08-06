procedures = {}

procedures['SIC_SMS_CLIENTE_AT'] = '''
    CREATE OR ALTER PROCEDURE SIC_SMS_CLIENTE_AT
    as
    BEGIN
        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'CLIENTES' and rf.RDB$FIELD_NAME = 'SIC_SMS_NOENVIAR')) then
            execute statement 'ALTER TABLE CLIENTES ADD SIC_SMS_NOENVIAR SMALLINT';
    END  
    '''