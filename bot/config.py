import os

BOT_TOKEN = os.environ.get("CHINAGUARD_BOT_TOKEN", "")
ADMIN_ID = int(os.environ.get("CHINAGUARD_ADMIN_ID", "0"))
DB_PATH = os.path.join(os.path.dirname(__file__), "orders.db")
REPORT_TEMPLATE = os.path.join(os.path.dirname(__file__), "..", "report", "template.html")
REPORT_STYLE = os.path.join(os.path.dirname(__file__), "..", "report", "style.css")
