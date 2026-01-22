from backend.db import engine, Base
from backend.models import PaymentLog

print("Creating payment_logs table...")
PaymentLog.__table__.create(engine)
print("Done.")
