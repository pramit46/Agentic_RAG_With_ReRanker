# 🦊 GitLab CI/CD Pipeline for AWS ECR

This guide explains how to set up GitLab CI/CD to automatically build your Docker image and push it to AWS ECR.

## 📋 Prerequisites

### 1. GitLab Runner
You need a GitLab Runner with Docker executor. If you're using GitLab.com, shared runners are available. For self-hosted:

```bash
# Install GitLab Runner (Ubuntu/Debian)
curl -L "https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh" | sudo bash
sudo apt-get install gitlab-runner

# Install GitLab Runner (macOS)
brew install gitlab-runner

# Register the runner
sudo gitlab-runner register
```

During registration:
- **GitLab URL**: Your GitLab instance URL
- **Registration token**: From GitLab project → Settings → CI/CD → Runners
- **Executor**: `docker`
- **Default image**: `docker:24-cli`

### 2. AWS Credentials in GitLab
Store AWS credentials as GitLab CI/CD variables:

1. Go to your GitLab project
2. Navigate to **Settings → CI/CD → Variables**
3. Add these variables:

| Variable | Value | Protected | Masked | Type |
|----------|-------|-----------|--------|------|
| `AWS_ACCESS_KEY_ID` | Your AWS access key | ✅ | ✅ | Variable |
| `AWS_SECRET_ACCESS_KEY` | Your AWS secret key | ✅ | ✅ | Variable |
| `AWS_DEFAULT_REGION` | `us-east-1` | ❌ | ❌ | Variable |

**Important**: Enable "Protected" and "Masked" for security!

## 📁 Pipeline File

The [.gitlab-ci.yml](.gitlab-ci.yml) file is already created with three stages:

### 1. **Build Stage**
- Builds Docker image using Docker-in-Docker (DinD)
- Tags with commit SHA and 'latest'
- Saves images as artifacts

### 2. **Push Stage**
- Loads built images from artifacts
- Authenticates with AWS ECR
- Pushes both tagged versions to ECR

### 3. **Verify Stage**
- Confirms image exists in ECR
- Provides verification output

## 🚀 Setting Up Your GitLab Project

### Step 1: Push Code to GitLab

```bash
# If not already a git repository
git init
git add .
git commit -m "Initial commit with GitLab CI/CD pipeline"

# Add GitLab remote (replace with your repo URL)
git remote add origin git@gitlab.com:your-username/agentic-rag.git

# Push to GitLab
git push -u origin main
```

### Step 2: Configure CI/CD Variables

1. Go to **Settings → CI/CD → Variables**
2. Click **Add variable**
3. Add the AWS credentials (see table above)

### Step 3: Enable GitLab Runner

1. Go to **Settings → CI/CD → Runners**
2. Either:
   - Enable shared runners (if using GitLab.com)
   - Register a specific runner (if self-hosted)

### Step 4: Trigger Pipeline

The pipeline runs automatically on:
- Push to `main` branch
- Push to `develop` branch
- Creating tags
- Merge requests (build only, no push)

**Manual trigger:**
1. Go to **CI/CD → Pipelines**
2. Click **Run pipeline**
3. Select branch and click **Run pipeline**

## 📊 Monitoring Pipeline

### View Pipeline Status

1. Go to **CI/CD → Pipelines**
2. Click on a pipeline to see stages
3. Click on a job to see logs

### Pipeline Badges

Add pipeline status badge to README:

```markdown
[![Pipeline Status](https://gitlab.com/your-username/agentic-rag/badges/main/pipeline.svg)](https://gitlab.com/your-username/agentic-rag/-/pipelines)
```

## 🔧 Pipeline Configuration Options

### Build Only Specific Branches

Edit `.gitlab-ci.yml`:

```yaml
only:
  - main           # Only main branch
  - /^release-.*$/ # All release branches
```

### Add Automatic Versioning

Use GitLab tags for versioning:

```yaml
variables:
  IMAGE_TAG: ${CI_COMMIT_TAG:-$CI_COMMIT_SHORT_SHA}
```

Then create tags:
```bash
git tag v1.0.0
git push origin v1.0.0
```

### Add Slack/Email Notifications

Add to `.gitlab-ci.yml`:

```yaml
notify:
  stage: .post
  script:
    - 'curl -X POST -H "Content-type: application/json" --data "{\"text\":\"✅ Build $CI_COMMIT_SHORT_SHA completed!\"}" $SLACK_WEBHOOK_URL'
  only:
    - main
```

## 🐛 Troubleshooting

### Issue: "ERROR: Cannot connect to the Docker daemon"

**Solution**: Ensure Docker-in-Docker service is running:

```yaml
services:
  - docker:24-dind

variables:
  DOCKER_TLS_CERTDIR: "/certs"
```

### Issue: "AccessDenied" when pushing to ECR

**Solution**: 
1. Verify AWS credentials in GitLab variables
2. Check IAM permissions (use [ecr-iam-policy.json](ecr-iam-policy.json))
3. Ensure ECR repository exists:

```bash
aws ecr describe-repositories \
  --repository-names agentic_rag_with_re-ranker \
  --region us-east-1
```

### Issue: "Runner not picking up jobs"

**Solution**:
1. Check runner status: `sudo gitlab-runner status`
2. Verify runner is registered: Go to **Settings → CI/CD → Runners**
3. Check runner tags match job tags
4. Restart runner: `sudo gitlab-runner restart`

### Issue: "Pipeline fails on merge requests"

**Solution**: MR builds don't need ECR push. The pipeline already handles this:

```yaml
build-mr:
  stage: build
  only:
    - merge_requests
  # Builds but doesn't push
```

## 🎯 Advanced Features

### Parallel Builds

Build for multiple architectures:

```yaml
build-amd64:
  stage: build
  script:
    - docker build --platform linux/amd64 -t $IMAGE_FULL:$IMAGE_TAG-amd64 .

build-arm64:
  stage: build
  script:
    - docker build --platform linux/arm64 -t $IMAGE_FULL:$IMAGE_TAG-arm64 .
```

### Scheduled Pipelines

Set up nightly builds:
1. Go to **CI/CD → Schedules**
2. Click **New schedule**
3. Set interval (e.g., "0 2 * * *" for 2 AM daily)
4. Select target branch

### Cache Docker Layers

Speed up builds with caching:

```yaml
build:
  cache:
    key: ${CI_COMMIT_REF_SLUG}
    paths:
      - .docker-cache/
  script:
    - docker build --cache-from $IMAGE_FULL:latest -t $IMAGE_FULL:$IMAGE_TAG .
```

### Multi-Environment Deployment

```yaml
deploy-dev:
  stage: deploy
  script:
    - echo "Deploying to dev..."
  environment:
    name: development
  only:
    - develop

deploy-prod:
  stage: deploy
  script:
    - echo "Deploying to production..."
  environment:
    name: production
  only:
    - main
  when: manual  # Requires manual approval
```

## 🔒 Security Best Practices

### 1. Use Protected Branches
- Go to **Settings → Repository → Protected Branches**
- Protect `main` and `develop` branches
- Require merge request approvals

### 2. Scan Images for Vulnerabilities

Add security scanning stage:

```yaml
security-scan:
  stage: verify
  image: aquasec/trivy:latest
  script:
    - trivy image --severity HIGH,CRITICAL $IMAGE_FULL:$IMAGE_TAG
  allow_failure: true
```

### 3. Sign Images

Use Docker Content Trust:

```yaml
variables:
  DOCKER_CONTENT_TRUST: 1
```

### 4. Rotate AWS Credentials

Regularly update AWS credentials in GitLab variables.

## 📈 Performance Optimization

### Use Kaniko (Faster builds, no Docker required)

Replace Docker-in-Docker with Kaniko:

```yaml
build:
  stage: build
  image:
    name: gcr.io/kaniko-project/executor:debug
    entrypoint: [""]
  script:
    - echo "{\"auths\":{\"$ECR_REGISTRY\":{\"auth\":\"$(echo -n AWS:$(aws ecr get-login-password --region $AWS_REGION) | base64)\"}}}" > /kaniko/.docker/config.json
    - /kaniko/executor --context . --dockerfile Dockerfile --destination $IMAGE_FULL:$IMAGE_TAG --destination $IMAGE_FULL:latest
```

Benefits:
- ✅ No privileged mode required
- ✅ Better layer caching
- ✅ Faster builds

## 🎉 Comparison: GitLab vs Jenkins

| Feature | GitLab CI/CD | Jenkins |
|---------|--------------|---------|
| **Configuration** | `.gitlab-ci.yml` in repo | `Jenkinsfile` in repo |
| **Setup** | Built-in, minimal setup | Requires installation & plugins |
| **UI** | Integrated with GitLab | Separate Jenkins interface |
| **Runners** | GitLab Runners | Jenkins agents |
| **Secrets** | GitLab CI/CD Variables | Jenkins Credentials |
| **Artifacts** | Native support | Plugin required |
| **Auto DevOps** | ✅ Yes | ❌ No |

## ✅ Success Checklist

- [ ] `.gitlab-ci.yml` file in repository
- [ ] AWS credentials added to GitLab CI/CD variables
- [ ] GitLab Runner configured and active
- [ ] ECR repository exists
- [ ] First pipeline run successful
- [ ] Image visible in ECR

## 🚀 Next Steps

After successful setup:

1. **Pull and run your image:**
   ```bash
   docker pull 797240615162.dkr.ecr.us-east-1.amazonaws.com/agentic_rag_with_re-ranker:latest
   docker run -it --rm 797240615162.dkr.ecr.us-east-1.amazonaws.com/agentic_rag_with_re-ranker:latest
   ```

2. **Deploy to Kubernetes/ECS:**
   - Use the ECR image in your deployment manifests
   - Configure auto-deployment on successful builds

3. **Set up monitoring:**
   - Track pipeline success rates
   - Monitor image sizes and build times
   - Set up alerts for failed builds

---

**ECR Repository**: `797240615162.dkr.ecr.us-east-1.amazonaws.com/agentic_rag_with_re-ranker`  
**Region**: `us-east-1`  
**GitLab Docs**: https://docs.gitlab.com/ee/ci/
