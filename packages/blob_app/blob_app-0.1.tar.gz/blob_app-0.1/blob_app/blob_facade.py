# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from gaegraph.business_base import NodeSearch, DeleteNode
from blob_app.blob_commands import ListBlobFileCommand, SaveBlobFileCommand, UpdateBlobFileCommand, BlobFileForm, \
    SaveBlobFiles, ListBlobsFromOwnerCmd, SaveBlobFilesWithOwner, DeleteBlobFiles, GetBlobFile


def save_blob_files_cmd(blob_infos, owner=None):
    """
    Save BlobFiles respective to blob_info on db.
    Try to generate to img_url
    :param owner: object
    :param blob_infos: BlobInfo from uploaded files
    :param owner: BlobFile's owner
    :return: CommandParallel containing BlobFile list as result
    """
    if owner is None:
        return SaveBlobFiles(*blob_infos)
    return SaveBlobFilesWithOwner(owner, *blob_infos)


def list_blob_files_cmd(owner=None):
    """
    Command to list BlobFile entities ordered by their creation dates.
    If owner is provided, search only for her file's

    :param owner: a Node
    :return: a Command proceed the db operations when executed
    """
    if owner is None:
        return ListBlobFileCommand()
    return ListBlobsFromOwnerCmd(owner)


def blob_file_form(**kwargs):
    """
    Function to get BlobFile's detail form.
    :param kwargs: form properties
    :return: Form
    """
    return BlobFileForm(**kwargs)


def get_blob_file_cmd(blob_file_id):
    """
    Find blob_file by her id
    :param blob_file_id: the blob_file id
    :return: Command
    """
    return GetBlobFile(blob_file_id)


def delete_blob_file_cmd(*blob_file_ids):
    """
    Construct a command to delete a BlobFile
    :param blob_file_id: blob_file's id
    :return: Command
    """
    return DeleteBlobFiles(*blob_file_ids)
