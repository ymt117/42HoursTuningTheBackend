ALTER TABLE record_comment ADD INDEX linked_record_at(linked_record_id);
ALTER TABLE session ADD INDEX idx_session_01(value);
