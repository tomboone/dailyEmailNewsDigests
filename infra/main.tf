terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}

resource "azurerm_resource_group" "main" {
  name     = "rg-dailyemailnewsdigests"
  location = var.location
}

data "azurerm_service_plan" "existing" {
  name                = var.app_service_plan_name
  resource_group_name = var.app_service_plan_resource_group
}

data "azurerm_client_config" "current" {}
