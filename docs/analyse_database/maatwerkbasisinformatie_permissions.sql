-- maatwerkbasisinformatie_permissions.sql
--
-- Creates (or replaces the existing) event trigger on newly created tables on the maatwerkbasisinformatie schema.
-- Trigger grants read access to all members of the maatwerkbasisinformatie_read role on all new tables in the
-- maatwerkbasisinformatie schema.
--
-- Needs to be run as Postgres superuser

CREATE OR REPLACE FUNCTION public.on_create_table_or_view_func()
 RETURNS event_trigger
 LANGUAGE plpgsql
AS $function$
DECLARE
    obj record;
BEGIN
  FOR obj IN SELECT * FROM pg_event_trigger_ddl_commands() WHERE command_tag in ('SELECT INTO','CREATE TABLE','CREATE TABLE AS','CREATE VIEW')
  LOOP
        if obj.schema_name = 'maatwerkbasisinformatie'
        then
        execute 'grant select ON ' || obj.object_identity || ' to maatwerkbasisinformatie_read';
        end if;
  END LOOP;
END;
$function$;

DROP EVENT TRIGGER IF EXISTS on_create_table_or_view;

CREATE EVENT TRIGGER
on_create_table_or_view ON ddl_command_end
WHEN TAG IN ('CREATE TABLE','CREATE VIEW', 'SELECT INTO', 'CREATE TABLE AS')
EXECUTE PROCEDURE on_create_table_or_view_func();