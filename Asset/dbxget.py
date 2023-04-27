import pathlib
# from pandas import DataFrame
import dropbox
from dropbox.exceptions import AuthError
import dbxdata

DROPBOX_ACCESS_TOKEN = dbxdata.DROPBOX_ACCESS_TOKEN
DROPBOX_REFRESH_TOKEN = dbxdata.DROPBOX_REFRESH_TOKEN


def dropbox_connect():
    """Create a connection to Dropbox."""

    try:
        dbx = dropbox.Dropbox(app_key=dbxdata.app_key, app_secret=dbxdata.app_secret,
                              oauth2_access_token=dbxdata.DROPBOX_ACCESS_TOKEN,
                              oauth2_refresh_token=dbxdata.DROPBOX_REFRESH_TOKEN)
    except AuthError as e:
        print('Error connecting to Dropbox with access token: ' + str(e))
    return dbx


def dropbox_list_files(path):
    """Return a Pandas dataframe of files in a given Dropbox folder path in the Apps directory.
    """

    dbx = dropbox_connect()

    try:
        files = dbx.files_list_folder(path).entries
        files_list = []
        for file in files:
            if isinstance(file, dropbox.files.FileMetadata):
                metadata = {
                    'name': file.name,
                    'path_display': file.path_display,
                    'client_modified': file.client_modified,
                    'server_modified': file.server_modified
                }
                files_list.append(metadata)

        df = DataFrame.from_records(files_list)
        return df.sort_values(by='server_modified', ascending=False)

    except Exception as e:
        print('Error getting list of files from Dropbox: ' + str(e))


def dropbox_download_file(dropbox_file_path, local_directory_path):
    """Download a file from Dropbox to the local machine."""

    try:
        dbx = dropbox_connect()

        with open(f"{local_directory_path}/{dropbox_file_path}", 'wb') as f:
            metadata, result = dbx.files_download(path=dropbox_file_path)
            f.write(result.content)
        return True
    except Exception as e:
        print('Error downloading file from Dropbox: ' + str(e))
        raise print("Can't access to dropbox")
        return False


def dropbox_upload_file(local_path, local_file, dropbox_file_path):
    """Upload a file from the local machine to a path in the Dropbox app directory.

    Args:
        local_path (str): The path to the local file.
        local_file (str): The name of the local file.
        dropbox_file_path (str): The path to the file in the Dropbox app directory.

    Example:
        dropbox_upload_file('.', 'test.csv', '/stuff/test.csv')

    Returns:
        meta: The Dropbox file metadata.
    """

    try:
        dbx = dropbox_connect()

        local_file_path = pathlib.Path(local_path) / local_file

        with local_file_path.open("rb") as f:
            meta = dbx.files_upload(f.read(), dropbox_file_path, mode=dropbox.files.WriteMode("overwrite"))

            return meta
    except Exception as e:
        print('Error uploading file to Dropbox: ' + str(e))
        raise print("I can't upload to dropbox.")

