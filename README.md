# D-Wave Quantum Data Integration

This repository scrapes data from D-Wave Quantum Computing regarding "parallel processing", "pattern recognition", and "quantum computing", and stores it in a Render PostgreSQL database.

## Scraped Data
A JSON file (`scraped_data.json`) containing the scraped text from 53 valid D-Wave URLs is included.

## Render Database Setup
A Render PostgreSQL database named `dwave-quantum-data` has been provisioned.

To insert the data into your Render database:
1. Ensure your local IP is whitelisted on the Render PostgreSQL dashboard if running locally, OR run this as a Render Background Job.
2. Set the `DATABASE_URL` environment variable to your Render internal or external connection string.
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `python3 render_job.py`
