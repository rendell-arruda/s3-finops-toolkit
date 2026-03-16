import boto3
import logging

from collectors import (
    list_buckets,
    has_lifecycle,
    get_buckets_region,
    get_bucket_size,
    get_storage_class_summary,
)

from analyzers import get_optimization_status
from exporters import export_to_csv


def setup_logging():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )


def main():
    setup_logging()
    logging.info("Iniciando o script para listar buckets S3")

    s3 = boto3.client("s3")
    buckets = list_buckets(s3)

    resultados = []
    for bucket in buckets:
        name = bucket["Name"]
        created = bucket["CreationDate"]
        arn = bucket["BucketArn"]

        lifecycle = has_lifecycle(s3, name)
        region = get_buckets_region(s3, name)
        size_mb = get_bucket_size(name, region)

        optimization, recomendation = get_optimization_status(size_mb, lifecycle)
        storage_summary = get_storage_class_summary(s3, name)

        logging.info(
            f"Bucket Name: {name} | Arn: {arn} | Criado em: {created} | Região: {region} | Tamanho: {size_mb} MB | Lifecycle: {lifecycle} | Status: {optimization}"
        )

        resultados.append(
            {
                "name": name,
                "created": created,
                "arn": arn,
                "lifecycle": lifecycle,
                "region": region,
                "size_mb": size_mb,
                "optimization": optimization,
                "recomendation": recomendation,
                "storage": storage_summary,
            }
        )
    todas_classes = set()
    for r in resultados:
        for classe in r["storage"].keys():
            todas_classes.add(classe)

    data = []
    for r in resultados:
        row = {
            "Bucket Name": r["name"],
            "Creation Date": r["created"],
            "Region": r["region"],
            "Size (MB)": r["size_mb"],
            "Has Lifecycle": r["lifecycle"],
            "ARN": r["arn"],
            "Optimization Status": r["optimization"],
            "Recomendation": r["recomendation"],
        }
        for classe in todas_classes:
            info = r["storage"].get(classe, {"count": 0, "size_mb": 0.0})
            row[f"{classe}_count"] = info["count"]
            row[f"{classe}_size_mb"] = round(info["size_mb"], 4)

        data.append(row)

    export_to_csv(data)
    logging.info(f"total de buckets encontrados: {len(buckets)}")


if __name__ == "__main__":
    main()
