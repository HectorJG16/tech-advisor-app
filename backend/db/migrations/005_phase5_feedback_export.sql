-- Phase 5: track feedback rows exported for offline retraining
ALTER TABLE recommendation_feedback
    ADD COLUMN IF NOT EXISTS exported_at TIMESTAMPTZ;

CREATE INDEX IF NOT EXISTS idx_feedback_unexported
    ON recommendation_feedback(created_at)
    WHERE exported_at IS NULL AND selected_tool_id IS NOT NULL;
