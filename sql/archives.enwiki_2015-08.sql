SELECT 
  ar_rev_id as id,
  ar_page_id as page_id,
  ar_user as user_id,
  ar_user_text as user_text,
  ar_timestamp as timestamp,
  ar_sha1 as sha1,
  ar_len as len,
  ar_deleted as deleted,
  True as archived
FROM archive
WHERE ar_timestamp BETWEEN "20131104144204" AND "20150801"
ORDER BY ar_timestamp ASC, ar_rev_id ASC
