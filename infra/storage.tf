resource "azurerm_storage_account" "main" {
  name                     = "stdailyemaildigests"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  # No container is public (azure-webjobs-hosts and -secrets are both private). Explicit because
  # azurerm 5.x flipped the default to false, which changed this account when the provider moved.
  allow_nested_items_to_be_public = false
}
