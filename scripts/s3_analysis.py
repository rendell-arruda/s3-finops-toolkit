import boto3
import logging

from collectors import list_buckets, has_lifecycle, get_buckets_region, get_bucket_size
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

    data = []
    for bucket in buckets:
        name = bucket["Name"]
        created = bucket["CreationDate"]
        arn = bucket["BucketArn"]

        lifecycle = has_lifecycle(s3, name)
        region = get_buckets_region(s3, name)
        size_mb = get_bucket_size(name, region)

        optimization, recomendation = get_optimization_status(size_mb, lifecycle)

        logging.info(
            f"Bucket Name: {name} | Arn: {arn} | Criado em: {created} | Região: {region} | Tamanho: {size_mb} MB | Lifecycle: {lifecycle} | Status: {optimization}"
        )

        data.append(
            {
                "Bucket Name": name,
                "Creation Date": created,
                "Region": region,
                "Size (MB)": size_mb,
                "Has Lifecycle": lifecycle,
                "ARN": arn,
                "Optimization Status": optimization,
                "Recomendation": recomendation,
            }
        )

    export_to_csv(data)
    logging.info(f"total de buckets encontrados: {len(buckets)}")


if __name__ == "__main__":
    main()
