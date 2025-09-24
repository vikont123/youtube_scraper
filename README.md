# The Ultimate Play: From Raw Data to Real-Time Insights with Gemini

### Building a Serverless Google Cloud Pipeline for Instant Community Intelligence

What if you could predict the next big trend in the gaming world the moment it starts? For any media agency, staying ahead of community sentiment isn't just an advantage; it's essential for survival. Consider a popular franchise like Madden NFL. Every day, countless gameplay videos, patch reviews, and fan reactions are uploaded to YouTube.

The traditional approach of scraping data, loading it into a warehouse, and running batch analysis jobs is too slow to keep up. By the time you have your insights, the conversation has already moved on.

We were faced with this exact problem. Our team needed immediate answers to crucial questions:

* What's the sentiment around the new "Franchise Mode" gameplay?
* Which features are players praising, and which are drawing criticism?
* What are the key discussion points from top creators after a new patch?

We realized that traditional data scraping is dead. We needed to empower our scraper to be an AI analyst from the very beginning. This is the story of how we built exactly that, leveraging the power of Gemini and Google Cloud to create a pipeline that delivers AI-enriched insights in near real-time.

***

### The Blueprint: An Architecture for Speed and Intelligence

Instead of analyzing data after the fact, our architecture enriches it with AI insights the moment it's collected. The process is automated, serverless, and designed for scalability.

**Process Diagram:** 📈

**Process Flow:**

1.  Cloud Scheduler triggers the Cloud Run Service (Python Scraper) hourly.
2.  The scraper fetches new YouTube video URLs from target channels.
3.  It calls the Vertex AI Gemini API with the video data.
4.  A structured JSON analysis is received back from Gemini.
5.  The enriched JSON is loaded directly into a BigQuery Table.
6.  A BigQuery View then cleans the JSON for easy visualization in Looker Studio.

To bring this to life, we'll use a suite of powerful Google Cloud services:

* [Cloud Run](https://cloud.google.com/run/docs): The perfect serverless platform for our Python service.
* [Vertex AI](https://cloud.google.com/vertex-ai/docs): Our gateway to the Gemini family of models.
* [Cloud Scheduler](https://cloud.google.com/scheduler/docs): Our cron job in the cloud to automate execution.
* [BigQuery](https://cloud.google.com/bigquery/docs): Our analytics warehouse where we'll store the clean, structured JSON objects from Gemini.
* [Looker Studio](https://cloud.google.com/looker/docs/studio): Our visualization tool for building interactive dashboards.

***

### Step 1: Crafting the Brain --- The Gemini Prompt (prompts.py)

The entire pipeline's effectiveness hinges on a high-quality, reliable prompt. To turn Gemini into a specialized analyst, we followed a few key principles:

* **Assign a Role:** We start by telling the model its persona: "You are a sophisticated AI analyst specializing in the gaming industry...". This sets the context for the entire task.
  [prompt](https://github.com/vikont123/youtube_scraper/blob/main/prompts.py)
  
This approach transforms Gemini from a general-purpose tool into a highly specialized and predictable analysis engine.

***

### Step 2: Building the Data Foundation in BigQuery
Before we write our scraper, we need a place to store the data. We use two main components in BigQuery: a raw table and a clean view.

First, we create a table to land the raw, AI-enriched JSON data. Storing the full JSON in a single string column is highly efficient for writing data.

[SQL](https://github.com/vikont123/youtube_scraper/blob/main/bigquery_setup_scripts.sql)

Querying raw JSON can be cumbersome for analysts. To solve this, we create a BigQuery View. A view acts as a virtual table that flattens the JSON into clean, structured columns, making it incredibly easy to use with tools like Looker Studio.

***

###  Step 3: The Intelligent Scraper Code (scrap_youtube.py)
Our Python script, scrap_youtube.py, orchestrates the entire process. Let's walk through its key components.

Setup and Dependencies
First, we define our dependencies in requirements.txt and our configuration variables in a .env file for easy management.

[requirements.txt](https://github.com/vikont123/youtube_scraper/blob/main/requirements.txt)
[.env](https://github.com/vikont123/youtube_scraper/blob/main/.env)

The Python Script ([scrap_youtube.py](https://github.com/vikont123/youtube_scraper/blob/main/scrap_youtube.py)
The script is built around several key functions that find data, enrich it with AI, and save the results.

1. **Finding New Videos** (get_channel_videos_last_hour) This function queries the YouTube Data API for any videos published by a specific channel in the last hour. It compiles a list of URLs and basic metadata.
2. **The AI Magic** (get_video_details) For each video URL we find, this function sends it along with our prompt to the Gemini API. It receives the structured JSON analysis in return.
3. **Saving the Insights** (upload_videos_to_bigquery) After all videos are analyzed, this function loads the entire batch of enriched data into our BigQuery table in a single operation.
4. **Orchestration** (process_multiple_channels and main) Finally, the main function orchestrates the entire process: it iterates through a list of target channels, calls the functions above in sequence, and kicks off the BigQuery upload.

***

###  Step 4: Deployment and Automation
With the code ready, we deploy it to Cloud Run and automate it with Cloud Scheduler.
  1.**Containerize the Application:** We create a Dockerfile to package our Python script and its dependencies into a portable container. This ensures it runs identically anywhere.
  2.**Deploy to Cloud Run:** A single gcloud run deploy command uploads our container and launches it as a serverless service with a secure HTTPS endpoint.
  3.**Schedule with Cloud Scheduler: **We create a scheduler job in the Google Cloud console to send an HTTPS request to our Cloud Run endpoint every hour, fully automating the pipeline without managing any servers.

***

###  Step 5: Powering Analytics with a BigQuery View
The pipeline is designed to first land all the raw, AI-enriched JSON data into a main BigQuery table. While it's efficient to store the full JSON in a single column, querying it directly can be cumbersome for business users or data analysts who would need to use JSON_VALUE for every request.

That's where a BigQuery View comes in. A view is a saved, virtual table that we build on top of our main table. It acts as a transformation layer, pre-processing the raw JSON and presenting it as clean, structured columns. This is a game-changer because it becomes the single, easy-to-use source for all your analytics needs.

By creating a view, we unlock powerful capabilities:

1.**Looker Studio Dashboards:** You can connect Looker Studio directly to this view. All the fields (like video_title, primary_sentiment, attitude_towards_feature) will appear as ready-to-use dimensions and metrics, making dashboard creation a simple drag-and-drop process.

2.**Conversational Analytics:** With tools like Looker Studio Pro or the Conversational Analytics API, your team can ask questions in plain English. Because the view has clearly named columns like game_feature_discussed, a query like "What was the sentiment for Franchise Mode last week?" can be easily translated into SQL that runs against this view.

3.**Foundation for Vector Search:** The view provides a clean starting point for more advanced AI applications. You could easily create an embeddings model in BigQuery that takes the text from the executive_summary or key_criticisms columns of this view, converts it into vectors, and enables powerful similarity searches like "find me other videos with similar complaints."

***

Beyond YouTube: Building a Unified Analytics Hub
This YouTube pipeline is just the beginning. The true power of this architecture is its scalability. You can apply the exact same pattern (Scrape -> Analyze with Gemini -> Store in BigQuery) to build a comprehensive analytics hub tracking sentiment across multiple platforms:

**Telegram:** Monitor fan channels and developer announcements.
**News Websites (RSS):** Analyze reviews and articles from top gaming publications.
**Twitter (X):** Track real-time reactions and viral posts from players and influencers.

With serverless technologies and generative AI, you can build this powerful system quickly and without a large team. You're not just collecting data; you're generating strategic insights on demand.

Ready to get started? Take this code, adapt it, and start turning data into decisions today.

And if you run into any challenges along the way, remember that Google Cloud specialists are always ready to help you bring your boldest ideas to life.

Full Code & Schema 🛠️
(https://github.com/vikont123/youtube_scraper)
