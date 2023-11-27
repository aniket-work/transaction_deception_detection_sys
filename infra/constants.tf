
variable "project_name" {
  type        = string
  default     = "my-feast-project-aws-cerebrium"
  description = "Unique project identifier for resource organization"
}

variable "region" {
  type        = string
  default     = "us-west-2"
  description = "Region in AWS where services will be provisioned"
}


variable "node_type" {
  type        = string
  default     = "dc2.large"
  description = "Type of node allocated for the cluster."
}

variable "database_name" {
  type        = string
  default     = "dev"
  description = "Initial database name created with the cluster"
}

variable "admin_user" {
  type        = string
  default     = "admin"
  description = " Master DB user's username"
}

variable "nodes" {
  type        = number
  default     = 1
  description = "Number of compute nodes in the cluster. Required when ClusterType is set to multi-node"
}

variable "admin_password" {
  type        = string
  default     = ""
  description = "Master DB user's password"
}

variable "cluster_type" {
  type        = string
  default     = "single-node"
  description = "Chosen cluster type: `single-node` or `multi-node`"
}


