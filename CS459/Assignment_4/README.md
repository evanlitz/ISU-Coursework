# CS459 Assignment 4: VPC Isolation Mechanisms

**Course**: ComS/CprE 459/559 – Introduction to Cloud Computing Security, Iowa State University

## Overview

Comparative study of three mechanisms for accessing services across AWS VPCs, using independent AWS environments for each. The assignment is entirely AWS console/CLI work; the deliverable is a PDF report with screenshots and command outputs.

## Tasks

### Task 1 – Access via Public Internet (cross-region)
A web server EC2 instance is deployed in a public subnet in Region A (`us-east-1`), and a client instance is deployed in a separate VPC in Region B (`us-west-2`). The client reaches the server using its public IPv4 address over the internet.

**Key resources:** Internet-VPC-A (`10.0.0.0/16`), Internet-VPC-B (`10.1.0.0/16`), Internet Gateway, Apache httpd.

### Task 2 – Access via AWS PrivateLink
A web server runs in a **private subnet** (no public IP) in VPC-A. Access from a client in VPC-B is provided privately through an AWS PrivateLink interface endpoint, with no traffic traversing the public internet.

**Key resources:**
- VPC-A (`10.10.0.0/16`): bastion host in public subnet, web server in private subnet
- Network Load Balancer fronting the web server
- VPC Endpoint Service (with acceptance required) attached to the NLB
- VPC-B (`10.20.0.0/16`): client instance, Interface Endpoint

### Task 3 – Access via VPC Peering
A web server in the private subnet of VPC-1 is accessed by a client in VPC-2 using a VPC Peering connection. Route tables in both VPCs are updated to route traffic across the peering connection.

**Key resources:**
- VPC-1 (`10.30.0.0/16`): bastion host, web server in private subnet
- VPC-2 (`10.40.0.0/16`): client instance
- VPC Peering Connection (Active)
- Route table entries: VPC-1 → `10.40.0.0/16` via peering; VPC-2 → `10.30.0.0/16` via peering

## Comparison Summary

| Mechanism | Traffic path | Server needs public IP | Use case |
|-----------|-------------|----------------------|----------|
| Public Internet | Over the internet | Yes | Simple cross-region access |
| AWS PrivateLink | AWS private network | No | Expose service to consumers without full network access |
| VPC Peering | AWS private network | No | Full bidirectional private connectivity between VPCs |

## Deliverable

`CS459-Assignment-4-Report.pdf` — screenshots and command outputs for all three tasks.
