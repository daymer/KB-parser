CREATE TABLE KnowledgeArticles
(ID uniqueidentifier,
title nvarchar(max),
url nvarchar(4000),
KB_ID uniqueidentifier,
Products nvarchar(255) NULL,
Version nvarchar(255) NULL,
Published datetime,
Last_Modified datetime NULL,
Languages xml NULL,
Last_check datetime NULL,
is_uptodate bit NULL)
CREATE UNIQUE INDEX iKB_ID ON KnowledgeArticles (KB_ID)
CREATE UNIQUE INDEX iID ON KnowledgeArticles (ID)

