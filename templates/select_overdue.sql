SELECT
    ID, Cislo, IIF(RefCM = 9, 'EUR', 'CZK') AS CURRENCY, 
    IIF(RefCM = 9,
        CAST(CmLikv AS DECIMAL(10, 2)),
        CAST(KcLikv AS DECIMAL(10, 2))
    ) AS AMOUNT,
    CASE
        WHEN Email LIKE '%tyre-world.de%' THEN 'buchhaltung@tyre-world.de'
        ELSE Email
    END AS 'Email'

FROM    FA
WHERE   FA.KcLikv > 0
        AND FA.RelStorn IS NULL
        AND FA.RelTpFak = 1
        AND FA.DatSplat BETWEEN DATEADD(yy, -1, GETDATE()) AND DATEADD(dd, -3, GETDATE())
        AND FA.RelForUh NOT IN (4, 17)
        AND FA.Email LIKE '%@%'
        AND FA.RelForUh NOT IN (5, 19, 21)
        AND FA.Email NOT LIKE '%bestdrive.cz%'
        -- For testing purpose uncomment line bellow
        -- AND (FA.Email LIKE '%shop@md-tuning.de%' OR FA.Email LIKE '%SALES@FRPNE%' OR FA.Email LIKE 'EDPS.M%')
