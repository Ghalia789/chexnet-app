# CheXNet GCP and GKE Deployment Guide

## Purpose
This guide documents a budget-friendly deployment path for the CheXNet app on Google Cloud Platform using Google Kubernetes Engine with three environments:

- development
- test
- production

The plan is optimized for a short academic demo and low credit usage.

## Architecture Summary
- One GKE cluster (zonal) to reduce cost.
- Three namespaces inside the cluster: chexnet-dev, chexnet-test, chexnet-prod.
- One container image stored in Artifact Registry.
- Internal services by default (ClusterIP).
- Temporary external LoadBalancer only when needed for demo day.

## Prerequisites
- Google Cloud project with billing enabled.
- gcloud CLI installed and authenticated.
- Docker installed locally.
- kubectl installed.
- Existing local Docker image build success.

## Cost-Aware Defaults
Use the following controls to stay close to the credit target:

1. Use a single zonal cluster instead of multiple clusters.
2. Use one small node pool with minimum practical size.
3. Keep replicas at 1 for development and test.
4. Keep production autoscaling capped at 2 replicas.
5. Keep production service as ClusterIP except for demo window.
6. Delete the cluster immediately after evaluation if no longer needed.

## Variables
Set these shell variables before running commands:

- PROJECT_ID: your Google Cloud project id
- REGION: Artifact Registry region, for example us-central1
- ZONE: GKE zone, for example us-central1-a
- REPO: Artifact Registry repository name, for example chexnet
- IMAGE: chexnet-app
- TAG: release tag, for example v1

## Step 1: Configure Project
1. Set active project:
   gcloud config set project PROJECT_ID

2. Enable required services:
   gcloud services enable container.googleapis.com artifactregistry.googleapis.com

## Step 2: Create Artifact Registry Repository
Create one Docker repository if it does not exist:

gcloud artifacts repositories create REPO --repository-format=docker --location=REGION --description="CheXNet container repository"

Configure Docker authentication for Artifact Registry:

gcloud auth configure-docker REGION-docker.pkg.dev

## Step 3: Tag and Push Image
Tag local image:

docker tag chexnet-app:local REGION-docker.pkg.dev/PROJECT_ID/REPO/IMAGE:TAG

Push image:

docker push REGION-docker.pkg.dev/PROJECT_ID/REPO/IMAGE:TAG

## Step 4: Create GKE Cluster
Create a zonal cluster with conservative defaults:

gcloud container clusters create chexnet-cluster --zone ZONE --num-nodes 1 --machine-type e2-standard-2

Get credentials:

gcloud container clusters get-credentials chexnet-cluster --zone ZONE

## Step 5: Update Kubernetes Image References
In these files, replace image placeholders with your pushed image:

- K8s/development.yaml
- K8s/test.yaml
- K8s/production.yaml

Format:

REGION-docker.pkg.dev/PROJECT_ID/REPO/IMAGE:TAG

## Step 6: Deploy Namespaces and Workloads
Apply manifests:

kubectl apply -f K8s/development.yaml
kubectl apply -f K8s/test.yaml
kubectl apply -f K8s/production.yaml

Verify:

kubectl get ns
kubectl -n chexnet-dev get all
kubectl -n chexnet-test get all
kubectl -n chexnet-prod get all

## Step 7: Demo Day External Access
Default state should remain internal only.

Turn external access on only for demo window:

kubectl apply -f K8s/production-lb.yaml
kubectl -n chexnet-prod get svc chexnet-service -w

After demo, disable external exposure:

kubectl -n chexnet-prod patch svc chexnet-service -p "{\"spec\":{\"type\":\"ClusterIP\"}}"

## Step 8: Basic Monitoring without Extra Stack
Use built-in GKE observability to avoid additional infrastructure cost:

1. Pod health and restart checks:
   kubectl -n chexnet-prod get pods -o wide
   kubectl -n chexnet-prod describe pod POD_NAME

2. Application logs:
   kubectl -n chexnet-prod logs deploy/chexnet-app --tail=200

3. Resource usage:
   kubectl top nodes
   kubectl -n chexnet-prod top pods

## Step 9: Cleanup to Stop Spending
When demo/testing is done:

gcloud container clusters delete chexnet-cluster --zone ZONE --quiet

gcloud artifacts docker images delete REGION-docker.pkg.dev/PROJECT_ID/REPO/IMAGE:TAG --delete-tags --quiet

## Troubleshooting Quick Notes
1. ImagePullBackOff:
   Verify image path and tag in YAML files.

2. Pending EXTERNAL-IP:
   Wait a few minutes, then inspect service events with:
   kubectl -n chexnet-prod describe svc chexnet-service

3. CrashLoopBackOff:
   Inspect logs and verify model file is available in the image.

4. High spending risk:
   Confirm LoadBalancer is not active outside demo windows and cluster is deleted when no longer needed.
