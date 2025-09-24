/*
SQLyog Ultimate v8.32 
MySQL - 8.0.43 : Database - ai_chat_app
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`ai_chat_app` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `ai_chat_app`;

/*Table structure for table `api_logs` */

DROP TABLE IF EXISTS `api_logs`;

CREATE TABLE `api_logs` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT (uuid()),
  `conversation_id` varchar(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '关联对话ID',
  `api_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'API类型: openai/stt/tts/rag',
  `api_endpoint` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'API端点',
  `request_params` json DEFAULT NULL COMMENT '请求参数',
  `response_status` int DEFAULT NULL COMMENT '响应状态码',
  `tokens_used` int DEFAULT '0' COMMENT '消耗的token数量',
  `response_time_ms` int DEFAULT NULL COMMENT '响应时间(毫秒)',
  `is_success` tinyint(1) DEFAULT '1' COMMENT '是否成功',
  `error_message` text COLLATE utf8mb4_unicode_ci COMMENT '错误信息',
  `request_id` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '请求ID',
  `cost_cents` int DEFAULT '0' COMMENT '成本(分)',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_api_type_time` (`api_type`,`created_at`),
  KEY `idx_api_success` (`is_success`,`created_at`),
  KEY `idx_conversation_id` (`conversation_id`),
  CONSTRAINT `api_logs_ibfk_1` FOREIGN KEY (`conversation_id`) REFERENCES `conversations` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='API调用日志表';

/*Data for the table `api_logs` */

/*Table structure for table `audio_files` */

DROP TABLE IF EXISTS `audio_files`;

CREATE TABLE `audio_files` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT (uuid()),
  `message_id` varchar(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '关联消息ID',
  `audio_type` enum('user_input','ai_response','background') COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '语音类型',
  `text_content` text COLLATE utf8mb4_unicode_ci COMMENT '对应的文本内容',
  `file_url` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '文件存储路径',
  `file_format` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '文件格式',
  `file_size` int DEFAULT NULL COMMENT '文件大小(字节)',
  `duration_seconds` float DEFAULT NULL COMMENT '音频时长(秒)',
  `voice_parameters` json DEFAULT NULL COMMENT '语音参数',
  `service_provider` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '服务提供商',
  `processing_status` enum('processing','completed','failed') COLLATE utf8mb4_unicode_ci DEFAULT 'processing' COMMENT '处理状态',
  `error_message` text COLLATE utf8mb4_unicode_ci COMMENT '错误信息',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_audio_type` (`audio_type`,`processing_status`),
  KEY `idx_audio_created` (`created_at`),
  KEY `idx_message_id` (`message_id`),
  CONSTRAINT `audio_files_ibfk_1` FOREIGN KEY (`message_id`) REFERENCES `messages` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='语音文件管理表';

/*Data for the table `audio_files` */

/*Table structure for table `conversations` */

DROP TABLE IF EXISTS `conversations`;

CREATE TABLE `conversations` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT (uuid()),
  `user_id` varchar(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '关联用户ID',
  `role_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '当前对话角色ID',
  `title` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '对话标题',
  `context_summary` text COLLATE utf8mb4_unicode_ci COMMENT '对话上下文摘要',
  `message_count` int DEFAULT '0' COMMENT '消息数量',
  `total_tokens` int DEFAULT '0' COMMENT '总token消耗',
  `last_message_at` timestamp NULL DEFAULT NULL COMMENT '最后消息时间',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `status` enum('active','archived','deleted') COLLATE utf8mb4_unicode_ci DEFAULT 'active' COMMENT '对话状态',
  PRIMARY KEY (`id`),
  KEY `idx_conversations_user` (`user_id`,`last_message_at`),
  KEY `idx_conversations_role` (`role_id`,`status`),
  KEY `idx_conversations_updated` (`updated_at`),
  CONSTRAINT `conversations_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='对话会话表';

/*Data for the table `conversations` */

/*Table structure for table `feedbacks` */

DROP TABLE IF EXISTS `feedbacks`;

CREATE TABLE `feedbacks` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT (uuid()),
  `message_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '关联消息ID',
  `conversation_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '关联对话ID',
  `rating` int DEFAULT NULL COMMENT '1-5星评分',
  `feedback_type` enum('accuracy','relevance','style','technical') COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '反馈类型',
  `comment` text COLLATE utf8mb4_unicode_ci COMMENT '详细反馈内容',
  `user_contact` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '用户联系方式',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `message_id` (`message_id`),
  KEY `conversation_id` (`conversation_id`),
  KEY `idx_feedback_rating` (`rating`,`created_at`),
  KEY `idx_feedback_type` (`feedback_type`,`created_at`),
  CONSTRAINT `feedbacks_ibfk_1` FOREIGN KEY (`message_id`) REFERENCES `messages` (`id`) ON DELETE CASCADE,
  CONSTRAINT `feedbacks_ibfk_2` FOREIGN KEY (`conversation_id`) REFERENCES `conversations` (`id`) ON DELETE CASCADE,
  CONSTRAINT `feedbacks_chk_1` CHECK (((`rating` >= 1) and (`rating` <= 5)))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户反馈表';

/*Data for the table `feedbacks` */

/*Table structure for table `knowledge_base` */

DROP TABLE IF EXISTS `knowledge_base`;

CREATE TABLE `knowledge_base` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT (uuid()),
  `role_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '关联角色ID',
  `title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '知识片段标题',
  `content` text COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '知识内容',
  `content_type` enum('background','dialogue','fact','style') COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '知识类型',
  `source_url` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '来源URL',
  `metadata` json DEFAULT NULL COMMENT '元数据信息',
  `embedding_vector` longblob COMMENT '向量嵌入数据',
  `embedding_model` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '嵌入模型名称',
  `chunk_index` int DEFAULT NULL COMMENT '分块索引',
  `is_active` tinyint(1) DEFAULT '1' COMMENT '是否激活',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_knowledge_role` (`role_id`,`content_type`),
  KEY `idx_knowledge_active` (`is_active`,`created_at`),
  KEY `idx_created_at` (`created_at`),
  CONSTRAINT `knowledge_base_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='知识库表';

/*Data for the table `knowledge_base` */

/*Table structure for table `messages` */

DROP TABLE IF EXISTS `messages`;

CREATE TABLE `messages` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT (uuid()),
  `conversation_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '关联对话ID',
  `message_type` enum('user','assistant') COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '消息类型',
  `content` text COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '消息文本内容',
  `audio_url` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '语音文件URL',
  `tokens_used` int DEFAULT '0' COMMENT '消耗的token数量',
  `rag_context` json DEFAULT NULL COMMENT 'RAG检索的相关知识',
  `metadata` json DEFAULT NULL COMMENT '扩展元数据',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_conversation_created` (`conversation_id`,`created_at`),
  KEY `idx_message_type` (`message_type`,`created_at`),
  KEY `idx_created_at` (`created_at`),
  CONSTRAINT `messages_ibfk_1` FOREIGN KEY (`conversation_id`) REFERENCES `conversations` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='消息内容表';

/*Data for the table `messages` */

/*Table structure for table `roles` */

DROP TABLE IF EXISTS `roles`;

CREATE TABLE `roles` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT (uuid()),
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '角色名称',
  `description` text COLLATE utf8mb4_unicode_ci COMMENT '角色详细描述',
  `avatar_url` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '角色头像URL',
  `system_prompt` text COLLATE utf8mb4_unicode_ci COMMENT '系统提示词模板',
  `voice_settings` json DEFAULT NULL COMMENT '语音设置参数',
  `is_active` tinyint(1) DEFAULT '1' COMMENT '是否激活',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色信息表';

/*Data for the table `roles` */

insert  into `roles`(`id`,`name`,`description`,`avatar_url`,`system_prompt`,`voice_settings`,`is_active`,`created_at`,`updated_at`) values ('8ac24f3c-992e-11f0-8493-00ffce8a042b','哈利·波特','霍格沃茨魔法学校的学生，格兰芬多学院，拥有闪电形伤疤','/avatars/harry_potter.jpg','你正在扮演哈利·波特。你是一个勇敢、正义的年轻巫师，在霍格沃茨学习魔法。你知道关于魔法世界的各种知识，使用英式英语表达，保持格兰芬多学院的勇敢和正义感。','{\"pitch\": 1.0, \"speed\": 1.1, \"voiceType\": \"young_male\"}',1,'2025-09-24 18:09:22','2025-09-24 18:09:22'),('8ac29f37-992e-11f0-8493-00ffce8a042b','苏格拉底','古希腊哲学家，西方哲学的奠基人之一','/avatars/socrates.jpg','你正在扮演苏格拉底。你以提问的方式引导对话，帮助对方发现真理。你相信\"我知道我一无所知\"，采用苏格拉底问答法，通过提问引导用户思考。','{\"pitch\": 0.9, \"speed\": 0.9, \"voiceType\": \"wise_male\"}',1,'2025-09-24 18:09:22','2025-09-24 18:09:22'),('8ac2a2a8-992e-11f0-8493-00ffce8a042b','莎士比亚','英国文学史上最杰出的戏剧家和诗人','/avatars/shakespeare.jpg','你正在扮演威廉·莎士比亚。你使用古典英语表达，富有诗意和戏剧性。你的对话充满隐喻和文学典故，体现文艺复兴时期的语言风格。','{\"pitch\": 1.1, \"speed\": 1.0, \"voiceType\": \"dramatic_male\"}',1,'2025-09-24 18:09:22','2025-09-24 18:09:22');

/*Table structure for table `system_configs` */

DROP TABLE IF EXISTS `system_configs`;

CREATE TABLE `system_configs` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT (uuid()),
  `config_key` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '配置键',
  `config_value` json NOT NULL COMMENT '配置值(JSON格式)',
  `config_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '配置类型',
  `description` text COLLATE utf8mb4_unicode_ci COMMENT '配置描述',
  `is_active` tinyint(1) DEFAULT '1' COMMENT '是否生效',
  `version` int DEFAULT '1' COMMENT '配置版本',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `config_key` (`config_key`),
  KEY `idx_config_type` (`config_type`,`is_active`),
  KEY `idx_config_key` (`config_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统配置表';

/*Data for the table `system_configs` */

insert  into `system_configs`(`id`,`config_key`,`config_value`,`config_type`,`description`,`is_active`,`version`,`created_at`,`updated_at`) values ('8ac4d31a-992e-11f0-8493-00ffce8a042b','rate_limit','{\"max_requests_per_hour\": 1000, \"max_requests_per_minute\": 60}','security','API频率限制配置',1,1,'2025-09-24 18:09:22','2025-09-24 18:09:22'),('8ac4daaf-992e-11f0-8493-00ffce8a042b','openai_settings','{\"model\": \"gpt-4\", \"max_tokens\": 1000, \"temperature\": 0.7}','llm','OpenAI API配置',1,1,'2025-09-24 18:09:22','2025-09-24 18:09:22'),('8ac4dce2-992e-11f0-8493-00ffce8a042b','tts_settings','{\"speed\": 1.0, \"voice_type\": \"alloy\"}','tts','文本转语音配置',1,1,'2025-09-24 18:09:22','2025-09-24 18:09:22'),('8ac4de5a-992e-11f0-8493-00ffce8a042b','stt_settings','{\"model\": \"whisper-1\", \"language\": \"zh-CN\"}','stt','语音识别配置',1,1,'2025-09-24 18:09:22','2025-09-24 18:09:22'),('8ac4e003-992e-11f0-8493-00ffce8a042b','rag_settings','{\"top_k\": 3, \"similarity_threshold\": 0.7}','rag','RAG检索配置',1,1,'2025-09-24 18:09:22','2025-09-24 18:09:22');

/*Table structure for table `users` */

DROP TABLE IF EXISTS `users`;

CREATE TABLE `users` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT (uuid()),
  `username` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户名，用于登录和显示',
  `email` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '用户邮箱，用于联系',
  `password_hash` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '加密后的密码',
  `avatar_url` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '用户头像URL',
  `preferences` json DEFAULT NULL COMMENT '用户偏好设置，JSON格式',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `last_login_at` timestamp NULL DEFAULT NULL COMMENT '最后登录时间',
  `status` enum('active','inactive','banned') COLLATE utf8mb4_unicode_ci DEFAULT 'active' COMMENT '用户状态',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户信息表';

/*Data for the table `users` */

insert  into `users`(`id`,`username`,`email`,`password_hash`,`avatar_url`,`preferences`,`created_at`,`updated_at`,`last_login_at`,`status`) values ('169c48cd-992f-11f0-8493-00ffce8a042b','test_user','test@example.com',NULL,NULL,'{\"theme\": \"dark\", \"language\": \"zh-CN\", \"auto_play_audio\": true}','2025-09-24 18:13:17','2025-09-24 18:13:17',NULL,'active'),('aa29acd1-992f-11f0-8493-00ffce8a042b','demo_user','demo@example.com',NULL,NULL,'{\"theme\": \"light\"}','2025-09-24 18:17:24','2025-09-24 18:17:24',NULL,'active');

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
