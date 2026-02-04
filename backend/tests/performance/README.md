# Performance Testing

This directory contains performance testing tools for MediNote-AI.

## Load Testing with Locust

[Locust](https://locust.io/) is used for load testing the API endpoints.

### Installation

```bash
pip install locust
```

### Running Load Tests

1. Start the backend server:
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

2. Run Locust:
```bash
cd tests/performance
locust -f locustfile.py --host=http://localhost:8000
```

3. Open the Locust web UI at http://localhost:8089

4. Configure the test:
   - Number of users: Start with 10-50
   - Spawn rate: 1-5 users per second
   - Run time: 5-10 minutes for meaningful results

### Test Scenarios

#### MediNoteUser
Simulates a typical doctor using the system:
- Lists patients (high frequency)
- Searches patients
- Creates new patients
- Views patient details
- Updates patient info
- Checks for duplicate phones

#### ExtractionUser
Tests AI extraction endpoints:
- Extracts patient details from transcripts
- Performs full extraction

### Performance Targets

| Endpoint | Target Response Time (p95) | Target RPS |
|----------|---------------------------|------------|
| GET /patients | < 200ms | 100+ |
| GET /patients/search | < 300ms | 50+ |
| POST /patients | < 500ms | 20+ |
| GET /patients/{id} | < 100ms | 100+ |
| POST /extraction/* | < 5000ms | 5+ |

### Interpreting Results

- **Response Time**: p50 (median) and p95 (95th percentile) are key metrics
- **Requests per Second (RPS)**: Higher is better
- **Failure Rate**: Should be < 1%
- **Users**: Number of concurrent virtual users

### Common Issues

1. **High response times under load**:
   - Check database query performance
   - Add database indexes
   - Implement caching

2. **Connection errors**:
   - Increase database connection pool
   - Check server resources

3. **Timeout errors**:
   - Optimize slow endpoints
   - Consider async processing for heavy tasks

## Database Performance

### Checking Slow Queries

```sql
-- PostgreSQL: Enable slow query logging
ALTER SYSTEM SET log_min_duration_statement = '100';
SELECT pg_reload_conf();

-- View slow queries
SELECT * FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;
```

### Recommended Indexes

```sql
-- Patient search optimization
CREATE INDEX idx_patient_name ON patients (first_name, last_name);
CREATE INDEX idx_patient_phone ON patients (phone_primary);
CREATE INDEX idx_patient_id ON patients (patient_id);
CREATE INDEX idx_patient_status ON patients (status);

-- Visit queries
CREATE INDEX idx_visit_patient ON visits (patient_id);
CREATE INDEX idx_visit_date ON visits (visit_date DESC);

-- Recording sessions
CREATE INDEX idx_recording_session ON recordings (session_id);
```

## Memory and CPU Profiling

### Using py-spy

```bash
pip install py-spy

# Record CPU profile
py-spy record -o profile.svg --pid <PID>

# Top-like view
py-spy top --pid <PID>
```

### Using memory_profiler

```python
from memory_profiler import profile

@profile
def my_function():
    # Your code here
    pass
```

## Continuous Performance Testing

For CI/CD integration, run Locust in headless mode:

```bash
locust -f locustfile.py \
  --host=http://localhost:8000 \
  --headless \
  --users 50 \
  --spawn-rate 5 \
  --run-time 5m \
  --csv=results
```

Check the results:
```bash
# View summary
cat results_stats.csv

# Check for failures
if [ -s results_failures.csv ]; then
  echo "Tests had failures!"
  exit 1
fi
```
