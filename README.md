# 🪣 S3 FinOps Toolkit

Conjunto de scripts Python para análise e otimização de custos em buckets S3 com foco em FinOps.

---

## 📦 Scripts disponíveis

### `s3_analysis.py`
Faz o inventário completo dos buckets S3 da conta AWS e exporta um relatório CSV com informações de custo e governança.

**O que coleta:**
- Nome do bucket
- Data de criação
- Região
- Tamanho em MB
- Status de lifecycle policy

---

## 🛠 Pré-requisitos

- Python 3.10+
- AWS CLI configurado com credenciais válidas (`~/.aws/credentials`)
- Permissões IAM necessárias:
  - `s3:ListAllMyBuckets`
  - `s3:GetBucketLocation`
  - `s3:GetLifecycleConfiguration`
  - `cloudwatch:GetMetricStatistics`

---

## 📦 Instalação
```bash
pip install -r requirements.txt
```

---

## ▶️ Como rodar
```bash
python3 scripts/s3_analysis.py
```

---

## 📁 Output

O relatório é gerado automaticamente em `scripts/reports/` com timestamp:
```
s3_analysis_20260304_193000.csv
```

| Coluna | Descrição |
|---|---|
| Bucket Name | Nome do bucket |
| Creation Date | Data de criação |
| Region | Região AWS |
| Size (MB) | Tamanho em MB |
| Has Lifecycle | Se tem lifecycle policy configurada |

---

## 💡 Insight FinOps

Buckets sem lifecycle policy acumulam objetos indefinidamente, gerando custo crescente sem controle. Use o relatório para identificar e priorizar quais buckets precisam de política de ciclo de vida.

---

## 🗺 Roadmap

- [x] Inventário de buckets com lifecycle e tamanho
- [ ] Análise de storage class inadequada
- [ ] Identificação de objetos sem acesso recente
- [ ] Geração automática de lifecycle policies
```

Salva, commita e sobe:
```
docs: add README with usage instructions and roadmap