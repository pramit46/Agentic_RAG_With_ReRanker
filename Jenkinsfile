pipeline {
    agent any
    
    environment {
        // AWS ECR Configuration
        AWS_REGION = 'us-east-1'
        ECR_REGISTRY = '797240615162.dkr.ecr.us-east-1.amazonaws.com'
        ECR_REPOSITORY = 'agentic_rag_with_re-ranker'
        IMAGE_TAG = "${BUILD_NUMBER}"
        
        // Docker image full name
        DOCKER_IMAGE = "${ECR_REGISTRY}/${ECR_REPOSITORY}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                checkout scm
            }
        }
        
        stage('Build Info') {
            steps {
                script {
                    echo "Building Docker image: ${DOCKER_IMAGE}:${IMAGE_TAG}"
                    echo "AWS Region: ${AWS_REGION}"
                    echo "Build Number: ${BUILD_NUMBER}"
                }
            }
        }
        
        stage('AWS ECR Login') {
            steps {
                script {
                    echo 'Logging in to AWS ECR...'
                    // Get ECR login password and authenticate Docker
                    sh '''
                        aws ecr get-login-password --region ${AWS_REGION} | \
                        docker login --username AWS --password-stdin ${ECR_REGISTRY}
                    '''
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    echo 'Building Docker image...'
                    sh """
                        docker build -t ${DOCKER_IMAGE}:${IMAGE_TAG} .
                        docker tag ${DOCKER_IMAGE}:${IMAGE_TAG} ${DOCKER_IMAGE}:latest
                    """
                }
            }
        }
        
        stage('Push to ECR') {
            steps {
                script {
                    echo 'Pushing Docker image to AWS ECR...'
                    sh """
                        docker push ${DOCKER_IMAGE}:${IMAGE_TAG}
                        docker push ${DOCKER_IMAGE}:latest
                    """
                }
            }
        }
        
        stage('Cleanup') {
            steps {
                script {
                    echo 'Cleaning up local Docker images...'
                    sh """
                        docker rmi ${DOCKER_IMAGE}:${IMAGE_TAG} || true
                        docker rmi ${DOCKER_IMAGE}:latest || true
                    """
                }
            }
        }
    }
    
    post {
        success {
            echo '✅ Docker image successfully built and pushed to ECR!'
            echo "Image: ${DOCKER_IMAGE}:${IMAGE_TAG}"
            echo "Latest: ${DOCKER_IMAGE}:latest"
        }
        failure {
            echo '❌ Pipeline failed! Check the logs above for details.'
        }
        always {
            // Logout from Docker (security best practice)
            sh 'docker logout ${ECR_REGISTRY} || true'
        }
    }
}
