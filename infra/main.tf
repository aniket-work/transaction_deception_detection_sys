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