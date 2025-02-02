from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class LoadFactOperator(BaseOperator):
    """
    Description: This operator loads data from a Redshift staging table to a dimension table.

    Arguments:
        redshift_conn_id: Redshift connection
        fact_table_name: Redshift fact table name where data will be stored
        fact_insert_columns: Column names to insert
        fact_insert_sql: Insert SQL statement
        truncate_table: if True, data will be truncated (deleted) before inserting
    """

    ui_color = '#F98866'

    TRUNCATE_FACT_SQL = """
        TRUNCATE TABLE {};
        """

    INSERT_FACT_SQL = """
        INSERT INTO {} ({}) {};
        """

    @apply_defaults
    def __init__(self,
                 redshift_conn_id='redshift',
                 fact_table_name='',
                 fact_insert_columns='',
                 fact_insert_sql='',
                 truncate_table=False,
                 *args, **kwargs):

        super(LoadFactOperator, self).__init__(*args, **kwargs)
        self.redshift_conn_id = redshift_conn_id
        self.fact_table_name = fact_table_name
        self.fact_insert_sql = fact_insert_sql
        self.fact_insert_columns = fact_insert_columns
        self.truncate_table = truncate_table

    def execute(self, context):
        redshift_hook = PostgresHook(self.redshift_conn_id)
        if self.truncate_table:
            self.log.info(f"Truncating table {self.fact_table_name}")
            redshift_hook.run(self.TRUNCATE_FACT_SQL.format(self.fact_table_name))    
        redshift_hook.run(self.INSERT_FACT_SQL.format(
            self.fact_table_name, 
            self.fact_insert_columns,
            self.fact_insert_sql))