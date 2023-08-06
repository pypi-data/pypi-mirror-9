# Monocyte - Search and Destroy unwanted AWS Resources relentlessly.
# Copyright 2015 Immobilien Scout GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from boto import cloudformation
from monocyte.handler import Resource, Handler


class Stack(Handler):

    VALID_TARGET_STATES = ["DELETE_COMPLETE", "DELETE_IN_PROGRESS"]

    def fetch_regions(self):
        return cloudformation.regions()

    def fetch_unwanted_resources(self):
        for region in self.regions:
            connection = cloudformation.connect_to_region(region.name)
            unwanted_states = set(connection.valid_states)
            unwanted_states.remove("DELETE_COMPLETE")
            resources = connection.list_stacks(stack_status_filters=list(unwanted_states)) or []
            for resource in resources:
                yield Resource(resource, region.name)

    def to_string(self, resource):
        return "CloudFormation Stack found in {region}, ".format(**vars(resource)) + \
               "with name {stack_name}, created {creation_time}, " \
               "with state {stack_status}".format(**vars(resource.wrapped))

    def delete(self, resource):
        if resource.wrapped.stack_status in Stack.VALID_TARGET_STATES:
            self.logger.info("Skipping deletion: State '{0}' is a valid target state.".format(
                resource.wrapped.stack_status))
            return
        if self.dry_run:
            return
        self.logger.info("Initiating deletion sequence for {stack_name}.".format(**vars(resource.wrapped)))
        connection = cloudformation.connect_to_region(resource.region)
        connection.delete_stack(resource.wrapped.stack_id)
