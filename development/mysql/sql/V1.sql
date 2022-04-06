ALTER TABLE record_comment ADD INDEX linked_record_at(linked_record_id);
ALTER TABLE session ADD INDEX idx_session_01(value);
ALTER TABLE record ADD INDEX idx_record_01(status);
