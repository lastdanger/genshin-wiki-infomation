-- PostgreSQL 初始化脚本
-- 创建中文全文搜索扩展

-- 创建 zhparser 扩展（中文分词）
CREATE EXTENSION IF NOT EXISTS zhparser;

-- 创建中文全文搜索配置
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_ts_config WHERE cfgname = 'chinese') THEN
        CREATE TEXT SEARCH CONFIGURATION chinese (PARSER = zhparser);
        ALTER TEXT SEARCH CONFIGURATION chinese ADD MAPPING FOR n,v,a,i,e,l WITH simple;
    END IF;
END
$$;