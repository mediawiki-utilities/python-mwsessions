SELECT 
  rev_id as id, 
  rev_page as page_id, 
  rev_user as user_id, 
  rev_user_text as user_text, 
  rev_timestamp as timestamp, 
  rev_sha1 as sha1, 
  rev_len as len,
  rev_deleted as deleted,
  False as archived
FROM revision
WHERE rev_timestamp <= "20150801"
ORDER BY rev_timestamp ASC, rev_id ASC;
