variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
}

variable "location" {
  description = "Azure region for all resources"
  type        = string
}

variable "app_service_plan_name" {
  description = "Name of the existing App Service Plan"
  type        = string
}

variable "app_service_plan_resource_group" {
  description = "Resource group containing the existing App Service Plan"
  type        = string
}

variable "terraform_sp_object_id" {
  description = "Object ID of the service principal used to run Terraform (for Key Vault access policy)"
  type        = string
}
