DO $$
BEGIN
    -- Cria o usuário 'my_site' com uma senha, se ele não existir
    IF NOT EXISTS (SELECT 1 FROM pg_catalog.pg_user WHERE usename = 'my_site') THEN
        CREATE USER my_site WITH PASSWORD 'master' CREATEDB CREATEROLE;
    END IF;

    -- Concede todos os privilégios no banco de dados 'my_site' para o usuário 'my_site', se o privilégio não existir
    IF NOT EXISTS (SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'my_site' AND datdba = (SELECT usesysid FROM pg_catalog.pg_user WHERE usename = 'my_site')) THEN
        GRANT ALL PRIVILEGES ON DATABASE my_site TO my_site;
    END IF;

    -- Concede todos os privilégios em todas as tabelas no schema 'public' do banco de dados 'my_site' para o usuário 'my_site'
    IF NOT EXISTS (SELECT 1 FROM pg_catalog.pg_tables WHERE schemaname = 'public' AND tableowner = 'my_site') THEN
        GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO my_site;
    END IF;

    -- Concede privilégios padrão para futuras tabelas criadas no schema 'public' para o usuário 'my_site'
    ALTER DEFAULT PRIVILEGES FOR ROLE my_site IN SCHEMA public GRANT ALL ON TABLES TO my_site;

    -- Concede todos os privilégios em todas as sequências no schema 'public' do banco de dados 'my_site' para o usuário 'my_site'
     IF NOT EXISTS (SELECT 1 FROM pg_catalog.pg_class WHERE relkind = 'S' AND relnamespace = (SELECT oid FROM pg_catalog.pg_namespace WHERE nspname = 'public') AND relowner = (SELECT usesysid FROM pg_catalog.pg_user WHERE usename = 'my_site')) THEN
        GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO my_site;
    END IF;

    -- Concede privilégios padrão para futuras sequências criadas no schema 'public' para o usuário 'my_site'
    ALTER DEFAULT PRIVILEGES FOR ROLE my_site IN SCHEMA public GRANT ALL ON SEQUENCES TO my_site;
END $$;