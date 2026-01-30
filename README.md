# Credit Approval System

This is a backend application built using Django and Django REST Framework to manage customer credit approval and loans.  
It stores data in PostgreSQL, reads initial customer and loan data from Excel files, and exposes REST APIs for registering customers, checking loan eligibility, creating loans, and viewing loan details.  
The entire application, including the database, runs using Docker with a single command.

---

## Tech Stack

- Python 3.14
- Django 4+
- Django REST Framework
- PostgreSQL
- Docker & Docker Compose
- Pandas (for Excel data ingestion)

---

## Project Structure
```bash
credit_system/
├── credit_system/          # Django project settings
├── core/                   # Core app (models, views, serializers, urls)
├── data_files/             # Excel files for initial data ingestion
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```
---

## Running the Application (Docker)

### Build and start containers

```bash
docker-compose up --build
```
**Startup Flow:**

    1. Docker Compose builds the Django image and installs all dependencies.
    2. The PostgreSQL database container starts and becomes ready.
    3. Django applies database migrations to create required tables.
    4. Initial customer and loan data is loaded from Excel files.
    5. The Django server starts and all APIs become available.

No additional setup or manual commands are required after this.

 The application will be available at:
```
http://localhost:8000
```

---

## API Endpoints

### Register Customer
```text
POST http://localhost:8000/api/register
```

### Check Loan Eligibility
```text
POST http://localhost:8000/api/check-eligibility
```

### Create Loan
```text
POST http://localhost:8000/api/create-loan
```

### View Loan by Loan ID
```text
GET http://localhost:8000/api/view-loan/<loan_id>
```

### View Loans by Customer ID
```text
GET http://localhost:8000/api/view-loans/<customer_id>
```

---

## Loan Eligibility Logic

The loan eligibility check is based on the customer’s existing loan history and current financial capacity.

The decision follows these steps:

1. **Approved limit check**
   - If the total amount of existing loans exceeds the customer’s approved credit limit, the loan is rejected.

2. **Repayment history**
   - Customers with unpaid or late EMIs receive a lower credit score.

3. **Number of existing loans**
   - Each additional active loan slightly reduces the credit score.

4. **Recent loan activity**
   - Loans taken in the current year reduce the credit score further.

5. **EMI burden check**
   - If total monthly EMIs exceed 50% of the customer’s monthly salary, the loan is rejected.

6. **Interest rate adjustment**
   - Based on the final credit score:
     - Good score → original interest rate
     - Medium score → interest rate increased
     - Low score → loan rejected

7. **Monthly installment calculation**
   - If approved, the monthly installment is calculated using standard EMI formula.




---

## Testing

Basic API tests are included and can be run using:

+ `docker-compose exec web bash`
+ `cd credit_system`
+ `python manage.py test`

---

## Notes

- Backend-only system
- Root URL (`/`) is intentionally not exposed
- API contracts are independent of database schema
- APIs tested using Postman
- Application is fully containerized and runs with a single Docker Compose command
- Database migrations and initial data ingestion run automatically on startup
- Designed to be easy to set up and test on any machine using Docker

