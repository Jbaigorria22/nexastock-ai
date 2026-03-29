resource "aws_lambda_function" "inventory_api" {
  function_name = var.project_name
  role          = var.lambda_role_arn
  handler       = "src.api.main.handler"
  runtime       = "python3.11"
  timeout       = 30
  memory_size   = 256

  filename         = "../function.zip"
  source_code_hash = filebase64sha256("../function.zip")

  environment {
    variables = {
      DATA_SOURCE      = "dynamodb"
      DYNAMODB_TABLE   = "inventory"
      AWS_REGION_NAME  = var.aws_region
    }
  }

  tags = {
    Project = var.project_name
    ManagedBy = "terraform"
  }
}

resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.inventory_api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.inventory.execution_arn}/*/*"
}

# Dale permiso a la Lambda para leer de SSM Parameter Store
resource "aws_iam_role_policy_attachment" "lambda_ssm_policy" {
  role       = split("/", var.lambda_role_arn)[1]
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMReadOnlyAccess"
}