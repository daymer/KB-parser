use KnowledgeArticles
CREATE TABLE KnowledgeArticles
(ID uniqueidentifier,
title nvarchar(max),
url nvarchar(255),
KB_ID nvarchar(255),
Products nvarchar(255) NULL,
Version nvarchar(255) NULL,
Published datetime,
Last_Modified datetime NULL,
Languages nvarchar(255) NULL,
Last_check datetime NULL,
is_uptodate bit NULL,
OwnerId nvarchar(255),
KnowledgeArticleId nvarchar(255),
OwnerName nvarchar(255)
)

CREATE UNIQUE INDEX iKB_ID ON KnowledgeArticles (KB_ID)
CREATE UNIQUE INDEX iID ON KnowledgeArticles (ID)
CREATE UNIQUE INDEX iURL ON KnowledgeArticles (url)
/*
    drop table [dbo].[KnowledgeArticles]
	drop index KnowledgeArticles.iKB_ID
	drop index KnowledgeArticles.iID

*/