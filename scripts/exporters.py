from datetime import datetime
import csv
import os
import logging

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def export_to_csv(data):
    reports_dir = os.path.join(BASE_DIR, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(reports_dir, f"s3_analysis_{timestamp}.csv")

    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

    logging.info(f"Relatório exportado para {filename}")
