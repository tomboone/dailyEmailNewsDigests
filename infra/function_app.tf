locals {
  key_vault_ref = "https://${azurerm_key_vault.main.name}.vault.azure.net/secrets"
}

resource "azurerm_linux_function_app" "main" {
  name                = "dailyemailnewsdigest"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  service_plan_id     = data.azurerm_service_plan.existing.id

  storage_account_name       = azurerm_storage_account.main.name
  storage_account_access_key = azurerm_storage_account.main.primary_access_key

  identity {
    type = "SystemAssigned"
  }

  site_config {
    always_on = true
    application_stack {
      python_version = "3.12"
    }
    cors {
      allowed_origins = ["https://portal.azure.com"]
    }
  }

  app_settings = {
    # Application Insights
    APPLICATIONINSIGHTS_CONNECTION_STRING = azurerm_application_insights.main.connection_string

    # Non-sensitive settings
    DIGEST_NAME       = "Racing News Digest"
    DIGESTS_NCRON     = "0 0 10 * * *"
    RSS_FETCH_NCRON   = "0 */5 * * * *"
    SMTP_PORT         = "587"
    WEBSITE_TIME_ZONE = "America/New_York"

    # Key Vault references
    SENDER                          = "@Microsoft.KeyVault(SecretUri=${local.key_vault_ref}/sender)"
    SMTP_SERVER                     = "@Microsoft.KeyVault(SecretUri=${local.key_vault_ref}/smtp-server)"
    SMTP_USER                       = "@Microsoft.KeyVault(SecretUri=${local.key_vault_ref}/smtp-user)"
    SMTP_PWD                        = "@Microsoft.KeyVault(SecretUri=${local.key_vault_ref}/smtp-pwd)"
    AZURE_STORAGE_CONNECTION_STRING = "@Microsoft.KeyVault(SecretUri=${local.key_vault_ref}/storage-connection-string)"
  }
}
