import os
from _datetime import datetime

import hurry.filesize

from tkinter import Tk, Frame, Label, Entry, Button
from tkinter.constants import VERTICAL, HORIZONTAL
from tkinter.filedialog import askdirectory
from tkinter.messagebox import showerror
from tkinter.ttk import Treeview, Scrollbar

from deterministic_encryption_utils.encryption.Encryption import Encryption
from deterministic_encryption_utils.encryption.VirtualFile import VirtualFile

class Decryptor(object):
    
    def __init__(self):
        self.fileBrowserShadowInformation = dict()
        self.startUI()
        
    def startUI(self):
        self.root = Tk()
        self.root.title('Decryptor')
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        mainFrame = Frame(self.root)
        mainFrame.grid(row=0, column=0, padx=5, pady=5, sticky='nswe')
        mainFrame.rowconfigure(1, weight=1)
        mainFrame.columnconfigure(0, weight=1)
        
        optionsFrame = Frame(mainFrame)
        optionsFrame.grid(row=0, column=0, pady=(5,0), sticky='nswe')
        optionsFrame.columnconfigure(0, pad=5)
        optionsFrame.columnconfigure(1, weight=1)
        optionsFrame.columnconfigure(2, pad=5)
        
        browserFrame = Frame(mainFrame)
        browserFrame.grid(row=1, column=0, pady=(5,0), sticky='nswe')
        browserFrame.rowconfigure(0, weight=1)
        browserFrame.columnconfigure(0, weight=1)
        
        actionFrame = Frame(mainFrame)
        actionFrame.grid(row=2, column=0, pady=(5,0), sticky='e')
        actionFrame.columnconfigure(0, weight=1)
        
        Label(optionsFrame, text="Secret").grid(row=0, column=0, sticky='w')
        self.secret = Entry(optionsFrame)
        self.secret.grid(row=0, column=1, sticky='nswe')
        self.secret.focus_set()
        self.secretToggleButton = Button(optionsFrame, text="Set", command=self.toggleSecret, width=8)
        self.secretToggleButton.grid(row=0, column=2, sticky='e')
        self.secretToggleButton.setvar('set', False)
        
        Label(optionsFrame, text="Encrypted Folder").grid(row=1, column=0, sticky='w')
        self.folderPath = Entry(optionsFrame, state='readonly')
        self.browseButton = Button(optionsFrame, text="Browse", command=self.chooseFolder, width=8)
        self.browseButton.grid(row=1, column=2, sticky='e')
        self.browseButton.configure(state='disabled')
        self.folderPath.grid(row=1, column=1, sticky='nswe')
        
        fileBrowserColumns = ('size', 'modified', 'encrypted name')
        self.fileBrowser = Treeview(browserFrame, columns=fileBrowserColumns)
        self.fileBrowser.heading('#0', text='File')
        for i in range(0, len(fileBrowserColumns)):
            self.fileBrowser.heading('#{0}'.format(i+1), text=fileBrowserColumns[i].title())
        self.fileBrowser.grid(row=0, column=0, sticky='nswe')
        
        scrollBarY = Scrollbar(orient=VERTICAL, command=self.fileBrowser.yview)
        scrollBarX = Scrollbar(orient=HORIZONTAL, command=self.fileBrowser.xview)
        self.fileBrowser['yscroll'] = scrollBarY.set
        self.fileBrowser['xscroll'] = scrollBarX.set
        scrollBarY.grid(in_=browserFrame, row=0, column=1, sticky='ns')
        scrollBarX.grid(in_=browserFrame, row=1, column=0, sticky='ew')
        
        Button(actionFrame, text="Decrypt Selected", command=self.decryptSelected).grid(row=0, column=0)
        Button(actionFrame, text="Decrypt All", command=self.decryptAll).grid(row=0, column=1)
        
        self.root.mainloop()

    def chooseFolder(self):
        dirPath = askdirectory(parent=self.root, mustexist=True)
        self.folderPath.configure(state='normal')
        self.folderPath.delete(0, len(self.folderPath.get()))
        self.folderPath.insert(0, dirPath)
        self.folderPath.configure(state='readonly')
        self.initializeFileBrowser()
        
    def toggleSecret(self):
        if self.secretToggleButton.getvar('set'):
            self.secret.configure(state='normal')
            self.secretToggleButton.setvar('set', False)
            self.secretToggleButton.configure(text='Set')
            self.browseButton.configure(state='disabled')
            self.__clearFileBrowser()
        else:
            if self.secret.get() == '':
                showerror('Invalid Secret', 'The provided secret must not be empty.')
                return
            self.secret.configure(state='readonly')
            self.secretToggleButton.setvar('set', True)
            self.secretToggleButton.configure(text='Change')
            self.browseButton.configure(state='normal')
            self.decryptor = Encryption(self.secret.get(), None, None)
        
    def initializeFileBrowser(self):
        self.__clearFileBrowser()
        self.__initializeFileBrowser(self.decryptor, self.folderPath.get())
        self.fileBrowser.focus_set()
        
    def decryptSelected(self):
        selectedItems = self.fileBrowser.selection()
        if len(selectedItems) < 1:
            return

        destinationFolder = self.__askForDestinationFolder()
        if destinationFolder is None:
            return

        transitiveSelectedItems = set()
        for selectedItem in selectedItems:
            transitiveSelectedItems.update(self.__getAllFileBrowserChildren(selectedItem))
        filteredSelectedItems = filter(lambda x: not x in transitiveSelectedItems, selectedItems)
        
        for selectedItem in filteredSelectedItems:
            self.__decryptFileBrowserItemToDestination(selectedItem, destinationFolder)
    
    
    def decryptAll(self):
        destinationFolder = self.__askForDestinationFolder()
        if destinationFolder is None:
            return
        
        children = self.fileBrowser.get_children('')
        for child in children:
            self.__decryptFileBrowserItemToDestination(child, destinationFolder)
    
    def __getAllFileBrowserChildren(self, identifier):
        children = set()
        queue = list()
        queue.append(identifier)
        while len(queue) > 0:
            for item in self.fileBrowser.get_children(queue.pop()):
                children.add(item)
                queue.append(item)
        return children
    
    def __askForDestinationFolder(self):
        return askdirectory(parent=self.root, mustexist=True, title='Destination Folder')
    
    def __decryptFileBrowserItemToDestination(self, selectedItem, destinationFolder):
        decryptedFileName = self.fileBrowser.item(selectedItem, option='text')
        destinationFullPath = os.path.join(destinationFolder, decryptedFileName)
        encryptedFullPath = self.fileBrowserShadowInformation.get(selectedItem)
        
        if os.path.isdir(encryptedFullPath):
            self.__decryptDirToDestination(encryptedFullPath, destinationFullPath)
        else:
            self.__decryptFileToDestination(encryptedFullPath, destinationFullPath)
            
    def __decryptFileToDestination(self, encryptedFullPath, destinationPath):
        chunkSize = 4096
        encryptedVirtualFile = VirtualFile(encryptedFullPath)
        try:
            decryptedFileSize = self.decryptor.decryptedFileSize(encryptedVirtualFile)
            with open(destinationPath, 'wb') as destinationFile:    
                for offset in range(0, decryptedFileSize, chunkSize):
                    destinationFile.write(self.decryptor.decryptedContent(encryptedVirtualFile, offset, chunkSize))
        finally:
            encryptedVirtualFile.closeFileHandle()
    
    def __decryptDirToDestination(self, encryptedFullPath, destinationFullPath):
        if not os.path.isdir(destinationFullPath):
            os.mkdir(destinationFullPath)
        for entry in os.listdir(encryptedFullPath):
            entryEncryptedFullPath = os.path.join(encryptedFullPath, entry)
            decryptedEntryName = self.decryptor.decryptFileName(entry)
            entryDestinationFullPath = os.path.join(destinationFullPath, decryptedEntryName)
            if os.path.isdir(entryEncryptedFullPath):
                self.__decryptDirToDestination(entryEncryptedFullPath, entryDestinationFullPath)
            else:
                self.__decryptFileToDestination(entryEncryptedFullPath, entryDestinationFullPath)
        
    def __clearFileBrowser(self):
        for child in self.fileBrowser.get_children():
            self.fileBrowser.delete(child)
        self.fileBrowserShadowInformation.clear()
            
    def __initializeFileBrowser(self, decryption, encryptedDir, parent=''):
        for entry in os.listdir(encryptedDir):
            decryptedName = decryption.decryptFileName(entry)
            encryptedFullPath = os.path.join(encryptedDir, entry)

            identifier = None
            printableModificationDate = datetime.fromtimestamp(os.path.getmtime(encryptedFullPath)).strftime('%Y-%m-%d %H:%M:%S')
            fileSize = os.path.getsize(encryptedFullPath)

            if os.path.isfile(encryptedFullPath):
                encryptedVirtualFile = VirtualFile(encryptedFullPath)
                fileSize = decryption.decryptedFileSize(encryptedVirtualFile)
                identifier = self.fileBrowser.insert(parent, 'end', text=decryptedName)
            else:
                identifier = self.fileBrowser.insert(parent, 'end', text=decryptedName)
                self.__initializeFileBrowser(decryption, encryptedFullPath, identifier)
                
            self.fileBrowser.set(identifier, 'size', hurry.filesize.size(fileSize))
            self.fileBrowser.set(identifier, 'modified', printableModificationDate)
            self.fileBrowser.set(identifier, 'encrypted name', entry)
            self.fileBrowserShadowInformation[identifier] = encryptedFullPath
            

def main():
    Decryptor()

if __name__ == '__main__':
    main()