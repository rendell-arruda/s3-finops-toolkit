from datetime import datetime
import csv
import os
import boto3
import logging 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def list_buckets(s3_client):
    response = s3_client.list_buckets()
    return response.get('Buckets', [])

def has_lifecycle(s3_client, bucket_name):
    try: 
        s3_client.get_bucket_lifecycle_configuration(Bucket = bucket_name)
        return "Sim"
    except s3_client.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchLifecycleConfiguration':
            return "Não"
        else:
            return "Erro"

def get_buckets_region(s3_client, bucket_name):
    try:
        response = s3_client.get_bucket_location(Bucket = bucket_name)
        region = response.get('LocationConstraint')
        if region is None:
            return "us-east-1"
        return region
    except Exception as e:
        logging.warning(f"Erro ao obter região do bucket {bucket_name}: {e}")
        return "Desconhecido" 

def get_bucket_size(bucket_name, region):
    try:
        cloudwatch = boto3.client('cloudwatch', region_name=region)
        response = cloudwatch.get_metric_statistics(
            Namespace='AWS/S3',
            MetricName='BucketSizeBytes',
            Dimensions=[
                {
                    'Name': 'BucketName',
                    'Value': bucket_name
                },
                {
                    'Name': 'StorageType',
                    'Value': 'StandardStorage'
                }
            ],
            StartTime=datetime.now().replace(hour=0, minute=0, second=0),
            EndTime=datetime.now(),
            Period=86400,
            Statistics=['Average']
        )
        datapoints = response.get('Datapoints', [])
        if datapoints:
            size_bytes = datapoints[-1]['Average']
            return round(size_bytes / (1024 ** 2), 4)  # Convertendo para MB
        return 0.0
    except Exception as e:        
        logging.warning(f"Erro ao obter tamanho do bucket {bucket_name}: {e}")
        return 0.0
    
def export_to_csv(data):
    reports_dir = os.path.join(BASE_DIR, 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = os.path.join(reports_dir, f"s3_analysis_{timestamp}.csv")

    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)  

    logging.info(f"Relatório exportado para {filename}")  

def main():
    setup_logging()
    logging.info("Iniciando o script para listar buckets S3")

    s3 = boto3.client('s3')
    buckets = list_buckets(s3)
    
    data = []
    for bucket in buckets:
        name = bucket['Name']
        created = bucket['CreationDate']
        arn = bucket['BucketArn']

        lifecycle = has_lifecycle(s3, name)
        region = get_buckets_region(s3, name)
        size_mb = get_bucket_size(name, region)
        
        logging.info(f"Bucket Name: {name} | Arn: {arn} | Criado em: {created} | Região: {region} | Tamanho: {size_mb} MB | Lifecycle: {lifecycle}") 
        data.append({
            'Bucket Name': name,
            'Creation Date': created,
            'Region': region,
            'Size (MB)': size_mb,
            'Has Lifecycle': lifecycle,
            'ARN':arn
        })

    export_to_csv(data)
    logging.info(f"total de buckets encontrados: {len(buckets)}")

if __name__ == "__main__":
    main()