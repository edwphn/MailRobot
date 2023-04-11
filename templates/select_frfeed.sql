-- ID Invoice Currency Order Amount Parcels Carrier Tracking
SELECT
    ID,
    Cislo AS 'Invoice',
    IIF(RefCM = 9, 'EUR', 'CZK') AS 'Currency',
    ISNULL(CisloObj, '–') AS 'Order',
    ISNULL(IIF(RefCM = 9, CAST(CmCelkem AS DECIMAL(10, 2)), CAST(KcCelkem AS DECIMAL(10, 2))), 0) AS 'Amount',
    CASE
        WHEN Email LIKE '%tyre-world.de%' THEN 'buchhaltung@tyre-world.de; info@tyre-world.de'
        ELSE Email
    END AS 'Email',
    ISNULL(VPrkolicesstvoba, 1) AS 'Parcels',
    CASE
        WHEN FA.RefDopravci IN (8, 18) THEN 'DPD'
        WHEN FA.RefDopravci IN (11, 16) THEN 'WeDo'
        WHEN FA.RefDopravci IN (10, 23) THEN 'Schenker'
        ELSE 'On demand'
    END AS 'Carrier',
    CASE
        WHEN VPrPackNumbers IS NULL THEN 'Not shipped yet'
        ELSE VPrPackNumbers
    END AS 'Tracking No'

FROM FA
WHERE   FA.RefStr = 38
        AND FA.RelTpFak = 1
        AND CAST(FA.Datum AS DATE) = CAST(GETDATE() AS DATE)
        -- AND FA.Datum = '2023-04-06'
        AND FA.Email LIKE '%@%'

-- ORDER BY Email