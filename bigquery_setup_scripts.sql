-- DDL for the main table to store raw, enriched data
CREATE OR REPLACE TABLE `gaming_analytics.youtube_analysis`
(
    id STRING NOT NULL,
    published_at TIMESTAMP NOT NULL OPTIONS(description="Timestamp of the video's publication, used for hourly partitioning"),
    title STRING,
    url STRING OPTIONS(description="YouTube video URL"),
    analysis STRING OPTIONS(description="The full JSON response from the Gemini AI analysis"),
    fetched_at TIMESTAMP OPTIONS(description="Timestamp when the data was fetched and analyzed"),
    source STRING OPTIONS(description="Source of the data, e.g., 'YouTube'"),
    channel STRING OPTIONS(description="YouTube channel handle")
)
PARTITION BY TIMESTAMP_TRUNC(published_at, HOUR)
OPTIONS(
    description="Table of AI-analyzed YouTube videos, partitioned by publication hour."
);




CREATE OR REPLACE VIEW `gaming_analytics.youtube_analysis_view` AS
SELECT
  id,
  published_at,
  url,
  fetched_at,
  source,
  channel,
  -- Fields extracted from the 'analysis' JSON column
  JSON_EXTRACT_SCALAR(analysis, '$.video_details.video_title') AS video_title,
  JSON_EXTRACT_SCALAR(analysis, '$.video_details.executive_summary') AS executive_summary,
  JSON_EXTRACT_SCALAR(analysis, '$.transcript_analysis.sentiment_analysis.primary_sentiment') AS primary_sentiment,
  SAFE_CAST(JSON_EXTRACT_SCALAR(analysis, '$.transcript_analysis.sentiment_analysis.sentiment_score') AS FLOAT64) AS sentiment_score,
  JSON_EXTRACT_SCALAR(analysis, '$.comment_section_analysis.overall_comment_sentiment') AS comment_sentiment,
  SAFE_CAST(JSON_EXTRACT_SCALAR(analysis, '$.comment_section_analysis.sentiment_score') AS FLOAT64) AS comment_sentiment_score,
  JSON_EXTRACT_SCALAR(analysis, '$.gaming_analysis_focus.primary_game_feature_discussed') AS game_feature_discussed,
  JSON_EXTRACT_SCALAR(analysis, '$.gaming_analysis_focus.attitude_towards_feature') AS attitude_towards_feature,
  JSON_EXTRACT(analysis, '$.gaming_analysis_focus.key_praises') AS key_praises,
  JSON_EXTRACT(analysis, '$.gaming_analysis_focus.key_criticisms') AS key_criticisms,
  JSON_EXTRACT(analysis, '$.transcript_analysis.entities') AS entities
FROM
  `my-project.gaming_analytics.youtube_analysis`;
