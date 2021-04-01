-- phpMyAdmin SQL Dump
-- version 4.8.4
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Feb 16, 2019 at 06:24 AM
-- Server version: 10.1.37-MariaDB
-- PHP Version: 7.3.0

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `agrogoti`
--

-- --------------------------------------------------------

--
-- Table structure for table `achievements`
--

CREATE TABLE `achievements` (
  `id` int(10) UNSIGNED NOT NULL,
  `activity_id` int(11) NOT NULL,
  `achievement_year` varchar(191) COLLATE utf8mb4_unicode_ci NOT NULL,
  `achievement_quarter` int(11) NOT NULL,
  `achievement_event_number` int(11) NOT NULL DEFAULT '1',
  `achievement_male_participant_number` int(11) NOT NULL DEFAULT '0',
  `achievement_female_participant_number` int(11) NOT NULL DEFAULT '0',
  `achievement_month` varchar(191) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `achievement_date` varchar(191) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `achievement_place` varchar(191) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `event_summary` text COLLATE utf8mb4_unicode_ci,
  `immediate_outcome` text COLLATE utf8mb4_unicode_ci,
  `learning` text COLLATE utf8mb4_unicode_ci,
  `challenge` text COLLATE utf8mb4_unicode_ci,
  `approved` tinyint(1) NOT NULL DEFAULT '0',
  `submitted_by_name` varchar(191) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `submitted_by_id` int(11) DEFAULT NULL,
  `approved_by_name` varchar(191) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `approved_by_id` int(11) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `achievements`
--

INSERT INTO `achievements` (`id`, `activity_id`, `achievement_year`, `achievement_quarter`, `achievement_event_number`, `achievement_male_participant_number`, `achievement_female_participant_number`, `achievement_month`, `achievement_date`, `achievement_place`, `event_summary`, `immediate_outcome`, `learning`, `challenge`, `approved`, `submitted_by_name`, `submitted_by_id`, `approved_by_name`, `approved_by_id`, `created_at`, `updated_at`) VALUES
(2, 1, '2019', 1, 1, 7, 6, 'January', '2019-01-25', '1234', 'abJKDSFGKMFHG.', 'dsfbsdfskdnfksdnkjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj', 'hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh', 'ccccccccccccccccccccccccccccccccccccccccccccccc', 1, 'Sourav Adhikary', 4, 'admin', 2, '2019-01-25 11:57:24', '2019-01-29 10:18:30'),
(3, 1, '2019', 3, 1, 18, 5555, 'Setember', '2019-01-26', 'gggggg', NULL, 'hhhhhhhhhhhhhhhhhh', 'hhhhhhhhhhhhhhhhhhh', 'hhhhhhhhhhhhhh', 1, 'ProjectAdmin', 3, NULL, NULL, '2019-01-26 09:56:21', '2019-01-26 09:56:52'),
(4, 2, '2019', 1, 1, 6, 7, 'January', '2019-01-29', 'aaaaaaaaa', NULL, NULL, NULL, NULL, 0, 'admin', 2, NULL, NULL, '2019-01-29 10:11:21', '2019-01-29 10:11:21'),
(5, 2, '2019', 1, 1, 0, 0, 'January', '2019-01-29', NULL, NULL, NULL, NULL, NULL, 0, 'admin', 2, NULL, NULL, '2019-01-29 10:15:30', '2019-01-29 10:15:30');

-- --------------------------------------------------------

--
-- Table structure for table `activities`
--

CREATE TABLE `activities` (
  `id` int(10) UNSIGNED NOT NULL,
  `project_id` int(11) NOT NULL,
  `activity_name` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `activities`
--

INSERT INTO `activities` (`id`, `project_id`, `activity_name`, `created_at`, `updated_at`) VALUES
(1, 1, 'Peer Leader Training', '2019-01-11 00:09:55', '2019-01-11 00:09:55'),
(2, 1, 'Peer Leader Training 2', '2019-01-25 12:36:13', '2019-01-25 12:36:13'),
(3, 1, 'Peer Leader Training 2', '2019-01-25 12:36:52', '2019-01-25 12:36:52');

-- --------------------------------------------------------

--
-- Table structure for table `migrations`
--

CREATE TABLE `migrations` (
  `id` int(10) UNSIGNED NOT NULL,
  `migration` varchar(191) COLLATE utf8mb4_unicode_ci NOT NULL,
  `batch` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `migrations`
--

INSERT INTO `migrations` (`id`, `migration`, `batch`) VALUES
(1, '2014_10_12_000000_create_users_table', 1),
(2, '2014_10_12_100000_create_password_resets_table', 1),
(3, '2018_08_08_100000_create_telescope_entries_table', 1),
(4, '2018_12_01_082105_create_staff_profiles_table', 1),
(5, '2018_12_01_083621_create_staff__leave__statuses_table', 1),
(6, '2018_12_09_125247_create_projects_table', 1),
(7, '2018_12_09_125742_create_activities_table', 1),
(8, '2018_12_09_130020_create_targets_table', 1),
(9, '2018_12_09_130111_create_achievements_table', 1),
(10, '2018_12_20_154340_create_user_profiles_table', 1),
(11, '2018_12_30_135420_create_notifications_table', 1);

-- --------------------------------------------------------

--
-- Table structure for table `notifications`
--

CREATE TABLE `notifications` (
  `id` int(10) UNSIGNED NOT NULL,
  `user_id` int(11) NOT NULL,
  `link` varchar(191) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `text` varchar(191) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `viewed` tinyint(1) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `notifications`
--

INSERT INTO `notifications` (`id`, `user_id`, `link`, `text`, `created_at`, `updated_at`, `viewed`) VALUES
(1, 3, 'http://agrogoti.joy/activity/1/achievement/2', 'Sourav Adhikary submitted new Achievement', '2019-01-25 11:57:24', '2019-01-25 13:18:57', 1),
(2, 4, 'http://agrogoti.joy/activity/1/achievement/2', 'Sourav Adhikary submitted new Achievement', '2019-01-25 11:57:24', '2019-01-26 00:53:43', 1),
(3, 3, 'http://agrogoti.joy/project/1/activity/4', 'New Activity Peer Leader Training 2 has created', '2019-01-25 12:37:18', '2019-01-25 12:37:18', 0),
(4, 4, 'http://agrogoti.joy/project/1/activity/4', 'New Activity Peer Leader Training 2 has created', '2019-01-25 12:37:18', '2019-01-25 12:37:18', 0),
(5, 3, 'http://agrogoti.joy/project/1/activity/4', 'New Target( Year:2019 Quarter:2) has Created', '2019-01-25 12:43:21', '2019-01-25 13:18:40', 1),
(6, 4, 'http://agrogoti.joy/project/1/activity/4', 'New Target( Year:2019 Quarter:2) has Created', '2019-01-25 12:43:21', '2019-01-25 12:43:21', 0),
(7, 3, 'http://agrogoti.joy/activity/1/achievement/3', 'ProjectAdmin submitted new Achievement', '2019-01-26 09:56:22', '2019-01-26 09:56:22', 0),
(8, 4, 'http://agrogoti.joy/activity/1/achievement/3', 'ProjectAdmin submitted new Achievement', '2019-01-26 09:56:22', '2019-01-29 08:25:12', 1),
(9, 3, 'http://agrogoti.joy/activity/2/achievement/4', 'admin submitted new Achievement', '2019-01-29 10:11:21', '2019-01-29 10:11:21', 0),
(10, 4, 'http://agrogoti.joy/activity/2/achievement/4', 'admin submitted new Achievement', '2019-01-29 10:11:21', '2019-01-29 10:11:21', 0),
(11, 2, 'http://agrogoti.joy/activity/2/achievement/4', 'admin submitted new Achievement', '2019-01-29 10:11:21', '2019-01-29 10:11:21', 0),
(12, 3, 'http://agrogoti.joy/activity/2/achievement/5', 'admin submitted new Achievement', '2019-01-29 10:15:30', '2019-01-29 10:15:30', 0),
(13, 4, 'http://agrogoti.joy/activity/2/achievement/5', 'admin submitted new Achievement', '2019-01-29 10:15:30', '2019-01-29 10:15:30', 0),
(14, 2, 'http://agrogoti.joy/activity/2/achievement/5', 'admin submitted new Achievement', '2019-01-29 10:15:30', '2019-01-29 10:15:30', 0);

-- --------------------------------------------------------

--
-- Table structure for table `password_resets`
--

CREATE TABLE `password_resets` (
  `email` varchar(191) COLLATE utf8mb4_unicode_ci NOT NULL,
  `token` varchar(191) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `projects`
--

CREATE TABLE `projects` (
  `id` int(10) UNSIGNED NOT NULL,
  `project_name` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `supported_by` varchar(191) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `date_from` varchar(191) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `date_to` varchar(191) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `working_area` varchar(191) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `projects`
--

INSERT INTO `projects` (`id`, `project_name`, `supported_by`, `date_from`, `date_to`, `working_area`, `created_at`, `updated_at`) VALUES
(1, 'Scott', 'Manusher Jonno Foundation', '12-January-2018', '12-january-2020', 'Bangladesh', '2019-01-11 00:09:22', '2019-01-11 00:09:22');

-- --------------------------------------------------------

--
-- Table structure for table `staff_profiles`
--

CREATE TABLE `staff_profiles` (
  `id` int(10) UNSIGNED NOT NULL,
  `name` varchar(191) COLLATE utf8mb4_unicode_ci NOT NULL,
  `designation` varchar(191) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `staff_id` varchar(191) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `nid` varchar(191) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `phone_no` varchar(191) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(191) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `project_name` varchar(191) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `working_place` varchar(191) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `joining_date` varchar(191) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `closing_date` varchar(191) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `special_comment` text COLLATE utf8mb4_unicode_ci,
  `experience` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `staff_profiles`
--

INSERT INTO `staff_profiles` (`id`, `name`, `designation`, `staff_id`, `nid`, `phone_no`, `email`, `project_name`, `working_place`, `joining_date`, `closing_date`, `special_comment`, `experience`, `created_at`, `updated_at`) VALUES
(1, 'Sourav Adhikary', 'Designation', '1213', '13123', '1767892049', 'joy@joy.com', 'SUSTAIN', NULL, '2019-01-24', 'Currently Working', NULL, NULL, '2019-01-24 12:29:52', '2019-01-24 12:32:35');

-- --------------------------------------------------------

--
-- Table structure for table `staff__leave__statuses`
--

CREATE TABLE `staff__leave__statuses` (
  `id` int(10) UNSIGNED NOT NULL,
  `staff_profile_id` int(11) NOT NULL,
  `earned_enjoy` int(11) NOT NULL DEFAULT '0',
  `earned_due` int(11) NOT NULL DEFAULT '0',
  `casual_enjoy` int(11) NOT NULL DEFAULT '0',
  `casual_due` int(11) NOT NULL DEFAULT '0',
  `medical_enjoy` int(11) NOT NULL DEFAULT '0',
  `medical_due` int(11) NOT NULL DEFAULT '0',
  `maternity_enjoy` int(11) NOT NULL DEFAULT '0',
  `maternity_due` int(11) NOT NULL DEFAULT '0',
  `paternity_enjoy` int(11) NOT NULL DEFAULT '0',
  `paternity_due` int(11) NOT NULL DEFAULT '0',
  `study_enjoy` int(11) NOT NULL DEFAULT '0',
  `study_due` int(11) NOT NULL DEFAULT '0',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `staff__leave__statuses`
--

INSERT INTO `staff__leave__statuses` (`id`, `staff_profile_id`, `earned_enjoy`, `earned_due`, `casual_enjoy`, `casual_due`, `medical_enjoy`, `medical_due`, `maternity_enjoy`, `maternity_due`, `paternity_enjoy`, `paternity_due`, `study_enjoy`, `study_due`, `created_at`, `updated_at`) VALUES
(1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '2019-01-24 12:29:52', '2019-01-24 12:29:52');

-- --------------------------------------------------------

--
-- Table structure for table `targets`
--

CREATE TABLE `targets` (
  `id` int(10) UNSIGNED NOT NULL,
  `activity_id` int(11) NOT NULL,
  `target_year` varchar(191) COLLATE utf8mb4_unicode_ci NOT NULL,
  `target_quarter` int(11) NOT NULL,
  `target_event_number` int(11) NOT NULL DEFAULT '0',
  `target_participant_number` int(11) NOT NULL DEFAULT '0',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `targets`
--

INSERT INTO `targets` (`id`, `activity_id`, `target_year`, `target_quarter`, `target_event_number`, `target_participant_number`, `created_at`, `updated_at`) VALUES
(1, 1, '2019', 1, 22, 200, '2019-01-11 00:10:05', '2019-01-11 00:22:05'),
(2, 1, '2020', 2, 200, 3000, '2019-01-11 00:10:36', '2019-01-11 00:10:36'),
(3, 1, '2021', 1, 1, 8, '2019-01-11 00:19:55', '2019-01-11 00:23:09'),
(4, 4, '2019', 1, 1, 35, '2019-01-25 12:41:45', '2019-01-25 12:41:45'),
(5, 4, '2019', 2, 2456, 1345657, '2019-01-25 12:43:21', '2019-01-25 12:43:21');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(10) UNSIGNED NOT NULL,
  `email` varchar(191) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email_verified_at` timestamp NULL DEFAULT NULL,
  `password` varchar(191) COLLATE utf8mb4_unicode_ci NOT NULL,
  `remember_token` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `email`, `email_verified_at`, `password`, `remember_token`, `created_at`, `updated_at`) VALUES
(2, 'SuperAdmin@mail.com', NULL, '$2y$10$N9CvumIbRSRaLQJayoNE7egQMOhlvmzUcVC.domOhA1vENmvC9gwq', 'seXhv8dje7jlw9NlfbiyMCxXdt5pQAjGvRnG90ROZlLQm9rLnpJSvICV5l3b', '2019-01-11 00:06:28', '2019-01-11 00:06:28'),
(3, 'ProjectAdmin@mail.com', NULL, '$2y$10$IjlZ89dEbSO.vuArhbFMmO8zddrx8ka.Oukk0ASDvcFftzFB19BuO', 'U9kDp5cw6qn2Jakzx9wKzh3MMrn5YWa2GsWG0RL7qsuo7a9JOMW9OI1MTUc0', '2019-01-11 00:28:25', '2019-01-11 00:28:25'),
(4, 'ProjectAgent@mail.com', NULL, '$2y$10$UclQj7Ac2ZfLBBH.BYak4OV8waFXertHkWHB/6RRH090YjKWFzcCa', 'ln0J6jUfk3dgjpkzs5IdbVJOJtHhdBkAgYgXKJQhcLrAO45S8WpOasU10yjS', '2019-01-25 11:53:32', '2019-01-25 11:53:32');

-- --------------------------------------------------------

--
-- Table structure for table `user_profiles`
--

CREATE TABLE `user_profiles` (
  `id` int(10) UNSIGNED NOT NULL,
  `user_id` int(11) NOT NULL,
  `name` varchar(191) COLLATE utf8mb4_unicode_ci NOT NULL,
  `designation` varchar(191) COLLATE utf8mb4_unicode_ci NOT NULL,
  `access` varchar(191) COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_id` int(11) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `user_profiles`
--

INSERT INTO `user_profiles` (`id`, `user_id`, `name`, `designation`, `access`, `project_id`, `created_at`, `updated_at`) VALUES
(1, 2, 'admin', 'admin', 'superAdmin', 0, '2019-01-11 00:06:28', '2019-01-11 00:06:28'),
(2, 3, 'ProjectAdmin', 'ProjectAdmin', 'projectAdmin', 1, '2019-01-11 00:28:25', '2019-01-11 00:28:25'),
(3, 4, 'Sourav Adhikary', 'ProjectAgent', 'projectAgent', 1, '2019-01-25 11:53:32', '2019-01-25 11:53:32');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `achievements`
--
ALTER TABLE `achievements`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `activities`
--
ALTER TABLE `activities`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `migrations`
--
ALTER TABLE `migrations`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `notifications`
--
ALTER TABLE `notifications`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `password_resets`
--
ALTER TABLE `password_resets`
  ADD KEY `password_resets_email_index` (`email`);

--
-- Indexes for table `projects`
--
ALTER TABLE `projects`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `staff_profiles`
--
ALTER TABLE `staff_profiles`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `staff__leave__statuses`
--
ALTER TABLE `staff__leave__statuses`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `targets`
--
ALTER TABLE `targets`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `users_email_unique` (`email`);

--
-- Indexes for table `user_profiles`
--
ALTER TABLE `user_profiles`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `achievements`
--
ALTER TABLE `achievements`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `activities`
--
ALTER TABLE `activities`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `migrations`
--
ALTER TABLE `migrations`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `notifications`
--
ALTER TABLE `notifications`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT for table `projects`
--
ALTER TABLE `projects`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `staff_profiles`
--
ALTER TABLE `staff_profiles`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `staff__leave__statuses`
--
ALTER TABLE `staff__leave__statuses`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `targets`
--
ALTER TABLE `targets`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `user_profiles`
--
ALTER TABLE `user_profiles`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
