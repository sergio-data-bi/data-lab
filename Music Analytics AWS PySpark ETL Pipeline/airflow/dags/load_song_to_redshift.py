from datetime import datetime, timedelta
import os
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators import (StageToRedshiftOperator, LoadFactOperator,
                                LoadDimensionOperator, DataQualityOperator)
from helpers import SqlQueries

# AWS_KEY = os.environ.get('AWS_KEY')
# AWS_SECRET = os.environ.get('AWS_SECRET')

default_args = {
    'owner': 'sparkify',
    'start_date': datetime(2019, 1, 12),
    'depends_on_past': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'catchup_by_default': False
}

dag = DAG('load_song_to_redshift',
          default_args=default_args,
          description='Load and transform data in Redshift with Airflow',
          schedule_interval='0 * * * *'
        )

start_operator = DummyOperator(task_id='Begin_execution',  dag=dag)

stage_events_to_redshift = StageToRedshiftOperator(
    task_id='Stage_events',
    dag=dag,
    redshift_conn_id='redshift',
    aws_credentials_id = 'aws_credentials',
    table_name='public.staging_events',
    s3_bucket='s3://udacity-dend/log_data',
    json_path = 's3://udacity-dend/log_json_path.json',
    use_paritioning = False,
    execution_date = '{{ execution_date }}',
    truncate_table=True
)

stage_songs_to_redshift = StageToRedshiftOperator(
    task_id='Stage_songs',
    dag=dag,
    redshift_conn_id='redshift',
    aws_credentials_id = 'aws_credentials',
    table_name='public.staging_songs',
    s3_bucket='s3://udacity-dend/song_data',
    json_path = 'auto',
    use_paritioning = False,
    execution_date = '{{ execution_date }}',
    truncate_table=True
)

load_songplays_table = LoadFactOperator(
    task_id='Load_songplays_fact_table',
    dag=dag,
    redshift_conn_id = 'redshift',
    fact_insert_sql = SqlQueries.songplay_table_insert,
    fact_table_name = 'public.songplays',
    fact_insert_columns = 'playid, start_time, userid, level, songid, artistid, sessionid, location, user_agent',
    truncate_table = True
)

load_user_dimension_table = LoadDimensionOperator(
    task_id='Load_user_dim_table',
    dag=dag,
    redshift_conn_id = 'redshift',
    dimension_insert_sql = SqlQueries.user_table_insert,
    dimension_table_name = 'public.users',
    dimension_insert_columns = 'userid, first_name, last_name, gender, level',
    truncate_table = True
)

load_song_dimension_table = LoadDimensionOperator(
    task_id='Load_song_dim_table',
    dag=dag,
    redshift_conn_id = 'redshift',
    dimension_insert_sql = SqlQueries.song_table_insert,
    dimension_table_name = 'public.songs',
    dimension_insert_columns = 'songid, title, artistid, year, duration',
    truncate_table = True
)

load_artist_dimension_table = LoadDimensionOperator(
    task_id='Load_artist_dim_table',
    dag=dag,
    redshift_conn_id = 'redshift',
    dimension_insert_sql = SqlQueries.artist_table_insert,
    dimension_table_name = 'public.artists',
    dimension_insert_columns = 'artistid, name, location, lattitude, longitude',
    truncate_table = True
)

load_time_dimension_table = LoadDimensionOperator(
    task_id='Load_time_dim_table',
    dag=dag,
    redshift_conn_id = 'redshift',
    dimension_table_name = 'public."time"',
    dimension_insert_sql = SqlQueries.time_table_insert,
    dimension_insert_columns = 'start_time, hour, day, week, month, year, weekday',
    truncate_table = True
)

run_quality_checks = DataQualityOperator(
    task_id='Run_data_quality_checks',
    dag=dag,
    redshift_conn_id='redshift',
    sql_check_queries=["SELECT COUNT(*) FROM songs WHERE songid IS NULL",
                       "SELECT COUNT(*) FROM songs",
                       "SELECT COUNT(*) FROM songplays",
                       "SELECT COUNT(*) FROM artists",
                       "SELECT COUNT(*) FROM artists",
                       "SELECT COUNT(*) FROM time"],
    expected_results=[lambda records: records==0,
                      lambda records: records>0,
                      lambda records: records>0,
                      lambda records: records>0,
                      lambda records: records>0,
                      lambda records: records>0]
)

end_operator = DummyOperator(task_id='Stop_execution',  dag=dag)

start_operator >> stage_events_to_redshift
start_operator >> stage_songs_to_redshift
stage_events_to_redshift >> load_songplays_table
stage_songs_to_redshift >> load_songplays_table
load_songplays_table >> load_song_dimension_table
load_songplays_table >> load_user_dimension_table
load_songplays_table >> load_artist_dimension_table
load_songplays_table >> load_time_dimension_table
load_song_dimension_table >> run_quality_checks
load_user_dimension_table >> run_quality_checks
load_artist_dimension_table >> run_quality_checks
load_time_dimension_table >> run_quality_checks
run_quality_checks >> end_operator