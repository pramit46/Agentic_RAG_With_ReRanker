# 🔄 CI/CD Options Comparison

This project supports both **Jenkins** and **GitLab CI/CD** for building and pushing Docker images to AWS ECR.

## 📊 Quick Comparison

| Feature | Jenkins | GitLab CI/CD |
|---------|---------|--------------|
| **Configuration File** | `Jenkinsfile` | `.gitlab-ci.yml` |
| **Setup Complexity** | Medium | Easy |
| **Prerequisites** | Jenkins server, plugins | GitLab Runner |
| **AWS Authentication** | AWS CLI + credentials | CI/CD variables |
| **Build Artifacts** | Workspace-based | Built-in artifact system |
| **UI Integration** | Separate Jenkins UI | Native GitLab UI |
| **Cost** | Free (self-hosted) | Free tier available |
| **Best For** | Existing Jenkins setup | GitLab users |

## 🚀 Which Should You Use?

### Choose **Jenkins** if:
- ✅ You already have Jenkins infrastructure
- ✅ You need complex, custom workflows
- ✅ You want standalone CI/CD server
- ✅ You use multiple Git providers (GitHub, Bitbucket, GitLab)
- ✅ You need extensive plugin ecosystem

### Choose **GitLab CI/CD** if:
- ✅ Your code is on GitLab
- ✅ You want integrated CI/CD in one platform
- ✅ You prefer configuration-as-code in repo
- ✅ You want simpler setup with less maintenance
- ✅ You need Auto DevOps features

## 📁 Files for Each Option

### Jenkins Pipeline
```
├── Jenkinsfile                 # Pipeline definition
├── JENKINS_ECR_SETUP.md        # Setup guide
└── ecr-iam-policy.json         # IAM permissions
```

**Quick Start:**
```bash
# See JENKINS_ECR_SETUP.md for full instructions
1. Install Jenkins + Docker
2. Configure AWS credentials
3. Create Pipeline job pointing to Jenkinsfile
4. Run build
```

### GitLab CI/CD
```
├── .gitlab-ci.yml              # Pipeline definition
└── GITLAB_CI_SETUP.md          # Setup guide
```

**Quick Start:**
```bash
# See GITLAB_CI_SETUP.md for full instructions
1. Push code to GitLab
2. Add AWS credentials to CI/CD variables
3. Enable GitLab Runner
4. Pipeline runs automatically
```

## 🎯 Common Setup (Both Options)

Both pipelines require:

### 1. AWS ECR Repository
```bash
aws ecr create-repository \
    --repository-name agentic_rag_with_re-ranker \
    --region us-east-1
```

### 2. AWS IAM Permissions
Attach the policy from `ecr-iam-policy.json` to your IAM user/role:

```bash
aws iam put-user-policy \
    --user-name your-user \
    --policy-name ECR-Push-Policy \
    --policy-document file://ecr-iam-policy.json
```

### 3. Docker Installed
Both need Docker to build images.

### 4. AWS Credentials
Configure access key and secret key.

## 🔄 Pipeline Stages Comparison

### Jenkins Pipeline Stages
```
1. Checkout         → Clone repository
2. Build Info       → Display build metadata
3. AWS ECR Login    → Authenticate with ECR
4. Build Image      → docker build
5. Push to ECR      → docker push
6. Cleanup          → Remove local images
```

### GitLab CI/CD Stages
```
1. Build            → docker build + save artifacts
2. Push             → Load images + push to ECR
3. Verify           → Confirm image in ECR
```

## 📋 Setup Time Comparison

| Task | Jenkins | GitLab CI/CD |
|------|---------|--------------|
| **Install CI Server** | 15-30 min | 0 min (if using GitLab.com) |
| **Install Plugins** | 5-10 min | 0 min |
| **Configure Runner** | 5-10 min | 5 min |
| **Add AWS Creds** | 5 min | 2 min |
| **Create Pipeline** | 5 min | 0 min (auto-detected) |
| **First Build** | ~5 min | ~5 min |
| **Total** | ~35-65 min | ~12 min |

## 💰 Cost Comparison

### Jenkins (Self-Hosted)
- **Software**: Free
- **Infrastructure**: Your machine/server costs
- **Maintenance**: Your time for updates, backups
- **Runners**: Free (your machines)

### GitLab CI/CD
- **GitLab.com Free Tier**: 
  - 400 CI/CD minutes/month
  - Shared runners included
- **Self-Hosted GitLab**:
  - Free Community Edition
  - Your infrastructure costs
  - Own runners (free)
- **GitLab Premium**: 
  - $19/user/month
  - 10,000 CI/CD minutes

## 🔒 Security Comparison

| Feature | Jenkins | GitLab CI/CD |
|---------|---------|--------------|
| **Secrets Management** | Credentials plugin | Protected variables |
| **Credential Masking** | ✅ Yes | ✅ Yes |
| **Audit Logs** | ✅ Yes (via plugins) | ✅ Yes (built-in) |
| **Role-Based Access** | ✅ Yes | ✅ Yes |
| **Secret Rotation** | Manual | Manual |
| **Integration with Vaults** | ✅ Yes (plugins) | ✅ Yes (built-in) |

## 🎨 Output Comparison

### Jenkins Console Output
```
[Pipeline] stage (Build Docker Image)
[Pipeline] { (Build Docker Image)
[Pipeline] sh
+ docker build -t 797240615162.dkr.ecr.us-east-1.amazonaws.com/agentic_rag_with_re-ranker:1 .
Sending build context to Docker daemon  245.8kB
Step 1/10 : FROM python:3.12-slim
...
Successfully tagged 797240615162.dkr.ecr.us-east-1.amazonaws.com/agentic_rag_with_re-ranker:1
```

### GitLab CI/CD Output
```
$ docker build -t $IMAGE_FULL:$IMAGE_TAG .
Sending build context to Docker daemon  245.8kB
Step 1/10 : FROM python:3.12-slim
...
Successfully tagged 797240615162.dkr.ecr.us-east-1.amazonaws.com/agentic_rag_with_re-ranker:abc123f
Job succeeded
```

## 📈 Performance

| Metric | Jenkins | GitLab CI/CD |
|--------|---------|--------------|
| **Build Time** | ~3-5 min | ~3-5 min |
| **Queue Time** | Depends on agents | Depends on runners |
| **Artifact Handling** | Workspace-based | Optimized artifacts |
| **Caching** | Via plugins | Built-in |
| **Parallel Builds** | ✅ Yes | ✅ Yes |

## 🔧 Maintenance

### Jenkins Maintenance
- **Updates**: Manual Jenkins + plugin updates
- **Backups**: Manual job configurations
- **Monitoring**: Via plugins
- **Effort**: Medium to High

### GitLab CI/CD Maintenance
- **Updates**: Automatic (GitLab.com) or manual (self-hosted)
- **Backups**: Included in GitLab backups
- **Monitoring**: Built-in pipeline analytics
- **Effort**: Low to Medium

## 🎯 Recommendation

### For This Project:

**If you're already on GitLab** → Use GitLab CI/CD
- Simpler setup
- Better integration
- Less maintenance

**If you have existing Jenkins** → Use Jenkins
- Reuse existing infrastructure
- Familiar workflows
- No need to change tools

**If starting fresh** → Use GitLab CI/CD
- Faster to set up
- Modern CI/CD features
- One platform for code + CI/CD

## 🔄 Can You Use Both?

**Yes!** Both pipeline files can coexist:
- Jenkins users can use `Jenkinsfile`
- GitLab users can use `.gitlab-ci.yml`
- Both push to the same ECR repository

The result is identical:
```
797240615162.dkr.ecr.us-east-1.amazonaws.com/agentic_rag_with_re-ranker:latest
```

## 📚 Documentation

- **Jenkins**: [JENKINS_ECR_SETUP.md](JENKINS_ECR_SETUP.md)
- **GitLab**: [GITLAB_CI_SETUP.md](GITLAB_CI_SETUP.md)
- **IAM Policy**: [ecr-iam-policy.json](ecr-iam-policy.json)

## ❓ Need Help?

Both setups are documented with:
- ✅ Step-by-step instructions
- ✅ Troubleshooting guides
- ✅ Common issues and solutions
- ✅ Security best practices

Choose the one that fits your existing infrastructure!
