aws s3api copy-object --bucket <bucket-name> --copy-source <bucket/key> --key <key> --metadata-directive "REPLACE" --metadata snowball-auto-extract=true
