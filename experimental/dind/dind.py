#!/usr/bin/env ~/virtualenvs/dind/bin/python3

import docker
import os
import sys

import docker.errors
import docker.models
import docker.models.containers
import docker.types

###
# 1 Start a dind container with name: dind-+=1
# 2 Exec into that container
# 3 Run systest perf tests
# 4 Record results to DB somewhere
#
# Back to 1 until limit of nested containers is reached

docker_client = docker.from_env()

def start_container(container_name: str, container_count: int, container_image: str):
    """Start a privileged Docker container

    Args:
        container_name (str): The name of the docker container
    """
    try:
        return docker_client.containers.run(
            name=container_name,
            image=container_image,
            remove=False,
            detach=True,
            hostname=container_name,
            environment={"count": container_count},
            privileged=True,
        )
    except docker.errors.ContainerError as container_error:
        print(
            f"A container error has occurred starting {container_name}: {container_error}"
        )
    except docker.errors.ImageNotFound as image_error:
        print("The specified container image could not be found. Exiting.")
        sys, exit(5)
    except docker.errors.APIError as docker_error:
        print(f"A Docker API error occurred starting {container_name}: {docker_error}")


def container_exec(container_object: docker.models.containers.Container, container_count: int):
    """Exec into a running container

    Args:
        container_name (str): The name of the Docker container to exec into
    """

    try:
        return container_object.exec_run(
            # cmd="sh -c 'echo Hello from $(hostname)'"
            # cmd = "./sysbench.sh",
            cmd = "sh"
        )
    except docker.errors.APIError as api_error:
        print(f"An API error occurred with the exec into {container_object.name}: {api_error}")


def run_perf_test():
    pass


def record_test_results(results):
    pass


def cleanup(container_object_list: list):
    print(f"Cleaning up {len(container_object_list)} containers...")
    for c in container_object_list:
        c.remove(force=True)


if __name__ == "__main__":
    container_image_name = "bench:1"
    # This is defined when starting the initial dind container
    max_container_count = os.environ['MAX_CONTAINER_COUNT']
    parent_container_count = os.environ['PARENT_CONTAINER_COUNT']
    hostname = os.environ['HOSTNAME']
    this_container_count = int(parent_container_count + 1)
    container_name = f"dind-{this_container_count}"

    start_container(container_name=container_name, container_count=this_container_count, container_image=docker:dind)
    running_containers = []
    for i in range(1, 6):
        container_name = f"dind-{i}"

        # Start all N containers
        print(f"Starting container {container_name}")

        running_containers.append(start_container(container_name, container_image_name))



    # print([type(i) for i in running_containers])
    # test_container = docker_client.containers.get("dd0ba876c4ce")

        # print(container_exec(running_containers[-1]))

    # for container in reversed(running_containers):
    #     # Start with the most deeply-nested container (last one created)
    #     print(f"Running script in {container_name}")
    #     container_exec(container)

    # cleanup(running_containers)
