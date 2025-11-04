# Production Deployment Checklist

## Pre-Deployment

- [ ] Set up Google Cloud Project
- [ ] Enable required APIs (Container, Container Registry, Cloud Build)
- [ ] Create Google API Key for GenAI
- [ ] Install required tools (gcloud, kubectl, docker)
- [ ] Authenticate with `gcloud auth login`
- [ ] Set project: `gcloud config set project YOUR_PROJECT_ID`

## Security

- [ ] Update `k8s/secret.yaml` with real Google API Key
- [ ] **Never commit** `k8s/secret.yaml` with real credentials to git
- [ ] Consider using Google Secret Manager instead of Kubernetes secrets
- [ ] Review and update RBAC policies
- [ ] Enable network policies for pod-to-pod communication
- [ ] Set up Cloud Armor for DDoS protection
- [ ] Enable binary authorization for image security

## Configuration

- [ ] Update `PROJECT_ID` in deployment scripts
- [ ] Review resource limits in `k8s/deployment.yaml`
- [ ] Configure HPA thresholds based on load testing
- [ ] Set appropriate log levels for production
- [ ] Configure retention policies for logs

## Testing

- [ ] Test Docker build locally: `docker build -t adk-triage-agent .`
- [ ] Test container locally: `docker run -p 8080:8080 adk-triage-agent`
- [ ] Verify health endpoint: `http://localhost:8080/health`
- [ ] Load test the application
- [ ] Test failover scenarios
- [ ] Verify autoscaling triggers

## Deployment

- [ ] Run deployment script: `.\deploy-gke.ps1 -ProjectId "your-project-id"`
- [ ] Verify pods are running: `kubectl get pods -n adk-triage-agent`
- [ ] Check service status: `kubectl get svc -n adk-triage-agent`
- [ ] Wait for external IP assignment
- [ ] Test application via external IP
- [ ] Verify health checks are passing

## Monitoring & Observability

- [ ] Set up Cloud Monitoring dashboards
- [ ] Configure alerts for:
  - Pod crashes
  - High CPU/Memory usage
  - Failed health checks
  - Error rate thresholds
- [ ] Enable Cloud Logging
- [ ] Set up log-based metrics
- [ ] Configure uptime checks
- [ ] Set up error reporting

## Documentation

- [ ] Document the deployment process
- [ ] Create runbooks for common issues
- [ ] Document rollback procedures
- [ ] Share credentials securely with team
- [ ] Update architecture diagrams

## Cost Management

- [ ] Set up billing alerts
- [ ] Review resource quotas
- [ ] Enable committed use discounts if applicable
- [ ] Consider preemptible nodes for non-critical workloads
- [ ] Set up autoscaling to optimize costs

## Compliance & Governance

- [ ] Review data residency requirements
- [ ] Ensure compliance with regulations (GDPR, HIPAA, etc.)
- [ ] Set up audit logging
- [ ] Document data retention policies
- [ ] Review access controls

## Backup & Disaster Recovery

- [ ] Set up automated backups for persistent data
- [ ] Test backup restoration procedures
- [ ] Document disaster recovery plan
- [ ] Set up multi-region deployment (if required)
- [ ] Test failover scenarios

## Post-Deployment

- [ ] Monitor application for 24-48 hours
- [ ] Review logs for errors
- [ ] Verify metrics are being collected
- [ ] Test all features in production
- [ ] Conduct security scan
- [ ] Update status page
- [ ] Notify stakeholders

## Continuous Improvement

- [ ] Set up CI/CD pipeline with Cloud Build
- [ ] Implement automated testing
- [ ] Configure canary deployments
- [ ] Set up A/B testing if needed
- [ ] Regular security updates
- [ ] Performance optimization reviews

## Emergency Contacts

- **On-Call Engineer**: ___________________
- **Project Lead**: ___________________
- **GCP Support**: https://cloud.google.com/support
- **Incident Management**: ___________________

## Rollback Plan

If deployment fails or issues are detected:

```powershell
# Rollback to previous version
kubectl rollout undo deployment/adk-triage-agent -n adk-triage-agent

# Verify rollback
kubectl rollout status deployment/adk-triage-agent -n adk-triage-agent
```

## Support Resources

- [GKE Documentation](https://cloud.google.com/kubernetes-engine/docs)
- [Kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [GCP Best Practices](https://cloud.google.com/architecture/framework)
- Project DEPLOYMENT.md for detailed instructions
