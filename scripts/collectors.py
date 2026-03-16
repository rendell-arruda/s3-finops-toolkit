from datetime import datetime
import boto3
import logging


def list_buckets(s3_client):
    response = s3_client.list_buckets()
    return response.get("Buckets", [])


def has_lifecycle(s3_client, bucket_name):
    try:
        s3_client.get_bucket_lifecycle_configuration(Bucket=bucket_name)
        return "Sim"
    except s3_client.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchLifecycleConfiguration":
            return "Não"
        else:
            return "Erro"


def get_buckets_region(s3_client, bucket_name):
    try:
        response = s3_client.get_bucket_location(Bucket=bucket_name)
        region = response.get("LocationConstraint")
        if region is None:
            return "us-east-1"
        return region
    except Exception as e:
        logging.warning(f"Erro ao obter região do bucket {bucket_name}: {e}")
        return "Desconhecido"


def get_bucket_size(bucket_name, region):
    try:
        cloudwatch = boto3.client("cloudwatch", region_name=region)
        response = cloudwatch.get_metric_statistics(
            Namespace="AWS/S3",
            MetricName="BucketSizeBytes",
            Dimensions=[
                {"Name": "BucketName", "Value": bucket_name},
                {"Name": "StorageType", "Value": "StandardStorage"},
            ],
            StartTime=datetime.now().replace(hour=0, minute=0, second=0),
            EndTime=datetime.now(),
            Period=86400,
            Statistics=["Average"],
        )
        datapoints = response.get("Datapoints", [])
        if datapoints:
            size_bytes = datapoints[-1]["Average"]
            return round(size_bytes / (1024**2), 4)  # Convertendo para MB
        return 0.0
    except Exception as e:
        logging.warning(f"Erro ao obter tamanho do bucket {bucket_name}: {e}")
        return 0.0


def get_storage_class_summary(s3_client, bucket_name):
    # 1. criar o paginator para list_objects_v2
    paginator = s3_client.get_paginator("list_objects_v2")

    # 2. criar um dict vazio para acumular os resultados
    summary = {}
    pages = paginator.paginate(Bucket=bucket_name)
    for page in pages:
        for obj in page.get("Contents", []):
            storage_class = obj.get("StorageClass", "STANDARD")
            size_mb = obj["Size"] / (1024**2)

            if storage_class not in summary:
                summary[storage_class] = {"count": 0, "size_mb": 0.0}

            summary[storage_class]["count"] += 1
            summary[storage_class]["size_mb"] += size_mb

    return summary

    # 3. iterar pelas páginas e objetos

    # 4. retornar o dict
    pass
