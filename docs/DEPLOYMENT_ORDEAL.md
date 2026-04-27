# CheXNet Deployment Ordeal

## Why this exists
This document records the full deployment path for the CheXNet app on GCP/GKE, including the failures, the fixes, and the final state reached for the demo.

## Short Version
The app was not just "pushed to GCP". It went through several real deployment failures before it became healthy:

1. Kubernetes manifests were applied for development, test, and production namespaces.
2. The initial container image could not start because it was missing a Linux library required by OpenCV.
3. The first Cloud Build attempts failed because of missing IAM permissions.
4. The first successful rebuilt image still crashed because the model artifact was not included in the Cloud Build upload.
5. After fixing the upload rules, rebuilding, and freeing the single-node cluster from old pods, all three environments reached a healthy 1/1 state.

## Timeline

### 1. Kubernetes manifests were applied
The following manifests were applied to the active GKE cluster:

- `K8s/development.yaml`
- `K8s/test.yaml`
- `K8s/production.yaml`

That created:

- `chexnet-dev`
- `chexnet-test`
- `chexnet-prod`

Production also created the HPA resource.

### 2. The first image failed at runtime
The container could pull, but the app crashed on startup because `cv2` could not import due to a missing OS library:

- `ImportError: libxcb.so.1: cannot open shared object file`

This meant the image itself needed to be rebuilt with the missing system dependency.

### 3. Local Docker was not the right path
Local Docker Desktop was unreliable and the machine was low on disk space.
To avoid relying on local Docker storage, the rebuild was moved to Cloud Build.

### 4. Cloud Build permissions had to be fixed first
Cloud Build submission initially failed because the active account and build service account did not have the right permissions.
The fixes applied were:

- enabled `cloudbuild.googleapis.com`
- granted `roles/cloudbuild.builds.builder` to the active user for submission
- granted `roles/storage.objectViewer` on the Cloud Build staging bucket to the default compute service account
- granted `roles/artifactregistry.writer` on the `chexnet` repository to the default compute service account
- granted `roles/logging.logWriter` to the same service account

### 5. The model file was missing from the build context
The app crashed again after the container was rebuilt because this file was not present in the image:

- `models/best_chexnet.pth`

Root cause:
- `.gitignore` excluded `*.pth`
- Cloud Build used the source upload rules and therefore skipped the model artifact

Fix:
- added `.gcloudignore`
- explicitly allowed `models/best_chexnet.pth` into the build context

### 6. The rebuilt image finally succeeded
After the `.gcloudignore` fix, Cloud Build successfully produced and pushed the new image:

- image tag: `v2`
- final digest: `sha256:88cf23de91f756304016c01cbc50598a8fe9e35fb676c82bcb6cf64c47f00cee`

### 7. The cluster rollout needed manual cleanup
The cluster is a single-node setup, so the rolling update briefly created old and new pods at the same time.
That caused temporary scheduling pressure and rollout timeouts.

Fix:
- deleted the old crashing pods so the new `v2` pods could schedule
- let the deployment settle on the single available node

### 8. Final healthy state
All three namespaces reached the desired state:

- `chexnet-dev`: 1/1 available
- `chexnet-test`: 1/1 available
- `chexnet-prod`: 1/1 available

## What actually changed
The important part is that this was not just a manifest apply.
The working deployment required all of the following:

- Kubernetes manifest application
- Artifact Registry access fixes
- Cloud Build submission permissions
- Cloud Build staging bucket access
- artifact upload rules for the model file
- image rebuild and push
- rollout cleanup on a single-node cluster

## Lessons Learned

1. A Kubernetes deployment can look correct while the image still fails at runtime.
2. A Cloud Build upload can succeed even when important runtime files are excluded.
3. A model artifact should be treated as a deployment dependency, not just a local project file.
4. On a small single-node cluster, rolling updates can stall if old pods are still holding resources.
5. If the app crashes at import time, the issue is usually in the container image, not the manifest.

## Useful Artifacts

- `K8s/development.yaml`
- `K8s/test.yaml`
- `K8s/production.yaml`
- `.gcloudignore`
- `Dockerfile`

## Final Status
The CheXNet app is now deployed to GKE across development, test, and production namespaces, and the `v2` image includes the required model artifact and runtime system libraries.