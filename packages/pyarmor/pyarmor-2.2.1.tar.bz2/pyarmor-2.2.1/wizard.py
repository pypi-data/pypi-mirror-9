#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
#############################################################
#                                                           #
#      Copyright @ 2013 - 2014 Dashingsoft corp.            #
#      All rights reserved.                                 #
#                                                           #
#      Pyarmor                                              #
#                                                           #
#      Version: 2.2.1 -                                     #
#                                                           #
#############################################################
#
#
#  @File: wizard.py
#
#  @Author: Jondy Zhao(jondy.zhao@gmail.com)
#
#  @Create Date: 2014/12/06
#
#  @Description:
#
#   GUI wizard of pyarmor.
#

import fnmatch
import getopt
import gettext
import glob
import logging
import json
import multiprocessing
import os
import platform
import shutil
import sys
import tempfile
import threading
import time
try:
    if sys.version_info[0] == 2:
        Tkinter = __import__('Tkinter')
        from tkFileDialog import asksaveasfilename, \
            askopenfilename, askdirectory, askopenfilenames
        from tkMessageBox import askyesno, showinfo
    else:
        Tkinter = __import__('tkinter')
        from tkinter.filedialog import asksaveasfilename, \
            askopenfilename, askdirectory, askopenfilenames
        from tkinter.messagebox import askyesno, showinfo
    Frame = Tkinter.Frame
except ImportError:
    raise RuntimeError('there is no tkinter installed')

# ----------------------------------------------------------
#
# Section: messages
#
# ----------------------------------------------------------
__intro_msg__ = '''Run/import encrypted python scripts

Is it cool to run/import encrypted python scripts, a python package
"Pyarmor" makes it possible. Pyarmor is designed for developers who
do not want distribute literal python scripts to their customers.

Here are the main differences of using pyarmor to run/import
encrypted python scripts:

  * transform python script to encrypted one with extension ".pyx"
  * add a few of auxiliary files

It means Pyarmor almost doesn't change anything, you can run/import
encrypted pythons scripts just as they're not encrypted. So you can
run/import encrypted python scripts in any environment which python
can run. For example, in a web framework, or as cgi scripts.

Besides, Pyarmor could distribute encrypted python scripts to target
machine as one of the following ways:
  * Run/import encrypted scripts in any target machine, or
  * only in a special machine (bind to hard disk serial number), or
  * expried on some day in any machine or a special machine

Pyarmor is command line tool, the main script is "pyarmor.py", you can
run it by python2.6 later. The basic scenario of using pyarmor looks
like this:

Step 1: Make project capsule for new project
Step 2: Encrypt python scripts with project capsule
Step 3: Generate "license.lic" for encrypted scripts

Finally copy all the required files to target machine.

This wizard will show you how to use Pyarmor to distribute encrypted
python scripts in a GUI mode. Click Next to enter a command page. In each
page, when you change any option, the meaning of each option will be print
in a text box.

At last page, Click Run to execute all the commands.

There is Save Command button in last page. Clicking Save Command will save
all the commands in shell script file.

There is Save Option button in last page. Clicking Save Option will save all
the command options to a json file, then you can load these options later.

For example,

    $ python wizard.py foo.json

The following examples include most of featuers of Pyarmor. Clicking Load
after an example will load the corresponding command options of this
example, then click Next. This wizard will show you how to use each
command for this example.

'''
__example_list__ = \
    ('Example1',
     '''This example shows how to run encrypted script "beer.py".
     '''), \
    ('Example2',
     '''This example shows how to import function from encrypted script "wiki.py".
    '''), \
    ('Example3',
     '''This example shows how to run encrypted "beer.py" only on specify machine.
    '''), \
    ('Example4',
     '''This example shows how to run encrypted "beer.py" in a valid period.
    '''), \
    ('Example5',
     '''This example shows how to run encrypted "beer.py" on specify machine and in a valid period.
    '''), \
    ('Example6',
     '''This example shows how to use option '--with-extension' to cross publish.
    '''), \
    # ('Example9',
    #  '''This example shows how to use option '--path' to specify source scripts to encrypted.
    # '''), \
    # ('Example10',
    #  '''This example shows how to list source scripts to encrypted in file.
    # '''), \

__finish_msg__ = '''Finally, copy license file to output path,
  $ cp %s %s
Then copy all the files in the target machine.

Run encrypted script:
  $ python -c "import pyimcore
import pytransform
pytransform.exec_file('main.pyx')"

Before import encrypted scripts, insert statement in your main script:
    import pyimcore
'''

# ----------------------------------------------------------
#
# Section: application options
#
# ----------------------------------------------------------

capsuleoptions = {
    # don't run capsule command, use exists capsule
    'runflag' : 1,
    # the filename of capsule
    'filename' : '',
    # path of output
    'output' : '',
    # custom des key
    'key' : '',
    # all the rest arguments
    'args' : '',
    }
encryptoptions = {
    # don't run encrypt command, just make license or capsule
    'runflag' : 1,
    # path of output
    'output' : '',
    # the capsule filename
    'with-capsule' : '',
    # the base path of source files
    'path' : '',
    # the filename of python extension "pytransform"
    'with-extension' : '',
    # all the rest arguments
    'args' : '',
}
licenseoptions = {
    # don't run license command, use exists license
    'runflag' : 1,
    # the license filename
    'filename' : '',
    # the capsule filename
    'with-capsule' : '',
    # path of output
    'output' : '',
    # bind serial number of harddisk or not
    'bind' : 0,
    # expired date of license: YYYY-MM-NN
    'expired-date' : '',
    # all the rest arguments
    'args' : '',
}
appoptions = {
    'capsule' : capsuleoptions,
    'encrypt' : encryptoptions,
    'license' : licenseoptions,
    }

def capsule_opt2arg(options):
    '''Transfrom option to argument list.'''
    valid = True
    comments = ['', 'Step 1: Create project capsule', '']
    arguments = []
    if options['runflag']:
        output = options['output'].strip()
        if output == '':
            output = os.getcwd()
            comments.append('option --output is empty, use current path: ')
            comments.append('   %s' % output)
        else:
            arguments.append('--output')
            arguments.append(output)
        comments.append('')
        name = options['args']
        if name == '':
            name = 'project'
            comments.append(
                'no arguments, use default capsule name: %s' % name
                )
        else:
            arguments.append(name)
        comments.append('')
        comments.append('This command will generate project capsule: ')
        filename = os.path.join(os.path.abspath(output), '%s.zip' % name)
        comments.append('   %s' % filename)
    else:
        filename = options['filename'].strip()
        comments.append('Nothing to do, use existing capsule:')
        if filename == '':
            comments.append('Error: filename could not be empty')
            valid = False
        elif os.path.exists(filename):
            comments.append('   %s' % options['filename'])
        else:
            comments.append('Error: no found %s' % options['filename'])
            valid = False
    return valid, '\n# '.join(comments), arguments

def encrypt_opt2arg(options):
    valid = True
    comments = ['', 'Step 2: Encrypt scripts', '']
    arguments = []
    if options['runflag']:
        arguments.append('--with-capsule')
        arguments.append(options['with-capsule'])
        output = options['output'].strip()
        if output == '':
            output = os.getcwd()
            comments.append('option --output is empty, use current path: ')
            comments.append('   %s' % output)
        else:
            arguments.append('--output')
            arguments.append(output)
        ext = options['with-extension']
        if ext == '':
            comments.append('option --with-extension is empty, not cross publish')
        else:
            arguments.append('--with-extension')
            arguments.append(ext)
        path = options['path']
        if path == '':
            path = os.getcwd()
            comments.append('option --path is empty, use default path:')
            comments.append('   %s' % path)
        else:
            arguments.append('--path')
            arguments.append(path)
        comments.append('All the source scripts not absolute path '\
                        'will base with --path')

        comments.append('')
        filenames = options['args'].strip()
        if filenames == '':
            valid = False
            comments.append('Error: no any script specified')
        else:
            arguments.append(filenames)
        comments.append('')
        if valid:
            comments.append('This command will encrypt all the list '\
                            'scripts to output path with extension ".pyd"')
    else:
        comments.append('# DO NOT encrypt any script')
    return valid, '\n# '.join(comments), arguments

def license_opt2arg(options):
    '''Transfrom option to argument list.'''
    valid = True
    comments = ['', 'Step 3: Create project license file', '']
    arguments = []
    if options['runflag']:
        arguments.append('--with-capsule')
        arguments.append(options['with-capsule'])
        output = options['output'].strip()
        if output == '':
            output = os.getcwd()
            comments.append('option --output is empty, use current path: ')
            comments.append('   %s' % output)
        else:
            arguments.append('--output')
            arguments.append(output)
        expired = options['expired-date'].strip()
        if expired == '':
            comments.append('option --expired-date is empty, project ' \
                            'license file never be expired')
        else:
            try:
                time.strptime(expired, '%Y-%m-%d')
                comments.append('project license will expired at certern ' \
                                'date, after that, the encrypted script ' \
                                'could not be run/imported')
                arguments.append('--expired-date')
                arguments.append(expired)
            except ValueError:
                valid = False
                comments.append('option --expired-date is invalid, not YYYY-MM-NN')
        comments.append('')
        code = options['args']
        if options['bind']:
            comments.append('option --bind is set, project license file is bind ' \
                            'to serial number of hard disk: ')
            if code == '':
                valid = False
                comments.append('Error: serial number could not be empty')
            else:
                comments.append('   %s' % code)
                arguments.append(code)
        else:
            if code == '':
                code = 'PROJECT-CODE'
                comments.append('use default license code: %s' % code)
            else:
                comments.append('use license code: %s' % code)
                arguments.append(code)
        comments.append('')
        comments.append('This command will generate project license file: ')
        filename = os.path.join(os.path.abspath(output), 'license.lic')
        comments.append('   %s' % filename)
    else:
        comments.append('# Nothing to do, use existing project license: ')
        filename = options['filename'].strip()
        if filename == '':
            comments.append('# Error: filename could not be empty')
        elif os.path.exists(filename):
            comments.append('#   %s' % options['filename'])
        else:
            comments.append('# Warning: no found %s ' % options['filename'])
    return valid, '\n# '.join(comments), arguments

def make_description(options):
    msg = ['Now click Run to execute all commands', '']
    if options['encrypt']['runflag']:
        msg.append(__finish_msg__)
    return '\n'.join(msg)

def get_capsule_filename(output, name):
    return os.path.join(
        os.path.abspath(output),
        'project.zip' if name == '' else '%s.zip' % name,
        ).replace('\\', '/')

# ----------------------------------------------------------
#
# Section: wizard pages
#
# ----------------------------------------------------------

class WizardPage(Frame):

    def __init__(self, master):
        Frame.__init__(self, master)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.wizard = self.nametowidget(master.winfo_parent())

class WizardPage1(WizardPage):

    def __init__(self, master):
        WizardPage.__init__(self, master)

        frame = Tkinter.LabelFrame(self)
        frame.configure(text='Intro', labelanchor='n')
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.grid(sticky='nesw')

        w = Tkinter.Text(frame)
        w.grid(row=0, column=0, sticky='nesw')

        sy = Tkinter.Scrollbar(frame, orient='vertical', command=w.yview)
        sy.grid(row=0, column=1, sticky='ens')
        w.configure(yscrollcommand=sy.set)

        w.insert('end', __intro_msg__)
        w.insert('end', '\n\n')

        for title, msg in __example_list__:
            filename = os.path.join('examples', title.lower() + '.json')
            b = Tkinter.Button(w, text='load')
            b.configure(
                command=lambda s=filename:self.loadOptions(s),
                cursor='arrow',
                )
            w.insert('end', title)
            w.window_create(index='end', window=b, padx=50)
            w.insert('end', '\n%s\n' % ('-' * 60))
            w.insert('end', msg + '\n\n')
        w.configure(state='disable')

    def loadOptions(self, filename):
        try:
            self.wizard.loadOptions(filename)
        except Exception as e:
            showinfo('Pyarmor Wizard', str(e))
        else:
            showinfo('Pyarmor Wizard', 'load options from %s' % filename)

class WizardPage2(WizardPage):

    def __init__(self, master):
        WizardPage.__init__(self, master)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        frame = Tkinter.LabelFrame(self)
        frame.configure(text='Command: capsule', labelanchor='n')
        frame.rowconfigure(3, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.grid(sticky='nesw')
        self.frame = frame

        b = Tkinter.Checkbutton(frame)
        v = self.wizard.varoptions['capsule']['runflag']
        b.configure(
            text=_('Use existing capsule'),
            variable=v,
            onvalue=0,
            offvalue=1,
            )
        b.bind(
            '<ButtonRelease-1>',
            lambda e, v=v:self.on_change_runflag(not v.get())
            )
        b.grid(row=0, column=0, sticky='w')

        frame1 = Tkinter.Frame(frame,
            name='frame1',
            borderwidth=2,
            relief='groove',
            )
        frame1.grid(row=1, column=0, sticky='nesw')
        frame1.columnconfigure(1, weight=1)

        label = Tkinter.Label(frame1, text=_('Filename:'))
        label.grid(row=0, column=0, sticky='w')

        v = self.wizard.varoptions['capsule']['filename']
        entry = Tkinter.Entry(frame1)
        entry.configure(
            width=80,
            textvariable=v,
            )
        entry.grid(row=0, column=1, sticky='we')

        button = Tkinter.Button(frame1, text='...')
        button.configure(command=self.on_select_capsule)
        button.grid(row=0, column=2, padx=5, sticky='e')

        frame2 = Tkinter.Frame(frame,
            name='frame2',
            borderwidth=2,
            relief='groove',
            )
        frame2.grid(row=2, column=0, sticky='nesw')
        frame2.columnconfigure(1, weight=1)

        label = Tkinter.Label(frame2, text=_('Output Path:'))
        label.grid(row=0, column=0, sticky='w')

        v = self.wizard.varoptions['capsule']['output']
        entry = Tkinter.Entry(frame2)
        entry.configure(
            width=80,
            textvariable=v,
            )
        entry.grid(row=0, column=1, sticky='we')

        button = Tkinter.Button(frame2, text='...')
        button.configure(command=self.on_select_output)
        button.grid(row=0, column=2, padx=5, sticky='e')

        label = Tkinter.Label(frame2, text=_('Name:'))
        label.grid(row=1, column=0, sticky='w')

        v = self.wizard.varoptions['capsule']['args']
        entry = Tkinter.Entry(frame2)
        entry.configure(
            width=80,
            textvariable=v,
            )
        entry.grid(row=1, column=1, sticky='we')

        w = Tkinter.Text(frame, name='command', state='disable')
        w.grid(row=3, column=0, sticky='nesw')

    def on_select_capsule(self):
        filename = askopenfilename(
            parent=self,
            filetypes=[('Project Capsule', '*.zip')],
            defaultextension='.zip',
            )
        if not filename == '':
            self.wizard.varoptions['capsule']['filename'].set(filename)

    def on_select_output(self):
        path = askdirectory(parent=self)
        if not path == '':
            self.wizard.varoptions['capsule']['output'].set(path)

    def on_change_runflag(self, flag):
        for w in self.frame.nametowidget('frame1').winfo_children():
            w.configure(state='disabled' if flag else 'normal')
        for w in self.frame.nametowidget('frame2').winfo_children():
            w.configure(state='normal' if flag else 'disabled')

class WizardPage3(WizardPage):

    def __init__(self, master=None):
        WizardPage.__init__(self, master)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        frame = Tkinter.LabelFrame(self)
        frame.configure(text='Command: encrypt', labelanchor='n')
        frame.rowconfigure(2, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.grid(sticky='nesw')
        self.frame = frame

        b = Tkinter.Checkbutton(frame)
        v = self.wizard.varoptions['encrypt']['runflag']
        b.configure(
            text=_('DO NOT encrypt any script'),
            variable=v,
            onvalue=0,
            offvalue=1,
            )
        b.grid(row=0, column=0, sticky='w')

        frame1 = Tkinter.Frame(frame,
            name='frame1',
            borderwidth=2,
            relief='groove',
            )
        frame1.grid(row=1, column=0, sticky='nesw')
        frame1.columnconfigure(1, weight=1)

        label = Tkinter.Label(frame1, text=_('Capsule:'))
        label.grid(row=0, column=0, sticky='w')

        v = self.wizard.varoptions['encrypt']['with-capsule']
        entry = Tkinter.Entry(frame1)
        entry.configure(
            width=80,
            textvariable=v,
            state='disabled',
            )
        entry.grid(row=0, column=1, sticky='we')

        label = Tkinter.Label(frame1, text=_('Output Path:'))
        label.grid(row=1, column=0, sticky='w')

        v = self.wizard.varoptions['encrypt']['output']
        entry = Tkinter.Entry(frame1)
        entry.configure(
            width=80,
            textvariable=v,
            )
        entry.grid(row=1, column=1, sticky='we')

        button = Tkinter.Button(frame1, text='...')
        button.configure(command=self.on_select_output)
        button.grid(row=1, column=2, padx=5, sticky='e')

        label = Tkinter.Label(frame1, text=_('Cross Publish:'))
        label.grid(row=2, column=0, sticky='w')

        v = self.wizard.varoptions['encrypt']['with-extension']
        entry = Tkinter.Entry(frame1)
        entry.configure(
            width=80,
            textvariable=v,
            )
        entry.grid(row=2, column=1, sticky='we')

        button = Tkinter.Button(frame1, text='...')
        button.configure(command=self.on_select_extension)
        button.grid(row=2, column=2, padx=5, sticky='e')

        label = Tkinter.Label(frame1, text=_('Base Path:'))
        label.grid(row=3, column=0, sticky='w')

        v = self.wizard.varoptions['encrypt']['path']
        entry = Tkinter.Entry(frame1)
        entry.configure(
            width=80,
            textvariable=v,
            )
        entry.grid(row=3, column=1, sticky='we')

        button = Tkinter.Button(frame1, text='...')
        button.configure(command=self.on_select_path)
        button.grid(row=3, column=2, padx=5, sticky='e')

        label = Tkinter.Label(frame1, text=_('Scripts:'))
        label.grid(row=9, column=0, sticky='w')

        v = self.wizard.varoptions['encrypt']['args']
        entry = Tkinter.Entry(frame1)
        entry.configure(
            width=80,
            textvariable=v,
            )
        entry.grid(row=9, column=1, sticky='we')

        button = Tkinter.Button(frame1, text='...')
        button.configure(command=self.on_select_scripts)
        button.grid(row=9, column=2, padx=5, sticky='e')

        w = Tkinter.Text(frame, name='command', state='disable')
        w.grid(row=2, column=0, sticky='nesw')

    def on_select_output(self):
        path = askdirectory(parent=self)
        if not path == '':
            self.wizard.varoptions['encrypt']['output'].set(path)

    def on_select_path(self):
        path = askdirectory(parent=self)
        if not path == '':
            self.wizard.varoptions['encrypt']['path'].set(path)

    def on_select_extension(self):
        ext = '.so' if sys.platform.startswith('linux') else '.pyd'
        filename = askopenfilename(
            parent=self,
            filetypes=[('Python Extension', 'pytransform-*' + ext)],
            )
        if not filename == '':
            self.wizard.varoptions['encrypt']['with-extension'].set(filename)

    def on_select_scripts(self):
        filename = askopenfilename(
            parent=self,
            filetypes=[('Python Script', '*.py'),
                       ('Python Extensions', '*.pyd'),
                       ('Python Extensions', '*.so'),
                       ('Python Extensions', '*.dll'),
                       ],
            )
        if not filename == '':
            values = self.wizard.varoptions['encrypt']['args'].get()
            if filename not in values:
                self.wizard.varoptions['encrypt']['args'].set(
                    values + ' ' + filename
                    )

class WizardPage4(WizardPage):

    def __init__(self, master=None):
        WizardPage.__init__(self, master)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        frame = Tkinter.LabelFrame(self)
        frame.configure(text='Command: license', labelanchor='n')
        frame.rowconfigure(3, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.grid(sticky='nesw')
        self.frame = frame

        b = Tkinter.Checkbutton(frame)
        v = self.wizard.varoptions['license']['runflag']
        b.configure(
            text=_('Use existing license file'),
            variable=v,
            onvalue=0,
            offvalue=1,
            )
        b.bind(
            '<ButtonRelease-1>',
            lambda e, v=v:self.on_change_runflag(not v.get())
            )
        b.grid(row=0, column=0, sticky='w')

        frame1 = Tkinter.Frame(frame,
            name='frame1',
            borderwidth=2,
            relief='groove',
            )
        frame1.grid(row=1, column=0, sticky='nesw')
        frame1.columnconfigure(1, weight=1)

        label = Tkinter.Label(frame1, text=_('Filename:'))
        label.grid(row=0, column=0, sticky='w')

        v = self.wizard.varoptions['license']['filename']
        entry = Tkinter.Entry(frame1)
        entry.configure(
            width=80,
            textvariable=v,
            )
        entry.grid(row=0, column=1, sticky='we')

        button = Tkinter.Button(frame1, text='...')
        button.configure(command=self.on_select_license)
        button.grid(row=0, column=2, padx=5, sticky='e')

        frame2 = Tkinter.Frame(frame,
            name='frame2',
            borderwidth=2,
            relief='groove',
            )
        frame2.grid(row=2, column=0, sticky='nesw')
        frame2.columnconfigure(1, weight=1)

        label = Tkinter.Label(frame2, text=_('Capsule:'))
        label.grid(row=0, column=0, sticky='w')

        v = self.wizard.varoptions['license']['with-capsule']
        entry = Tkinter.Entry(frame2)
        entry.configure(
            width=80,
            textvariable=v,
            state='disabled',
            )
        entry.grid(row=0, column=1, sticky='we')

        label = Tkinter.Label(frame2, text=_('Output Path:'))
        label.grid(row=1, column=0, sticky='w')

        v = self.wizard.varoptions['license']['output']
        entry = Tkinter.Entry(frame2)
        entry.configure(
            width=80,
            textvariable=v,
            )
        entry.grid(row=1, column=1, sticky='we')

        button = Tkinter.Button(frame2, text='...')
        button.configure(command=self.on_select_output)
        button.grid(row=1, column=2, padx=5, sticky='e')

        label = Tkinter.Label(frame2, text=_('Expired Date:'))
        label.grid(row=2, column=0, sticky='w')

        v = self.wizard.varoptions['license']['expired-date']
        entry = Tkinter.Entry(frame2)
        entry.configure(
            width=80,
            textvariable=v,
            )
        entry.grid(row=2, column=1, sticky='we')

        b = Tkinter.Checkbutton(frame2)
        v = self.wizard.varoptions['license']['bind']
        b.configure(
            text=_('Bind license code to serial number of hard disk'),
            variable=v,
            )
        b.grid(row=3, column=0, columnspan=2, sticky='w')

        label = Tkinter.Label(frame2, text=_('License Code:'))
        label.grid(row=4, column=0, sticky='w')

        v = self.wizard.varoptions['license']['args']
        entry = Tkinter.Entry(frame2)
        entry.configure(
            width=80,
            textvariable=v,
            )
        entry.grid(row=4, column=1, sticky='we')

        w = Tkinter.Text(frame, name='command', state='disable')
        w.grid(row=3, column=0, sticky='nesw')

    def on_select_license(self):
        filename = askopenfilename(
            parent=self,
            filetypes=[('License File', '*.lic')],
            defaultextension='.lic',
            )
        if not filename == '':
            self.wizard.varoptions['license']['filename'].set(filename)

    def on_select_output(self):
        path = askdirectory(parent=self)
        if not path == '':
            self.wizard.varoptions['license']['output'].set(path)

    def on_change_runflag(self, flag):
        for w in self.frame.nametowidget('frame1').winfo_children():
            w.configure(state='disabled' if flag else 'normal')
        for w in self.frame.nametowidget('frame2').winfo_children():
            w.configure(state='normal' if flag else 'disabled')

class WizardPage5(WizardPage):

    def __init__(self, master=None):
        WizardPage.__init__(self, master)

        frame = Tkinter.LabelFrame(self)
        frame.configure(text='Finish', labelanchor='n')
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.grid(sticky='nesw')
        self.frame = frame

        w = Tkinter.Text(frame, name='command', state='disabled')
        w.grid(row=0, column=0, sticky='nesw')

        sy = Tkinter.Scrollbar(frame, orient='vertical', command=w.yview)
        sy.grid(row=0, column=1, sticky='ens')
        w.configure(yscrollcommand=sy.set)

        cmdframe = Tkinter.Frame(frame)
        cmdframe.grid(row=0, column=2, sticky='ns')
        btn = Tkinter.Button(cmdframe)
        btn.config(text='Save Option', width=14, command=self.wizard.saveOptions)
        btn.grid(padx=5, pady=10, sticky='s')

        btn = Tkinter.Button(cmdframe)
        btn.config(text='Save Command', width=14, command=self.wizard.saveCommands)
        # Not implemented
        btn.config(state='disabled')
        btn.grid(padx=5, pady=10, sticky='s')

        btn = Tkinter.Button(cmdframe)
        btn.config(text='Run', width=14, command=self.wizard.startBuild)
        btn.grid(padx=5, pady=10, sticky='n')

# ----------------------------------------------------------
#
# Section: Running Dialog
#
# ----------------------------------------------------------

class RunDialog(Frame):

    def __init__(self, master):
        Frame.__init__(self, master)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self._process = None
        self._thread = None

        self._msg = Tkinter.Text(self, state='disable')
        self._msg.grid(row=0, column=0, sticky='nesw')

        frame = Tkinter.Frame(self)
        frame.grid(row=1, column=0)
        self._btn = Tkinter.Button(frame)
        self._btn.configure(text='Abort', command=self.doCloseOrAbort)
        self._btn.grid(padx=2, pady=2)

        self.setup()
        self.master.protocol(
                'WM_DELETE_WINDOW',
                self.doCloseOrAbort
                )

    def start(self, options):
        self._process = multiprocessing.Process(
            target=buildCapsule,
            args=(options,)
            )
        self._thread = threading.Thread(target=self.waitProcess)
        try:
            self._process.start()
            self._thread.start()
        except Exception as e:
            showinfo(
                'Pyarmor Wizard',
                'Failed to start building: %s' % str(e)
                )
            self.doCloseOrAbort()

    def setup(self):
        # install log handler to show output of runing scripts
        self.handler = logging.StreamHandler(self)
        self.handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        self.handler.setFormatter(formatter)
        logging.getLogger().addHandler(self.handler)

    def clean(self):
        logging.getLogger().removeHandler(self.handler)

    def write(self, text):
        self._msg.insert('end', text)

    def flush(self):
        pass

    def waitProcess(self):
        if self._process.is_alive():
            self._process.join()
        self._btn.configure(text='Close')

    def doCloseOrAbort(self):
        if self._process.is_alive():
            self._process.terminate()
        self.clean()
        if self._thread.is_alive():
            self._thread.join(0.1)
        if self._thread.is_alive():
            logging.warning('thread is waiting for building process to exit')
        self.master.destroy()

# ----------------------------------------------------------
#
# Section: main
#
# ----------------------------------------------------------
class Wizard(Frame):

    cmdbuttons = 'Prev', 'Next', 'Close'
    pagecount = 5

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master.protocol(
                'WM_DELETE_WINDOW',
                self.wm_delete_window
                )

        master.rowconfigure(0, weight=1)
        master.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.grid(sticky='nesw')

        self.varoptions = appoptions.copy()
        for c in self.varoptions:
            self.varoptions[c] = {}
            options = appoptions[c]
            for k in options:
                if isinstance(options[k], int):
                    var = Tkinter.IntVar(self)
                else:
                    var = Tkinter.StringVar(self)
                self.varoptions[c][k] = var

        self.pages = []
        self.pageindex = -1
        self.__createWidgets()
        self.setPageIndex(0)

        self.setOptionVariables(appoptions)
        self.on_change_capsule()
        self.setTextCommands(appoptions)

    def __createWidgets(self):
        _mainframe = Frame(self, width=800, height=480)
        _mainframe.rowconfigure(0, weight=1)
        _mainframe.columnconfigure(0, weight=1)
        _mainframe.grid_propagate(0)
        _mainframe.grid(row=0, column=0, sticky='nesw')

        for i in range(Wizard.pagecount):
            w = eval('WizardPage%s(_mainframe)' % (i+1))
            self.pages.append(w)

        _cmdframe = Frame(self)
        _cmdframe.grid(row=1, column=0, sticky='e')
        i = 0
        for title in Wizard.cmdbuttons:
            w = Tkinter.Button(_cmdframe, text=title, width=8)
            w.configure(command=lambda s=title:self.doCommand(s.lower()))
            w.grid(row=0, column=i, padx=15, pady=5, sticky='e')
            i += 1

    def doCommand(self, name):
        if name == 'prev':
            if self.pageindex > 0:
                self.setPageIndex(self.pageindex - 1)
        elif name == 'next':
            if self.pageindex < Wizard.pagecount - 1:
                self.setPageIndex(self.pageindex + 1)
        elif name == 'close':
            self.quit()

    def setPageIndex(self, index):
        self.pages[self.pageindex].grid_forget()
        self.pages[index].grid(row=0, column=0, sticky='nesw')
        self.pageindex = index

    def loadOptions(self, filename):
        f = open(filename, 'r')
        try:
            options = json.load(f)
        finally:
            f.close()
        self.setOptionVariables(options)
        self.setTextCommands(options)

    def setTextCommands(self, options):
        commands = 'capsule', 'encrypt', 'license'
        arguments = capsule_opt2arg(options['capsule']), \
                    encrypt_opt2arg(options['encrypt']), \
                    license_opt2arg(options['license'])
        cs = []
        for i in range(3):
            c = '\npython pyarmor.py %s %s' % (
                    commands[i],
                    ' '.join(arguments[i][-1])
                    ) if options[commands[i]]['runflag'] else ''
            cs.append('%s\n%s' % (arguments[i][1], c))
            w = self.pages[i+1].frame.nametowidget('command')
            w.config(state='normal')
            w.delete('1.0', 'end')
            w.insert('end', cs[i])
            w.config(state='disabled')
        cs.append('-' * 60)
        if not (arguments[0][0] and arguments[1][0] and arguments[2][0]):
            cs.append('''Error: Something is wrong with these commands! ''')
        else:
            cs.append(make_description(options))
        w = self.pages[-1].frame.nametowidget('command')
        w.config(state='normal')
        w.delete('1.0', 'end')
        w.insert('end', '\n\n'.join(cs))
        w.config(state='disabled')

    def setOptionVariables(self, options):
        for c in options:
            if not c in self.varoptions:
                raise RuntimeError('invalid key "%s" in option file', c)
            for k in options[c]:
                if not k in self.varoptions[c]:
                    raise RuntimeError('invalid key "%s.%s" in option file', (c, k))
                v = self.varoptions[c][k]
                for ts in v.trace_vinfo():
                    for cb in ts[1:]:
                        v.trace_vdelete(ts[0], cb)
                v.set(options[c][k])
                if k != 'with-capsule':
                    v.trace_variable(
                        'w',
                        lambda v,i,m:self.on_change_variable()
                        )

    def setOptionValues(self, varoptions):
        result = {}
        for c in varoptions:
            options = {}
            for k in varoptions[c]:
                options[k] = self.varoptions[c][k].get()
            result[c] = options
        return result

    def saveOptions(self, filename=None):
        if filename is None:
            filename = asksaveasfilename(
                parent=self,
                filetypes=[('*.json', '*.json')],
                defaultextension='.json',
                )
            if filename == '':
                return
        f = open(filename, 'w')
        json.dump(self.setOptionValues(self.varoptions), f, indent=2)
        f.close()

    def saveCommands(self, filename=None):
        if filename is None:
            ext = '.sh' if sys.platform.startswith('linux') else '.bat'
            filename = asksaveasfilename(
                parent=self,
                filetypes=[(_('Shell Script'), '*' + ext)],
                defaultextension=ext,
                )
            if filename == '':
                return
        f = open(filename, 'w')
        f.close()

    def startBuild(self):
        return showinfo('Pyarmor Wizard', 'Not Implemented')
        dlg = Tkinter.Toplevel(self)
        dlg.title('Running...')
        dlg.resizable(False, False)
        frame = RunDialog(dlg)
        frame.grid(sticky='nesw')

        dlg.transient()
        dlg.state("normal")
        dlg.wait_visibility()
        dlg.focus_set()
        dlg.grab_set()
        self.after_idle(frame.start, self.setOptionValues(self.varoptions))

    def wm_delete_window(self):
        self.master.destroy()

    def on_change_capsule(self):
        if self.varoptions['capsule']['runflag'].get():
            capsule = get_capsule_filename(
                self.varoptions['capsule']['output'].get().strip(),
                self.varoptions['capsule']['args'].get().strip(),
                )
        else:
            capsule = self.varoptions['capsule']['filename'].get()
        self.varoptions['encrypt']['with-capsule'].set(capsule)
        self.varoptions['license']['with-capsule'].set(capsule)

    def on_change_variable(self):
        self.on_change_capsule()
        options = self.setOptionValues(self.varoptions)
        self.setTextCommands(options)

def buildCapsule(options):
    pyarmor = __import__('pyarmor')
    try:
        pyarmor.pytransform = __import__('pytransform')
    except ImportError as e:
        logging.info(str(e))
        if str(e).startswith('Invalid license.'):
            logging.info(pyarmor.__dict__['__errormsg__'])
        return
    capsules = capsule_opt2arg(options['capsule'])
    encrypts = encrypt_opt2arg(options['encrypt'])
    licenses = license_opt2arg(options['license'])
    if not (capsules[0] and encrypts[0] and licenses[0]):
        logging.info(_('Invalid options'))
    else:
        if options['capsule']['runflag']:
            pyarmor.do_capsule(capsules[2])
        if options['encrypt']['runflag']:
            pyarmor.do_encrypt(encrypts[2])
        if options['license']['runflag']:
            pyarmor.do_license(licenses[2])

def main(filename=None):
    app = Wizard(Tkinter.Tk())
    app.master.title('Pyarmor Wizard')
    if filename is not None:
        app.loadOptions(filename)
    app.mainloop()

if __name__ == "__main__":
    sys.rootdir = os.path.dirname(os.path.abspath(sys.argv[0]))
    try:
        logging.basicConfig(
            level=logging.INFO,
            format='%(levelname)-8s %(message)s',
            )
    except TypeError:
        # Only for Python 2.3
        logging.basicConfig()

    opts, args = getopt.getopt(sys.argv[1:], 'hv', ['help', 'version',])
    for o, a in opts:
        if o in ('-h', '--help'):
            pass
        elif o in ('-v', '--version'):
            pass
    try:
        lang = gettext.translation('pyarmor')
    except IOError:
        lang = gettext.NullTranslations()
    lang.install()

    if Tkinter is None:
        logging.error('there is no tkinter installed')
    else:
        try:
            filename = args[0]
            if len(args[1:2]) == 1:
                logging.warning('two many arguments, ingore %s' % args[1:])
        except IndexError:
            filename = None
        main(filename=filename)
