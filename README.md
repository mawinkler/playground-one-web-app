# Playground One Web Application

- [Playground One Web Application](#playground-one-web-application)
  - [Prerequisites](#prerequisites)
  - [Usage](#usage)
    - [Docker](#docker)
    - [Docker-Compose](#docker-compose)
    - [Kubernetes with `eks-ec2` and `kind`](#kubernetes-with-eks-ec2-and-kind)
    - [Kubernetes with `kubectl`](#kubernetes-with-kubectl)
    - [With ArgoCD](#with-argocd)
    - [Run from Source](#run-from-source)
      - [Setup the Backend Application - Shell Session #1](#setup-the-backend-application---shell-session-1)
      - [Create the Frontent - Shell Session #2](#create-the-frontent---shell-session-2)
    - [Build your own Docker Image](#build-your-own-docker-image)
  - [Support](#support)
  - [Contribute](#contribute)
  - [Credits: Mad Scientist](#credits-mad-scientist)


PGOWeb is likely to become a central component of Playground One. Currently it's functionality is limited to scanning files using various technologies offered by Vision One:

- File Security for S3 Buckets secured by Vision One.
- Direct sending of files to the Vision One Sandbox.
- Scanning via the File Security SDK.
- Dropping files into the container to scan with Container Security Runtime Malware Scan. 

## Prerequisites

- Vision One Cloud Security File Scanner API-Key with the following permissions:
    - Cloud Security Operations
        - File Security
            - Run file scan via SDK
    - Platform Capabilities
        - Threat Intelligence
            - Sandbox Analysis
                - View, filter, and search
                - Submit object
- If using the Sandbox, ensure to have credits assigned.
- Know your Vision One region.

## Usage

### Docker

```sh
docker run \
  -p 5000:5000 \
  -e AWS_ACCESS_KEY_ID=<AWS_ACCESS_KEY_ID> \
  -e AWS_SECRET_ACCESS_KEY=<AWS_SECRET_ACCESS_KEY> \
  -e V1_API_KEY=<V1_API_KEY> \
  mawinkler/pgoweb
```

### Docker-Compose

`docker-compose.yaml`:

```yaml
services:
  pgoweb:
    container_name: pgoweb
    image: mawinkler/pgoweb
    environment:
      - AWS_ACCESS_KEY_ID=<AWS_ACCESS_KEY_ID>
      - AWS_SECRET_ACCESS_KEY=<AWS_SECRET_ACCESS_KEY>
      - V1_API_KEY=<V1_API_KEY>
    ports:
      - 5000:5000
    restart: unless-stopped
```

```sh
docker compose up pgoweb
```

### Kubernetes with `eks-ec2` and `kind`

If you've enabled PGOWeb in your configuration, it will be automatically deployed when the EKS EC2 Kubernetes cluster is created.

Verify, that you have enabled PGOWeb in your configuration.

```sh
pgo --config
```

```sh
...
Section: Kubernetes Deployments
Please set/update your Integrations configuration
...
Deploy PGOWeb? [true]:
...
```

```sh
# EKS
pgo --apply eks-ec2

# Kind
pgo --apply kind
```

The following outputs are created:

```sh
# EKS
Outputs:

loadbalancer_dns_pgoweb = "k8s-pgoweb-pgowebin-69953cce7e-847792142.eu-central-1.elb.amazonaws.com"
# Browser link: http://k8s-pgoweb-pgowebin-69953cce7e-847792142.eu-central-1.elb.amazonaws.com

# Kind
Outputs:

loadbalancer_port_forward = "kubectl -n projectcontour port-forward service/contour-envoy 8080:80 --address='0.0.0.0'"

# Run
kubectl -n projectcontour port-forward service/contour-envoy 8080:80 --address='0.0.0.0'
# Browser link: http://<IP OF KIND SERVER>:8080>
```

### Kubernetes with `kubectl`

```sh
export AWS_ACCESS_KEY_ID=<AWS_ACCESS_KEY_ID>
export AWS_SECRET_ACCESS_KEY=<$AWS_SECRET_ACCESS_KEY>
export V1_API_KEY=<V1_API_KEY>
kubectl create ns pgoweb
kubectl -n pgoweb create secret generic pgo-credentials --from-env-file=<(envsubst <pgo.env)
kubectl -n pgoweb apply -f app.yml

kubectl -n pgoweb port-forward service/pgoweb 8080:80 --address='0.0.0.0'
# Browser link: http://<IP OF KIND SERVER>:8080>
```

### With ArgoCD

`app-pgoweb.yaml`:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: pgoweb
  namespace: argocd
spec:
  project: default
  source:
    repoURL: 'https://github.com/mawinkler/playground-one-web-app'
    path: .
    targetRevision: main
  destination:
    server: https://kubernetes.default.svc
    namespace: pgoweb
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

```sh
kubectl apply -f app-pgoweb.yaml
```

### Run from Source

Get the sources:

```sh
git clone https://github.com/mawinkler/playground-one-web-app
cd playground-one-web-app
```

#### Setup the Backend Application - Shell Session #1

```sh
venv
pip install -r backend/requirements.txt 
python3 backend/app.py 
```

#### Create the Frontent - Shell Session #2

Verify that you have a recent version of NodeJS and NPM:

```sh
node version
npm -version
```

```sh
Node.js v22.12.0
10.9.2
```

Eventually update with

```sh
sudo npm install -g n
sudo n lts
sudo npm install npm -g
npm -version
npm cache clean --force
```

In `frontend/App.jsx` update the variable `BASEURL` with the IP of your host (here: `192.168.1.122`).

```js
  const BASEURL = "http://192.168.1.122:5000"
```

Now, start the frontend:

```sh
cd frontend
npm install # installing the dependencies
npm run dev -- --host
```

### Build your own Docker Image

In `frontend/App.jsx` set the variable `BASEURL` to an empty string.

```js
  const BASEURL = ""
```

Build

```sh
docker build -t pgoweb . --progress=plain --load --no-cache
```

Run

```sh
docker run \
  -p 5000:5000 \
  -e AWS_ACCESS_KEY_ID=<AWS_ACCESS_KEY_ID> \
  -e AWS_SECRET_ACCESS_KEY=<AWS_SECRET_ACCESS_KEY> \
  -e V1_API_KEY=<V1_API_KEY> \
  pgoweb
```

## Support

This is an Open Source community project. Project contributors may be able to help, depending on their time and availability. Please be specific about what you're trying to do, your system, and steps to reproduce the problem.

For bug reports or feature requests, please [open an issue](../../issues). You are welcome to [contribute](#contribute).

Official support from Trend Micro is not available. Individual contributors may be Trend Micro employees, but are not official support.

## Contribute

I do accept contributions from the community. To submit changes:

1. Fork this repository.
1. Create a new feature branch.
1. Make your changes.
1. Submit a pull request with an explanation of your changes or additions.

I will review and work with you to release the code.

## Credits: Mad Scientist

Link: <https://en.wikipedia.org/wiki/File:Mad_scientist.svg#/media/File:Mad_scientist_transparent_background.svg>

