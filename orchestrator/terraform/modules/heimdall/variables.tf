###############################################################################
# Environment-specific variables
#
# These must be set to the specific environment and so do not have defaults.
###############################################################################

variable "ver" {
  description = "Application version"
}

variable "environment" {
  description = "Environment name"
}

variable "db_read_capacity" {
  description = "The DynamoDB read capacity"
}

variable "db_write_capacity" {
  description = "The DynamoDB write capacity"
}

variable "aws_region" {
  description = "The region in which to deploy"
}

variable "tags" {
  type = map(string)
}

variable "domain_name" {
  description = "Domain to associate with the ACM certificate."
}

variable "zone_id" {
  description = "The Route53 zone ID in which to create records"
}

variable "api_stage" {
  default     = "v1"
  description = "API stage name"
}

variable "scan_orgs" {
  description = "Orgs to queue scans for"
  default     = []
}

variable "external_orgs" {
  description = "Orgs to only queue scans of private repos for"
  default     = []
}

variable "artemis_s3_bucket" {
  description = "Artemis S3 bucket where services.json is stored"
}

variable "artemis_api" {
  description = "Artemis API URL to initiate repo scans with"
}

variable "repo_scan_loop_rate" {
  description = "Rate at which to run the repo-scan-loop lambda"
}

variable "lambda_availability_zone" {
  description = "The AZ in which to deploy VPC Lambdas"
}

variable "scanning_enabled" {
  description = "Whether Heimdall actually initiates Artemis scans"
  default     = true
}

###############################################################################
# Environment-agnostic variables
#
# The default value should be correct for any environment and not need to be
# overridden.
###############################################################################

variable "app" {
  default = "heimdall"
}

variable "vpc_cidr" {
  description = "CIDR for the VPC"
  default     = "10.0.0.0/16"
}

variable "nat_gw_cidr" {
  description = "CIDR for the Lambdas NAT GW"
  default     = "10.0.15.0/24"
}

variable "lambda_cidr" {
  description = "CIDR for the Lambdas"
  default     = "10.0.16.0/20"
}

variable "org_queue_lambda_timeout" {
  description = "Timeout of org_queue Lambda in Seconds"
  default     = 900
}

variable "repo_queue_lambda_timeout" {
  description = "Timeout of repo_queue Lambda in Seconds"
  default     = 900
}

variable "repo_scan_lambda_timeout" {
  description = "Timeout of repo_scan Lambda in Seconds"
  default     = 900
}

variable "repo_scan_loop_lambda_timeout" {
  description = "Timeout of repo_scan_loop Lambda in Seconds"
  default     = 900
}

variable "lambda_runtime" {
  default = "python3.9"
}

variable "lambda_architecture" {
  default = "arm64"
}


variable "revproxy_api_key" {
  description = "API key if Artemis uses an authenticated revproxy to access private VCS instances"
  default     = "artemis/revproxy_api_key"
}

################################################
# GitHub App
################################################
variable "github_app_id" {}

variable "github_private_key" {
  description = "Secrets Manager key name containing the GitHub app private key"
  default     = "artemis/github-app-private-key"
}
