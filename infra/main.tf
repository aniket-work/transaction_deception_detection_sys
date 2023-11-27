resource "aws_s3_bucket" "trans_decp_detect_s3_bucket" {
  bucket        = "${var.project_name}-bucket"
  acl           = "private"
  force_destroy = true
}

resource "aws_s3_bucket_object" "trans_decp_detect_feature_upload" {
  bucket = aws_s3_bucket.trans_decp_detect_s3_bucket.bucket
  key    = "trans_decp_detect_features/table.parquet"
  source = "${path.module}/../data/trans_decp_detect.parquet"
}

resource "aws_iam_role" "s3_trans_decp_role" {
  name = "s3_trans_decp_role"

  assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "redshift.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF
}

data "aws_iam_role" "AWSServiceRoleForRedshift" {
  name = "AWSServiceRoleForRedshift"
}

resource "aws_iam_role_policy_attachment" "s3_read" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
  role       = aws_iam_role.s3_trans_decp_role.name
}

resource "aws_iam_role_policy_attachment" "glue_full" {
  policy_arn = "arn:aws:iam::aws:policy/AWSGlueConsoleFullAccess"
  role       = aws_iam_role.s3_trans_decp_role.name
}


resource "aws_iam_policy" "s3_full_access_policy" {
  name = "s3_full_access_policy"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "s3:*"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "s3-policy-attachment" {
  role       = aws_iam_role.s3_trans_decp_role.name
  policy_arn = aws_iam_policy.s3_full_access_policy.arn
}

resource "aws_redshift_cluster" "trans_decp_redshift_cluster" {
  cluster_identifier = "${var.project_name}-redshift-cluster"
  iam_roles = [
    data.aws_iam_role.AWSServiceRoleForRedshift.arn,
    aws_iam_role.s3_trans_decp_role.arn
  ]
  database_name   = var.database_name
  master_username = var.admin_user
  master_password = var.admin_password
  node_type       = var.node_type
  cluster_type    = var.cluster_type
  number_of_nodes = var.nodes

  skip_final_snapshot = true
}


resource "aws_glue_catalog_table" "trans_decp_detect_features_table" {
  name          = "trans_decp_detect_features"
  database_name = var.database_name

  table_type = "EXTERNAL_TABLE"

  parameters = {
    EXTERNAL              = "TRUE"
    "parquet.compression" = "SNAPPY"
  }

  storage_descriptor {
    location      = "s3://${aws_s3_bucket.trans_decp_detect_s3_bucket.bucket}/trans_decp_detect_features/"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      name                  = "transcation-stream"
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"

      parameters = {
        "serialization.format" = 1
      }
    }

    columns {
      name = "transactionid"
      type = "BIGINT"
    }
  
  }
  depends_on = [
    resource.aws_glue_catalog_database.glue_db
  ]
}