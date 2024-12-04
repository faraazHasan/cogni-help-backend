# Common function to format query results
from sqlalchemy import inspect


def format_results(results):
    output = []
    for row in results:
        item_dict = {}
        for obj in row:
            table_name = obj.__table__.name
            column_names = [col.name for col in inspect(obj).mapper.column_attrs]
            item_dict[table_name] = {col: getattr(obj, col) for col in column_names}
        output.append(item_dict)
    return output
