# Project documentation
Project acronym: *kube-vip* \
Authors: 
- Piotr Kowalczyk
- Wojciech Łoboda
- Aleksandra Smela
- Juliusz Wasieleski

Year: 2024/2025

## Contents list
- [1. Introduction](#1-introduction)
- [2. Theoretical background/technology stack](#2-theoretical-backgroundtechnology-stack)
- [3. Case study concept description](#3-case-study-concept-description)
- [4. Solution architecture](#4-solution-architecture)
- [5. Environment configuration description](#5-environment-configuration-description)
    - [5.1 Sample Kubernetes workload](#52-sample-kubernetes-workload)
- [6. Installation method](#6-installation-method)
    - [6.1 Prepare local Kubernetes cluster](#62-prepare-local-kubernetes-cluster)
- [7. Demo deployment steps:](#7-demo-deployment-steps)
- [8. Summary – conclusions](#8-summary-–-conclusions)
- [9. References](#9-references)

## 1. Introduction
KubeVIP is a cloud-native high availability and load balancing solution built for Kubernetes environments, designed to provide resilient virtual IP addressing for both control plane components and service workloads across on-premises, edge, and multi-cloud deployments. By focusing on simplicity and platform independence, KubeVIP eliminates the need for external load balancers while ensuring critical Kubernetes components remain accessible even during node failures. It encompasses both control plane high availability and service load balancing capabilities, enabling organizations to build robust Kubernetes infrastructures without cloud provider dependencies. KubeVIP is platform-agnostic, operating effectively across bare metal, virtual machines, and various cloud environments. Its Kubernetes-native approach leverages either static pods or DaemonSets with support for multiple VIP advertisement methods including ARP, BGP, and Layer 2, enabling flexible network integration. KubeVIP aims to democratize high availability for Kubernetes clusters of all sizes, reducing operational complexity and costs associated with traditional load balancing solutions, ultimately enhancing resilience in both production and edge deployments.
## 2. Theoretical background/technology stack

### kube-vip - What is it? 
KubeVIP is a specialized tool that provides virtual IP address management and load balancing capabilities within Kubernetes environments. It delivers highly available endpoints for both Kubernetes control plane components and application services without relying on external load balancing infrastructure. By using cloud-native principles, KubeVIP ensures that critical Kubernetes components remain accessible even during node failures, making it particularly valuable for on-premises, bare metal, and edge deployments where traditional cloud load balancers aren't available.

### What problem does kube-vip solves?
High availability in Kubernetes environments traditionally requires external load balancers to provide stable entry points to the control plane and services. In cloud environments, this is typically handled by managed load balancing offerings, but in on-premises or edge deployments, these resources may not be available or may be prohibitively expensive.

KubeVIP addresses this gap by providing a Kubernetes-native solution that creates and manages virtual IP addresses that can float between nodes. This ensures continuous availability of the Kubernetes API server and services even when individual nodes fail. By eliminating the dependency on external load balancing infrastructure, KubeVIP simplifies the creation of highly available Kubernetes clusters in any environment, reducing complexity and cost while improving resilience.

### How does kube-vip work? 
KubeVIP tackles the high availability challenge through two main approaches:

1. It operates as either a static pod (for control plane HA) or a DaemonSet (for service load balancing), providing a consistent way to manage virtual IPs across the cluster regardless of the underlying infrastructure.

2. It supports multiple VIP advertisement methods (ARP, BGP, Layer 2) to accommodate different networking environments, making it adaptable to various infrastructure configurations.
### Overview of kube-vip functional components
* KubeVIP instances run on each control plane node, monitoring the health of the local Kubernetes components
* A leader election mechanism ensures only one instance actively advertises the virtual IP at any time
* When a node failure is detected, leadership transfers to another instance, which then takes ownership of the virtual IP
* For service load balancing, the KubeVIP DaemonSet watches for services of type LoadBalancer and provisions virtual IPs accordingly

### Architecture 
The modes of using kube-vip do change it's architecture. There are two things to concider:
 * where KubeVIP runs
 * how KubeVIP advertises the VIP to the network

1. where KubeVIP runs
   * Static Pod Mode (Control Plane HA)
       * Deployed as static pods on control plane nodes only
       * Managed directly by the kubelet on each control plane node, not by the Kubernetes API server
   ![alt text](images/diagram2.png)
   * DaemonSet Mode (Service Load Balancing)
       * Deployed as a DaemonSet across worker nodes (can also include control plane nodes)
       * Managed by the Kubernetes API server like other workloads
       * Runs on all nodes or a selected subset using node selectors/affinities
![alt text](images/diagram3.png)
2. how KubeVIP advertises the VIP to the network
   * ARP Mode
       * This node distributes the traffic further to other components (e.g., to other control plane nodes or pods).
       * From an external network point of view, there is only one IP address (VIP), assigned to one host.
       * In this mode, the leader must be ready to distribute/distribute traffic further.
   ![alt text](images/diagram4.png)
   * BGP mode
       * The external network sees the VIP advertised by multiple nodes, and routing decides which node the traffic will go to.
       * Traffic doesn't have to go through a single point - it can go to any node announcing VIP.
       * There is no “VIP Leader Node” as a central point - each node operates independently.
![alt text](images/diagram5.png)

This architecture enables KubeVIP to deliver robust high availability for both the Kubernetes control plane and application services without external dependencies, making it ideal for environments where cloud provider load balancing services are unavailable.

## 3. Case study concept description

KubeVIP Case Study
This case study demonstrates the use of KubeVIP to enable load balancing in a Kubernetes cluster deployed in a non-cloud, bare-metal environment. The cluster hosts a lightweight microservices-based application designed to test and showcase KubeVIP’s functionality.

The application consists of three identical microservices, each deployed as a single container within its own Pod. Each microservice exposes a simple HTTP endpoint that returns a static message - echo microservice, allowing for easy identification of which pod serves each request.

KubeVIP is deployed in static mode with ARP enabled on a single control-plane node. It advertises a virtual IP (VIP) on the local network, acting as a stable, external-facing IP address for the service. Traffic directed to this VIP is automatically distributed across the three microservice Pods, demonstrating basic layer 4 load balancing functionality.

![Case Study new drawio](https://github.com/user-attachments/assets/ff5a2ae2-b578-4b98-9689-94693d5146fc)


This setup replicates a LoadBalancer-type service typically found in managed Kubernetes environments, without relying on external hardware or cloud infrastructure. It highlights KubeVIP's utility in on-premises or edge deployments, providing a practical and minimal solution for high availability, traffic distribution, and network resilience in small to medium-scale Kubernetes clusters

### **Testing Scenarios**

To validate the effectiveness of KubeVIP as a load balancer in a Kubernetes environment, several test scenarios are executed against the deployed microservices. Each scenario is designed to evaluate a specific aspect of KubeVIP’s performance and reliability.

#### 1. **Round-Robin Load Balancing Across Pods**

A series of HTTP requests are sent to the virtual IP managed by KubeVIP using tools such as `curl`. The responses, which include pod-specific identifiers, confirme that requests were being distributed evenly across all three microservices. This demonstrates basic round-robin behavior and verified that KubeVIP correctly routed traffic among available pods.
#### 2. **Unreachable Pod Handling**

One of the pods is intentionally made unresponsive by killing the container or forcing a readiness probe failure. Subsequent requests to the VIP no longer routed traffic to the unhealthy pod, in order to check that Kubernetes' built-in health checks, in conjunction with KubeVIP’s service routing, effectively prevent traffic from reaching unavailable endpoints.

#### 3. **Simulated Load Testing**

Concurrent traffic is generated to the VIP using load testing tools such `ab` (Apache Benchmark). The system is tested for its ability to handle high request volumes while efficiently distributing traffic across all healthy pods.

### **Monitoring and Observability**

To ensure the Kubernetes cluster's performance, reliability, and health, monitoring and observability tools are integrated into the environment. Specifically, **Grafana** and **OpenTelemetry** (Otel) are utilized for real-time monitoring and gathering of application-level metrics, traces, and logs.

## 4. Solution architecture

## 5. Environment configuration description

## 6. Installation method

### Prerequisites:
...

## 7.How to reproduce - step by step
<!---Infrastructure as Code approach--->

## 8. Demo deployment steps
### 8.1. Configuration set-up
### 8.2. Data preparation
### 8.3. Execution procedure
### 8.4. Results presentation

## 9. Using AI in the project

## 10. Summary – conclusions

## 11. References

[1]: [...](...)
...
