import pulumi
import pulumi_azure_native as azure_native
import pulumi_random as random

db_password = random.RandomPassword("db_password", length=16, special=True)
config = pulumi.Config()
stack_name = config.require('stack_name')

resource_group = azure_native.resources.ResourceGroup("resource-group",
    location="uksouth",
    resource_group_name="CreditSuisse2_AnnieBedford_Workshop",
    opts=pulumi.ResourceOptions(protect=True))

app_service_plan = azure_native.web.AppServicePlan(f"{stack_name}-app-service-plan",
    hyper_v=False,
    is_spot=False,
    is_xenon=False,
    kind="linux",
    location="UK South",
    maximum_elastic_worker_count=1,
    per_site_scaling=False,
    reserved=True,
    resource_group_name=resource_group.name,
    sku=azure_native.web.SkuDescriptionArgs(
        capacity=1,
        family="B",
        name="B1",
        size="B1",
        tier="Basic",
    ),
    target_worker_count=0,
    target_worker_size_id=0,
    opts=pulumi.ResourceOptions(protect=True))

sql_server = azure_native.sql.Server(f"{stack_name}-sql-server",
    administrator_login="db",
    administrator_login_password=db_password.result,
    location="uksouth",
    public_network_access="Enabled",
    resource_group_name=resource_group.name,
    server_name="cs2mod12anniebedford-non-iac-sqlserver",
    version="12.0",
    opts=pulumi.ResourceOptions(protect=True))

sql_database = azure_native.sql.Database(f"{stack_name}-sql-database",
    catalog_collation="SQL_Latin1_General_CP1_CI_AS",
    collation="SQL_Latin1_General_CP1_CI_AS",
    database_name="cs2mod12anniebedford-non-iac-db",
    location="uksouth",
    maintenance_configuration_id="/subscriptions/d33b95c7-af3c-4247-9661-aa96d47fccc0/providers/Microsoft.Maintenance/publicMaintenanceConfigurations/SQL_Default",
    max_size_bytes=2147483648,
    read_scale="Disabled",
    requested_backup_storage_redundancy="Geo",
    resource_group_name=resource_group.name,
    server_name=sql_server.name,
    sku=azure_native.sql.SkuArgs(
        capacity=5,
        name="Basic",
        tier="Basic",
    ),
    zone_redundant=False,
    opts=pulumi.ResourceOptions(protect=True))

connection_string = pulumi.Output.all(sql_server.fully_qualified_domain_name, sql_database.name, sql_server.administrator_login, db_password.result) \
    .apply(lambda args: 
        f'Server=tcp:{args[0]},1433;Initial Catalog={args[1]};Persist Security Info=False;User ID={args[2]};Password={args[3]};MultipleActiveResultSets=False;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;'
    )

web_app = azure_native.web.WebApp(f"{stack_name}-web-app",
    client_affinity_enabled=False,
    client_cert_enabled=False,
    client_cert_mode="Required",
    container_size=0,
    custom_domain_verification_id="C11362A7BC6B6AE47600B6CA026E5B947B6577DA4AE022E214743600719CCB1D",
    daily_memory_time_quota=0,
    enabled=True,
    host_name_ssl_states=[
        azure_native.web.HostNameSslStateArgs(
            host_type="Standard",
            name="cs2mod12anniebedford-non-iac-app.azurewebsites.net",
            ssl_state="Disabled",
        ),
        azure_native.web.HostNameSslStateArgs(
            host_type="Repository",
            name="cs2mod12anniebedford-non-iac-app.scm.azurewebsites.net",
            ssl_state="Disabled",
        ),
    ],
    host_names_disabled=False,
    https_only=False,
    hyper_v=False,
    is_xenon=False,
    key_vault_reference_identity="SystemAssigned",
    kind="app,linux,container",
    location="UK South",
    redundancy_mode="None",
    reserved=True,
    resource_group_name=resource_group.name,
    scm_site_also_stopped=False,
    server_farm_id=app_service_plan.id,
    site_config=azure_native.web.SiteConfigArgs(
        acr_use_managed_identity_creds=False,
        always_on=False,
        function_app_scale_limit=0,
        http20_enabled=False,
        linux_fx_version="DOCKER|corndelldevopscourse/mod12app:latest",
        minimum_elastic_instance_count=0,
        number_of_workers=1,
        windows_fx_version="",
        app_settings=[
            azure_native.web.NameValuePairArgs(name="CONNECTION_STRING", value=connection_string),
            azure_native.web.NameValuePairArgs(name="DEPLOYMENT_METHOD", value="pulumi")
            ]
    ),
    storage_account_required=False,
    opts=pulumi.ResourceOptions(protect=True))


