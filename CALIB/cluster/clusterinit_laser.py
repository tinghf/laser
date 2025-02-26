from kubernetes import client, config, utils
import logging
import yaml
#import time

# Run this python script to set up the ray cluster.
# Be sure you have downloaded the kube config file for this cluster.

### USER CONFIGS ###

# kube_config = "C:/Users/Administrator/.kube/starsimcal (1)" # This is the config file downloaded from k8s cluster self service
kube_config = "/home/tinghf/laser/CALIB/cluster/aks-rayaks-cditest.txt" # This is the config file downloaded from k8s cluster self service
name = "laser"                               # This name will be used for all pods
num_pods = 128                                     # The max number of pods to scale to. This should be the same as the # of configured pods from the self service tool
docker_image_repo = "idm-docker-staging.packages.idmod.org" # IDM's artifactory server
docker_image = "rhull/rsvsim-ray-calibration"  # The docker image to be deployed to each pod.

### END OF USER CONFIGS ###
yaml_file = "cluster/ray-cluster-laser-calib.yaml"  # This is the kube config definition file
image_pull_secret_name = "idmodregcred3" # This is the name of the kubernetes secret to use to pull the docker images
namespace = "default"

config.load_kube_config(config_file=kube_config)
k8s_client = client.ApiClient()
k8s_client_instance = client.CoreV1Api()
k8s_client_apps_instance = client.AppsV1Api()

parsed_config = []
with open(yaml_file) as f:
    configfile = yaml.safe_load_all(f)
    for k8s_config in configfile:
        if k8s_config['kind'] == "RayCluster":
            k8s_config['metadata']['name'] = f"ray-cluster-{name}"
            k8s_config['spec']['headGroupSpec']['template']['metadata']['labels']['rayCluster'] = f"ray-cluster-{name}"
            k8s_config['spec']['headGroupSpec']['template']['spec']['containers'][0][
                'image'] = f"{docker_image_repo}/{docker_image}"
            k8s_config['spec']['headGroupSpec']['template']['spec']['imagePullSecrets'][0][
                'name'] = image_pull_secret_name
            k8s_config['spec']['workerGroupSpecs'][0]['template']['spec']['containers'][0][
                'image'] = f"{docker_image_repo}/{docker_image}"
            k8s_config['spec']['workerGroupSpecs'][0]['template']['spec']['imagePullSecrets'][0][
                'name'] = image_pull_secret_name
            k8s_config['spec']['workerGroupSpecs'][0]['maxReplicas'] = num_pods
        parsed_config.append(k8s_config)

def init_cluster():
    '''
    Instantiates all necessary cluster components if they haven't already been created
    '''
    namespacelist = k8s_client_instance.list_namespace()
    namespaces = [existing_namespace.metadata.name for existing_namespace in namespacelist.items]
    if namespace not in namespaces:
        k8s_client_instance.create_namespace(client.V1Namespace(metadata=client.V1ObjectMeta(name=namespace)))
    else:
        print("Namespace already exists. Continuing...")

    for k8s_config in parsed_config:
        if k8s_config['kind'] == "RayCluster":
            client.CustomObjectsApi().create_namespaced_custom_object(group="ray.io", version="v1alpha1",
                                                                      namespace=namespace, plural="rayclusters",
                                                                      body=k8s_config)
        else:
            utils.create_from_dict(k8s_client, k8s_config, namespace=namespace)


def delete_cluster():
    '''
    Wipes all traces of the config from the cluster
    '''
    for k8s_config in parsed_config:
        if k8s_config['kind'] == "RayCluster":
            api_response = client.CustomObjectsApi().delete_namespaced_custom_object(group="ray.io", version="v1alpha1",
                                                                      namespace=namespace, plural="rayclusters",
                                                                      name=k8s_config['metadata']['name'])
            logging.log(logging.DEBUG, f"RayCluster created. status={api_response}")
        elif k8s_config['kind'] == "Service":
            k8s_client_instance.delete_namespaced_service(name=k8s_config['metadata']['name'], namespace=namespace)
        elif k8s_config['kind'] == "StatefulSet":
            k8s_client_apps_instance.delete_namespaced_stateful_set(name=k8s_config['metadata']['name'], namespace=namespace)
        elif k8s_config['kind'] == "Secret":
            k8s_client_instance.delete_namespaced_secret(name=k8s_config['metadata']['name'], namespace=namespace)


def reset_ray_cluster():
    '''
    Resets only the RayCluster components. Use this if the docker image is updated
    '''
    for k8s_config in parsed_config:
        if k8s_config['kind'] == "RayCluster":
            try:
                # Delete the old raycluster resource
                client.CustomObjectsApi().delete_namespaced_custom_object(group="ray.io", version="v1alpha1",
                                                                          namespace=namespace, plural="rayclusters",
                                                                          name=k8s_config['metadata']['name'])
            except client.exceptions.ApiException:
                print("No raycluster to delete. Continuing with reset...")

            # Create a new raycluster resource
            client.CustomObjectsApi().create_namespaced_custom_object(group="ray.io", version="v1alpha1",
                                                                      namespace=namespace, plural="rayclusters",
                                                                      body=k8s_config)
action = "install" # "install", "delete", "reset"



# time.sleep(15)
#

if action == "delete":
    print("requesting delete_cluster...")
    delete_cluster()
    print("Complete")

if action == "install":
    init_cluster()
    print("ray cluster launched!")

if action == "reset":
    reset_ray_cluster()
    print("ray cluster reset!")