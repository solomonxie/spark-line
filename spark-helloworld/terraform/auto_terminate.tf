# Safety net: self-terminates aws_instance.spark_hello_node ~2 hours after
# creation so a forgotten sandbox doesn't rack up cost. One-time EventBridge
# Scheduler rule, no Lambda involved:
#
#   time_offset.self_terminate_at        (now + 2h, pinned to instance_id
#                                          via `triggers` so re-applies don't
#                                          keep pushing the deadline out)
#   data.aws_caller_identity.current     (account id, for the IAM resource ARN)
#           │
#           ▼
#   aws_iam_role.scheduler_terminate     (trust: scheduler.amazonaws.com)
#     └─ aws_iam_role_policy             (ec2:TerminateInstances, scoped to
#                                          this one instance's ARN only)
#           │
#           ▼
#   aws_scheduler_schedule.self_terminate
#     ├─ schedule_expression = at(<time_offset>)   — fires once, UTC
#     └─ target = EC2 TerminateInstances (AWS SDK universal target)
#
# This only ever calls TerminateInstances on aws_instance.spark_hello_node —
# it cannot touch any other resource. `make destroy-infra` still works fine
# before the 2h mark; the schedule fires a no-op if the instance is already
# gone by then. It stays around afterward (state COMPLETED) rather than
# deleting itself, so it doesn't drift out from under Terraform's state.

resource "time_offset" "self_terminate_at" {
  offset_hours = 2

  triggers = {
    instance_id = aws_instance.spark_hello_node.id
  }
}

data "aws_caller_identity" "current" {}

resource "aws_iam_role" "scheduler_terminate" {
  name = "spark-hello-scheduler-terminate-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "scheduler.amazonaws.com" }
      Action    = "sts:AssumeRole"
      Condition = {
        StringEquals = { "aws:SourceAccount" = data.aws_caller_identity.current.account_id }
      }
    }]
  })
}

resource "aws_iam_role_policy" "scheduler_terminate" {
  name = "terminate-spark-hello-node"
  role = aws_iam_role.scheduler_terminate.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "ec2:TerminateInstances"
      Resource = "arn:aws:ec2:${var.aws_region}:${data.aws_caller_identity.current.account_id}:instance/${aws_instance.spark_hello_node.id}"
    }]
  })
}

resource "aws_scheduler_schedule" "self_terminate" {
  name = "spark-hello-self-terminate"

  flexible_time_window {
    mode = "OFF"
  }

  # AWS `at()` expressions take no timezone suffix; default schedule
  # timezone is UTC.
  schedule_expression = "at(${formatdate("YYYY-MM-DD'T'hh:mm:ss", time_offset.self_terminate_at.rfc3339)})"

  target {
    arn      = "arn:aws:scheduler:::aws-sdk:ec2:terminateInstances"
    role_arn = aws_iam_role.scheduler_terminate.arn

    input = jsonencode({
      InstanceIds = [aws_instance.spark_hello_node.id]
    })
  }

  # No action_after_completion knob in this provider version — AWS defaults
  # a one-time schedule to ActionAfterCompletion=NONE, i.e. it stays around
  # (state COMPLETED) after firing instead of deleting itself.
}
