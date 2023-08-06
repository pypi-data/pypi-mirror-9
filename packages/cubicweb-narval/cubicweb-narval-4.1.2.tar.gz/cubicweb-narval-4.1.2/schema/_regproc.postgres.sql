/* -*- sql -*-

   postgres specific registered procedures

*/

CREATE OR REPLACE FUNCTION IS_NULL(anyelement) RETURNS bool
    AS $$ BEGIN RETURN ($1 is null); END $$ LANGUAGE plpgsql;
