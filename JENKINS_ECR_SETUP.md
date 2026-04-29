# 🔧 Jenkins CI/CD Pipeline for AWS ECR

This guide explains how to set up Jenkins to automatically build your Docker image and push it to AWS ECR.

## 📋 Prerequisites

### 1. Jenkins Installation
Ensure Jenkins is installed and running on your machine:
```bash
# Check if Jenkins is running
curl http://localhost:8080
```

### 2. Required Jenkins Plugins
Install these plugins in Jenkins (Manage Jenkins → Plugin Manager):
- **Docker Pipeline** - For Docker build/push operations
- **AWS Steps** - For AWS CLI operations (optional, but helpful)
- **Pipeline** - For pipeline support
- **Git** - For source code management

### 3. AWS CLI Installation
Jenkins needs AWS CLI to authenticate with ECR:

```bash
# macOS
brew install awscli

# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Verify installation
aws --version
```

### 4. Docker Access
Ensure Jenkins user has Docker permissions:

```bash
# Add Jenkins user to docker group
sudo usermod -aG docker jenkins

# Restart Jenkins
sudo systemctl restart jenkins
```

## 🔐 AWS Credentials Setup

### Option 1: AWS Credentials File (Recommended for Local Jenkins)

1. **Configure AWS credentials on your machine:**

```bash
aws configure
```

Enter:
- AWS Access Key ID
- AWS Secret Access Key
- Default region: `us-east-1`
- Default output format: `json`

2. **Copy credentials to Jenkins user:**

```bash
# If running Jenkins as jenkins user
sudo cp -r ~/.aws /var/lib/jenkins/
sudo chown -R jenkins:jenkins /var/lib/jenkins/.aws
```

### Option 2: Jenkins Credentials (Recommended for Shared Jenkins)

1. Go to **Jenkins Dashboard → Manage Jenkins → Credentials**
2. Click **Add Credentials**
3. Select **AWS Credentials** type
4. Enter:
   - **ID**: `aws-credentials`
   - **Access Key ID**: Your AWS access key
   - **Secret Access Key**: Your AWS secret key
5. Click **OK**

Then update the Jenkinsfile to use credentials:

```groovy
stage('AWS ECR Login') {
    steps {
        withCredentials([
            [
                $class: 'AmazonWebServicesCredentialsBinding',
                credentialsId: 'aws-credentials'
            ]
        ]) {
            sh '''
                aws ecr get-login-password --region ${AWS_REGION} | \
                docker login --username AWS --password-stdin ${ECR_REGISTRY}
            '''
        }
    }
}
```

## 🚀 Creating the Jenkins Pipeline

### Method 1: Pipeline from SCM (Recommended)

1. **Create a new Jenkins Pipeline job:**
   - Go to Jenkins Dashboard
   - Click **New Item**
   - Enter name: `Agentic-RAG-ECR-Build`
   - Select **Pipeline**
   - Click **OK**

2. **Configure the pipeline:**
   - Scroll to **Pipeline** section
   - Select **Pipeline script from SCM**
   - **SCM**: Git (or your version control)
   - **Repository URL**: Your repository URL (or local path)
   - **Script Path**: `Jenkinsfile`
   - Click **Save**

### Method 2: Direct Pipeline Script

1. Create a new Pipeline job as above
2. In **Pipeline** section, select **Pipeline script**
3. Copy the contents of `Jenkinsfile` into the script box
4. Click **Save**

## 📦 ECR Repository Setup

Ensure your ECR repository exists:

```bash
# Create ECR repository (if not exists)
aws ecr create-repository \
    --repository-name agentic_rag_with_re-ranker \
    --region us-east-1

# Verify repository exists
aws ecr describe-repositories \
    --repository-names agentic_rag_with_re-ranker \
    --region us-east-1
```

## ▶️ Running the Pipeline

### Manual Build

1. Go to your Jenkins job
2. Click **Build Now**
3. Click on the build number (e.g., #1) to see progress
4. View **Console Output** for detailed logs

### Automatic Builds

Configure triggers in your Jenkins job:
- **Poll SCM**: Check for changes periodically
- **GitHub webhook**: Trigger on git push
- **Build periodically**: Scheduled builds

Example Poll SCM (check every 5 minutes):
```
H/5 * * * *
```

## 🔍 Verifying the Push

After successful build, verify the image in ECR:

```bash
# List images in ECR repository
aws ecr list-images \
    --repository-name agentic_rag_with_re-ranker \
    --region us-east-1

# Get image details
aws ecr describe-images \
    --repository-name agentic_rag_with_re-ranker \
    --region us-east-1
```

## 📥 Pulling the Image from ECR

On any machine with AWS credentials:

```bash
# Authenticate Docker with ECR
aws ecr get-login-password --region us-east-1 | \
    docker login --username AWS --password-stdin \
    797240615162.dkr.ecr.us-east-1.amazonaws.com

# Pull the image
docker pull 797240615162.dkr.ecr.us-east-1.amazonaws.com/agentic_rag_with_re-ranker:latest

# Or specific build
docker pull 797240615162.dkr.ecr.us-east-1.amazonaws.com/agentic_rag_with_re-ranker:1
```

## 🎯 Running the Image from ECR

```bash
# Run with Docker Compose (update docker-compose.yml)
services:
  rag-app:
    image: 797240615162.dkr.ecr.us-east-1.amazonaws.com/agentic_rag_with_re-ranker:latest
    # ... rest of configuration

# Or run directly
docker run -it --rm \
    --network rag-network \
    -e NEO4J_URI=bolt://neo4j:7687 \
    -e LLM_PROVIDER=ollama \
    797240615162.dkr.ecr.us-east-1.amazonaws.com/agentic_rag_with_re-ranker:latest
```

## 🐛 Troubleshooting

### Issue: "Cannot connect to Docker daemon"

**Solution:**
```bash
# Add Jenkins user to docker group
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

### Issue: "AWS CLI not found"

**Solution:**
```bash
# Find AWS CLI path
which aws

# If not in Jenkins PATH, update Jenkinsfile:
environment {
    PATH = "/usr/local/bin:${env.PATH}"
}
```

### Issue: "Access Denied" when pushing to ECR

**Solution:**
```bash
# Verify AWS credentials
aws sts get-caller-identity

# Check ECR permissions
aws ecr get-authorization-token --region us-east-1

# Ensure IAM user has these permissions:
# - ecr:GetAuthorizationToken
# - ecr:BatchCheckLayerAvailability
# - ecr:PutImage
# - ecr:InitiateLayerUpload
# - ecr:UploadLayerPart
# - ecr:CompleteLayerUpload
```

### Issue: "Docker build fails due to missing files"

**Solution:**
Ensure `.dockerignore` is properly configured and all required files are present:
```bash
# Check what Docker sees
docker build --no-cache -t test .
```

## 🔒 Security Best Practices

1. **Use IAM roles** instead of access keys when possible
2. **Rotate credentials** regularly
3. **Use ECR lifecycle policies** to clean up old images:

```bash
# Create lifecycle policy to keep last 10 images
aws ecr put-lifecycle-policy \
    --repository-name agentic_rag_with_re-ranker \
    --lifecycle-policy-text '{
        "rules": [{
            "rulePriority": 1,
            "description": "Keep last 10 images",
            "selection": {
                "tagStatus": "any",
                "countType": "imageCountMoreThan",
                "countNumber": 10
            },
            "action": {
                "type": "expire"
            }
        }]
    }'
```

4. **Scan images** for vulnerabilities:

```bash
aws ecr start-image-scan \
    --repository-name agentic_rag_with_re-ranker \
    --image-id imageTag=latest \
    --region us-east-1
```

## 📊 Advanced: Multi-Stage Pipeline

For more complex workflows, extend the Jenkinsfile:

```groovy
stage('Test') {
    steps {
        script {
            echo 'Running tests...'
            sh 'docker run --rm ${DOCKER_IMAGE}:${IMAGE_TAG} python -m pytest'
        }
    }
}

stage('Security Scan') {
    steps {
        script {
            echo 'Scanning for vulnerabilities...'
            sh '''
                aws ecr start-image-scan \
                    --repository-name ${ECR_REPOSITORY} \
                    --image-id imageTag=${IMAGE_TAG} \
                    --region ${AWS_REGION}
            '''
        }
    }
}

stage('Deploy to Dev') {
    steps {
        script {
            echo 'Deploying to development environment...'
            // Add your deployment logic here
        }
    }
}
```

## 🎉 Success!

Once configured, your Jenkins pipeline will:
1. ✅ Checkout your code
2. ✅ Build the Docker image
3. ✅ Tag with build number and 'latest'
4. ✅ Push to AWS ECR
5. ✅ Clean up local images

Each build creates a versioned image that's ready to deploy!

---

**ECR Repository**: `797240615162.dkr.ecr.us-east-1.amazonaws.com/agentic_rag_with_re-ranker`  
**Region**: `us-east-1`  
**Tags**: `latest`, `1`, `2`, `3`, etc.
