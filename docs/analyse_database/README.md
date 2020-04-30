# Analyse database
The analyse database (gob_analyse) is used by basisinformatie to perform analyses on the GOB data.
Employees of basisinformatie have direct access to this database. Their access is controlled with
Postgres roles. This directory contains the necessary SQL scripts. This file explains how to use them.

## Design
### Schemas and default roles
All registrations in GOB have their own schemas in the analyse database. There is a bag schema, brk schema,
gebieden, etc. For each schema there is a corresponding _read role (bag_read, brk_read, gebieden_read,
etc). This read role has, as the name suggests, read permissions on the schema. There are no write roles
for these schemas.

There is one extra schema called 'maatwerkbasisinformatie', where (some) basisinformatie employees have
write permissions. This is their playground where they can place the results of their analyses. Two roles
exist for this schema: maatwerkbasisinformatie_read and maatwerkbasisinformatie_write.

The next section explains how these roles are used in practice.

### Access control
Two main roles are used to control access to new analyse database users: agm_basis and agm_plus. Users
are granted either only the agm_basis role or both the agm_basis AND agm_plus roles.

- The agm_basis role provides read access to all registrations except BRK and read access to the
maatwerkbasisinformatie schema.
- The agm_plus role provides read access to BRK and write access to the maatwerkbasisinformatie schema.

## SQL scripts in this directory
### default_roles.sql
This file contains the SQL to create the default roles, including agm_basis and agm_plus. The SQL in this
file should only have to be run when creating a new analyse database from scratch. Only when a new
registration is added should parts of this file be edited and run. See 'Adding a new registration'

### maatwerkbasisinformatie_permissions.sql
This file contains the SQL to create a trigger that makes sure that the maatwerkbasisinformatie_read
role has read access to every table created in the maatwerkbasisinformatie schema.
Should only be run during initial setup.

 
## Adding a new registration
Use default_role.sql as a reference. Line numbers refer to this file.
1. Make a default _read role using the create_default_read_role_for_schema function and add this call
to the list of similar calls for future use (line 20).
2. Grant this new read role to either agm_basis or agm_plus, and add the new role to one of the grant
statements (line 37 of 41).

## Adding a new user
1. Create a new Postgres user with the command
    ```
    CREATE USER username PASSWORD '********' 
    -- (Make sure to replace username with the correct username and ******* with an actual password.)
    ```    

2. Grant agm_basis or agm_plus (or both) to the new user:
    ```
    GRANT agm_basis/agm_plus to username;
    ```

That's it!

## Initial setup
Run both default_roles.sql and maatwerkbasisinformatie_permissions.sql on the new analyse database.
Make sure the database is already filled with data once, so that the schemas for the registrations are
already present.
