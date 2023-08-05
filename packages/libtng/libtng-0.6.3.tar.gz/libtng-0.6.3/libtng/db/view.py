from sqlalchemy import Table
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import Executable
from sqlalchemy.sql.expression import  ClauseElement



class View(Executable, ClauseElement):

    def __init__(self, name, query):
        self.name = name
        self.select = query



@compiles(View)
def visit_create_view(element, compiler, **kw):
    return "CREATE VIEW IF NOT EXISTS {0} AS {1}"\
        .format(element.name, compiler.process(element.query, literal_binds=True))