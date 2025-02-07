#!/bin/bash

set -e

# export PATH=/usr/local/bin/:${PATH}
VERSION=$(cat .VERSION)

printf '%s\n' "Building pgoweb version ${VERSION}"

# docker run --privileged multiarch/qemu-user-static:latest --reset -p yes --credential yes 

if [[ "${VERSION}" == "dev" ]]; then
        # --no-cache \
    #,linux/arm64/v8
    printf '%s\n' "Building development version"
        # --platform linux/amd64,linux/arm64/v8 \
    docker buildx build --progress=plain \
        -t mawinkler/pgoweb:${VERSION} \
        --platform linux/amd64 \
        --no-cache \
        --push -f Dockerfile .
    docker pull mawinkler/pgoweb:dev
    docker run --rm \
      -p 5000:5000 \
      -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
      -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
      -e V1_API_KEY=${V1_API_KEY} \
    mawinkler/pgoweb:dev
else
    printf '%s\n' "Building public version"
    docker buildx build \
        -t mawinkler/pgoweb:${VERSION} \
        -t mawinkler/pgoweb:latest \
        --platform linux/amd64 \
        --push .
fi
