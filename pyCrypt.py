#!/usr/bin/python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import threading # completion % not updating with master.after()
import os
import pickle as pk
import string
import cryptutils


acceptedChars = string.printable[:string.printable.index(' ')]

class CrypterGUI():
    def __init__(self, master):
        self.master = master
        self.currentPath = "" # user path entry
        self.completion = 0.0 # % completion of the encryption/decryption
        self.encryptionRunning = False
        self.cursor = 0
        self.EncKey = ""
        self.gui()
        threading.Thread(target=self.update_speed).start()

    def aaa(self, event=None):
        if event.char in acceptedChars and event.char != '':
            self.EncKey = self.EncKey[:self.cursor] + event.char +\
                          self.EncKey[self.cursor:]
            self.cursor += 1
        else:
            if event.keysym == "Right":
                self.cursor = min(self.cursor+1, len(self.EncKey))
            elif event.keysym == "Left":
                self.cursor = max(self.cursor-1, 0)
            elif event.keysym == "Home":
                self.cursor = 0
            elif event.keysym == "End":
                self.cursor = len(self.EncKey)
            elif event.keysym == "BackSpace":
                if self.cursor != 0:
                    self.EncKey = self.EncKey[:self.cursor-1] +\
                                  self.EncKey[self.cursor:]
                    self.cursor -= 1
            elif event.keysym == "Delete":
                self.EncKey = self.EncKey[:self.cursor] +\
                              self.EncKey[self.cursor+1:]
        if self.EncKey != '':
            toDisp = '*'*(self.cursor-1) + self.EncKey[self.cursor-1] +\
                     '*'*(len(self.EncKey)-self.cursor)
            self.hiddenKey.set(toDisp)
    
    def gui(self):
        self.mainFrame = tk.Frame(self.master)
        self.statusBar = tk.Frame(self.master)
        self.mainFrame.pack()
        self.statusBar.pack(fill='x', side='bottom')
        
        self.hiddenKey = tk.StringVar()
        self.keyEntry = tk.Entry(self.mainFrame,
                                 textvariable=self.hiddenKey)
        self.keyEntry.bind("<KeyRelease>", self.aaa)
        keyLab = tk.Label(self.mainFrame, text='Encryption key')
        keyLab.grid(row=0, column=0, pady=20)
        self.keyEntry.grid(row=0, column=1)
        
        self.pathType = tk.IntVar()
        self.rbFE = tk.Radiobutton(self.mainFrame, text="File encryption",
                       variable=self.pathType, value=0)
        self.rbFE.grid(row=1, column=0)
        self.rbDE = tk.Radiobutton(self.mainFrame, text="Directory encryption",
                       variable=self.pathType, value=1)
        self.rbDE.grid(row=1, column=1)
        self.rbFDD = tk.Radiobutton(self.mainFrame, text="File / Directory decryption",
                       variable=self.pathType, value=2)
        self.rbFDD.grid(row=2, columnspan=2)
            
        
        self.pathVar = tk.StringVar(value="Click here to choose a path")
        self.pathEnt = tk.Entry(self.mainFrame, textvariable=self.pathVar,
                                width=40)
        self.pathEnt.bind("<Button-1>", self.select_path)
        self.pathEnt.grid(row=3, column=0, columnspan=2, padx=20, pady=10)

        self.encryB = tk.Button(self.mainFrame, text="Encrypt/Decrypt",
                                command=self.encrypt_event)
        self.encryB.grid(row=5, column=0, columnspan=2, pady=25)

        self.speedVar = tk.StringVar()
        speedLab = tk.Label(self.statusBar, textvariable=self.speedVar,
                            relief="sunken")
        self.notification = tk.StringVar()
        self.notification.set("Time required : 0s")
        notifLab = tk.Label(self.statusBar, textvariable=self.notification,
                            relief="sunken")
        
        speedLab.pack(side='right', fill='x', expand=True)
        notifLab.pack(side='left', fill='x', expand=True)

    def widgets_lock(self, unlock=False):
        """When an encryption is running, lock the gui"""
        if unlock:
            self.pathEnt.bind("<Button-1>", self.select_path)
        else:
            self.pathEnt.unbind("<Button-1>")
        state = "normal" if unlock else "disabled"
        self.keyEntry["state"] = state
        self.pathEnt["state"] = state
        self.encryB["state"] = state
        self.rbFE["state"] = state
        self.rbDE["state"] = state
        self.rbFDD["state"] = state
        
    
    def update_speed(self):
        """Update the speed notification"""
        self.speedVar.set("Estimating speed...")
        self.master.update_idletasks()
        sz = 1e6 # 1 Mo
        self.avgTime = sum(cryptutils.test_encryption_speed(sz))/2
        self.speed = sz/self.avgTime # in octets per second
        self.speedVar.set("Speed : "+str(round(self.speed/sz, 1))+" (Mo/s)")

    def update_notification(self):
        """
        Update the completion % if an encryption is running
        otherwise update the time required to encrypt the path
        """
        if self.encryptionRunning:
            cmp = str(round(100 * self.completion, 2)).ljust(5, '0')
            self.notification.set("Completion : " + cmp + "%")
            self.master.after(50, self.update_notification)
        else:
            self.notification.set("Estimating time...")
            self.master.update_idletasks()
            self.currentPathSize = cryptutils.path_size(self.currentPath)
            duration = round(self.currentPathSize / self.speed)
            self.notification.set("Time required : " + str(duration) + "s")

    def select_path(self, event=None):
        """When the path entry is selected"""
        if os.path.isfile(self.currentPath):
            self.currentPath = os.path.dirname(self.currentPath)
        if self.pathType.get() in (0, 2): # for file encry OR file/folder decry
            path = filedialog.askopenfilename(initialdir=self.currentPath)
        elif self.pathType.get() == 1: # for folder decryption
            path = filedialog.askdirectory(initialdir=self.currentPath)
        # if user erased the entry manually or quit the filedialog
        if path == '' or isinstance(path, tuple): # for windows and unix
            return
        self.currentPath = os.path.abspath(path)
        self.pathVar.set(path)
        self.update_notification()

    def path_exists(self, path):
        """Return True if path exists and display error message if not"""
        if (self.pathType.get() in (0, 2) and not os.path.isfile(path)) or\
           (self.pathType.get() == 1 and not os.path.isdir(path)):
            msg = "The path :\n{0}\ndoesn't exists".format(self.currentPath)
            messagebox.showerror("Path not found", message=msg)
            return False
        return True

    def is_safe_key(self, key):
        """Return True if len(key)>3 and display error message if not"""
        if len(key) <= 3:
            msg = "The key must be >3 characters long"
            messagebox.showerror("Unsafe key", message=msg)
            return False
        return True

    def is_good_key(self, key, hashedKey):
        """Check if the key entered is good"""
        if cryptutils.hash_key(key) != hashedKey:
            messagebox.showerror("Key error", "You entered the wrong key")
            return False
        return True

    def encrypt_event(self):
        """When the 'Encrypt/Decrypt' button is pressed"""
        self.currentPath = os.path.abspath(self.pathEnt.get())
        key = self.EncKey
        if not self.path_exists(self.currentPath) or not self.is_safe_key(key):
            return
        self.encryptionRunning = True
        self.completion = 0.0
        if self.pathType.get() == 0:
            threading.Thread(target=self.file_encryption, args=(key,)).start()
        elif self.pathType.get() == 1:
            threading.Thread(target=self.fold_encryption, args=(key,)).start()
        elif self.pathType.get() == 2:
            threading.Thread(target=self.decryption, args=(key,)).start()
        self.widgets_lock()
        self.update_notification()

    def file_encryption(self, key):
        """Encrypts a file"""
        data = {"file":bytes(), "key":''}
        try:
            with open(self.currentPath, 'rb') as fileToEncrypt:
                data["file"] = cryptutils.encrypt_bytes(fileToEncrypt.read(), key)
        except:
            return self.write_err_log([self.currentPath])
        data["key"] = cryptutils.hash_key(key)
        with open(self.currentPath+'.crypted', 'wb') as cryptedFile:
            pk.dump(data, cryptedFile)
        self.encryptionRunning = False
        self.widgets_lock(unlock=True)

    def fold_encryption(self, key):
        """Encrypts an entire folder"""
        data = {"empty_dirs":[], "files":{}, "key":''}
        errors = []
        ignored = len(self.currentPath) + 1
        for root, folders, files in os.walk(self.currentPath):
            if not files and not folders: # empty dir
                encname = cryptutils.string_to_ints(root[ignored:])
                data["empty_dirs"].append(encname)
                continue
            for f in files:
                filePath = root + os.sep + f
                encname = cryptutils.string_to_ints(filePath[ignored:])
                try:
                    with open(filePath, 'rb') as fileToEncrypt:
                        crypted = cryptutils.encrypt_bytes(fileToEncrypt.read(), key)
                    data["files"][encname] = crypted
                    self.completion += os.path.getsize(filePath)/self.currentPathSize
                except:
                    errors.append(filePath)
                self.master.update_idletasks()
        data["key"] = cryptutils.hash_key(key)
        with open(self.currentPath + ".crypted", 'wb') as cryptedFolder:
            pk.dump(data, cryptedFolder)
        self.write_err_log(errors)
        self.encryptionRunning = False
        self.widgets_lock(unlock=True)

    def decryption(self, key):
        """Initialization of the decryption process"""
        try:
            with open(self.currentPath, 'rb') as cryptedFile:
                data = pk.load(cryptedFile)
            if set(data.keys()) not in (set(("file", "key")), set(("empty_dirs", "files", "key"))):
                raise Exception
        except:
            messagebox.showerror("File Corrupted",
                                 "Impossible to read the file")
            self.encryptionRunning = False
        if "empty_dirs" in data.keys(): # ie folder
            threading.Thread(target=self.fold_decryption, args=(key, data)).start()
        else: # ie file
            threading.Thread(target=self.file_decryption, args=(key, data)).start()
        self.widgets_lock()
        self.update_notification()

    def file_decryption(self, key, data):
        """Decrypt a file given in data"""
        if not self.is_good_key(key, data["key"]):
            return
        if not self.currentPath.endswith('.crypted'):
            name = self.currentPath
        else:
            name = self.currentPath[:-8]
        with open(name, 'wb') as decryFile:
            decryFile.write(cryptutils.decrypt_bytes(data["file"], key))
        self.encryptionRunning = False
        self.widgets_lock(unlock=True)

    def fold_decryption(self, key, data):
        """Decrypt a folder given in data"""
        if not self.is_good_key(key, data["key"]):
            return
        parent, base = os.path.split(self.currentPath)
         # eight last char are '.crypted'
        base = base[:-8] if base.endswith('.crypted') else base
        for encpath, crypted in data["files"].items():
            relPath = cryptutils.ints_to_string(encpath)
            newPath = os.path.join(parent, base, relPath)
            # make the parent directory of the file
            # if it already exists, no exception is raised
            os.makedirs(os.path.dirname(newPath), exist_ok=True)
            with open(newPath, 'wb') as decryptedFile:
                decryptedFile.write(cryptutils.decrypt_bytes(crypted, key))
            self.completion += os.path.getsize(newPath)/self.currentPathSize
        for encDirName in data["empty_dirs"]:
            empty_dir = cryptutils.ints_to_string(encDirName)
            os.makedirs(os.path.join(parent, base, empty_dir), exist_ok=True)
        self.encryptionRunning = False
        self.widgets_lock(unlock=True)

    def check_files(self, key):
        """Check the files created after encryption"""
        pass # todo

    def write_err_log(self, errors):
        # display them in a separate window ?
        if not errors:
            return
        if os.path.isfile(self.currentPath):
            path = os.path.dirname(self.currentPath)
        else:
            path = self.currentPath
        with open(os.path.join(path, "PyCrypter_errors.log"), 'a') as err:
            err.write("Files not crypted : " + self.currentPath + '\n')
            for p in errors:
                err.write(p + '\n')

if __name__ == '__main__':
    os.chdir(os.path.dirname(__file__))
    print(os.getcwd())
    root = tk.Tk()
    root.title("PyCrypter")
    root.resizable(False, False)
    myApp = CrypterGUI(root)
    root.mainloop()
