"""
Contains possible interactions with the Galaxy Data Libraries
"""
from bioblend.galaxy.client import Client


class LibraryClient(Client):

    def __init__(self, galaxy_instance):
        self.module = 'libraries'
        super(LibraryClient, self).__init__(galaxy_instance)

    def create_library(self, name, description=None, synopsis=None):
        """
        Create a data library with the properties defined in the arguments.
        Return a list of JSON dicts, looking like so::

        :type name: str
        :param name: Name of the new data library

        :type description: str
        :param description: Optional data library description

        :type synopsis: str
        :param synopsis: Optional data library synopsis

        :rtype: list
        :return: List of dicts describing created library

            [{"id": "f740ab636b360a70",
              "name": "Library from bioblend",
              "url": "/api/libraries/f740ab636b360a70"}]

        """
        payload = {'name': name}
        if description:
            payload['description'] = description
        if synopsis:
            payload['synopsis'] = synopsis
        return Client._post(self, payload)

    def delete_library(self, library_id):
        """
        Delete a data library.

        :type library_id: str
        :param library_id: Encoded data library ID identifying the library to be deleted

        .. warning::
            Deleting a data library is irreversible - all of the data from
            the library will be permanently deleted.
        """
        payload = {}
        return Client._delete(self, payload, id=library_id)

    def __show_item(self, library_id, item_id):
        url = self.gi._make_url(self, library_id, contents=True)
        url = '/'.join([url, item_id])
        return Client._get(self, url=url)

    def delete_library_dataset(self, library_id, dataset_id, purged=False):
        """
        Delete a library dataset in a data library.

        :type library_id: str
        :param library_id: library id where dataset is found in

        :type dataset_id: str
        :param dataset_id: id of the dataset to be deleted

        :type purged: bool
        :param purged: Indicate that the dataset should be purged (permanently deleted)

        :rtype: dict
        :return: A dictionary containing the dataset id and whether the dataset has been deleted
                 For example::

                 {u'deleted': True, u'id': u'60e680a037f41974'}
        """

        url = self.gi._make_url(self, library_id, contents=True)
        # Append the dataset_id to the base history contents URL
        url = '/'.join([url, dataset_id])
        return Client._delete(self, url=url, payload={'purged': purged})

    def show_dataset(self, library_id, dataset_id):
        """
        Get details about a given library dataset. The required ``library_id``
        can be obtained from the datasets's library content details.

        :type library_id: str
        :param library_id: library id where dataset is found in

        :type dataset_id: str
        :param dataset_id: id of the dataset to be inspected

        :rtype: dict
        :return: A dictionary containing information about the dataset in the library
        """
        return self.__show_item(library_id, dataset_id)

    def show_folder(self, library_id, folder_id):
        """
        Get details about a given folder. The required ``folder_id``
        can be obtained from the folder's library content details.

        :type library_id: str
        :param library_id: library id to inspect folders in

        :type folder_id: str
        :param folder_id: id of the folder to be inspected
        """
        return self.__show_item(library_id, folder_id)

    def _get_root_folder_id(self, library_id):
        """
        Find the root folder (i.e. '/') of a library.

        :type library_id: str
        :param library_id: library id to find root of
        """
        l = self.show_library(library_id=library_id)
        if 'root_folder_id' in l:
            return l['root_folder_id']
        # Galaxy previous to release_13.04 does not have root_folder_id in
        # library dictionary, so resort to find the folder with name '/'
        library_contents = self.show_library(library_id=library_id, contents=True)
        for f in library_contents:
            if f['name'] == '/':
                return f['id']

    def create_folder(self, library_id, folder_name, description=None, base_folder_id=None):
        """
        Create a folder in a library.

        :type library_id: str
        :param library_id: library id to use

        :type folder_name: str
        :param folder_name: name of the new folder in the data library

        :type description: str
        :param description: description of the new folder in the data library

        :type base_folder_id: str
        :param base_folder_id: id of the folder where to create the new folder.
          If not provided, the root folder will be used
        """
        # Get root folder ID if no ID was provided
        if base_folder_id is None:
            base_folder_id = self._get_root_folder_id(library_id)
        # Compose the payload
        payload = {}
        payload['name'] = folder_name
        payload['folder_id'] = base_folder_id
        payload['create_type'] = 'folder'
        if description is not None:
            payload['description'] = description
        return Client._post(self, payload, id=library_id, contents=True)

    def get_folders(self, library_id, folder_id=None, name=None, deleted=False):
        """
        Get all the folders or filter specific one(s) via the provided ``name``
        or ``folder_id`` in data library with id ``library_id``. Provide only one
        argument: ``name`` or ``folder_id``, but not both.

        :type folder_id: str
        :param folder_id: filter for folder by folder id

        :type name: str
        :param name: filter for folder by name. For ``name`` specify the full
                     path of the folder starting from the library's root
                     folder, e.g. ``/subfolder/subsubfolder``.

        :type deleted: bool
        :param deleted: If set to ``True``, return folders that have been
                        deleted.

        :rtype: dict
        :return: list of dicts each containing basic information about a folder.
        """
        if folder_id is not None and name is not None:
            raise ValueError('Provide only one argument between name or folder_id, but not both')
        library_contents = self.show_library(library_id=library_id, contents=True)
        if folder_id is not None:
            folder = next((_ for _ in library_contents if _['type'] == 'folder' and _['id'] == folder_id), None)
            folders = [folder] if folder is not None else []
        elif name is not None:
            folders = [_ for _ in library_contents if _['type'] == 'folder' and _['name'] == name]
        else:
            folders = [_ for _ in library_contents if _['type'] == 'folder']
        return folders

    def get_libraries(self, library_id=None, name=None, deleted=False):
        """
        Get all the libraries or filter for specific one(s) via the provided name or ID.
        Provide only one argument: ``name`` or ``library_id``, but not both.

        :type library_id: str
        :param library_id: filter for library by library id

        :type name: str
        :param name: If ``name`` is set and multiple names match the given
                     name, all the libraries matching the argument will be
                     returned.

        :type deleted: bool
        :param deleted: If set to ``True``, return libraries that have been
                        deleted.

        :rtype: dict
        :return: list of dicts each containing basic information about a library.
        """
        if library_id is not None and name is not None:
            raise ValueError('Provide only one argument between name or library_id, but not both')
        libraries = Client._get(self, deleted=deleted)
        if library_id is not None:
            library = next((_ for _ in libraries if _['id'] == library_id), None)
            libraries = [library] if library is not None else []
        if name is not None:
            libraries = [_ for _ in libraries if _['name'] == name]
        return libraries

    def show_library(self, library_id, contents=False):
        """
        Get information about a library.

        :type library_id: str
        :param library_id: filter for library by library id

        :type contents: bool
        :param contents: True if want to get contents of the library (rather than just the library details).

        :rtype: list
        :return: a list of dicts containing library details.
        """
        return Client._get(self, id=library_id, contents=contents)

    def _do_upload(self, **keywords):
        """
        Set up the POST request and do the actual data upload to a data library.
        This method should not be called directly but instead refer to the methods
        specific for the desired type of data upload.
        """
        library_id = keywords['library_id']
        folder_id = keywords.get('folder_id', None)
        if folder_id is None:
            folder_id = self._get_root_folder_id(library_id)
        files_attached = False
        # Compose the payload dict
        payload = {}
        payload['folder_id'] = folder_id
        payload['file_type'] = keywords.get('file_type', 'auto')
        payload['dbkey'] = keywords.get('dbkey', '?')
        payload['create_type'] = 'file'
        if keywords.get("roles", None):
            payload["roles"] = keywords["roles"]
        if keywords.get("link_data_only", None) and keywords['link_data_only'] != 'copy_files':
            payload["link_data_only"] = 'link_to_files'
        # upload options
        if keywords.get('file_url', None) is not None:
            payload['upload_option'] = 'upload_file'
            payload['files_0|url_paste'] = keywords['file_url']
        elif keywords.get('pasted_content', None) is not None:
            payload['upload_option'] = 'upload_file'
            payload['files_0|url_paste'] = keywords['pasted_content']
        elif keywords.get('server_dir', None) is not None:
            payload['upload_option'] = 'upload_directory'
            payload['server_dir'] = keywords['server_dir']
        elif keywords.get('file_local_path', None) is not None:
            payload['upload_option'] = 'upload_file'
            payload['files_0|file_data'] = open(keywords['file_local_path'], 'rb')
            files_attached = True
        elif keywords.get("filesystem_paths", None) is not None:
            payload["upload_option"] = "upload_paths"
            payload["filesystem_paths"] = keywords["filesystem_paths"]

        r = Client._post(self, payload, id=library_id, contents=True,
                         files_attached=files_attached)

        if payload.get('files_0|file_data', None) is not None:
            payload['files_0|file_data'].close()

        return r

    def upload_file_from_url(self, library_id, file_url, folder_id=None, file_type='auto', dbkey='?'):
        """
        Upload a file to a library from a URL.

        :type library_id: str
        :param library_id: id of the library where to place the uploaded file

        :type file_url: str
        :param file_url: URL of the file to upload

        :type folder_id: str
        :param folder_id: id of the folder where to place the uploaded file.
          If not provided, the root folder will be used

        :type file_type: str
        :param file_type: Galaxy file format name

        :type dbkey: str
        :param dbkey: Dbkey
        """
        # TODO: Is there a better way of removing self from locals?
        vars = locals().copy()
        del vars['self']
        return self._do_upload(**vars)

    def upload_file_contents(self, library_id, pasted_content, folder_id=None, file_type='auto', dbkey='?'):
        """
        Upload pasted_content to a data library as a new file.

        :type library_id: str
        :param library_id: id of the library where to place the uploaded file

        :type pasted_content: str
        :param pasted_content: Content to upload into the library

        :type folder_id: str
        :param folder_id: id of the folder where to place the uploaded file.
          If not provided, the root folder will be used

        :type file_type: str
        :param file_type: Galaxy file format name

        :type dbkey: str
        :param dbkey: Dbkey
        """
        vars = locals().copy()
        del vars['self']
        return self._do_upload(**vars)

    def upload_file_from_local_path(self, library_id, file_local_path,
                                    folder_id=None, file_type='auto', dbkey='?'):
        """
        Read local file contents from file_local_path and upload data to a
        library.

        :type library_id: str
        :param library_id: id of the library where to place the uploaded file

        :type file_local_path: str
        :param file_local_path: path of local file to upload

        :type folder_id: str
        :param folder_id: id of the folder where to place the uploaded file.
          If not provided, the root folder will be used

        :type file_type: str
        :param file_type: Galaxy file format name

        :type dbkey: str
        :param dbkey: Dbkey
        """
        vars = locals().copy()
        del vars['self']
        return self._do_upload(**vars)

    def upload_file_from_server(self, library_id, server_dir, folder_id=None,
                                file_type='auto', dbkey='?', link_data_only=None,
                                roles=""):
        """
        Upload all files in the specified subdirectory of the Galaxy library
        import directory to a library.

        .. note::
          For this method to work, the Galaxy instance must have the
          ``library_import_dir`` option configured in the ``config/galaxy.ini``
          configuration file.

        :type library_id: str
        :param library_id: id of the library where to place the uploaded file

        :type server_dir: str
        :param server_dir: relative path of the subdirectory of
          ``library_import_dir`` to upload. All and only the files (i.e. no
          subdirectories) contained in the specified directory will be
          uploaded.

        :type folder_id: str
        :param folder_id: id of the folder where to place the uploaded files.
          If not provided, the root folder will be used

        :type file_type: str
        :param file_type: Galaxy file format name

        :type dbkey: str
        :param dbkey: Dbkey

        :type link_data_only: str
        :param link_data_only: either 'copy_files' (default) or
          'link_to_files'. Setting to 'link_to_files' symlinks instead of
          copying the files

        :type roles: str
        :param roles: ???
        """
        vars = locals().copy()
        del vars['self']
        return self._do_upload(**vars)

    def upload_from_galaxy_filesystem(self, library_id, filesystem_paths, folder_id=None,
                                      file_type="auto", dbkey="?", link_data_only=None,
                                      roles=""):
        """
        Upload a set of files already present on the filesystem of the Galaxy
        server to a library.

        .. note::
          For this method to work, the Galaxy instance must have the
          ``allow_library_path_paste`` option set to ``True`` in the
          ``config/galaxy.ini`` configuration file.

        :type library_id: str
        :param library_id: id of the library where to place the uploaded file

        :type filesystem_paths: str
        :param filesystem_paths: file paths on the Galaxy server to upload to
          the library, one file per line

        :type folder_id: str
        :param folder_id: id of the folder where to place the uploaded files.
          If not provided, the root folder will be used

        :type file_type: str
        :param file_type: Galaxy file format name

        :type dbkey: str
        :param dbkey: Dbkey

        :type link_data_only: str
        :param link_data_only: either 'copy_files' (default) or
          'link_to_files'. Setting to 'link_to_files' symlinks instead of
          copying the files

        :type roles: str
        :param roles: ???
        """
        vars = locals().copy()
        del vars['self']
        return self._do_upload(**vars)

    def copy_from_dataset(self, library_id, dataset_id, folder_id=None, message=''):
        """
        Copy a Galaxy dataset into a library.

        :type library_id: str
        :param library_id: id of the library where to place the uploaded file

        :type dataset_id: str
        :param dataset_id: id of the dataset to copy from

        :type folder_id: str
        :param folder_id: id of the folder where to place the uploaded files.
          If not provided, the root folder will be used

        :type message: str
        :param message: message for copying action
        """
        if folder_id is None:
            folder_id = self._get_root_folder_id(library_id)
        payload = {}
        payload['folder_id'] = folder_id
        payload['create_type'] = 'file'
        payload['from_hda_id'] = dataset_id
        payload['ldda_message'] = message
        return Client._post(self, payload, id=library_id, contents=True)

    def set_library_permissions(self, library_id, access_in=None, modify_in=None,
                                add_in=None, manage_in=None):
        """
        Sets the permissions for a library.  Note: it will override all
        security for this library even if you leave out a permission type.

        :type library_id: str
        :param library_id: id of the library

        :type access_in: list
        :param access_in: list of user ids

        :type modify_in: list
        :param modify_in: list of user ids

        :type add_in: list
        :param add_in: list of user ids

        :type manage_in: list
        :param manage_in: list of user ids
        """

        payload = {}
        if access_in:
            payload['LIBRARY_ACCESS_in'] = access_in
        if modify_in:
            payload['LIBRARY_MODIFY_in'] = modify_in
        if add_in:
            payload['LIBRARY_ADD_in'] = add_in
        if manage_in:
            payload['LIBRARY_MANAGE_in'] = manage_in

        # create the url
        url = self.url
        url = '/'.join([url, library_id, 'permissions'])

        return Client._post(self, payload, url=url)
