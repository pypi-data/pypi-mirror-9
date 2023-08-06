#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 DNAnexus, Inc.
#
# This file is part of dx-toolkit (DNAnexus platform client libraries).
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may not
#   use this file except in compliance with the License. You may obtain a copy
#   of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

from __future__ import print_function, unicode_literals, division, absolute_import

import os
import unittest
import json
import tempfile
import shutil
import pipes
import dxpy
from dxpy_testutil import DXTestCase, check_output, temporary_project
import dxpy_testutil as testutil

def run(command, **kwargs):
    try:
        if isinstance(command, list) or isinstance(command, tuple):
            print("$ %s" % ' '.join(pipes.quote(f) for f in command))
            output = check_output(command, **kwargs)
        else:
            print("$ %s" % (command,))
            output = check_output(command, shell=True, **kwargs)
    except testutil.DXCalledProcessError as e:
        print('== stdout ==')
        print(e.output)
        print('== stderr ==')
        print(e.stderr)
        raise
    print(output)
    return output

TEST_APPS = os.path.join(os.path.dirname(__file__), 'file_load')
LOCAL_SCRIPTS = os.path.join(os.path.dirname(__file__), '..', 'scripts')
LOCAL_UTILS = os.path.join(os.path.dirname(__file__), '..', 'dxpy', 'utils')


def build_app_with_bash_helpers(app_dir, project_id):
    tempdir = tempfile.mkdtemp()
    try:
        updated_app_dir = os.path.join(tempdir, os.path.basename(app_dir))
        shutil.copytree(app_dir, updated_app_dir)
        # Copy the scripts we'd like to test. These can go directly into
        # /usr/local/bin in the guest, since the normal executables will
        # have been installed into /usr/bin, and /usr/local/bin will
        # appear earlier on the PATH, overriding them.
        resources_bindir = os.path.join(updated_app_dir, 'resources', 'usr', 'local', 'bin')
        if not os.path.exists(resources_bindir):
            os.makedirs(resources_bindir)
        shutil.copy(os.path.join(LOCAL_SCRIPTS, 'dx-download-all-inputs'), resources_bindir)
        shutil.copy(os.path.join(LOCAL_SCRIPTS, 'dx-upload-all-outputs'), resources_bindir)

        # Now copy any libraries we depend on. This is tricky to get
        # right in general (because we will end up with some subset of
        # the files from whatever version is installed on the worker by
        # default, and some subset of files replaced with our custom
        # versions here). So it might be wise to keep at a minimum the
        # number of files that will be replaced here.
        #
        # In order to prevent the files in the resources bundle that go
        # into /usr/share/dnanexus/... from being clobbered at
        # execDepends installation time with the (older) versions from
        # dx-toolkit, we do the following multi-stage deployment:
        # (1) At build time, copy the files into /opt/utils_staging_area
        # (2) Then, at runtime, copy the files into the proper place.
        utils_staging_area = os.path.join(updated_app_dir, 'resources', 'opt', 'utils_staging_area')
        os.makedirs(utils_staging_area)
        preamble = []
        for filename in ('file_load_utils.py', 'printing.py'):
            shutil.copy(os.path.join(LOCAL_UTILS, filename), utils_staging_area)
            cmd = "cp /opt/utils_staging_area/{f} /usr/share/dnanexus/lib/python2.7/site-packages/*/dxpy/utils;\n"
            preamble.append(cmd.format(f=filename))
        # Now find the applet entry point file and prepend the copy
        # operations (step 2 above), overwriting it in place.
        dxapp_json = json.load(open(os.path.join(app_dir, 'dxapp.json')))
        if dxapp_json['runSpec']['interpreter'] != 'bash':
            raise Exception('Sorry, I only know how to patch bash apps for remote testing')
        entry_point_filename = os.path.join(app_dir, dxapp_json['runSpec']['file'])
        entry_point_data = ''.join(preamble) + open(entry_point_filename).read()
        with open(os.path.join(updated_app_dir, dxapp_json['runSpec']['file']), 'w') as fh:
            fh.write(entry_point_data)

        build_output = run(['dx', 'build', '--json', '--destination', project_id + ':', updated_app_dir])
        return json.loads(build_output)['id']
    finally:
        shutil.rmtree(tempdir)

def update_environ(**kwargs):
    """
    Returns a copy of os.environ with the specified updates (VAR=value for each kwarg)
    """
    output = os.environ.copy()
    for k, v in kwargs.iteritems():
        if v is None:
            del output[k]
        else:
            output[k] = v
    return output


@unittest.skipUnless(testutil.TEST_RUN_JOBS, 'skipping tests that would run jobs')
class TestDXBashHelpers(DXTestCase):
    def test_vars(self):
        '''  Quick test for the bash variables '''
        with temporary_project('TestDXBashHelpers.test_app1 temporary project') as p:
            env = update_environ(DX_PROJECT_CONTEXT_ID=p.get_id())

            # Upload some files for use by the applet
            dxpy.upload_string("1234\n", project=p.get_id(), name="A.txt")

            # Build the applet, patching in the bash helpers from the
            # local checkout
            applet_id = build_app_with_bash_helpers(os.path.join(TEST_APPS, 'vars'), p.get_id())

            # Run the applet
            applet_args = ['-iseq1=A.txt', '-iseq2=A.txt', '-igenes=A.txt', '-igenes=A.txt',
                           '-ii=5', '-ix=4.2', '-ib=true', '-is=hello',
                           '-iil=6', '-iil=7', '-iil=8',
                           '-ixl=3.3', '-ixl=4.4', '-ixl=5.0',
                           '-ibl=true', '-ibl=false', '-ibl=true',
                           '-isl=hello', '-isl=world', '-isl=next',
                           '-imisc={"hello": "world", "foo": true}']
            cmd_args = ['dx', 'run', '--yes', '--watch', applet_id]
            cmd_args.extend(applet_args)
            run(cmd_args, env=env)

    def test_basic(self):
        with temporary_project('TestDXBashHelpers.test_app1 temporary project') as dxproj:
            env = update_environ(DX_PROJECT_CONTEXT_ID=dxproj.get_id())

            # Upload some files for use by the applet
            dxpy.upload_string("1234\n", project=dxproj.get_id(), name="A.txt")
            dxpy.upload_string("ABCD\n", project=dxproj.get_id(), name="B.txt")

            # Build the applet, patching in the bash helpers from the
            # local checkout
            applet_id = build_app_with_bash_helpers(os.path.join(TEST_APPS, 'basic'), dxproj.get_id())

            # Run the applet
            applet_args = ['-iseq1=A.txt', '-iseq2=B.txt', '-iref=A.txt', '-iref=B.txt', "-ivalue=5", "-iages=4"]
            cmd_args = ['dx', 'run', '--yes', '--watch', applet_id]
            cmd_args.extend(applet_args)
            run(cmd_args, env=env)

    def test_sub_jobs(self):
        '''  Tests a bash script that generates sub-jobs '''
        with temporary_project('TestDXBashHelpers.test_app1 temporary project') as dxproj:
            env = update_environ(DX_PROJECT_CONTEXT_ID=dxproj.get_id())

             # Upload some files for use by the applet
            dxpy.upload_string("1234\n", project=dxproj.get_id(), name="A.txt")
            dxpy.upload_string("ABCD\n", project=dxproj.get_id(), name="B.txt")

            # Build the applet, patching in the bash helpers from the
            # local checkout
            applet_id = build_app_with_bash_helpers(os.path.join(TEST_APPS, 'with-subjobs'), dxproj.get_id())
             # Run the applet.
            # Since the job creates two sub-jobs, we need to be a bit more sophisticated
            # in order to wait for completion.
            applet_args = ["-ifiles=A.txt", "-ifiles=B.txt"]
            cmd_args = ['dx', 'run', '--yes', '--brief', applet_id]
            cmd_args.extend(applet_args)
            job_id = run(cmd_args, env=env).strip()

            dxpy.DXJob(job_id).wait_on_done()

            # Assertions -- making sure the script worked
            # Assertions to make about the job's output after it is done running:
            # - *first_file* is a file named first_file.txt containing the string:
            #     "contents of first_file"
            # - *final_file* is a file named final_file.txt containing the
            #   *concatenation of the two input files in *files*
            print("Test completed successfully, checking file content\n")

            job_handler = dxpy.get_handler(job_id)
            job_output = job_handler.output

            def strip_white_space(_str):
                return ''.join(_str.split())

            def silent_file_remove(filename):
                try:
                    os.remove(filename)
                except OSError:
                    pass

            # The output should include two files, this section verifies that they have
            # the correct data.
            def check_file_content(out_param_name, out_filename, tmp_fname, str_content):
                """
                Download a file, read it from local disk, and verify that it has the correct contents
                """
                if not out_param_name in job_output:
                    raise "Error: key {} does not appear in the job output".format(out_param_name)
                dxlink = job_output[out_param_name]

                # check that the filename gets preserved
                trg_fname = dxpy.get_handler(dxlink).name
                self.assertEqual(trg_fname, out_filename)

                # download the file and check the contents
                silent_file_remove(tmp_fname)
                dxpy.download_dxfile(dxlink, tmp_fname)
                with open(tmp_fname, "r") as fh:
                    data = fh.read()
                    print(data)
                    if not (strip_white_space(data) == strip_white_space(str_content)):
                        raise Exception("contents of file {} do not match".format(out_param_name))
                silent_file_remove(tmp_fname)

            check_file_content('first_file', 'first_file.txt', "f1.txt", "contents of first_file")
            check_file_content('final_file', 'final_file.txt', "f2.txt", "1234ABCD")

    def test_parseq(self):
        ''' Tests the parallel/sequential variations '''
        with temporary_project('TestDXBashHelpers.test_app1 temporary project') as dxproj:
            env = update_environ(DX_PROJECT_CONTEXT_ID=dxproj.get_id())

            # Upload some files for use by the applet
            dxpy.upload_string("1234\n", project=dxproj.get_id(), name="A.txt")
            dxpy.upload_string("ABCD\n", project=dxproj.get_id(), name="B.txt")

            # Build the applet, patching in the bash helpers from the
            # local checkout
            applet_id = build_app_with_bash_helpers(os.path.join(TEST_APPS, 'parseq'), dxproj.get_id())

            # Run the applet
            applet_args = ["-iseq1=A.txt", "-iseq2=B.txt", "-iref=A.txt", "-iref=B.txt"]
            cmd_args = ['dx', 'run', '--yes', '--watch', applet_id]
            cmd_args.extend(applet_args)
            run(cmd_args, env=env)

    def test_prefix_patterns(self):
        """ Tests that the bash prefix variable works correctly, and
        respects patterns.
        """
        with temporary_project('TestDXBashHelpers.test_app1 temporary project') as dxproj:
            env = update_environ(DX_PROJECT_CONTEXT_ID=dxproj.get_id())
            filenames = ["A.bar", "A.json.dot.bar", "A.vcf.pam", "A.foo.bar",
                         "fooxxx.bam", "A.bar.gz", "x13year23.sam"]
            for fname in filenames:
                dxpy.upload_string("1234", project=dxproj.get_id(), name=fname)

            # Build the applet, patching in the bash helpers from the
            # local checkout
            applet_id = build_app_with_bash_helpers(os.path.join(TEST_APPS, 'prefix_patterns'), dxproj.get_id())

            # Run the applet
            applet_args = ['-iseq1=A.bar',
                           '-iseq2=A.json.dot.bar',
                           '-igene=A.vcf.pam',
                           '-imap=A.foo.bar',
                           '-imap2=fooxxx.bam',
                           '-imap3=A.bar',
                           '-imap4=A.bar.gz',
                           '-imulti=x13year23.sam']
            cmd_args = ['dx', 'run', '--yes', '--watch', applet_id]
            cmd_args.extend(applet_args)
            run(cmd_args, env=env)

    def test_deepdirs(self):
        ''' Tests the use of subdirectories in the output directory '''
        def check_output_key(job_output, out_param_name, num_files, dxproj):
            ''' check that an output key appears, and has the correct number of files '''
            print('checking output for param={}'.format(out_param_name))
            if out_param_name not in job_output:
                raise "Error: key {} does not appear in the job output".format(out_param_name)
            dxlink_id_list = job_output[out_param_name]
            if not len(dxlink_id_list) == num_files:
                raise Exception("Error: key {} should have {} files, but has {}".
                                format(out_param_name, num_files, len(dxlink_id_list)))

        def verify_files_in_dir(path, expected_filenames, dxproj):
            ''' verify that a particular set of files resides in a directory '''
            dir_listing = dxproj.list_folder(folder=path, only="objects")
            for elem in dir_listing["objects"]:
                handler = dxpy.get_handler(elem["id"])
                if not isinstance(handler, dxpy.DXFile):
                    continue
                if handler.name not in expected_filenames:
                    raise Exception("Error: file {} should reside in directory {}".
                                    format(handler.name, path))

        with temporary_project('TestDXBashHelpers.test_app1 temporary project') as dxproj:
            env = update_environ(DX_PROJECT_CONTEXT_ID=dxproj.get_id())

            # Build the applet, patching in the bash helpers from the
            # local checkout
            applet_id = build_app_with_bash_helpers(os.path.join(TEST_APPS, 'deepdirs'), dxproj.get_id())

            # Run the applet
            cmd_args = ['dx', 'run', '--yes', '--brief', applet_id]
            job_id = run(cmd_args, env=env).strip()

            dxpy.DXJob(job_id).wait_on_done()

            print("Test completed successfully, checking outputs\n")

            # Assertions about the output. There should be three result keys
            job_handler = dxpy.get_handler(job_id)
            job_output = job_handler.output

            check_output_key(job_output, "genes", 8, dxproj)
            check_output_key(job_output, "phenotypes", 7, dxproj)
            check_output_key(job_output, "report", 1, dxproj)
            check_output_key(job_output, "helix", 1, dxproj)

            verify_files_in_dir("/clue", ["X_1.txt", "X_2.txt", "X_3.txt"], dxproj)
            verify_files_in_dir("/hint", ["V_1.txt", "V_2.txt", "V_3.txt"], dxproj)
            verify_files_in_dir("/clue2", ["Y_1.txt", "Y_2.txt", "Y_3.txt"], dxproj)
            verify_files_in_dir("/hint2", ["Z_1.txt", "Z_2.txt", "Z_3.txt"], dxproj)
            verify_files_in_dir("/foo/bar", ["luke.txt"], dxproj)
            verify_files_in_dir("/", ["A.txt", "B.txt", "C.txt", "num_chrom.txt"], dxproj)


@unittest.skipUnless(testutil.TEST_RUN_JOBS and testutil.TEST_BENCHMARKS,
                     'skipping tests that would run jobs, or, run benchmarks')
class TestDXBashHelpersBenchmark(DXTestCase):

    def create_file_of_size(self, fname, size_bytes):
        assert(size_bytes > 1);
        try:
            os.remove(fname)
        except:
            pass
        with open(fname, "wb") as out:
            out.seek(size_bytes - 1)
            out.write('\0')

    def run_applet_with_flags(self, flag_list, num_files, file_size_bytes):
        with temporary_project('TestDXBashHelpers.test_app1 temporary project') as dxproj:
            env = update_environ(DX_PROJECT_CONTEXT_ID=dxproj.get_id())

            # Upload file
            self.create_file_of_size("A.txt", file_size_bytes);
            remote_file = dxpy.upload_local_file(filename="A.txt", project=dxproj.get_id(), folder='/')

            # Build the applet, patching in the bash helpers from the
            # local checkout
            applet_id = build_app_with_bash_helpers(os.path.join(TEST_APPS, 'benchmark'), dxproj.get_id())

            # Add several files to the output
            applet_args = []
            applet_args.extend(['-iref=A.txt'] * num_files)
            cmd_args = ['dx', 'run', '--yes', '--watch', '--instance-type=mem1_ssd1_x2', applet_id]
            cmd_args.extend(applet_args)
            cmd_args.extend(flag_list)
            run(cmd_args, env=env)

    def test_seq(self):
        self.run_applet_with_flags(["-iparallel=false"], 40, 1024 * 1024)

    def test_par(self):
        self.run_applet_with_flags(["-iparallel=true"], 40, 1024 * 1024)

    def test_seq_100m(self):
        self.run_applet_with_flags(["-iparallel=false"], 40, 100 * 1024 * 1024)

    def test_par_100m(self):
        self.run_applet_with_flags(["-iparallel=true"], 40, 100 * 1024 * 1024)

    def test_par_1g(self):
        self.run_applet_with_flags(["-iparallel=true"], 10, 1024 * 1024 * 1024)


if __name__ == '__main__':
    unittest.main()
