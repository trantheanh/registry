import os


def print_log(message, debug=False):
    if debug:
        print()
        print(message)
        print()

    return


def scan(path, job=None, debug=False):
    images = set()
    print_log("SCAN: {}".format(path), debug)
    file_names = os.listdir(path)

    for file_name in file_names:
        file_path = os.path.join(path, file_name)

        if os.path.isfile(file_path) and (".yaml" in file_name or ".yml" in file_name):
            if job is not None:
                images.update(job(file_path))

            print_log("PROCESS FILE: {}".format(file_name), debug)

        if os.path.isdir(file_path):
            images.update(scan(file_path, job))

    return list(images)


def get_images(file_path):
    images = []
    with open(file_path) as f:

        for line in f:
            line = line.replace("\n", "")
            tokens = line.split(" ")
            for token in tokens:
                if "gcr.io/" in token or "k8s.gcr.io/" in token or "public.ecr.aws/" in token:
                    images.append(token.replace('"', ""))

    return images


def update_image_name(file_path):
    with open(file_path) as f:
        text = f.read()

    with open(file_path, "w") as f:
        for line in text.split("\n"):
            line = line.replace("\n", "")
            tokens = line.split(" ")
            for token in tokens:
                if "gcr.io/" in token or "k8s.gcr.io/" in token or "public.ecr.aws/" in token:
                    token.replace('"', "")
                    parts = token.split("@sha256")
                    if len(parts) == 2:
                        text = text.replace("@sha256{}".format(parts[1]), ":latest")
        f.write(text)

    return []


def pull_image(images):
    for image in images:
        os.system("docker pull {}".format(image))

    return


folders = [
    "./common/cert-manager/cert-manager/base",
    "./common/cert-manager/kubeflow-issuer/base",
    "./common/istio-1-9/istio-crds/base",
    "./common/istio-1-9/istio-namespace/base",
    "./common/istio-1-9/istio-install/base",
    "./common/dex/overlays/istio",
    "./common/oidc-authservice/base",
    "./common/knative/knative-serving/base",
    "./common/istio-1-9/cluster-local-gateway/base",
    "./common/knative/knative-eventing/base",
    "./common/kubeflow-namespace/base",
    "./common/kubeflow-roles/base",
    "./common/istio-1-9/kubeflow-istio-resources/base",
    "./apps/pipeline/upstream/env/platform-agnostic-multi-user",
    "./apps/pipeline/upstream/env/platform-agnostic-multi-user-pns",
    "./apps/kfserving/upstream/overlays/kubeflow",
    "./apps/katib/upstream/installs/katib-with-kubeflow",
    "./apps/centraldashboard/upstream/overlays/istio",
    "./apps/admission-webhook/upstream/overlays/cert-manager",
    "./apps/jupyter/notebook-controller/upstream/overlays/kubeflow",
    "./apps/jupyter/jupyter-web-app/upstream/overlays/istio",
    "./apps/profiles/upstream/overlays/kubeflow",
    "./apps/volumes-web-app/upstream/overlays/istio",
    "./apps/tensorboard/tensorboards-web-app/upstream/overlays/istio",
    "./apps/tensorboard/tensorboard-controller/upstream/overlays/kubeflow",
    "./apps/tf-training/upstream/overlays/kubeflow",
    "./apps/pytorch-job/upstream/overlays/kubeflow",
    "./apps/mpi-job/upstream/overlays/kubeflow",
    "./apps/mxnet-job/upstream/overlays/kubeflow",
    "./apps/xgboost-job/upstream/overlays/kubeflow",
    "./common/user-namespace/base",
]


for folder in folders:
    results = scan(folder, job=get_images)
    pull_image(results)

# CHANGE ALL @sha* to latest
for folder in folders:
    scan(folder, job=update_image_name)
