# 📈 Stock Data Pipeline with Apache Airflow and PostgreSQL

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-2.7+-orange.svg)](https://airflow.apache.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-20.10+-blue.svg)](https://www.docker.com/)

A robust data pipeline to fetch stock market data from external APIs and store it in PostgreSQL using Apache Airflow for orchestration.

## 🚀 Features

- Automated stock data fetching from configurable APIs
- Data validation and duplicate handling with UPSERT operations
- Error handling with retry logic and comprehensive logging
- Scalable architecture with connection pooling and batch processing
- Fully containerized with Docker Compose
- Scheduled ETL workflows via Airflow DAG

## 📁 Project Structure

```
stock-data-pipeline/
├── dags/
│   └── stock_dag.py              # Airflow DAG definition
├── scripts/
│   └── fetch_stock_data.py       # ETL logic
├── .env                          # Environment variables
├── docker-compose.yml            # Services definition
├── requirements.txt              # Python dependencies
└── README.md
```

## ⚙️ Quick Start

### Prerequisites
- Docker & Docker Compose installed
- Ports 5432 and 8080 available

### Setup

1. **Clone and configure**:
   ```bash
   git clone https://github.com/yourusername/stock-data-pipeline.git
   cd stock-data-pipeline
   ```

2. **Create `.env` file**:
   ```env
   API_URL=https://api.example.com/stocks
   API_KEY=your_api_key_here
   DB_HOST=postgres
   DB_NAME=stocks
   DB_USER=airflow
   DB_PASSWORD=airflow_password
   BATCH_SIZE=500
   MAX_RETRIES=3
   ```

3. **Deploy**:
   ```bash
   docker-compose up --build -d
   ```

4. **Access Airflow UI**: http://localhost:8080
   - Username: `airflow`
   - Password: `airflow`

## 🗃️ Database Schema

```sql
CREATE TABLE stock_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    volume BIGINT,
    date DATE NOT NULL,
    timestamp_utc TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, date)
);
```

## 📊 Usage

1. Enable the `stock_data_pipeline` DAG in Airflow UI
2. DAG runs hourly by default
3. Manual trigger: Click "Trigger DAG" button
4. Monitor logs and progress in the Airflow UI

## 🧪 Testing

```bash
# Test database connection
docker-compose exec postgres psql -U airflow -d stocks -c "SELECT COUNT(*) FROM stock_data;"

# Check API connectivity
curl $API_URL
```

## 🔧 Configuration

- **Schedule**: Modify `schedule_interval` in `stock_dag.py`
- **API Source**: Update `API_URL` and format in `.env`
- **Batch Size**: Adjust `BATCH_SIZE` for performance tuning


## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Built with ❤️ by [Your Name]**
