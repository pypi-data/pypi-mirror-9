procedures = {}

procedures[ 'SIC_PUERTA_DEL_TRIGGERS' ] = '''
    CREATE OR ALTER PROCEDURE SIC_PUERTA_DEL_TRIGGERS 
    as
    begin
        if (exists(
            select 1 from RDB$Triggers
            where RDB$Trigger_name = 'SIC_PUERTA_INV_DOCTOSIN_BU')) then
            execute statement 'drop trigger SIC_PUERTA_INV_DOCTOSIN_BU';
    end
    '''

procedures[ 'SIC_ALMACENES_AT' ] = '''
    CREATE OR ALTER PROCEDURE SIC_ALMACENES_AT 
    as
    begin
        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'ALMACENES' and rf.RDB$FIELD_NAME = 'SIC_INVENTARIANDO')) then
            execute statement 'ALTER TABLE ALMACENES ADD SIC_INVENTARIANDO SMALLINT DEFAULT 1';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'ALMACENES' and rf.RDB$FIELD_NAME = 'SIC_INVCONAJUSTES')) then
            execute statement 'ALTER TABLE ALMACENES ADD SIC_INVCONAJUSTES SMALLINT DEFAULT 0';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'ALMACENES' and rf.RDB$FIELD_NAME = 'SIC_INVMODIFCOSTOS')) then
            execute statement 'ALTER TABLE ALMACENES ADD SIC_INVMODIFCOSTOS SMALLINT DEFAULT 0';
    end
    '''

procedures['SIC_DOCTOSINDET_AT'] = '''
    CREATE OR ALTER PROCEDURE SIC_DOCTOSINDET_AT
    as
    BEGIN

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'DOCTOS_IN_DET' and rf.RDB$FIELD_NAME = 'SIC_FECHAHORA_U')) then
            execute statement 'ALTER TABLE DOCTOS_IN_DET ADD SIC_FECHAHORA_U FECHA_Y_HORA';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'DOCTOS_IN_DET' and rf.RDB$FIELD_NAME = 'SIC_USUARIO_ULT_MODIF')) then
            execute statement 'ALTER TABLE DOCTOS_IN_DET ADD SIC_USUARIO_ULT_MODIF USUARIO_TYPE';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'DOCTOS_IN_DET' and rf.RDB$FIELD_NAME = 'SIC_DETALLETIME_MODIFICACIONES')) then
            execute statement 'ALTER TABLE DOCTOS_IN_DET ADD SIC_DETALLETIME_MODIFICACIONES MEMO';
    END  
    '''