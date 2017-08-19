from database import connection as conn
from vigo import Boletos
from datetime import datetime as dt

boletos = Boletos(conn, dt(2014, 1, 1), dt(2014, 12, 1), 
                  "EMITIR TODO MES", "'L'", "15")
print boletos.count

for boleto in boletos:
    print boleto
