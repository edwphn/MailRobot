WITH raw AS (
  SELECT 
    StwPh_27458920_2022.dbo.FA.ID AS idFa, 
    StwPh_27458920_2022.dbo.FA.Cislo AS cisloFa, 
    StwPh_27458920_2022.dbo.FA.CisloObj, 
	CAST(FA.DatCreate AS DATE) AS DatVytvor,
    CASE WHEN (
      FA.Ulice2 IS NOT NULL 
      AND FA.PSC2 IS NOT NULL 
      AND FA.Obec2 IS NOT NULL 
      AND FA.Firma2 IS NOT NULL
    ) THEN FA.Firma2 ELSE FA.Firma END AS firm, 
    CASE WHEN (
      FA.Ulice2 IS NOT NULL 
      AND FA.PSC2 IS NOT NULL 
      AND FA.Obec2 IS NOT NULL 
      AND FA.Jmeno2 IS NOT NULL
    ) THEN FA.Jmeno2 ELSE FA.Jmeno END AS name, 
    CASE WHEN (
      FA.Ulice2 IS NOT NULL 
      AND FA.PSC2 IS NOT NULL 
      AND FA.Obec2 IS NOT NULL 
      AND FA.Tel2 IS NOT NULL
    ) THEN REPLACE(FA.Tel2, ' ', '') ELSE REPLACE(FA.Tel, ' ', '') END AS tel, 
    CASE WHEN FA.Ulice2 IS NOT NULL 
    AND FA.PSC2 IS NOT NULL 
    AND FA.Obec2 IS NOT NULL THEN FA.Ulice2 ELSE FA.Ulice END AS street, 
    CASE WHEN FA.Ulice2 IS NOT NULL 
    AND FA.PSC2 IS NOT NULL 
    AND FA.Obec2 IS NOT NULL THEN FA.PSC2 ELSE FA.PSC END AS zipCode, 
    CASE WHEN FA.Ulice2 IS NOT NULL 
    AND FA.PSC2 IS NOT NULL 
    AND FA.Obec2 IS NOT NULL THEN FA.Obec2 ELSE FA.Obec END AS city, 
    CASE WHEN FA.RefDopravci = 6 THEN 'Tursko' WHEN FA.RefDopravci = 20 THEN 'Brno' ELSE 'Neznámé' END AS depo, 
    StwPh_27458920_2022.dbo.FA.VPrMinDatum AS dateFrom, 
    CASE WHEN FA.VPrmaxdatum IS NULL THEN (
      CASE WHEN DATENAME(WEEKDAY, FA.Datum) = 'Friday' THEN FA.Datum + 5 WHEN DATENAME(WEEKDAY, FA.Datum + 3) IN ('Saturday') THEN FA.Datum + 5 WHEN DATENAME(WEEKDAY, FA.Datum + 3) IN ('Sunday') THEN FA.Datum + 4 ELSE FA.Datum + 3 END
    ) ELSE FA.VPrmaxdatum END AS dateBy, 
    CASE WHEN FA.VPrtimeFrom LIKE '%,%' THEN REPLACE(FA.VPrtimeFrom, ',', ':') WHEN FA.VPrtimeFrom LIKE '%.%' THEN REPLACE(FA.VPrtimeFrom, '.', ':') WHEN FA.VPrtimeFrom IS NULL 
    OR FA.VPrtimeFrom LIKE '%:%' THEN FA.VPrtimeFrom ELSE CONCAT(FA.VPrtimeFrom, ':00') END AS timeFrom, 
    CASE WHEN FA.VPrtimeBy LIKE '%,%' THEN REPLACE(FA.VPrtimeBy, ',', ':') WHEN FA.VPrtimeBy LIKE '%.%' THEN REPLACE(FA.VPrtimeBy, '.', ':') WHEN FA.VPrtimeBy IS NULL 
    OR FA.VPrtimeBy LIKE '%:%' THEN FA.VPrtimeBy ELSE CONCAT(FA.VPrtimeBy, ':00') END AS timeBy, 
    StwPh_27458920_2022.dbo.FA.Pozn AS note1, 
    { fn CONCAT(
      ISNULL(StwPh_27458920_2022.dbo.FA.Tel, ''), 
      ISNULL(StwPh_27458920_2022.dbo.FA.GSM, '')
    ) } AS note2, 
    '_' AS Vratka, 
    StwPh_27458920_2022.dbo.FA.KcCelkem AS Castka, 
    CASE WHEN StwPh_27458920_2022.dbo.FA.RelForUh IN (4, 17)
    THEN CAST(1 AS BIT) ELSE CAST(0 AS BIT) END AS Dobirka, 
    PolDetail.kusu AS Kusu,
    PolDetail.hmotnost AS Hmotnost,
    STUFF(
		(
			SELECT CHAR(13) + CHAR(10) + CAST(FApol.Mnozstvi AS NVARCHAR) + 'x ' + FApol.SText
			FROM StwPh_27458920_2022.dbo.FApol
			WHERE FApol.RefAg = FA.ID
				AND FApol.VPrSklad IS NOT NULL
				AND FApol.VPrSklad <> 'Služby'
			FOR XML PATH(''), TYPE
		).value('.', 'NVARCHAR(MAX)'), 1, 2, ''
	) AS Polozky

	FROM StwPh_27458920_2022.dbo.FA 

	LEFT OUTER JOIN (
			SELECT
				pol.RefAg, 
				SUM(pol.Mnozstvi) AS kusu,
				ISNULL(SUM(pol.Mnozstvi * StwPh_27458920_2022.dbo.SKz.Hmotnost), 0) AS hmotnost 
			FROM StwPh_27458920_2022.dbo.FApol AS pol 
			LEFT OUTER JOIN StwPh_27458920_2022.dbo.SKz ON pol.RefSKz = StwPh_27458920_2022.dbo.SKz.ID 
			WHERE pol.VPrSklad IS NOT NULL AND pol.VPrSklad <> 'Služby'
			GROUP BY pol.RefAg
		) AS PolDetail ON StwPh_27458920_2022.dbo.FA.ID = PolDetail.RefAg

  WHERE FA.RefDopravci IN (6, 20)
    AND FA.RelTpFak = 1
    AND FA.VPrDopravaStav IS NULL
    AND FA.DatCreate > DATEADD(mm, -1, GETDATE())
	AND FA.Cislo = '230103714'
)

SELECT 
  idFa, 
  cisloFa, 
  DatVytvor,
  CisloObj, 
  CASE WHEN firm IS NULL 
  AND [name] IS NOT NULL THEN [name] ELSE firm END AS firm, 
  [name], 
  tel, 
  street, 
  zipCode, 
  city, 
  depo, 
  dateFrom, 
  dateBy, 
  timeFrom, 
  timeBy,
  note1, 
  note2, 
  Vratka, 
  Castka,
  Dobirka, 
  Kusu,
  Hmotnost,
  Polozky

FROM raw AS raw_1

-- ORDER BY cisloFa;