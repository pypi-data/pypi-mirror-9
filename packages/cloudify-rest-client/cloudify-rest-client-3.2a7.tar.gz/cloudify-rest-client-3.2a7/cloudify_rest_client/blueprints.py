########
# Copyright (c) 2014 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.

import os
import tempfile
import shutil
import tarfile
import urllib
import urlparse
import contextlib

from os.path import expanduser

from cloudify_rest_client import bytes_stream_utils


class Blueprint(dict):

    def __init__(self, blueprint):
        self.update(blueprint)

    @property
    def id(self):
        """
        :return: The identifier of the blueprint.
        """
        return self.get('id')

    @property
    def created_at(self):
        """
        :return: Timestamp of blueprint creation.
        """
        return self.get('created_at')

    @property
    def plan(self):
        """
        Gets the plan the blueprint represents: nodes, relationships etc...

        :return: The content of the blueprint.
        """
        return self.get('plan')


class BlueprintsClient(object):

    def __init__(self, api):
        self.api = api

    @staticmethod
    def _tar_blueprint(blueprint_path, tempdir):
        blueprint_path = expanduser(blueprint_path)
        blueprint_name = os.path.basename(os.path.splitext(blueprint_path)[0])
        blueprint_directory = os.path.dirname(blueprint_path)
        if not blueprint_directory:
            # blueprint path only contains a file name from the local directory
            blueprint_directory = os.getcwd()
        tar_path = '{0}/{1}.tar.gz'.format(tempdir, blueprint_name)
        with tarfile.open(tar_path, "w:gz") as tar:
            tar.add(blueprint_directory,
                    arcname=os.path.basename(blueprint_directory))
        return tar_path

    def _upload(self, archive_location,
                blueprint_id,
                application_file_name=None):
        query_params = {}
        if application_file_name is not None:
            query_params['application_file_name'] = \
                urllib.quote(application_file_name)

        uri = '/blueprints/{0}'.format(blueprint_id)

        # For a Windows path (e.g. "C:\aaa\bbb.zip") scheme is the
        # drive letter and therefore the 2nd condition is present
        if urlparse.urlparse(archive_location).scheme and \
                not os.path.exists(archive_location):
            # archive location is URL
            query_params['blueprint_archive_url'] = archive_location
            data = None
        else:
            # archive location is a system path - upload it in chunks
            data = bytes_stream_utils.request_data_file_stream_gen(
                archive_location)

        return self.api.put(uri, params=query_params, data=data,
                            expected_status_code=201)

    def list(self, _include=None):
        """
        Returns a list of currently stored blueprints.

        :param _include: List of fields to include in response.
        :return: Blueprints list.
        """
        response = self.api.get('/blueprints', _include=_include)
        return [Blueprint(item) for item in response]

    def publish_archive(self, archive_location, blueprint_id,
                        blueprint_filename=None):
        """
        Publishes a blueprint archive to the Cloudify manager.

        :param archive_location: Path or Url to the archive file.
        :param blueprint_id: Id of the uploaded blueprint.
        :param blueprint_filename: The archive's main blueprint yaml filename.
        :return: Created blueprint.

        Archive file should contain a single directory in which there is a
        blueprint file named `blueprint_filename` (if `blueprint_filename`
        is None, this value will be passed to the REST service where a
        default value should be used).
        Blueprint ID parameter is available for specifying the
        blueprint's unique Id.
        """

        blueprint = self._upload(
            archive_location,
            blueprint_id=blueprint_id,
            application_file_name=blueprint_filename)
        return Blueprint(blueprint)

    def upload(self, blueprint_path, blueprint_id):
        """
        Uploads a blueprint to Cloudify's manager.

        :param blueprint_path: Main blueprint yaml file path.
        :param blueprint_id: Id of the uploaded blueprint.
        :return: Created blueprint.

        Blueprint path should point to the main yaml file of the blueprint
        to be uploaded. Its containing folder will be packed to an archive
        and get uploaded to the manager.
        Blueprint ID parameter is available for specifying the
        blueprint's unique Id.
        """
        tempdir = tempfile.mkdtemp()
        try:
            tar_path = self._tar_blueprint(blueprint_path, tempdir)
            application_file = os.path.basename(blueprint_path)

            blueprint = self._upload(
                tar_path,
                blueprint_id=blueprint_id,
                application_file_name=application_file)
            return Blueprint(blueprint)
        finally:
            shutil.rmtree(tempdir)

    def get(self, blueprint_id, _include=None):
        """
        Gets a blueprint by its id.

        :param blueprint_id: Blueprint's id to get.
        :param _include: List of fields to include in response.
        :return: The blueprint.
        """
        assert blueprint_id
        uri = '/blueprints/{0}'.format(blueprint_id)
        response = self.api.get(uri, _include=_include)
        return Blueprint(response)

    def delete(self, blueprint_id):
        """
        Deletes the blueprint whose id matches the provided blueprint id.

        :param blueprint_id: The id of the blueprint to be deleted.
        :return: Deleted blueprint.
        """
        assert blueprint_id
        response = self.api.delete('/blueprints/{0}'.format(blueprint_id))
        return Blueprint(response)

    def download(self, blueprint_id, output_file=None):
        """
        Downloads a previously uploaded blueprint from Cloudify's manager.

        :param blueprint_id: The Id of the blueprint to be downloaded.
        :param output_file: The file path of the downloaded blueprint file
         (optional)
        :return: The file path of the downloaded blueprint.
        """
        uri = '/blueprints/{0}/archive'.format(blueprint_id)

        with contextlib.closing(
                self.api.get(uri, stream=True)) as streamed_response:

            output_file = bytes_stream_utils.write_response_stream_to_file(
                streamed_response, output_file)

            return output_file
