import pulumi
import pulumi_aws as aws
from pulumi_aws.glue import CatalogTableStorageDescriptorColumnArgs as ColumnArgs

if __name__ == "__main__":
    landing_bucket = aws.s3.BucketV2(
        "landing-bucket",
        bucket="sandbox-landing-abc123",
    )
    aws.s3.BucketLifecycleConfigurationV2(
        "landing-bucket-data-lifecycle",
        bucket=landing_bucket.id,
        rules=[
            {
                "id": "expire-all-data",
                "status": "Enabled",
                "expiration": {
                    "days": 30,
                },
            }
        ],
    )
    users_data_object = aws.s3.BucketObject(
        "users-data-object",
        key="users/users.json",
        bucket=landing_bucket.id,
        source=pulumi.FileAsset("../data/users.json"),
    )
    landing_database = aws.glue.CatalogDatabase(
        "landing-database",
        name="sandbox_landing",
        create_table_default_permissions=[
            aws.glue.CatalogDatabaseCreateTableDefaultPermissionArgs(
                permissions=["ALL"],
                principal=aws.glue.CatalogDatabaseCreateTableDefaultPermissionPrincipalArgs(
                    data_lake_principal_identifier="IAM_ALLOWED_PRINCIPALS"
                ),
            )
        ],
    )
    landing_users_table = aws.glue.CatalogTable(
        "landing-users-table",
        database_name=landing_database.name,
        name="user",
        table_type="EXTERNAL_TABLE",
        storage_descriptor=aws.glue.CatalogTableStorageDescriptorArgs(
            location=pulumi.Output.concat("s3://", landing_bucket.bucket, "/users/"),
            input_format="org.apache.hadoop.mapred.TextInputFormat",
            output_format="org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat",
            ser_de_info=aws.glue.CatalogTableStorageDescriptorSerDeInfoArgs(
                serialization_library="org.apache.hive.hcatalog.data.JsonSerDe",
            ),
            columns=[
                ColumnArgs(name="id", type="bigint"),
                ColumnArgs(name="name", type="string"),
                ColumnArgs(name="is_admin", type="boolean"),
            ],
        ),
    )

    dbt_staging_bucket = aws.s3.BucketV2(
        "dbt-staging-bucket",
        bucket="sandbox-dbt-staging-abc123",
    )
    aws.s3.BucketLifecycleConfigurationV2(
        "dbt-staging-bucket-data-lifecycle",
        bucket=dbt_staging_bucket.id,
        rules=[
            {
                "id": "expire-all-data",
                "status": "Enabled",
                "expiration": {
                    "days": 30,
                },
            }
        ],
    )

    dbt_data_bucket = aws.s3.BucketV2(
        "dbt-data-bucket",
        bucket="sandbox-dbt-data-abc123",
    )
    aws.s3.BucketLifecycleConfigurationV2(
        "dbt-data-bucket-data-lifecycle",
        bucket=dbt_data_bucket.id,
        rules=[
            {
                "id": "expire-clean-data",
                "status": "Enabled",
                "filter": {
                    "prefix": "clean/",
                },
                "expiration": {
                    "days": 30,
                },
            },
            {
                "id": "expire-mart-data",
                "status": "Enabled",
                "filter": {
                    "prefix": "mart/",
                },
                "expiration": {
                    "days": 365,
                },
            },
        ],
    )
    clean_database = aws.glue.CatalogDatabase(
        "clean-database",
        name="sandbox_clean",
        create_table_default_permissions=[
            aws.glue.CatalogDatabaseCreateTableDefaultPermissionArgs(
                permissions=["ALL"],
                principal=aws.glue.CatalogDatabaseCreateTableDefaultPermissionPrincipalArgs(
                    data_lake_principal_identifier="IAM_ALLOWED_PRINCIPALS"
                ),
            )
        ],
    )
    mart_database = aws.glue.CatalogDatabase(
        "mart-database",
        name="sandbox_mart",
        create_table_default_permissions=[
            aws.glue.CatalogDatabaseCreateTableDefaultPermissionArgs(
                permissions=["ALL"],
                principal=aws.glue.CatalogDatabaseCreateTableDefaultPermissionPrincipalArgs(
                    data_lake_principal_identifier="IAM_ALLOWED_PRINCIPALS"
                ),
            )
        ],
    )
