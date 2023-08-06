# Copyright 2014 Isotoma Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from touchdown.core.plan import Plan
from touchdown.core import argument, serializers

from .account import BaseAccount, Account

from .session import Session


class ExternalRole(BaseAccount):

    resource_name = "external_role"

    name = argument.String(field="RoleSessionName")
    arn = argument.String(field="RoleArn")
    policy = argument.String(field="Policy")
    duration = argument.Integer(min=900, max=3600, field="DurationSeconds")

    external_id = argument.String(field="ExternalId")

    mfa_device = argument.String(field="SerialNumber")
    mfa_token = argument.String(field="TokenCode")

    account = argument.Resource(Account)


class Describe(Plan):

    resource = ExternalRole
    default = True
    name = "describe"
    _session = None
    _client = None

    @property
    def session(self):
        if not self._session:
            self.object = self.client.assume_role(
                **serializers.Resource().render(self.runner, self.resource)
            )

            c = self.object['Credentials']
            self._session = Session(
                access_key_id=c['AccessKeyId'],
                secret_access_key=c['SecretAccessKey'],
                session_token=c['SessionToken'],
                expiration=c['Expiration'],
                region=self.resource.account.region,
            )

        return self._session

    @property
    def client(self):
        session = self.runner.get_plan(self.resource.account).session
        if not self._client:
            self._client = session.create_client("sts")
        return self._client
