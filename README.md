# 🔬 Sergio's Data Lab

## Projects

## 🎼 Music Analytics  
[Project Repository](./Music%20Analytics)  

**Objective:** Transformed raw data from the Million Song Dataset and stored it in a cloud-based environment to analyze user engagement, song popularity, and emerging artist trends.

**Key Metrics:**  
- **1M+ tracks** analyzed across multiple genres
- **48M+ user play records** processed for engagement insights
- **10K+ artists** tracked for trend detection
- Identification of most-streamed songs and top artists
- Analysis of user behavior and consumption trends
- Data preparation for recommendation systems

**Data Model**  
The solution implements a star schema with one fact table (`songplays`) and four supporting dimensions (`songs`, `artists`, `users`, `time`), all optimized for analytic queries on user behavior and song popularity. Data first lands in staging tables (`staging_events`, `staging_songs`) and is then transformed into the final star schema, supporting scalable analytics on user engagement, trends, and recommendations.

**Tech Stack:**  
- **Python** – ETL automation
- **SQL** – Querying and structuring data
- **Apache Spark** – Large-scale data processing
- **Apache Airflow** – Pipeline orchestration and scheduling
- **PostgreSQL** – Local testing database
- **Amazon Redshift** – High-performance analytics with clustering
- **Amazon S3** – Scalable Cloud data storage

**Source:** [Million Song Dataset (MSD)](http://millionsongdataset.com/)  
