module "public_engine_cluster" {
  source = "./modules/engine_cluster"

  app               = var.app
  name              = "public"
  aws_region        = var.aws_region
  availability_zone = var.availability_zone
  tags              = var.tags

  vpc_id             = var.vpc_id
  vpc_route_table_id = var.vpc_route_table_id
  engine_cidr        = "10.0.4.0/24"

  engine_size           = var.pub_engine_size
  engine_scale_min      = var.engine_scale_min_public
  engine_scale_max      = var.engine_scale_max_public
  plugin_java_heap_size = var.pub_plugin_java_heap_size

  s3_analyzer_files_arn    = var.s3_analyzer_files_arn
  s3_analyzer_files_bucket = var.s3_analyzer_files_bucket
  s3_analyzer_files_id     = var.s3_analyzer_files_id

  maintenance_mode     = var.maintenance_mode
  system_status_lambda = aws_lambda_function.system_status

  aqua_enabled     = var.aqua_enabled
  veracode_enabled = var.veracode_enabled
  snyk_enabled     = var.snyk_enabled
  ghas_enabled     = var.ghas_enabled

  github_app_id = var.github_app_id

  docker_compose_ver = "2.5.1"

  heimdall_scans_cron = var.heimdall_scans_cron

  lambda_layers = concat([
    aws_lambda_layer_version.artemislib.arn,
    aws_lambda_layer_version.artemisdb.arn
  ], var.extra_lambda_layers_engine_scale_down)

  lambda_subnet = aws_subnet.lambdas
  lambda_sg     = aws_security_group.lambda-sg

  domain_name = var.domain_name

  metadata_scheme_modules = var.metadata_scheme_modules
  mandatory_include_paths = var.mandatory_include_paths

  revproxy_domain_substring = var.revproxy_domain_substring
  revproxy_secret           = var.revproxy_secret
  revproxy_secret_region    = var.revproxy_secret_region

  secrets_events_enabled       = var.secrets_events_enabled
  inventory_events_enabled     = var.inventory_events_enabled
  configuration_events_enabled = var.configuration_events_enabled
}

module "nat_engine_cluster" {
  source = "./modules/engine_cluster"

  app               = var.app
  name              = "nat"
  public            = false
  aws_region        = var.aws_region
  availability_zone = var.availability_zone
  tags              = var.tags

  vpc_id             = var.vpc_id
  vpc_route_table_id = aws_route_table.lambda_routes.id
  engine_cidr        = "10.0.1.0/24"

  engine_size           = var.nat_engine_size
  engine_scale_min      = var.engine_scale_min_nat
  engine_scale_max      = var.engine_scale_max_nat
  plugin_java_heap_size = var.nat_plugin_java_heap_size

  s3_analyzer_files_arn    = var.s3_analyzer_files_arn
  s3_analyzer_files_bucket = var.s3_analyzer_files_bucket
  s3_analyzer_files_id     = var.s3_analyzer_files_id

  maintenance_mode     = var.maintenance_mode
  system_status_lambda = aws_lambda_function.system_status

  aqua_enabled     = var.aqua_enabled
  veracode_enabled = var.veracode_enabled
  snyk_enabled     = var.snyk_enabled
  ghas_enabled     = var.ghas_enabled

  github_app_id = var.github_app_id

  docker_compose_ver = "2.5.1"

  heimdall_scans_cron = var.heimdall_scans_cron

  lambda_layers = concat([
    aws_lambda_layer_version.artemislib.arn,
    aws_lambda_layer_version.artemisdb.arn
  ], var.extra_lambda_layers_engine_scale_down)

  lambda_subnet = aws_subnet.lambdas
  lambda_sg     = aws_security_group.lambda-sg

  domain_name = var.domain_name

  metadata_scheme_modules = var.metadata_scheme_modules
  mandatory_include_paths = var.mandatory_include_paths

  revproxy_domain_substring = var.revproxy_domain_substring
  revproxy_secret           = var.revproxy_secret
  revproxy_secret_region    = var.revproxy_secret_region

  secrets_events_enabled       = var.secrets_events_enabled
  inventory_events_enabled     = var.inventory_events_enabled
  configuration_events_enabled = var.configuration_events_enabled
}
