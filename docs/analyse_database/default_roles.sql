-- Create work schema for basinformatie
create schema maatwerkbasisinformatie;

-- Creates default read role for given schema and assigns read rights to read role
CREATE OR REPLACE FUNCTION public.create_default_read_role_for_schema(schema varchar)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
DECLARE
    read_role varchar := schema || '_read';
BEGIN
    execute 'create role ' || read_role;
    execute 'grant usage on schema ' || schema || ' to ' || read_role;
    execute 'grant select on all tables in schema ' || schema || ' to ' || read_role;
    execute 'alter default privileges in schema ' || schema || ' grant select on tables to ' || read_role;
END;
$function$;

-- Create default read roles to schemas
select create_default_read_role_for_schema('bag'),
       create_default_read_role_for_schema('brk'),
       create_default_read_role_for_schema('bgt'),
       create_default_read_role_for_schema('gebieden'),
       create_default_read_role_for_schema('meetbouten'),
       create_default_read_role_for_schema('nap'),
       create_default_read_role_for_schema('wkpb'),
       create_default_read_role_for_schema('maatwerkbasisinformatie')
;

-- Create maatwerkbasisinformatie_write role
create role maatwerkbasisinformatie_write;
grant usage on schema maatwerkbasisinformatie to maatwerkbasisinformatie_write;
grant all on schema maatwerkbasisinformatie to maatwerkbasisinformatie_write;

-- Create agm_basis role (read all schemas except BRK)
create role agm_basis;
grant bag_read, gebieden_read, wkpb_read, nap_read, meetbouten_read, bgt_read, maatwerkbasisinformatie_read TO agm_basis;

-- Create agm_plus role (read BRK and write to maatwerkbasisinformatie schema)
create role agm_plus;
grant brk_read, maatwerkbasisinformatie_write to agm_plus;
