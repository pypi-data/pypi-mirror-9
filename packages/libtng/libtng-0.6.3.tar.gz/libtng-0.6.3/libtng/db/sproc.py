from sqlalchemy import func


def mapsp(name, schema='public', scalar=True):
    """
    Maps a stored procedure to a Python function.

    Args:
        name: the stored procedure name.
        schema: the schema holding the name of the schema holding
            the stored procedure.

    Returns:
        object: a callable that executes the stored procedure.
    """
    schema_qualified = getattr(getattr(func, schema), name)
    return lambda session, *args: session.execute(schema_qualified(*args))