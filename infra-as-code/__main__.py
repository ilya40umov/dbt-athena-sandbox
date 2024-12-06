from typing import Mapping, Optional

import pulumi
import pulumi_aws as aws
from pulumi_aws.glue import CatalogTableStorageDescriptorColumnArgs as ColumnArgs


def create_bucket(
    name: str, expiration_by_prefix: Optional[Mapping[str, int]] = None
) -> aws.s3.BucketV2:
    if expiration_by_prefix is None:
        expiration_by_prefix = {"": 30}

    bucket = aws.s3.BucketV2(
        f"{name}-bucket",
        bucket=f"{name}-abc123",
        force_destroy=True,
    )
    aws.s3.BucketLifecycleConfigurationV2(
        f"{name}-bucket-lifecycle",
        bucket=bucket.id,
        rules=[
            {
                "id": f"expire-{prefix if prefix else 'all'}-data",
                "status": "Enabled",
                "filter": {"prefix": f"{prefix}/*"},
                "expiration": {
                    "days": expiration_days,
                },
            }
            for (prefix, expiration_days) in expiration_by_prefix.items()
        ],
    )
    return bucket


def create_database(name: str) -> aws.glue.CatalogDatabase:
    return aws.glue.CatalogDatabase(
        f"{name}-database",
        name=name.replace("-", "_"),
        create_table_default_permissions=[
            aws.glue.CatalogDatabaseCreateTableDefaultPermissionArgs(
                permissions=["ALL"],
                principal=aws.glue.CatalogDatabaseCreateTableDefaultPermissionPrincipalArgs(
                    data_lake_principal_identifier="IAM_ALLOWED_PRINCIPALS"
                ),
            )
        ],
    )


def create_users_table(bucket: aws.s3.BucketV2, database: aws.glue.CatalogDatabase):
    aws.s3.BucketObject(
        "users-data-object",
        key="users/users.json",
        bucket=bucket.id,
        source=pulumi.FileAsset("data/users.json"),
    )
    aws.glue.CatalogTable(
        "landing-users-table",
        database_name=database.name,
        name="user",
        table_type="EXTERNAL_TABLE",
        storage_descriptor=aws.glue.CatalogTableStorageDescriptorArgs(
            location=pulumi.Output.concat(
                "s3://", sandbox_landing_bucket.bucket, "/users/"
            ),
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


def create_user_events_table(
    bucket: aws.s3.BucketV2, database: aws.glue.CatalogDatabase
):
    aws.s3.BucketObject(
        "user-events-data-object",
        key="user_events/user_events.json",
        bucket=bucket.id,
        source=pulumi.FileAsset("data/user_events.json"),
    )
    aws.glue.CatalogTable(
        "landing-user-events-table",
        database_name=database.name,
        name="user_event",
        table_type="EXTERNAL_TABLE",
        storage_descriptor=aws.glue.CatalogTableStorageDescriptorArgs(
            location=pulumi.Output.concat(
                "s3://", sandbox_landing_bucket.bucket, "/user_events/"
            ),
            input_format="org.apache.hadoop.mapred.TextInputFormat",
            output_format="org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat",
            ser_de_info=aws.glue.CatalogTableStorageDescriptorSerDeInfoArgs(
                serialization_library="org.apache.hive.hcatalog.data.JsonSerDe",
            ),
            columns=[
                ColumnArgs(name="id", type="bigint"),
                ColumnArgs(name="user_id", type="bigint"),
                ColumnArgs(name="type", type="string"),
                ColumnArgs(name="time", type="timestamp"),
            ],
        ),
    )


if __name__ == "__main__":
    sandbox_landing_bucket = create_bucket(name="sandbox-landing")
    create_bucket(name="sandbox-dbt-staging")
    create_bucket(
        name="sandbox-dbt-data",
        expiration_by_prefix={"sandbox_foundation": 30, "sandbox_mart": 365},
    )

    sandbox_landing_database = create_database(name="sandbox-landing")
    create_database(name="sandbox-foundation")
    create_database(name="sandbox-mart")

    create_users_table(sandbox_landing_bucket, sandbox_landing_database)
    create_user_events_table(sandbox_landing_bucket, sandbox_landing_database)
