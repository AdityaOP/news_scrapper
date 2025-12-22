import pandas as pd
from datetime import datetime
from config import OUTPUT_FILE

def save_excel(records):
    df = pd.DataFrame(records)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # If OUTPUT_FILE = "digital_health_news.xlsx"
    base_name = OUTPUT_FILE.replace(".xlsx", "")
    file_name = f"{base_name}_{timestamp}.xlsx"

    df.to_excel(file_name, index=False)
    print(f"✅ Saved {len(records)} articles to {file_name}")