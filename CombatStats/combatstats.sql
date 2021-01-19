-- phpMyAdmin SQL Dump
-- version 4.8.5
-- https://www.phpmyadmin.net/
--
-- Host: mysql.robiii.dreamhosters.com
-- Generation Time: Jan 19, 2021 at 02:16 PM
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

CREATE DEFINER=`marytm`@`208.113.128.0/255.255.128.0` PROCEDURE `campaign_insert` (IN `p_campaign_name` VARCHAR(255), OUT `p_campaign_id` INT)  BEGIN
	
	INSERT INTO Campaigns (campaign_name, created_date)
    VALUES (p_campaign_name, NOW());
    
    SELECT LAST_INSERT_ID();
    
    COMMIT;
        
END$$

CREATE DEFINER=`marytm`@`208.113.128.0/255.255.128.0` PROCEDURE `encounters_get_bycampaignid` (IN `p_campaign_id` INTEGER)  BEGIN

	SELECT id, campaign_id, date_created, encounter_name
    FROM Encounters
    WHERE is_inactive = 0 OR ISNULL(is_inactive) = 0;

END$$

CREATE DEFINER=`marytm`@`208.113.128.0/255.255.128.0` PROCEDURE `encounter_insert` (IN `p_campaign_id` INT, IN `p_encounter_name` VARCHAR(1000))  BEGIN
	INSERT INTO Encounters (campaign_id, encounter_name, created_date)
    VALUES (p_campaign_id, p_encounter_name, NOW());
    
    COMMIT;
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
  `is_inactive` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `Campaigns`
--

CREATE TABLE `Campaigns` (
  `id` int(11) NOT NULL,
  `campaign_name` text NOT NULL,
  `created_date` datetime NOT NULL,
  `is_inactive` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `Encounters`
--

CREATE TABLE `Encounters` (
  `id` int(11) NOT NULL,
  `campaign_id` int(11) NOT NULL,
  `encounter_name` text NOT NULL,
  `created_date` datetime NOT NULL,
  `is_inactive` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

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
