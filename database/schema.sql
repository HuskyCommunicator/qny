-- AI角色扮演聊天应用数据库结构
-- 数据库: qny_db

-- 删除已存在的表（如果需要重新创建）
DROP TABLE IF EXISTS `user_agents`;
DROP TABLE IF EXISTS `chat_messages`;
DROP TABLE IF EXISTS `chat_sessions`;
DROP TABLE IF EXISTS `agents`;
DROP TABLE IF EXISTS `users`;

-- 用户表
CREATE TABLE `users` (
    `id` int NOT NULL AUTO_INCREMENT,
    `username` varchar(50) NOT NULL,
    `email` varchar(100) DEFAULT NULL,
    `hashed_password` varchar(255) NOT NULL,
    `is_active` tinyint(1) DEFAULT '1',
    `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
    `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `username` (`username`),
    UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- AI角色表
CREATE TABLE `agents` (
    `id` int NOT NULL AUTO_INCREMENT,
    `name` varchar(100) NOT NULL,
    `description` text,
    `system_prompt` text NOT NULL,
    `avatar_url` varchar(255) DEFAULT NULL,
    `is_public` tinyint(1) DEFAULT '1',
    `category` varchar(50) DEFAULT 'general',
    `creator_id` int DEFAULT NULL,
    `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
    `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `creator_id` (`creator_id`),
    KEY `category` (`category`),
    KEY `is_public` (`is_public`),
    CONSTRAINT `agents_ibfk_1` FOREIGN KEY (`creator_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 聊天会话表
CREATE TABLE `chat_sessions` (
    `id` int NOT NULL AUTO_INCREMENT,
    `session_id` varchar(100) NOT NULL,
    `user_id` int NOT NULL,
    `agent_id` int NOT NULL,
    `title` varchar(200) DEFAULT NULL,
    `is_active` tinyint(1) DEFAULT '1',
    `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
    `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `session_id` (`session_id`),
    KEY `user_id` (`user_id`),
    KEY `agent_id` (`agent_id`),
    KEY `is_active` (`is_active`),
    CONSTRAINT `chat_sessions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    CONSTRAINT `chat_sessions_ibfk_2` FOREIGN KEY (`agent_id`) REFERENCES `agents` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 聊天消息表
CREATE TABLE `chat_messages` (
    `id` int NOT NULL AUTO_INCREMENT,
    `session_id` int NOT NULL,
    `user_id` int NOT NULL,
    `agent_id` int NOT NULL,
    `user_message` text NOT NULL,
    `assistant_message` text NOT NULL,
    `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `session_id` (`session_id`),
    KEY `user_id` (`user_id`),
    KEY `agent_id` (`agent_id`),
    KEY `created_at` (`created_at`),
    CONSTRAINT `chat_messages_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `chat_sessions` (`id`) ON DELETE CASCADE,
    CONSTRAINT `chat_messages_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    CONSTRAINT `chat_messages_ibfk_3` FOREIGN KEY (`agent_id`) REFERENCES `agents` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 用户和AI角色的多对多关系表
CREATE TABLE `user_agents` (
    `user_id` int NOT NULL,
    `agent_id` int NOT NULL,
    `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`user_id`, `agent_id`),
    KEY `agent_id` (`agent_id`),
    CONSTRAINT `user_agents_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    CONSTRAINT `user_agents_ibfk_2` FOREIGN KEY (`agent_id`) REFERENCES `agents` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;