procedures={}

procedures['SIC_PROVEEDORES_DIOT'] = '''
    CREATE OR ALTER PROCEDURE SIC_PROVEEDORES_DIOT
    as
    begin
     if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'PROVEEDORES' and rf.RDB$FIELD_NAME = 'SIC_CUENTA_COMPRAS')) then
        execute statement 'ALTER TABLE PROVEEDORES ADD SIC_CUENTA_COMPRAS ENTERO_ID';
	end  
    '''