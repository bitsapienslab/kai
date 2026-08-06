-- Apply after schema creation in a controlled PostgreSQL environment.
-- The API must set app.tenant_id at transaction start, then PostgreSQL enforces scope.
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE consents ENABLE ROW LEVEL SECURITY;
ALTER TABLE objectives ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE memories ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_users ON users USING (tenant_id::text = current_setting('app.tenant_id', true));
CREATE POLICY tenant_consents ON consents USING (tenant_id::text = current_setting('app.tenant_id', true));
CREATE POLICY tenant_objectives ON objectives USING (tenant_id::text = current_setting('app.tenant_id', true));
CREATE POLICY tenant_events ON conversation_events USING (tenant_id::text = current_setting('app.tenant_id', true));
CREATE POLICY tenant_memories ON memories USING (tenant_id::text = current_setting('app.tenant_id', true));

