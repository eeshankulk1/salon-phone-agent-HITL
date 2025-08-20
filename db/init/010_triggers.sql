-- function: after a supervisor response arrives, resolve the help_request and notify listeners
CREATE OR REPLACE FUNCTION trg_supervisor_response_notify() RETURNS trigger AS $$
DECLARE
  hr help_requests%ROWTYPE;
BEGIN
  -- mark the help request resolved if it isn't already
  UPDATE help_requests
     SET status = 'resolved',
         resolved_at = COALESCE(resolved_at, now())
   WHERE id = NEW.help_request_id
   RETURNING * INTO hr;

  -- if UPDATE matched nothing (rare), still fetch the row for payload fields
  IF NOT FOUND THEN
    SELECT * INTO hr FROM help_requests WHERE id = NEW.help_request_id;
  END IF;

  PERFORM pg_notify(
    'help_request_updates',
    json_build_object(
      'id',           hr.id,
      'customer_id',  hr.customer_id,
      'call_id',      hr.call_id,
      'response_id',  NEW.id,
      'responder_id', NEW.responder_id,
      'answer_text',  NEW.answer_text,
      'resolved_at',  hr.resolved_at
    )::text
  );

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS supervisor_responses_ai_notify ON supervisor_responses;
CREATE TRIGGER supervisor_responses_ai_notify
AFTER INSERT ON supervisor_responses
FOR EACH ROW
EXECUTE FUNCTION trg_supervisor_response_notify();

CREATE OR REPLACE FUNCTION notify_help_request_status_update() RETURNS trigger AS $$
DECLARE
  ans TEXT;
BEGIN
  IF NEW.status = 'resolved' AND COALESCE(OLD.status, '') <> 'resolved' THEN
    SELECT sr.answer_text
      INTO ans
      FROM supervisor_responses sr
     WHERE sr.help_request_id = NEW.id;

    PERFORM pg_notify(
      'help_request_updates',
      json_build_object(
        'id',           NEW.id,
        'customer_id',  NEW.customer_id,
        'call_id',      NEW.call_id,
        'response_id',  NULL,
        'responder_id', NULL,
        'answer_text',  ans,
        'resolved_at',  COALESCE(NEW.resolved_at, now())
      )::text
    );
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS help_requests_au_notify ON help_requests;
CREATE TRIGGER help_requests_au_notify
AFTER UPDATE ON help_requests
FOR EACH ROW
EXECUTE FUNCTION notify_help_request_status_update();