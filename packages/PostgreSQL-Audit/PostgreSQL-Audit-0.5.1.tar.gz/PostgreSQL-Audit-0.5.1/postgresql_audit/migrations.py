import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from .expressions import jsonb_change_key_name, jsonb_merge


def get_activity_table():
    return sa.Table(
        'activity',
        sa.MetaData(),
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('table_name', sa.String),
        sa.Column('verb', sa.String),
        sa.Column('old_data', JSONB),
        sa.Column('changed_data', JSONB),
        schema='audit',
    )


def alter_column(conn, table, column_name, func):
    """
    Run given callable against given table and given column in activity table
    jsonb data columns. This function is useful when you want to reflect type
    changes in your schema to activity table.

    In the following example we change the data type of User's age column from
    string to integer.


    ::

        from alembic import op
        from postgresql_audit import alter_column


        def upgrade():
            op.alter_column(
                'user',
                'age',
                type_=sa.Integer
            )

            alter_column(
                op,
                'user',
                'age',
                lambda value, activity_table: sa.cast(value, sa.Integer)
            )


    :param conn:
        An object that is able to execute SQL (either SQLAlchemy Connection,
        Engine or Alembic Operations object)
    :param table:
        The table to run the column name changes against
    :param column_name:
        Name of the column to run callable against
    :param func:
        A callable to run against specific column in activity table jsonb data
        columns. The callable should take two parameters the jsonb value
        corresponding to given column_name and activity table object.
    """
    activity_table = get_activity_table()
    query = (
        activity_table
        .update()
        .values(
            old_data=jsonb_merge(
                activity_table.c.old_data,
                sa.cast(sa.func.json_build_object(
                    column_name,
                    func(
                        activity_table.c.old_data[column_name],
                        activity_table
                    )
                ), JSONB)
            ),
            changed_data=jsonb_merge(
                activity_table.c.changed_data,
                sa.cast(sa.func.json_build_object(
                    column_name,
                    func(
                        activity_table.c.changed_data[column_name],
                        activity_table
                    )
                ), JSONB)
            )
        )
        .where(activity_table.c.table_name == table)
    )
    return conn.execute(query)


def change_column_name(conn, table, old_column_name, new_column_name):
    """
    Changes given audit.activity jsonb data column key. This function is useful
    when you want to reflect column name changes to activity table.

    ::

        from alembic import op
        from postgresql_audit import change_column_name


        def upgrade():
            op.alter_column(
                'my_table',
                'my_column',
                new_column_name='some_column'
            )

            change_column_name(op, 'my_table', 'my_column', 'some_column')


    :param conn:
        An object that is able to execute SQL (either SQLAlchemy Connection,
        Engine or Alembic Operations object)
    :param table:
        The table to run the column name changes against
    :param old_column_name:
        Name of the column to change
    :param new_column_name:
        New colum name
    """
    activity_table = get_activity_table()
    query = (
        activity_table
        .update()
        .values(
            old_data=jsonb_change_key_name(
                activity_table.c.old_data,
                old_column_name,
                new_column_name
            ),
            changed_data=jsonb_change_key_name(
                activity_table.c.changed_data,
                old_column_name,
                new_column_name
            )
        )
        .where(activity_table.c.table_name == table)
    )
    return conn.execute(query)


def add_column(conn, table, column_name, default_value=None):
    """
    Adds given column to `audit.activity` table jsonb data columns.

    In the following example we reflect the changes made to our schema to
    activity table.

    ::

        import sqlalchemy as sa
        from alembic import op
        from postgresql_audit import add_column


        def upgrade():
            op.remove_column('article', sa.Column('created_at', sa.DateTime()))
            add_column(op, 'article', 'created_at')


    :param conn:
        An object that is able to execute SQL (either SQLAlchemy Connection,
        Engine or Alembic Operations object)
    :param table:
        The table to remove the column from
    :param column_name:
        Name of the column to add
    :param default_value:
        The default value of the column
    """
    activity_table = get_activity_table()
    data = {column_name: default_value}
    query = (
        activity_table
        .update()
        .values(
            old_data=sa.case(
                [
                    (
                        activity_table.c.old_data.isnot(None),
                        jsonb_merge(
                            activity_table.c.old_data,
                            data
                        )
                    ),
                ],
                else_=None
            ),
            changed_data=sa.case(
                [
                    (
                        sa.and_(
                            activity_table.c.changed_data.isnot(None),
                            activity_table.c.verb != 'update'
                        ),
                        jsonb_merge(
                            activity_table.c.changed_data,
                            data
                        ),
                    )
                ],
                else_=activity_table.c.changed_data
            ),
        )
        .where(activity_table.c.table_name == table)
    )
    return conn.execute(query)


def remove_column(conn, table, column_name):
    """
    Removes given audit.activity jsonb data column key. This function is useful
    when you are doing schema changes that require removing a column.

    Let's say you've been using PostgreSQL-Audit for a while for a table called
    article. Now you want to remove one audited column called 'created_at' from
    this table.

    ::

        from alembic import op
        from postgresql_audit import remove_column


        def upgrade():
            op.remove_column('article', 'created_at')
            remove_column(op, 'article', 'created_at')


    :param conn:
        An object that is able to execute SQL (either SQLAlchemy Connection,
        Engine or Alembic Operations object)
    :param table:
        The table to remove the column from
    :param column_name:
        Name of the column to remove
    """
    activity_table = get_activity_table()
    remove = sa.cast(column_name, sa.Text)
    query = (
        activity_table
        .update()
        .values(
            old_data=activity_table.c.old_data - remove,
            changed_data=activity_table.c.changed_data - remove,
        )
        .where(activity_table.c.table_name == table)
    )
    return conn.execute(query)
