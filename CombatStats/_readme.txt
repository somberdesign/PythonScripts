=== Add New Data to DB ===

1. Find CampaignId (SELECT * FROM Campaigns;)

2. Get the dates of the sheets that are already in the db (SELECT DISTINCT encounter_date FROM Encounters WHERE campaign_id = 50 ORDER BY encounter_date DESC;)

3. Delete all CSVs in ~\DownloadCsv\csvs

4. Open the google sheet that contains the relevant combat data. Download each missing sheet as a CSV to ~\DownloadCsv\csvs.

5. Name files <index>_<CampaignName>_<SheetName>.csv

6. Execute CombatStats.py <CampaignId>

=== Generate Report ===

1. Execute CreateStatsHtml.py <CampaignId>


