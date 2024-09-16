# Challenge Report

## Contact Information

**Name:** Vicente Ignacio Navarrete Ruiz  
**Email:** vicente@bridgeglobal.ai  
**Personal Email:** vicente.navarrete.r@gmail.com  
**GitHub:** [github.com/vnavarrete](https://github.com/vicenteign)  
**LinkedIn:** [linkedin.com/in/vicenav](https://www.linkedin.com/in/vicente-navarrete/)  

## 1. Introduction

### Project Overview:
The goal of this project is to create a machine learning model that can predict flight delays. The project is divided into several parts: model implementation, API development, deployment, and CI/CD integration. The challenge is to demonstrate the ability to build a robust, scalable solution from data processing to deploying the model as an API.

### Dataset Description:
The dataset provided includes information about flights such as airline (`OPERA`), flight type (`TIPOVUELO`), and month (`MES`). These features are used to predict whether a flight will be delayed. Key features include categorical variables like `OPERA` and `TIPOVUELO`, as well as numerical features like `MES`. Initial exploration revealed missing values and irregular formats in some columns, which required preprocessing.

## 2. Part I: Model Implementation

### Transcription of exploration.ipynb to model.py:
The exploration notebook was converted into a Python script (`model.py`). The main challenge was translating the notebook's step-by-step execution into a more modular format with functions that could be reused and tested. This included creating a preprocessing pipeline and defining a model training function.

### Bug Fixes:
During the transcription process, several issues were identified:
- Incorrect column handling during preprocessing.
- The model was not saving properly after training.
These issues were fixed by ensuring consistent use of column names and adding explicit save/load functions for the model.

### Model Selection:
Several models were proposed, including XGBoost and Logistic Regression, with and without class balancing. The final choice was **Logistic Regression** with class balancing. Here’s the comparison of the model performances:

1. **XGBoost with 10 best features and class balancing**:
   - Precision (Class 1): 25%
   - Recall (Class 1): 69%
   - Overall accuracy: 55%
   - This model showed an improvement in recall for the "1" class (delays), which is crucial for identifying more delay cases.

2. **Logistic Regression with 10 best features and class balancing**:
   - Precision (Class 1): 25%
   - Recall (Class 1): 69%
   - Overall accuracy: 55%
   - This model performed similarly to XGBoost, with nearly identical improvements in recall for the "1" class.

3. **Models without class balancing (XGBoost and Logistic Regression)** performed worse, with very low recall for the "1" class, indicating a failure in detecting delayed flights.

The **Logistic Regression** model was selected due to its simplicity, interpretability, and similar performance to XGBoost. Given that the challenge is to build a scalable and interpretable model, Logistic Regression was a better choice in terms of computational efficiency and ease of deployment.

### Programming Practices:
The script follows good programming practices by organizing code into reusable functions, adding error handling for missing or malformed data, and using clear variable names. Additionally, docstrings were added to ensure clarity for future developers.

### Testing:
The model passes all the tests when running `make model-test`. Some initial issues with data formatting during testing were fixed by adding more robust data validation and preprocessing steps.

## 3. Part II: API Development

### Implementation of api.py:
The API was developed using FastAPI. It exposes two main endpoints:
- `/health`: A simple health check endpoint.
- `/predict`: Takes in flight data and returns a prediction of whether the flight will be delayed.

### Handling Requests and Responses:
The API accepts input in JSON format, validates it using Pydantic models, and returns predictions in JSON format. Validation was added to ensure that inputs like month (`MES`) fall within the valid range (1-12) and that categorical fields (`OPERA`, `TIPOVUELO`) have valid values.

### Testing:
The API passes the tests when running `make api-test`. Initially, there were issues with the model not being loaded properly, which were resolved by ensuring the model is loaded during API startup.

## 4. Part III: Deployment

### Cloud Provider Selection:
Google Cloud Platform (GCP) was chosen for deployment due to its robust Cloud Run service, which allows for easy containerized deployments with minimal infrastructure management.

### Deployment Process:
1. **Containerization with Docker**:
   The API was containerized using Docker with the following `Dockerfile`:

    ```dockerfile
    # Use an official Python runtime as a parent image
    FROM python:3.9-slim

    # Set the working directory in the container
    WORKDIR /app

    # Copy the requirements file into the container
    COPY requirements.txt .

    # Install any needed packages specified in requirements.txt
    RUN pip install --no-cache-dir -r requirements.txt

    # Copy the rest of the application code into the container
    COPY . .

    # Expose port 8080 for the API
    EXPOSE 8080

    # Define environment variable for the host
    ENV HOST 0.0.0.0

    # Command to run the application
    CMD ["uvicorn", "challenge.api:app", "--host", "0.0.0.0", "--port", "8080"]
    ```

    This Dockerfile sets up a lightweight Python environment, installs the necessary dependencies, and runs the FastAPI app using Uvicorn. The container exposes port 8080 for the application to communicate with external requests.

2. **Pushing Docker Image to Google Artifact Registry**:
    The Docker image was pushed to Google Artifact Registry using the following commands:
    ```bash
    docker tag delay-api us-central1-docker.pkg.dev/challengevnlatam/challengelatamvnrepo/delay-api
    docker push us-central1-docker.pkg.dev/challengevnlatam/challengelatamvnrepo/delay-api
    ```

3. **Deploying to Google Cloud Run**:
    The container was deployed to Cloud Run using:
    ```bash
    gcloud run deploy delay-api \
    --image us-central1-docker.pkg.dev/challengevnlatam/challengelatamvnrepo/delay-api \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated
    ```

### API URL:
The API is hosted at:

https://delay-api-95188822905.us-central1.run.app

### Stress Testing:
The API passed the stress test (`make stress-test`) without any major issues. Google Cloud Run's autoscaling handled the load effectively. Minor optimizations were made to the container's memory limits to ensure smooth operation under high loads.

## 5. Part IV: CI/CD Implementation

### Setting Up CI/CD Pipelines:
CI/CD was implemented using GitHub Actions. Two workflows were defined:
- **ci.yml**: Runs the tests (`make model-test` and `make api-test`) on every pull request to ensure code quality.
- **cd.yml**: Automatically builds and deploys the Docker container to GCP on every push to the main branch.

### Automation of Tests and Deployment:
The CI/CD pipelines automate the process of running tests and deploying the application to production whenever changes are merged into the main branch.

### Challenges and Resolutions:
Some issues were encountered with authentication during deployment to GCP. These were resolved by configuring service account keys and setting them as secrets in the GitHub repository.

## 6. Conclusion

### Learnings:
This challenge reinforced key skills in:
- Building scalable machine learning models.
- Developing APIs with FastAPI.
- Deploying containerized applications using Docker and GCP.
- Implementing CI/CD pipelines for automated testing and deployment.

### Future Improvements:
Potential improvements include:
- Adding more features to the model to improve prediction accuracy.
- Implementing logging and monitoring in the API to capture usage statistics and detect issues.
- Further optimizing the model for performance in a production environment.

## 7. References

### Resources Used:
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [XGBoost Documentation](https://xgboost.readthedocs.io/en/latest/)