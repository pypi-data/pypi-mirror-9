from __future__ import unicode_literals

import json
from six.moves.urllib.parse import urlparse

from moto.core.responses import BaseResponse
from moto.s3 import s3_backend
from .models import cloudformation_backends


class CloudFormationResponse(BaseResponse):

    @property
    def cloudformation_backend(self):
        return cloudformation_backends[self.region]

    def _get_stack_from_s3_url(self, template_url):
        template_url_parts = urlparse(template_url)
        bucket_name = template_url_parts.netloc.split(".")[0]
        key_name = template_url_parts.path.lstrip("/")

        key = s3_backend.get_key(bucket_name, key_name)
        return key.value.decode("utf-8")

    def create_stack(self):
        stack_name = self._get_param('StackName')
        stack_body = self._get_param('TemplateBody')
        template_url = self._get_param('TemplateURL')
        parameters_list = self._get_list_prefix("Parameters.member")

        # Hack dict-comprehension
        parameters = dict([
            (parameter['parameter_key'], parameter['parameter_value'])
            for parameter
            in parameters_list
        ])
        if template_url:
            stack_body = self._get_stack_from_s3_url(template_url)
        stack_notification_arns = self._get_multi_param('NotificationARNs.member')

        stack = self.cloudformation_backend.create_stack(
            name=stack_name,
            template=stack_body,
            parameters=parameters,
            region_name=self.region,
            notification_arns=stack_notification_arns
        )
        stack_body = {
            'CreateStackResponse': {
                'CreateStackResult': {
                    'StackId': stack.stack_id,
                }
            }
        }
        return json.dumps(stack_body)

    def describe_stacks(self):
        stack_name_or_id = None
        if self._get_param('StackName'):
            stack_name_or_id = self.querystring.get('StackName')[0]
        stacks = self.cloudformation_backend.describe_stacks(stack_name_or_id)

        template = self.response_template(DESCRIBE_STACKS_TEMPLATE)
        return template.render(stacks=stacks)

    def describe_stack_resources(self):
        stack_name = self._get_param('StackName')
        stack = self.cloudformation_backend.get_stack(stack_name)

        template = self.response_template(LIST_STACKS_RESOURCES_RESPONSE)
        return template.render(stack=stack)

    def list_stacks(self):
        stacks = self.cloudformation_backend.list_stacks()
        template = self.response_template(LIST_STACKS_RESPONSE)
        return template.render(stacks=stacks)

    def get_template(self):
        name_or_stack_id = self.querystring.get('StackName')[0]

        stack = self.cloudformation_backend.get_stack(name_or_stack_id)
        return stack.template

    # def update_stack(self):
    #     stack_name = self._get_param('StackName')
    #     stack_body = self._get_param('TemplateBody')

    #     stack = self.cloudformation_backend.update_stack(
    #         name=stack_name,
    #         template=stack_body,
    #     )
    #     stack_body = {
    #         'UpdateStackResponse': {
    #             'UpdateStackResult': {
    #                 'StackId': stack.name,
    #             }
    #         }
    #     }
    #     return json.dumps(stack_body)

    def delete_stack(self):
        name_or_stack_id = self.querystring.get('StackName')[0]

        self.cloudformation_backend.delete_stack(name_or_stack_id)
        return json.dumps({
            'DeleteStackResponse': {
                'DeleteStackResult': {},
            }
        })


DESCRIBE_STACKS_TEMPLATE = """<DescribeStacksResult>
  <Stacks>
    {% for stack in stacks %}
    <member>
      <StackName>{{ stack.name }}</StackName>
      <StackId>{{ stack.stack_id }}</StackId>
      <CreationTime>2010-07-27T22:28:28Z</CreationTime>
      <StackStatus>{{ stack.status }}</StackStatus>
      {% if stack.notification_arns %}
      <NotificationARNs>
        {% for notification_arn in stack.notification_arns %}
        <member>{{ notification_arn }}</member>
        {% endfor %}
      </NotificationARNs>
      {% else %}
      <NotificationARNs/>
      {% endif %}
      <DisableRollback>false</DisableRollback>
      <Outputs>
      {% for output in stack.stack_outputs %}
        <member>
          <OutputKey>{{ output.key }}</OutputKey>
          <OutputValue>{{ output.value }}</OutputValue>
        </member>
      {% endfor %}
      </Outputs>
      <Parameters>
      {% for param_name, param_value in stack.stack_parameters.items() %}
        <member>
          <ParameterKey>{{ param_name }}</ParameterKey>
          <ParameterValue>{{ param_value }}</ParameterValue>
        </member>
      {% endfor %}
      </Parameters>
    </member>
    {% endfor %}
  </Stacks>
</DescribeStacksResult>"""


LIST_STACKS_RESPONSE = """<ListStacksResponse>
 <ListStacksResult>
  <StackSummaries>
    {% for stack in stacks %}
    <member>
        <StackId>{{ stack.id }}</StackId>
        <StackStatus>{{ stack.status }}</StackStatus>
        <StackName>{{ stack.name }}</StackName>
        <CreationTime>2011-05-23T15:47:44Z</CreationTime>
        <TemplateDescription>{{ stack.description }}</TemplateDescription>
    </member>
    {% endfor %}
  </StackSummaries>
 </ListStacksResult>
</ListStacksResponse>"""


LIST_STACKS_RESOURCES_RESPONSE = """<DescribeStackResourcesResult>
  <StackResources>
    {% for resource in stack.stack_resources %}
    <member>
      <StackId>{{ stack.stack_id }}</StackId>
      <StackName>{{ stack.name }}</StackName>
      <LogicalResourceId>{{ resource.logical_resource_id }}</LogicalResourceId>
      <PhysicalResourceId>{{ resource.physical_resource_id }}</PhysicalResourceId>
      <ResourceType>{{ resource.type }}</ResourceType>
      <Timestamp>2010-07-27T22:27:28Z</Timestamp>
      <ResourceStatus>{{ stack.status }}</ResourceStatus>
    </member>
    {% endfor %}
  </StackResources>
</DescribeStackResourcesResult>"""
