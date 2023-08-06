
-- Run all the sql scripts in the dependencies folder
\i '/Users/alexei/Work/Projects/Arches3/arches/db/install/dependencies/batch_index.sql'
\i '/Users/alexei/Work/Projects/Arches3/arches/db/install/dependencies/django_authentication.sql'
\i '/Users/alexei/Work/Projects/Arches3/arches/db/install/dependencies/isstring.sql'
\i '/Users/alexei/Work/Projects/Arches3/arches/db/install/dependencies/postgis_backward_compatibility.sql'
\i '/Users/alexei/Work/Projects/Arches3/arches/db/install/dependencies/uuid-ossp.sql'

-- Reload all managed schemas
\i '/Users/alexei/Work/Projects/Arches3/arches/db/ddl/db_ddl.sql'

-- Add all the data in the dml folder
\i '/Users/alexei/Work/Projects/Arches3/arches/db/dml/db_data.sql'

-- Run all the sql in teh postdeployment folder
\i '/Users/alexei/Work/Projects/Arches3/arches/db/install/postdeployment/django_auth.sql'

-- Spring cleaning
VACUUM ANALYZE;
