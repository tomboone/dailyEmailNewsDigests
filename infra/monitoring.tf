data "azurerm_log_analytics_workspace" "existing" {
  name                = var.log_analytics_workspace_name
  resource_group_name = var.log_analytics_workspace_resource_group
}

resource "azurerm_application_insights" "main" {
  name                = "appi-dailyemaildigests"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  workspace_id        = data.azurerm_log_analytics_workspace.existing.id
  application_type    = "web"
}
