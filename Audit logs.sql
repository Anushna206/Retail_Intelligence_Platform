SELECT
  query_id,
  query_text,
  user_name,
  role_name,
  database_name,
  schema_name,
  start_time,
  execution_status,
  total_elapsed_time
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE database_name = 'RETAIL_INTELLIGENCE'
ORDER BY start_time DESC
LIMIT 50;

--access history 
SELECT
  query_id,
  user_name,
  query_start_time,
  direct_objects_accessed,
  base_objects_accessed
FROM SNOWFLAKE.ACCOUNT_USAGE.ACCESS_HISTORY
WHERE query_start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
ORDER BY query_start_time DESC
LIMIT 50;