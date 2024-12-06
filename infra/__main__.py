import pulumi
import pulumi_aws as aws
from pulumi_aws.glue import CatalogTableStorageDescriptorColumnArgs as ColumnArgs


def create_bucket(name: str, expiration_in_days: int = 30) -> aws.s3.BucketV2:
    bucket = aws.s3.BucketV2(
        f"{name}-bucket",
        bucket=f"sandbox-{name}-abc123",
    )
    aws.s3.BucketLifecycleConfigurationV2(
        f"{name}-bucket-data-lifecycle",
        bucket=bucket.id,
        rules=[
            {
                "id": "expire-all-data",
                "status": "Enabled",
                "expiration": {
                    "days": expiration_in_days,
                },
            }
        ],
    )
    return bucket


def create_database(name: str) -> aws.glue.CatalogDatabase:
    return aws.glue.CatalogDatabase(
        f"{name}-database",
        name=f"sandbox_{name}",
        create_table_default_permissions=[
            aws.glue.CatalogDatabaseCreateTableDefaultPermissionArgs(
                permissions=["ALL"],
                principal=aws.glue.CatalogDatabaseCreateTableDefaultPermissionPrincipalArgs(
                    data_lake_principal_identifier="IAM_ALLOWED_PRINCIPALS"
                ),
            )
        ],
    )


def create_landing():
    landing_bucket = create_bucket(name="landing")
    landing_database = create_database(name="landing")

    aws.s3.BucketObject(
        "users-data-object",
        key="users/users.json",
        bucket=landing_bucket.id,
        source=pulumi.FileAsset("../data/users.json"),
    )
    aws.glue.CatalogTable(
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


def create_dbt_staging():
    create_bucket(name="dbt-staging")


def create_foundation():
    create_bucket(name="foundation")
    create_database(name="foundation")


def create_mart():
    create_bucket(name="mart", expiration_in_days=365)
    create_database(name="mart")


if __name__ == "__main__":
    create_landing()
    create_foundation()
    create_mart()
    create_dbt_staging()
