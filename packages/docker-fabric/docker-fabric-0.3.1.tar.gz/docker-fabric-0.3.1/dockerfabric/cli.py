# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import posixpath

from fabric.api import cd, get, run, sudo
from fabric.network import needs_host

from dockermap.shortcuts import chmod, chown, targz
from .utils.containers import temp_container
from .utils.files import temp_dir, is_directory


@needs_host
def copy_resource(container, resource, local_filename, contents_only=True):
    """
    Copies a resource from a container to a compressed tarball and downloads it.

    :param container: Container name or id.
    :type container: unicode
    :param resource: Name of resource to copy.
    :type resource: unicode
    :param local_filename: Path to store the tarball locally.
    :type local_filename: unicode
    :param contents_only: In case ``resource`` is a directory, put all contents at the root of the tar file. If this is
      set to ``False``, the directory itself will be at the root instead.
    :type contents_only: bool
    """
    with temp_dir() as remote_tmp:
        base_name = os.path.basename(resource)
        copy_path = posixpath.join(remote_tmp, 'copy_tmp')
        remote_name = posixpath.join(copy_path, base_name)
        archive_name = 'container_{0}.tar.gz'.format(container)
        archive_path = posixpath.join(remote_tmp, archive_name)
        run('docker cp {0}:{1} {2}'.format(container, resource, copy_path), shell=False)
        if contents_only and is_directory(remote_name):
            src_dir = remote_name
            src_files = '*'
        else:
            src_dir = copy_path
            src_files = base_name
        with cd(src_dir):
            run(targz(archive_path, src_files))
        get(archive_path, local_filename)


@needs_host
def copy_resources(src_container, src_resources, storage_dir, dst_directories={}, apply_chown=None, apply_chmod=None):
    """
    Copies files and directories from a Docker container. Multiple resources can be copied and additional options are
    available than in :func:`copy_resource`. Unlike in :func:`copy_resource`, Resources are copied as they are and not
    compressed to a tarball, and they are left on the remote machine.

    :param src_container: Container name or id.
    :type src_container: unicode
    :param src_resources: Resources, as (file or directory) names to copy.
    :type src_resources: iterable
    :param storage_dir: Remote directory to store the copied objects in.
    :type storage_dir: unicode
    :param dst_directories: Optional dictionary of destination directories, in the format ``resource: destination``. If
      not set, resources will be in the same relative structure to one another as inside the container. For setting a
      common default, use ``*`` as the resource key.
    :type dst_directories: dict
    :param apply_chown: Owner to set for the copied resources. Can be a user name or id, group name or id, both in the
      notation ``user:group``, or as a tuple ``(user, group)``.
    :type apply_chown: unicode or tuple
    :param apply_chmod: File system permissions to set for the copied resources. Can be any notation as accepted by
      `chmod`.
    :type apply_chmod: unicode
    """
    def _copy_resource(resource):
        default_dest_path = generic_path if generic_path is not None else resource
        dest_path = dst_directories.get(resource, default_dest_path).strip(posixpath.sep)
        head, tail = posixpath.split(dest_path)
        rel_path = posixpath.join(storage_dir, head)
        run('docker cp {0}:{1} {2}'.format(src_container, resource, rel_path), shell=False)

    generic_path = dst_directories.get('*')
    for res in src_resources:
        _copy_resource(res)
    if apply_chmod:
        run(chmod(apply_chmod, storage_dir))
    if apply_chown:
        sudo(chown(apply_chown, storage_dir))


@needs_host
def isolate_and_get(src_container, src_resources, local_dst_dir, **kwargs):
    """
    Uses :func:`copy_resources` to copy resources from a container, but afterwards generates a compressed tarball
    and downloads it.

    :param src_container: Container name or id.
    :type src_container: unicode
    :param src_resources: Resources, as (file or directory) names to copy.
    :type src_resources: iterable
    :param local_dst_dir: Local directory to store the compressed tarball in. Can also be a file name; the default file
      name is ``container_<container name>.tar.gz``.
    :type local_dst_dir: unicode
    :param kwargs: Additional kwargs for :func:`copy_resources`.
    """
    with temp_dir() as remote_tmp:
        copy_path = posixpath.join(remote_tmp, 'copy_tmp')
        archive_path = posixpath.join(remote_tmp, 'container_{0}.tar.gz'.format(src_container))
        copy_resources(src_container, src_resources, copy_path, **kwargs)
        with cd(copy_path):
            sudo(targz(archive_path, '*'))
        get(archive_path, local_dst_dir)


@needs_host
def isolate_to_image(src_container, src_resources, dst_image, **kwargs):
    """
    Uses :func:`copy_resources` to copy resources from a container, but afterwards imports the contents into a new
    (otherwise empty) Docker image.

    :param src_container: Container name or id.
    :type src_container: unicode
    :param src_resources: Resources, as (file or directory) names to copy.
    :type src_resources: iterable
    :param dst_image: Tag for the new image.
    :type dst_image: unicode
    :param kwargs: Additional kwargs for :func:`copy_resources`.
    """
    with temp_dir() as remote_tmp:
        copy_resources(src_container, src_resources, remote_tmp, **kwargs)
        with cd(remote_tmp):
            sudo('tar -cz * | docker import - {0}'.format(dst_image))


@needs_host
def save_image(image, local_filename):
    """
    Saves a Docker image as a compressed tarball. This command line client method is a suitable alternative, if the
    Remove API method is too slow.

    :param image: Image id or tag.
    :type image: unicode
    :param local_filename: Local file name to store the image into. If this is a directory, the image will be stored
      there as a file named ``image_<Image name>.tar.gz``.
    """
    r_name, __, i_name = image.rpartition('/')
    i_name, __, __ = i_name.partition(':')
    with temp_dir() as remote_tmp:
        archive = posixpath.join(remote_tmp, 'image_{0}.tar.gz'.format(i_name))
        run('docker save {0} | gzip --stdout > {1}'.format(image, archive), shell=False)
        get(archive, local_filename)


@needs_host
def flatten_image(image, dest_image=None, no_op_cmd='/bin/true', create_kwargs={}, start_kwargs={}):
    """
    Exports a Docker image's file system and re-imports it into a new (otherwise new) image. Note that this does not
    transfer the image configuration. In order to gain access to the container contents, the image is started with a
    non-operational command, such as ``/bin/true``. The container is removed once the new image has been created.

    :param image: Image id or tag.
    :type image: unicode
    :param dest_image: Tag for the new image.
    :type dest_image: unicode
    :param no_op_cmd: Dummy command for starting temporary container.
    :type no_op_cmd: unicode
    :param create_kwargs: Optional additional kwargs for creating the temporary container.
    :type create_kwargs: dict
    :param start_kwargs: Optional additional kwargs for starting the temporary container.
    :type start_kwargs: dict
    """
    dest_image = dest_image or image
    with temp_container(image, no_op_cmd=no_op_cmd, create_kwargs=create_kwargs, start_kwargs=start_kwargs) as c:
        run('docker export {0} | docker import - {1}'.format(c, dest_image), shell=False)
