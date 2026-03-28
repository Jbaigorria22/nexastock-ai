resource "aws_api_gateway_rest_api" "inventory" {
  name        = "${var.project_name}-gateway"
  description = "AI Inventory Dashboard API"
}

resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = aws_api_gateway_rest_api.inventory.id
  parent_id   = aws_api_gateway_rest_api.inventory.root_resource_id
  path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "proxy" {
  rest_api_id   = aws_api_gateway_rest_api.inventory.id
  resource_id   = aws_api_gateway_resource.proxy.id
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda" {
  rest_api_id             = aws_api_gateway_rest_api.inventory.id
  resource_id             = aws_api_gateway_resource.proxy.id
  http_method             = aws_api_gateway_method.proxy.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.inventory_api.invoke_arn
}

resource "aws_api_gateway_method" "root" {
  rest_api_id   = aws_api_gateway_rest_api.inventory.id
  resource_id   = aws_api_gateway_rest_api.inventory.root_resource_id
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "root" {
  rest_api_id             = aws_api_gateway_rest_api.inventory.id
  resource_id             = aws_api_gateway_rest_api.inventory.root_resource_id
  http_method             = aws_api_gateway_method.root.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.inventory_api.invoke_arn
}

resource "aws_api_gateway_deployment" "inventory" {
  rest_api_id = aws_api_gateway_rest_api.inventory.id

  depends_on = [
    aws_api_gateway_integration.lambda,
    aws_api_gateway_integration.root,
  ]
}

resource "aws_api_gateway_stage" "prod" {
  deployment_id = aws_api_gateway_deployment.inventory.id
  rest_api_id   = aws_api_gateway_rest_api.inventory.id
  stage_name    = "prod"
}

output "api_url" {
  description = "URL pública del API"
  value       = "${aws_api_gateway_stage.prod.invoke_url}"
}