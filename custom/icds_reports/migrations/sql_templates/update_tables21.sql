ALTER TABLE child_health_monthly ADD COLUMN zscore_grading_hfa smallint;
ALTER TABLE child_health_monthly ADD COLUMN zscore_grading_hfa_recorded_in_month smallint;
ALTER TABLE child_health_monthly ADD COLUMN zscore_grading_wfh smallint;
ALTER TABLE child_health_monthly ADD COLUMN zscore_grading_wfh_recorded_in_month smallint;
ALTER TABLE child_health_monthly ADD COLUMN muac_grading smallint;
ALTER TABLE child_health_monthly ADD COLUMN muac_grading_recorded_in_month smallint;
ALTER TABLE agg_child_health ADD COLUMN zscore_grading_hfa_normal int;
ALTER TABLE agg_child_health ADD COLUMN zscore_grading_hfa_moderate int;
ALTER TABLE agg_child_health ADD COLUMN zscore_grading_hfa_severe int;
ALTER TABLE agg_child_health ADD COLUMN wasting_normal_v2 int;
ALTER TABLE agg_child_health ADD COLUMN wasting_moderate_v2 int;
ALTER TABLE agg_child_health ADD COLUMN wasting_severe_v2 int;
