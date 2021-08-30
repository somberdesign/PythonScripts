-- phpMyAdmin SQL Dump
-- version 4.8.5
-- https://www.phpmyadmin.net/
--
-- Host: mysql.robiii.dreamhosters.com
-- Generation Time: Aug 30, 2021 at 07:44 AM
-- Server version: 5.7.28-log
-- PHP Version: 7.1.22

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `combatstats`
--

DELIMITER $$
--
-- Procedures
--
CREATE DEFINER=`marytm`@`208.113.128.0/255.255.128.0` PROCEDURE `actions_get_byencounterid` (IN `p_encounter_id` INTEGER)  BEGIN
	SELECT 
    	encounter_id, 
        round, 
        order_in_round, 
        primary_name, 
        target_name, 
        action, 
        result, 
        hit_points, 
        notes
    FROM Actions
    WHERE encounter_id = p_encounter_id
    ORDER BY round, order_in_round;
    
END$$

CREATE DEFINER=`marytm`@`208.113.128.0/255.255.128.0` PROCEDURE `action_insert` (IN `p_action_text` TEXT, IN `p_encounter_id` INT, IN `p_hit_points` INT, IN `p_notes` TEXT, IN `p_order_in_round` INT, IN `p_primary_name` TEXT, IN `p_result` TEXT, IN `p_round` INT, IN `p_target_name` TEXT)  NO SQL
BEGIN

	INSERT INTO Actions(action_text, encounter_id, hit_points, notes, order_in_round, primary_name, result, round, target_name, created_date)
    VALUES (p_action_text, p_encounter_id, p_hit_points, p_notes, p_order_in_round, p_primary_name, p_result, p_round, p_target_name, NOW());

	COMMIT;

    SELECT LAST_INSERT_ID();

END$$

CREATE DEFINER=`marytm`@`208.113.128.0/255.255.128.0` PROCEDURE `action_stats_byCampaignId` (IN `p_campaignId` INT)  NO SQL
BEGIN

SELECT campaign_name
FROM Campaigns
WHERE id = p_campaignId
;

SELECT e.encounter_date, e.encounter_name, a.primary_name, SUM(a.hit_points) "Damage Inflicted"
FROM 
	Actions a
    INNER JOIN Encounters e ON a.encounter_id = e.id
WHERE e.campaign_id = p_campaignId
GROUP BY e.encounter_date, e.encounter_name, a.primary_name
ORDER BY e.encounter_date, e.encounter_name, SUM(a.hit_points) DESC, a.primary_name
;

SELECT e.encounter_date, e.encounter_name, a.target_name, SUM(a.hit_points) "Damage Taken"
FROM 
	Actions a
    INNER JOIN Encounters e ON a.encounter_id = e.id
WHERE e.campaign_id = p_campaignId
GROUP BY e.encounter_date, e.encounter_name, a.target_name
ORDER BY e.encounter_date, e.encounter_name, SUM(a.hit_points) DESC, a.target_name
;

SELECT e.encounter_date, e.encounter_name, a.action_text, SUM(a.hit_points) "hit_points"
FROM 
	Actions a
    INNER JOIN Encounters e ON a.encounter_id = e.id
WHERE e.campaign_id = p_campaignId
GROUP BY e.encounter_date, e.encounter_name, a.action_text
ORDER BY e.encounter_date, e.encounter_name, SUM(a.hit_points) DESC, a.action_text
;

END$$

CREATE DEFINER=`marytm`@`208.113.128.0/255.255.128.0` PROCEDURE `action_stats_byCampaignId_EncounterGroup` (IN `p_campaignId` INT)  NO SQL
BEGIN

SELECT campaign_name
FROM Campaigns
WHERE id = p_campaignId
;

SELECT e.encounter_date, e.encounter_name, a.primary_name, SUM(a.hit_points) "Damage Inflicted"
FROM 
	Actions a
    INNER JOIN Encounters e ON a.encounter_id = e.id
WHERE e.campaign_id = p_campaignId
GROUP BY e.encounter_date, e.encounter_name, a.primary_name
ORDER BY e.encounter_date, e.encounter_name, SUM(a.hit_points) DESC, a.primary_name
;

/*
SELECT e.encounter_date, e.encounter_name, a.target_name, SUM(a.hit_points) "Damage Taken"
FROM 
	Actions a
    INNER JOIN Encounters e ON a.encounter_id = e.id
WHERE e.campaign_id = p_campaignId
GROUP BY e.encounter_date, e.encounter_name, a.target_name
ORDER BY e.encounter_date, e.encounter_name, SUM(a.hit_points) DESC, a.target_name
;

SELECT e.encounter_date, e.encounter_name, a.action_text, SUM(a.hit_points) "hit_points"
FROM 
	Actions a
    INNER JOIN Encounters e ON a.encounter_id = e.id
WHERE e.campaign_id = p_campaignId
GROUP BY e.encounter_date, e.encounter_name, a.action_text
ORDER BY e.encounter_date, e.encounter_name, SUM(a.hit_points) DESC, a.action_text
;
*/

END$$

CREATE DEFINER=`marytm`@`208.113.128.0/255.255.128.0` PROCEDURE `action_stats_by_date` (IN `p_encounter_date` DATE)  NO SQL
BEGIN

SELECT e.encounter_date, e.encounter_name, a.primary_name, SUM(a.hit_points) "Damage Inflicted"
FROM 
	Actions a
    INNER JOIN Encounters e ON a.encounter_id = e.id
WHERE e.encounter_date = STR_TO_DATE(p_encounter_date, '%Y-%m-%d')
GROUP BY e.encounter_date, e.encounter_name, a.primary_name
ORDER BY e.encounter_date, e.encounter_name, SUM(a.hit_points) DESC, a.primary_name
;

SELECT e.encounter_date, e.encounter_name, a.target_name, SUM(a.hit_points) "Damage Taken"
FROM 
	Actions a
    INNER JOIN Encounters e ON a.encounter_id = e.id
WHERE e.encounter_date = STR_TO_DATE(p_encounter_date, '%Y-%m-%d')
GROUP BY e.encounter_date, e.encounter_name, a.target_name
ORDER BY e.encounter_date, e.encounter_name, SUM(a.hit_points) DESC, a.target_name
;

SELECT e.encounter_date, e.encounter_name, a.action_text, SUM(a.hit_points) "hit_points"
FROM 
	Actions a
    INNER JOIN Encounters e ON a.encounter_id = e.id
WHERE e.encounter_date = STR_TO_DATE(p_encounter_date, '%Y-%m-%d')
GROUP BY e.encounter_date, e.encounter_name, a.action_text
ORDER BY e.encounter_date, e.encounter_name, SUM(a.hit_points) DESC, a.action_text
;

END$$

CREATE DEFINER=`marytm`@`208.113.128.0/255.255.128.0` PROCEDURE `campaigns_get` ()  BEGIN

	SELECT id, campaign_name, created_date
    FROM Campaigns
    WHERE is_inactive IS NULL or is_inactive = 0
	;
END$$

CREATE DEFINER=`marytm`@`208.113.128.0/255.255.128.0` PROCEDURE `campaign_get_byname` (IN `p_campaign_name` VARCHAR(255))  BEGIN
	
	SELECT id, campaign_name, created_date
	FROM Campaigns
	WHERE campaign_name = p_campaign_name; 
        
END$$

CREATE DEFINER=`marytm`@`208.113.128.0/255.255.128.0` PROCEDURE `campaign_insert` (IN `p_campaign_name` VARCHAR(255))  BEGIN
	
	INSERT INTO Campaigns (campaign_name, created_date)
    VALUES (p_campaign_name, NOW());
    
    SELECT LAST_INSERT_ID();
    
    COMMIT;
        
END$$

CREATE DEFINER=`marytm`@`208.113.128.0/255.255.128.0` PROCEDURE `delete_actionsEncountersCampaigns_byCampaignId` (IN `p_campaignId` INT)  NO SQL
BEGIN

DELETE FROM Actions
WHERE encounter_id IN (SELECT id FROM Encounters WHERE campaign_id = p_campaignId);

DELETE FROM Encounters WHERE campaign_id = p_campaignId;

DELETE FROM Campaigns WHERE id = p_campaignId;

END$$

CREATE DEFINER=`marytm`@`208.113.128.0/255.255.128.0` PROCEDURE `encounters_get_bycampaignid` (IN `p_campaign_id` INT)  BEGIN

	SELECT id, campaign_id, created_date, encounter_name, encounter_date
    FROM Encounters
    WHERE 1=1
    	AND (is_inactive = 0 OR is_inactive IS NULL)
        AND campaign_id = p_campaign_id
    ;

END$$

CREATE DEFINER=`marytm`@`208.113.128.0/255.255.128.0` PROCEDURE `encounter_insert` (IN `p_campaign_id` INT, IN `p_encounter_name` VARCHAR(1000), IN `p_encounter_date` DATE)  BEGIN
	INSERT INTO Encounters (campaign_id, encounter_name, encounter_date, created_date)
    VALUES (p_campaign_id, p_encounter_name, str_to_date(p_encounter_date, '%Y-%m-%d'), NOW());
    
    COMMIT;
    
    SELECT LAST_INSERT_ID();
    
END$$

CREATE DEFINER=`marytm`@`208.113.128.0/255.255.128.0` PROCEDURE `player_stats_byCampaignId` (IN `p_campaignID` INT)  NO SQL
BEGIN

SELECT campaign_name, source_location
FROM Campaigns
WHERE id = p_campaignID
;

SELECT 
	e.encounter_date, 
    e.encounter_name, 
    a.primary_name,
    IFNULL((SELECT COUNT(*) FROM Actions a0 INNER JOIN Encounters e0 ON a0.encounter_id = e0.id WHERE a0.primary_name = a.primary_name AND a0.encounter_id = e.id AND a0.result IN ('Hit', 'Miss', 'Failed save', 'Successful save')), 0) "attacks_made",
    ( SELECT
        (SELECT COUNT(*) FROM Actions a0 INNER JOIN Encounters e0 ON a0.encounter_id = e0.id WHERE a0.primary_name = a.primary_name AND a0.encounter_id = e.id AND a0.result IN ('Hit', 'Failed save', 'Successful save'))
        / (SELECT COUNT(*) FROM Actions a0 INNER JOIN Encounters e0 ON a0.encounter_id = e0.id WHERE a0.primary_name = a.primary_name AND a0.encounter_id = e.id AND a0.result IN ('Hit', 'Miss', 'Failed save', 'Successful save'))
    ) "hit_ratio", 
    IFNULL((SELECT SUM(hit_points) FROM Actions a0 WHERE a0.primary_name = a.primary_name AND a0.encounter_id = e.id AND a0.result IN ('Hit', 'Failed save', 'Successful save')), 0) "damage_inflicted",
    IFNULL((SELECT COUNT(*) FROM Actions a0 INNER JOIN Encounters e0 ON a0.encounter_id = e0.id WHERE a0.target_name = a.primary_name AND a0.encounter_id = e.id AND ( a0.result IN ('Hit', 'Miss') OR a0.result LIKE '% save') ), 0) "attacks_defended", /* this is "Attacks Received" */
    ( SELECT
        (SELECT COUNT(*) FROM Actions a0 INNER JOIN Encounters e0 ON a0.encounter_id = e0.id WHERE a0.target_name = a.primary_name AND a0.encounter_id = e.id AND a0.result = 'Miss')
        / (SELECT COUNT(*) FROM Actions a0 INNER JOIN Encounters e0 ON a0.encounter_id = e0.id WHERE a0.target_name = a.primary_name AND a0.encounter_id = e.id AND a0.result IN ('Hit', 'Miss'))
    ) "defense_ratio",
    IFNULL((SELECT SUM(hit_points) FROM Actions a0 WHERE a0.target_name = a.primary_name AND a0.encounter_id = e.id AND a0.result IN ('Hit', 'Failed save', 'Successful save')), 0) "damage_received",
    IFNULL((SELECT SUM(hit_points) FROM Actions a0 WHERE a0.primary_name = a.primary_name AND a0.encounter_id = e.id AND a0.result = 'Heal'), 0) "healing_provided",
    IFNULL((SELECT SUM(hit_points) FROM Actions a0 WHERE a0.target_name = a.primary_name AND a0.encounter_id = e.id AND a0.result = 'Heal'), 0) "healing_received",
    IFNULL((SELECT COUNT(*) FROM Actions a0 WHERE a0.primary_name = a.primary_name AND a0.encounter_id = e.id AND a0.result = 'Buff'), 0) "buffs_provided",
    IFNULL((SELECT COUNT(*) FROM Actions a0 WHERE a0.target_name = a.primary_name AND a0.encounter_id = e.id AND a0.result = 'Buff'), 0) "buffs_received"

FROM 
	Actions a
    INNER JOIN Encounters e ON a.encounter_id = e.id
WHERE e.campaign_id = p_campaignId
GROUP BY e.encounter_date, e.encounter_name, a.primary_name
ORDER BY e.encounter_date DESC, e.encounter_name, SUM(a.hit_points) DESC, a.primary_name
;

END$$

CREATE DEFINER=`marytm`@`208.113.128.0/255.255.128.0` PROCEDURE `player_stats_byCampaignId_20210705` (IN `p_campaignId` INT)  NO SQL
BEGIN

SELECT campaign_name, source_location
FROM Campaigns
WHERE id = p_campaignID
;

SELECT 
	e.encounter_date, 
    e.encounter_name, 
    a.primary_name,
    IFNULL((SELECT COUNT(*) FROM Actions a0 INNER JOIN Encounters e0 ON a0.encounter_id = e0.id WHERE a0.primary_name = a.primary_name AND a0.encounter_id = e.id AND a0.result IN ('Hit', 'Miss', 'Failed save', 'Successful save')), 0) "attacks_made",
    ( SELECT
        (SELECT COUNT(*) FROM Actions a0 INNER JOIN Encounters e0 ON a0.encounter_id = e0.id WHERE a0.primary_name = a.primary_name AND a0.encounter_id = e.id AND a0.result IN ('Hit', 'Failed save', 'Successful save'))
        / (SELECT COUNT(*) FROM Actions a0 INNER JOIN Encounters e0 ON a0.encounter_id = e0.id WHERE a0.primary_name = a.primary_name AND a0.encounter_id = e.id AND a0.result IN ('Hit', 'Miss', 'Failed save', 'Successful save'))
    ) "hit_ratio", 
    IFNULL((SELECT SUM(hit_points) FROM Actions a0 WHERE a0.primary_name = a.primary_name AND a0.encounter_id = e.id AND a0.result IN ('Hit', 'Failed save', 'Successful save')), 0) "damage_inflicted",
    IFNULL((SELECT COUNT(*) FROM Actions a0 INNER JOIN Encounters e0 ON a0.encounter_id = e0.id WHERE a0.target_name = a.primary_name AND a0.encounter_id = e.id), 0) "attacks_defended",
    ( SELECT
        (SELECT COUNT(*) FROM Actions a0 INNER JOIN Encounters e0 ON a0.encounter_id = e0.id WHERE a0.target_name = a.primary_name AND a0.encounter_id = e.id AND a0.result = 'Miss')
        / (SELECT COUNT(*) FROM Actions a0 INNER JOIN Encounters e0 ON a0.encounter_id = e0.id WHERE a0.target_name = a.primary_name AND a0.encounter_id = e.id AND a0.result IN ('Hit', 'Miss'))
    ) "defense_ratio",
    IFNULL((SELECT SUM(hit_points) FROM Actions a0 WHERE a0.target_name = a.primary_name AND a0.encounter_id = e.id AND a0.result IN ('Hit', 'Failed save', 'Successful save')), 0) "damage_received",
    IFNULL((SELECT SUM(hit_points) FROM Actions a0 WHERE a0.primary_name = a.primary_name AND a0.encounter_id = e.id AND a0.result = 'Heal'), 0) "healing_provided",
    IFNULL((SELECT SUM(hit_points) FROM Actions a0 WHERE a0.target_name = a.primary_name AND a0.encounter_id = e.id AND a0.result = 'Heal'), 0) "healing_received",
    IFNULL((SELECT COUNT(*) FROM Actions a0 WHERE a0.primary_name = a.primary_name AND a0.encounter_id = e.id AND a0.result = 'Buff'), 0) "buffs_provided",
    IFNULL((SELECT COUNT(*) FROM Actions a0 WHERE a0.target_name = a.primary_name AND a0.encounter_id = e.id AND a0.result = 'Buff'), 0) "buffs_received"

FROM 
	Actions a
    INNER JOIN Encounters e ON a.encounter_id = e.id
WHERE e.campaign_id = p_campaignId
GROUP BY e.encounter_date, e.encounter_name, a.primary_name
ORDER BY e.encounter_date DESC, e.encounter_name, SUM(a.hit_points) DESC, a.primary_name
;

END$$

CREATE DEFINER=`marytm`@`208.113.128.0/255.255.128.0` PROCEDURE `player_stats_cumulative_byCampaignId` (IN `p_campaignId` INT)  NO SQL
BEGIN

SELECT campaign_name, source_location
FROM Campaigns
WHERE id = p_campaignID
;

SELECT 
    a.primary_name,
    IFNULL((SELECT COUNT(*) FROM Actions a0 INNER JOIN Encounters e0 ON a0.encounter_id = e0.id WHERE a0.primary_name = a.primary_name AND a0.encounter_id = e.id AND a0.result IN ('Hit', 'Miss', 'Failed save', 'Successful save')), 0) "attacks_made",
    ( SELECT
        (SELECT COUNT(*) FROM Actions a0 INNER JOIN Encounters e0 ON a0.encounter_id = e0.id WHERE a0.primary_name = a.primary_name AND a0.encounter_id = e.id AND a0.result IN ('Hit', 'Failed save', 'Successful save'))
        / (SELECT COUNT(*) FROM Actions a0 INNER JOIN Encounters e0 ON a0.encounter_id = e0.id WHERE a0.primary_name = a.primary_name AND a0.encounter_id = e.id AND a0.result IN ('Hit', 'Miss', 'Failed save', 'Successful save'))
    ) "hit_ratio", 
    IFNULL((SELECT SUM(hit_points) FROM Actions a0 WHERE a0.primary_name = a.primary_name AND a0.encounter_id = e.id AND a0.result IN ('Hit', 'Failed save', 'Successful save')), 0) "damage_inflicted",
    IFNULL((SELECT COUNT(*) FROM Actions a0 INNER JOIN Encounters e0 ON a0.encounter_id = e0.id WHERE a0.target_name = a.primary_name AND a0.encounter_id = e.id), 0) "attacks_defended",
    ( SELECT
        (SELECT COUNT(*) FROM Actions a0 INNER JOIN Encounters e0 ON a0.encounter_id = e0.id WHERE a0.target_name = a.primary_name AND a0.encounter_id = e.id AND a0.result = 'Miss')
        / (SELECT COUNT(*) FROM Actions a0 INNER JOIN Encounters e0 ON a0.encounter_id = e0.id WHERE a0.target_name = a.primary_name AND a0.encounter_id = e.id AND a0.result IN ('Hit', 'Miss'))
    ) "defense_ratio",
    IFNULL((SELECT SUM(hit_points) FROM Actions a0 WHERE a0.target_name = a.primary_name AND a0.encounter_id = e.id AND a0.result IN ('Hit', 'Failed save', 'Successful save')), 0) "damage_received",
    IFNULL((SELECT SUM(hit_points) FROM Actions a0 WHERE a0.primary_name = a.primary_name AND a0.encounter_id = e.id AND a0.result = 'Heal'), 0) "healing_provided",
    IFNULL((SELECT SUM(hit_points) FROM Actions a0 WHERE a0.target_name = a.primary_name AND a0.encounter_id = e.id AND a0.result = 'Heal'), 0) "healing_received",
    IFNULL((SELECT COUNT(*) FROM Actions a0 WHERE a0.primary_name = a.primary_name AND a0.encounter_id = e.id AND a0.result = 'Buff'), 0) "buffs_provided",
    IFNULL((SELECT COUNT(*) FROM Actions a0 WHERE a0.target_name = a.primary_name AND a0.encounter_id = e.id AND a0.result = 'Buff'), 0) "buffs_received"

FROM 
	Actions a
    INNER JOIN Encounters e ON a.encounter_id = e.id
WHERE 
	e.campaign_id = p_campaignId
    /*AND a.primary_name IN (
        SELECT ec.primary_name
        FROM 
            ( -- include primary_names that appear in more than 50% of encounters - the player characters
                SELECT COUNT(DISTINCT a.encounter_id) encounter_count, a.primary_name 
                FROM Actions a
                    INNER JOIN Encounters e ON a.encounter_id = e.id
                    INNER JOIN Campaigns c ON e.campaign_id = c.id
                WHERE 
                    c.id = 50
                GROUP BY a.primary_name
            ) ec
        WHERE ec.encounter_count / (SELECT COUNT(DISTINCT id) FROM Encounters WHERE campaign_id = 50) > 0.5
    )*/
GROUP BY a.primary_name
ORDER BY SUM(a.hit_points) DESC, a.primary_name
;

END$$

DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `Actions`
--

CREATE TABLE `Actions` (
  `id` bigint(20) NOT NULL,
  `encounter_id` int(11) NOT NULL,
  `round` smallint(6) NOT NULL,
  `order_in_round` smallint(6) NOT NULL,
  `primary_name` text NOT NULL,
  `target_name` text,
  `action_text` text,
  `result` text,
  `hit_points` smallint(6) DEFAULT NULL,
  `notes` text,
  `is_inactive` tinyint(1) DEFAULT NULL,
  `created_date` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Stand-in structure for view `all_encounters`
-- (See below for the actual view)
--
CREATE TABLE `all_encounters` (
`campaign_id` int(11)
,`campaign_name` text
,`encounter_id` int(11)
,`encounter_name` varchar(100)
,`encounter_date` date
);

-- --------------------------------------------------------

--
-- Table structure for table `Campaigns`
--

CREATE TABLE `Campaigns` (
  `id` int(11) NOT NULL,
  `campaign_name` text NOT NULL,
  `created_date` datetime NOT NULL,
  `source_location` text,
  `is_inactive` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `Encounters`
--

CREATE TABLE `Encounters` (
  `id` int(11) NOT NULL,
  `campaign_id` int(11) NOT NULL,
  `encounter_name` varchar(100) NOT NULL,
  `encounter_date` date NOT NULL,
  `created_date` datetime NOT NULL,
  `is_inactive` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Structure for view `all_encounters`
--
DROP TABLE IF EXISTS `all_encounters`;

CREATE ALGORITHM=UNDEFINED DEFINER=`marytm`@`208.113.128.0/255.255.128.0` SQL SECURITY DEFINER VIEW `all_encounters`  AS  select `c`.`id` AS `campaign_id`,`c`.`campaign_name` AS `campaign_name`,`e`.`id` AS `encounter_id`,`e`.`encounter_name` AS `encounter_name`,`e`.`encounter_date` AS `encounter_date` from (`Campaigns` `c` join `Encounters` `e` on((`c`.`id` = `e`.`campaign_id`))) order by `c`.`created_date` desc,`e`.`created_date` desc ;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `Actions`
--
ALTER TABLE `Actions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_encounter_id` (`encounter_id`);

--
-- Indexes for table `Campaigns`
--
ALTER TABLE `Campaigns`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `Encounters`
--
ALTER TABLE `Encounters`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `encounter_name` (`encounter_name`,`encounter_date`,`campaign_id`) USING BTREE,
  ADD KEY `fk_campaign_id` (`campaign_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `Actions`
--
ALTER TABLE `Actions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `Campaigns`
--
ALTER TABLE `Campaigns`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `Encounters`
--
ALTER TABLE `Encounters`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `Actions`
--
ALTER TABLE `Actions`
  ADD CONSTRAINT `fk_encounter_id` FOREIGN KEY (`encounter_id`) REFERENCES `Encounters` (`id`);

--
-- Constraints for table `Encounters`
--
ALTER TABLE `Encounters`
  ADD CONSTRAINT `fk_campaign_id` FOREIGN KEY (`campaign_id`) REFERENCES `Campaigns` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
