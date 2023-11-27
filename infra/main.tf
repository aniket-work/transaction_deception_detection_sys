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


