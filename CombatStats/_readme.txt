=== Add New Data to DB ===

1. Find CampaignId (SELECT * FROM Campaigns;)
	o Strahd is 50
	o Evarnus is 53
	o Cheese Chronicles is 56

2. Get the dates of the sheets that are already in the db (SELECT DISTINCT encounter_date FROM Encounters WHERE campaign_id = 50 ORDER BY encounter_date DESC;)

3. Delete all CSVs in ~\DownloadCsv\csvs

4. Open the google sheet that contains the relevant combat data. Download each missing sheet as a CSV to ~\DownloadCsv\csvs.

5. Name files <index>_<CampaignName>_<SheetName>.csv (01_Curse of Strahd_2021-09-19.csv)

6. Execute CombatStats.py <CampaignId>

=== Generate Report ===

1. Execute CreateStatsHtml.py <CampaignId>


